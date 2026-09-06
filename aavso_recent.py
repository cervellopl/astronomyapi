"""
Shared AAVSO client.

AAVSO retired the open VSX delimited endpoints (they now sit behind Cloudflare
and answer 403), so everything here goes through the apps.aavso.org v2 API,
which needs a per-user token: Settings -> AAVSO Integration -> API key.

Used by the web AJAX endpoints, the observation form's magnitude check and the
REST API, so all of them return the same JSON for the same star.
"""

import datetime as _dt

import requests as _requests

API_BASE = 'https://apps.aavso.org/v2/api'
# The API paginates at a fixed 10 rows; results come back newest first, so the
# first page is the current state of the star and later pages are history.
PAGE_SIZE = 10
DEFAULT_TIMEOUT = 20

# Band codes used by the v2 API (see /v2/api/schema/)
BAND_NAMES = {
    '0': 'Visual', '1': 'Unknown', '2': 'V', '3': 'B', '4': 'R', '5': 'I',
    '6': 'Orange', '7': 'U', '8': 'CV', '9': 'CR', '10': 'Johnson R',
    '11': 'Johnson I', '13': 'Halpha', '14': 'Halpha-cont', '21': 'Blue',
    '22': 'Green', '23': 'Red', '24': 'Yellow', '26': 'K', '27': 'H',
    '28': 'J', '29': 'Sloan z', '30': 'Stromgren u', '31': 'Stromgren v',
    '32': 'Stromgren b', '33': 'Stromgren y', '34': 'Stromgren Hbw',
    '35': 'Stromgren Hbn', '40': 'Sloan u', '41': 'Sloan g', '42': 'Sloan r',
    '43': 'Sloan i', '44': 'PanSTARRS Z-short', '45': 'PanSTARRS Y',
    '50': 'TG', '51': 'TB', '52': 'TR', '55': 'Optec Wing A',
    '56': 'Optec Wing B', '57': 'Optec Wing C',
}
VISUAL_BANDS = ('0', '2')          # Visual and Johnson V


def band_name(code):
    return BAND_NAMES.get(str(code or '').strip(), str(code or '') or 'Unknown')


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


class AavsoAuthError(Exception):
    """Raised when AAVSO rejects (or is not given) an API key."""


def _get(path, api_key, params=None, timeout=DEFAULT_TIMEOUT):
    """One authenticated GET against the v2 API."""
    if not (api_key or '').strip():
        raise AavsoAuthError('No AAVSO API key set - add one in Settings.')
    resp = _requests.get(
        f'{API_BASE}{path}',
        params=params or {},
        headers={'Authorization': f'Token {api_key.strip()}',
                 'User-Agent': 'astronomyapi observation logger'},
        timeout=timeout)
    if resp.status_code in (401, 403):
        raise AavsoAuthError('AAVSO rejected the API key - check it in Settings.')
    if resp.status_code == 400:
        # The API answers 400 for a target it cannot resolve
        raise ValueError('AAVSO does not recognise this star name')
    resp.raise_for_status()
    return resp.json()


def fetch_star_info(star_name, api_key):
    """VSX summary for a star: AUID, position, magnitude range, type."""
    star_name = (star_name or '').strip()
    if not star_name:
        return {'error': 'No star name provided'}
    try:
        data = _get('/stars/search/', api_key, {'name': star_name})
    except AavsoAuthError as e:
        return {'error': str(e), 'auth': True}
    except Exception as e:
        return {'error': f'Failed to fetch star information: {e}'}
    if not isinstance(data, dict) or data.get('error'):
        return {'error': (data or {}).get('error', 'Star not found in VSX')}
    return {
        'name': data.get('name') or star_name,
        'auid': data.get('auid') or '',
        'ra': data.get('ra'),
        'dec': data.get('dec'),
        'mag_max': data.get('magmax'),
        'mag_min': data.get('magmin'),
        'vartype': data.get('vartype') or '',
    }


def _observation_rows(star_name, api_key, start_date, end_date, max_pages):
    """Photometry rows for a star, newest first, over at most max_pages pages."""
    rows = []
    truncated = False
    total = None
    page = 1
    while page <= max_pages:
        data = _get('/observations/photometry/', api_key, {
            'target': star_name,
            'start_date': start_date,
            'end_date': end_date,
            'page': page,
        })
        if total is None:
            total = data.get('count') or 0
        batch = data.get('results') or []
        rows.extend(batch)
        if not data.get('next') or not batch:
            break
        page += 1
    else:
        truncated = True
    if total and len(rows) < total:
        truncated = True
    return rows, (total or len(rows)), truncated


