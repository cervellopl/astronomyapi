"""
Shared AAVSO "recent observations" summary.

Fetches the last year of AAVSO VSX observations for a variable star and
reduces them to a small summary (latest magnitude, last/first observation
date, span and brightness tendency). Used by both the web AJAX endpoint
(/web/aavso/recent/<star>) and the REST API (/api/aavso/recent[...]), so the
two return byte-for-byte the same JSON.
"""

import urllib.request as _urlreq
import urllib.parse as _urlparse
import datetime as _dt


def _jd_to_date(jd):
    """Convert a Julian Date to an approximate 'YYYY-MM-DD' calendar date."""
    jd_int = int(jd + 0.5)
    l = jd_int + 68569
    n = (4 * l) // 146097
    l = l - (146097 * n + 3) // 4
    i = (4000 * (l + 1)) // 1461001
    l = l - (1461 * i) // 4 + 31
    j = (80 * l) // 2447
    day = l - (2447 * j) // 80
    l = j // 11
    month = j + 2 - 12 * l
    year = 100 * (n - 49) + i + l
    return '{:04d}-{:02d}-{:02d}'.format(year, month, day)


def fetch_recent(star_name):
    """Return a summary dict for a variable star's last year of AAVSO data.

    On success: {obs_count, last_date, last_mag, first_date, days_span,
    tendency, band}. When nothing is found: {'error': ..., 'obs_count': 0}.
    On a fetch/parse failure: {'error': 'Failed to fetch AAVSO data: ...'}.
    Never raises.
    """
    star_name = (star_name or '').strip()
    if not star_name:
        return {'error': 'No star name provided'}

    try:
        # Compute JD range: last 365 days
        now = _dt.datetime.utcnow()
        a = (14 - now.month) // 12
        y = now.year + 4800 - a
        m_val = now.month + 12 * a - 3
        jdn = now.day + (153 * m_val + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd_now = jdn + (now.hour - 12) / 24.0 + now.minute / 1440.0
        jd_from = jd_now - 365

        url = ('https://www.aavso.org/vsx/index.php?view=api.delim'
               '&ident={ident}&fromjd={fromjd:.2f}&tojd={tojd:.2f}'
               '&delimiter=%40%40%40').format(
            ident=_urlparse.quote(star_name),
            fromjd=jd_from,
            tojd=jd_now
        )

        req = _urlreq.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with _urlreq.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode('utf-8', errors='replace')

        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        if len(lines) < 2:
            return {'error': 'No observations found for this star in the past year', 'obs_count': 0}

        # First line is header: JD@@@magnitude@@@uncertainty@@@band@@@...
        headers = [h.strip().lower() for h in lines[0].split('@@@')]

        try:
            jd_idx = headers.index('jd')
        except ValueError:
            jd_idx = 0
        try:
            mag_idx = headers.index('magnitude')
        except ValueError:
            mag_idx = 1
        try:
            band_idx = headers.index('band')
        except ValueError:
            band_idx = 3

        # Parse observation rows — prefer Visual (Vis.) or V band
        obs_all = []
        obs_visual = []
        for line in lines[1:]:
            parts = line.split('@@@')
            if len(parts) <= max(jd_idx, mag_idx, band_idx):
                continue
            try:
                jd_val = float(parts[jd_idx])
                mag_val = parts[mag_idx].strip()
                band_val = parts[band_idx].strip() if band_idx < len(parts) else ''
                if not mag_val or mag_val in ('<', '>'):
                    continue
                is_limit = mag_val.startswith('<') or mag_val.startswith('>')
                mag_num = float(mag_val.lstrip('<>')) if not is_limit else None
                obs_all.append({'jd': jd_val, 'mag': mag_num, 'mag_str': mag_val, 'band': band_val, 'limit': is_limit})
                if band_val.lower() in ('vis.', 'visual', 'v', ''):
                    obs_visual.append({'jd': jd_val, 'mag': mag_num, 'mag_str': mag_val, 'band': band_val, 'limit': is_limit})
            except (ValueError, IndexError):
                continue

        obs_list = obs_visual if obs_visual else obs_all
        obs_list.sort(key=lambda x: x['jd'])

        if not obs_list:
            return {'error': 'No valid observations found', 'obs_count': 0}

        first_obs = obs_list[0]
        last_obs = obs_list[-1]

        last_date = _jd_to_date(last_obs['jd'])
        first_date = _jd_to_date(first_obs['jd'])
        days_span = int(round(last_obs['jd'] - first_obs['jd']))

        # Tendency: compare last 5 obs vs previous 5 obs (actual mag values only)
        real_mags = [o for o in obs_list if o['mag'] is not None]
        tendency = None
        if len(real_mags) >= 4:
            half = min(5, len(real_mags) // 2)
            recent_avg = sum(o['mag'] for o in real_mags[-half:]) / half
            older_avg = sum(o['mag'] for o in real_mags[-2 * half:-half]) / half
            diff = recent_avg - older_avg
            if diff < -0.2:
                tendency = 'brightening'   # magnitude decreasing = brighter
            elif diff > 0.2:
                tendency = 'fading'        # magnitude increasing = fainter
            else:
                tendency = 'stable'

        return {
            'obs_count': len(obs_list),
            'last_date': last_date,
            'last_mag': last_obs['mag_str'],
            'first_date': first_date,
            'days_span': days_span,
            'tendency': tendency,
            'band': last_obs['band'] or 'Visual',
        }

    except Exception as e:
        return {'error': 'Failed to fetch AAVSO data: {}'.format(str(e))}
