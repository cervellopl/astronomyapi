# create_star_catalog.py
"""
Build the naked-eye star catalogue used by the Sky Map page.

Pulls every star brighter than V 5.5 from SIMBAD once and writes a compact
static/stars.json. The sky map does its own position maths in the browser, so
this file is the only data it needs.

Safe to re-run: an existing catalogue with a plausible star count is left
alone, so a container restart does not re-query SIMBAD.
"""

import json
import os

import requests

TAP_URL = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"
CATALOG_PATH = os.path.join('static', 'stars.json')
MAG_LIMIT = 5.5
# Naked-eye sky is ~2900 stars at V 5.5; anything far below that means a
# truncated download we should redo.
MIN_EXPECTED = 2000
# Label only the genuinely bright ones - more would clutter the chart.
NAME_MAG_LIMIT = 2.5
# Star-like otypes that do not belong on a naked-eye chart: clusters, and
# supernovae (SIMBAD records a peak V for them, so SN 2009jb would otherwise
# sit in Pegasus at V 1.07 forever).
NON_STELLAR_TYPES = {'Cl*', 'GlC', 'OpC', 'As*', 'SN*', 'SN?'}


def _tap(query, timeout=180):
    resp = requests.get(TAP_URL, params={
        'request': 'doQuery', 'lang': 'adql', 'format': 'json', 'query': query,
    }, timeout=timeout)
    resp.raise_for_status()
    return resp.json().get('data', [])


def _clean_designation(main_id):
    """'*  61 Cyg A' -> '61 Cyg A'."""
    name = (main_id or '').strip()
    if name.startswith('*'):
        name = name[1:]
    return ' '.join(name.split())


def fetch_proper_names():
    """{main_id: 'Vega'} for the brightest stars, shortest name wins."""
    rows = _tap(
        "SELECT b.main_id, i.id FROM basic AS b "
        "JOIN allfluxes AS f ON f.oidref = b.oid "
        "JOIN ident AS i ON i.oidref = b.oid "
        f"WHERE f.V <= {NAME_MAG_LIMIT} AND i.id LIKE 'NAME %'")
    names = {}
    for main_id, ident in rows:
        # Skip non-stellar entries that share the magnitude join
        if not (main_id or '').startswith('*'):
            continue  # e.g. 'NAME CMa Dwarf Galaxy' rides along on the flux join
        label = (ident or '')[5:].strip()
        if not label:
            continue
        current = names.get(main_id)
        if current is None or len(label) < len(current):
            names[main_id] = label
    return names


def build_catalog():
    """Write static/stars.json unless a good one is already there."""
    if os.path.isfile(CATALOG_PATH):
        try:
            with open(CATALOG_PATH) as f:
                existing = json.load(f)
            if len(existing.get('stars', [])) >= MIN_EXPECTED:
                print(f"Star catalogue already present "
                      f"({len(existing['stars'])} stars) - skipping download.")
                return True
        except Exception:
            pass  # unreadable/partial file: rebuild it

    print(f"Downloading stars brighter than V {MAG_LIMIT} from SIMBAD...")
    try:
        rows = _tap(
            "SELECT b.main_id, b.ra, b.dec, f.V, b.otype FROM basic AS b "
            "JOIN allfluxes AS f ON f.oidref = b.oid "
            f"WHERE f.V <= {MAG_LIMIT} AND b.ra IS NOT NULL AND b.dec IS NOT NULL")
    except Exception as e:
        print(f"Could not download star catalogue: {e}")
        print("Sky map will report the missing catalogue; it is fetched again "
              "on the next start or on first use.")
        return False

    try:
        names = fetch_proper_names()
    except Exception as e:
        print(f"Proper names unavailable ({e}) - continuing without labels.")
        names = {}

    stars = []
    for main_id, ra, dec, vmag, otype in rows:
        if ra is None or dec is None or vmag is None:
            continue
        # The magnitude join also catches clusters and the odd galaxy; every
        # stellar otype carries a '*', clusters excepted.
        otype = (otype or '').strip()
        if '*' not in otype or otype in NON_STELLAR_TYPES:
            continue
        # [ra_deg, dec_deg, mag, designation, proper name]
        star = [round(float(ra), 5), round(float(dec), 5), round(float(vmag), 2),
                _clean_designation(main_id)]
        proper = names.get(main_id)
        if proper:
            star.append(proper)
        stars.append(star)

    stars.sort(key=lambda s: s[2])

    os.makedirs('static', exist_ok=True)
    with open(CATALOG_PATH, 'w') as f:
        json.dump({'mag_limit': MAG_LIMIT, 'count': len(stars),
                   'source': 'SIMBAD (CDS Strasbourg)', 'stars': stars}, f,
                  separators=(',', ':'))

    named = sum(1 for s in stars if len(s) > 4)
    print(f"Star catalogue written: {len(stars)} stars, {named} named "
          f"({os.path.getsize(CATALOG_PATH) // 1024} KB)")
    return True


if __name__ == '__main__':
    build_catalog()