def _parse_rows(rows):
    """Normalise API rows into {jd, mag, mag_str, band, limit} dicts."""
    parsed = []
    for row in rows:
        try:
            jd = float(row.get('jd_dbl'))
        except (TypeError, ValueError):
            continue
        raw_mag = str(row.get('magnitude') or '').strip()
        if not raw_mag:
            continue
        is_limit = bool(row.get('fainterthan')) or raw_mag[0] in '<>'
        try:
            mag = float(raw_mag.lstrip('<>'))
        except ValueError:
            continue
        code = str(row.get('band') or '')
        parsed.append({
            'jd': jd,
            'mag': None if is_limit else mag,
            # AAVSO's own text, so 6.0 does not come back as 6
            'mag_str': raw_mag if raw_mag[0] in '<>' else (
                ('<' if is_limit else '') + raw_mag),
            'band': band_name(code),
            'band_code': code,
            'limit': is_limit,
            'obscode': row.get('obscode') or '',
            'uncertainty': row.get('uncertainty'),
        })
    return parsed


def fetch_recent(star_name, api_key=None, days=365, max_pages=6):
    """Summarise a star's recent AAVSO observations.

    On success: {obs_count, last_date, last_mag, first_date, days_span,
    tendency, band, ...}. Never raises.
    """
    star_name = (star_name or '').strip()
    if not star_name:
        return {'error': 'No star name provided'}

    now = _dt.datetime.utcnow()
    start = (now - _dt.timedelta(days=days)).strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')

    try:
        rows, total, truncated = _observation_rows(
            star_name, api_key, start, end, max_pages)
    except AavsoAuthError as e:
        return {'error': str(e), 'auth': True, 'obs_count': 0}
    except Exception as e:
        return {'error': f'Failed to fetch AAVSO data: {e}', 'obs_count': 0}

    observations = _parse_rows(rows)
    if not observations:
        return {'error': f'No observations found for this star in the past {days} days',
                'obs_count': 0}

    # Prefer visual/V so the summary matches what a visual observer would see
    visual = [o for o in observations if o['band_code'] in VISUAL_BANDS]
    chosen = visual if visual else observations
    chosen.sort(key=lambda o: o['jd'])          # oldest -> newest

    first_obs, last_obs = chosen[0], chosen[-1]
    real_mags = [o for o in chosen if o['mag'] is not None]

    tendency = None
    if len(real_mags) >= 4:
        half = min(5, len(real_mags) // 2)
        recent_avg = sum(o['mag'] for o in real_mags[-half:]) / half
        older_avg = sum(o['mag'] for o in real_mags[-2 * half:-half]) / half
        diff = recent_avg - older_avg
        if diff < -0.2:
            tendency = 'brightening'
        elif diff > 0.2:
            tendency = 'fading'
        else:
            tendency = 'stable'

    return {
        'obs_count': len(chosen),
        'total_available': total,
        'truncated': truncated,
        'last_date': _jd_to_date(last_obs['jd']),
        'last_mag': last_obs['mag_str'],
        'last_jd': round(last_obs['jd'], 4),
        'last_observer': last_obs['obscode'],
        'first_date': _jd_to_date(first_obs['jd']),
        'days_span': int(round(last_obs['jd'] - first_obs['jd'])),
        'tendency': tendency,
        'band': last_obs['band'] or 'Visual',
    }


def fetch_light_curve(star_name, api_key=None, days=365, max_pages=40):
    """Observation points for a light curve, grouped by band.

    Returns {points: {band: [{jd, date, mag, uncertainty}]}, ...}. Faint/bright
    limits are skipped: they are not measurements.
    """
    star_name = (star_name or '').strip()
    if not star_name:
        return {'error': 'No star name provided'}

    now = _dt.datetime.utcnow()
    start = (now - _dt.timedelta(days=days)).strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')

    try:
        rows, total, truncated = _observation_rows(
            star_name, api_key, start, end, max_pages)
    except AavsoAuthError as e:
        return {'error': str(e), 'auth': True}
    except Exception as e:
        return {'error': f'Failed to fetch AAVSO data: {e}'}

    observations = [o for o in _parse_rows(rows) if not o['limit']]
    if not observations:
        return {'error': f'No valid magnitude observations for this star in the past {days} days'}

    by_band = {}
    for obs in sorted(observations, key=lambda o: o['jd']):
        by_band.setdefault(obs['band'], []).append({
            'jd': round(obs['jd'], 4),
            'date': _jd_to_date(obs['jd']),
            'mag': obs['mag'],
            'uncertainty': obs['uncertainty'],
        })

    mags = [o['mag'] for o in observations]
    return {
        'star': star_name,
        'days': days,
        'obs_count': len(observations),
        'total_available': total,
        'truncated': truncated,
        'mag_min': min(mags),
        'mag_max': max(mags),
        'points': by_band,
    }
