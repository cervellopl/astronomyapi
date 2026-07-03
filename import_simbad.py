"""
Search and import astronomical objects from SIMBAD (CDS Strasbourg)
Source: https://simbad.cds.unistra.fr/simbad/

Uses SIMBAD TAP service for queries and sim-id for individual lookups.
"""

import requests
import json
import re
from models import Object, Type
from database import db


# SIMBAD object type mapping to our types
SIMBAD_TYPE_MAP = {
    'V*': 'Variable Star',
    'LP*': 'Variable Star',
    'Mi*': 'Variable Star',
    'Ce*': 'Variable Star',
    'RR*': 'Variable Star',
    'dS*': 'Variable Star',
    'EB*': 'Variable Star',
    'El*': 'Variable Star',
    'SB*': 'Variable Star',
    'CV*': 'Variable Star',
    'No*': 'Variable Star',
    'DN*': 'Variable Star',
    'sr*': 'Variable Star',
    'Pu*': 'Variable Star',
    'bC*': 'Variable Star',
    'gD*': 'Variable Star',
    'BY*': 'Variable Star',
    'RS*': 'Variable Star',
    'Ir*': 'Variable Star',
    'Or*': 'Variable Star',
    'WR*': 'Variable Star',
    'Be*': 'Variable Star',
    'RCB': 'Variable Star',
    'SN*': 'Variable Star',
    'GlC': 'Globular Cluster',
    'OpC': 'Open Cluster',
    'Cl*': 'Cluster',
    'As*': 'Cluster',
    'G': 'Galaxy',
    'GiG': 'Galaxy',
    'GiP': 'Galaxy',
    'BiC': 'Galaxy',
    'SyG': 'Galaxy',
    'AGN': 'Galaxy',
    'QSO': 'Galaxy',
    'Bla': 'Galaxy',
    'LeI': 'Galaxy',
    'SBG': 'Galaxy',
    'IG': 'Galaxy',
    'PN': 'Planetary Nebula',
    'HII': 'Nebula',
    'RNe': 'Nebula',
    'SNR': 'Nebula',
    'ISM': 'Nebula',
    'Cld': 'Nebula',
    'DNe': 'Nebula',
    'EmO': 'Nebula',
    '*': 'Star',
    '**': 'Double Star',
    'PM*': 'Star',
    'HB*': 'Star',
    'Em*': 'Star',
    'Psr': 'Pulsar',
    'Com': 'Comet',
    'Ast': 'Asteroid',
    'Pl': 'Planet',
}


# The 88 IAU constellations, keyed by their 3-letter abbreviation. Variable
# star designations encode the constellation as a genitive abbreviation suffix
# (e.g. "R Cas", "SS Cyg"), so the abbreviation doubles as a name-suffix filter.
CONSTELLATIONS = {
    'And': 'Andromeda', 'Ant': 'Antlia', 'Aps': 'Apus', 'Aql': 'Aquila',
    'Aqr': 'Aquarius', 'Ara': 'Ara', 'Ari': 'Aries', 'Aur': 'Auriga',
    'Boo': 'Bootes', 'CMa': 'Canis Major', 'CMi': 'Canis Minor', 'CVn': 'Canes Venatici',
    'Cae': 'Caelum', 'Cam': 'Camelopardalis', 'Cap': 'Capricornus', 'Car': 'Carina',
    'Cas': 'Cassiopeia', 'Cen': 'Centaurus', 'Cep': 'Cepheus', 'Cet': 'Cetus',
    'Cha': 'Chamaeleon', 'Cir': 'Circinus', 'Cnc': 'Cancer', 'Col': 'Columba',
    'Com': 'Coma Berenices', 'CrA': 'Corona Australis', 'CrB': 'Corona Borealis',
    'Crt': 'Crater', 'Cru': 'Crux', 'Crv': 'Corvus', 'Cyg': 'Cygnus',
    'Del': 'Delphinus', 'Dor': 'Dorado', 'Dra': 'Draco', 'Equ': 'Equuleus',
    'Eri': 'Eridanus', 'For': 'Fornax', 'Gem': 'Gemini', 'Gru': 'Grus',
    'Her': 'Hercules', 'Hor': 'Horologium', 'Hya': 'Hydra', 'Hyi': 'Hydrus',
    'Ind': 'Indus', 'LMi': 'Leo Minor', 'Lac': 'Lacerta', 'Leo': 'Leo',
    'Lep': 'Lepus', 'Lib': 'Libra', 'Lup': 'Lupus', 'Lyn': 'Lynx',
    'Lyr': 'Lyra', 'Men': 'Mensa', 'Mic': 'Microscopium', 'Mon': 'Monoceros',
    'Mus': 'Musca', 'Nor': 'Norma', 'Oct': 'Octans', 'Oph': 'Ophiuchus',
    'Ori': 'Orion', 'Pav': 'Pavo', 'Peg': 'Pegasus', 'Per': 'Perseus',
    'Phe': 'Phoenix', 'Pic': 'Pictor', 'PsA': 'Piscis Austrinus', 'Psc': 'Pisces',
    'Pup': 'Puppis', 'Pyx': 'Pyxis', 'Ret': 'Reticulum', 'Scl': 'Sculptor',
    'Sco': 'Scorpius', 'Sct': 'Scutum', 'Ser': 'Serpens', 'Sex': 'Sextans',
    'Sge': 'Sagitta', 'Sgr': 'Sagittarius', 'Tau': 'Taurus', 'Tel': 'Telescopium',
    'TrA': 'Triangulum Australe', 'Tri': 'Triangulum', 'Tuc': 'Tucana', 'UMa': 'Ursa Major',
    'UMi': 'Ursa Minor', 'Vel': 'Vela', 'Vir': 'Virgo', 'Vol': 'Volans', 'Vul': 'Vulpecula',
}

# Case-insensitive lookup from full name / abbreviation to the canonical abbreviation
_CONSTELLATION_LOOKUP = {}
for _abbr, _name in CONSTELLATIONS.items():
    _CONSTELLATION_LOOKUP[_abbr.lower()] = _abbr
    _CONSTELLATION_LOOKUP[_name.lower()] = _abbr


# Variable-star type search strategies. Each entry says how to filter SIMBAD:
#   'otype'  -> match basic.otype directly (fast, one table)
#   'vartyp' -> match GCVS variability types in the mesVar table via EXISTS
#               (needed for sub-types like SRA/SRB that have no distinct otype;
#               slower because mesVar is very large)
VARIABLE_TYPE_QUERIES = {
    'Mira':             {'otype': ['Mi*'], 'desc': 'Mira (long-period) variables'},
    'Semiregular':      {'vartyp': ['SR', 'SRA', 'SRB', 'SRC', 'SRD', 'SR-SA', 'SR+L'],
                         'desc': 'Semiregular variables (SR, SRA, SRB, ...)'},
    'Long-Period':      {'otype': ['LP*'], 'desc': 'Long-period / slow irregular variables'},
    'RR Lyrae':         {'otype': ['RR*'], 'desc': 'RR Lyrae variables'},
    'Cepheid':          {'otype': ['Ce*', 'cC*', 'WV*'], 'desc': 'Cepheid variables (classical & type II)'},
    'Delta Scuti':      {'otype': ['dS*'], 'desc': 'Delta Scuti variables'},
    'RV Tauri':         {'vartyp': ['RV', 'RVA', 'RVB'], 'desc': 'RV Tauri variables'},
    'Irregular':        {'otype': ['Ir*', 'Or*'], 'desc': 'Irregular variables'},
    'Eclipsing Binary': {'otype': ['EB*'], 'desc': 'Eclipsing binaries'},
    'Any variable':     {'desc': 'Any named variable star in the constellation'},
}


def normalize_constellation(value):
    """Return the canonical 3-letter constellation abbreviation, or None."""
    if not value:
        return None
    return _CONSTELLATION_LOOKUP.get(str(value).strip().lower())


def search_variables_by_constellation(var_types, constellation, max_records=50):
    """Find variable stars of one or more types within a constellation.

    Variable stars are matched by their designation suffix (e.g. "V* R Cas"
    for Cassiopeia). ``var_types`` may be a single type or a list of types;
    each is resolved against VARIABLE_TYPE_QUERIES (fast ``otype`` filter or a
    mesVar GCVS-type filter). Any unrecognised value is treated as a raw GCVS
    variability code (prefix match, e.g. "SRA"). Multiple types are combined
    with OR, so "Mira" + "Semiregular" returns stars of either type.

    Each result includes the star's maximum and minimum brightness (GCVS
    Vmax/Vmin) from the mesVar table.

    Returns a list of object dictionaries (possibly empty).
    """
    abbr = normalize_constellation(constellation)
    if not abbr:
        return []
    # Abbreviations are a fixed vocabulary, but sanitise defensively anyway.
    safe_abbr = abbr.replace("'", "")
    name_filter = f"b.main_id LIKE 'V* % {safe_abbr}'"

    # Accept a single type or a list of types
    if isinstance(var_types, str):
        var_types = [var_types]
    var_types = [v for v in (var_types or []) if v]

    def _quote(codes):
        return ",".join("'%s'" % c.replace("'", "") for c in codes)

    otype_codes = set()
    vartyp_codes = set()
    raw_codes = []          # unrecognised values -> GCVS code prefix match
    any_variable = False

    for vt in var_types:
        spec = VARIABLE_TYPE_QUERIES.get(vt)
        if spec is None:
            code = str(vt).replace("'", "").strip().upper()
            if code:
                raw_codes.append(code)
        elif spec.get('otype'):
            otype_codes.update(spec['otype'])
        elif spec.get('vartyp'):
            vartyp_codes.update(spec['vartyp'])
        else:
            any_variable = True  # 'Any variable' - no type restriction

    # Build the (OR-combined) type condition
    type_clauses = []
    if not any_variable and var_types:
        if otype_codes:
            type_clauses.append(f"b.otype IN ({_quote(sorted(otype_codes))})")
        if vartyp_codes:
            type_clauses.append(
                f"EXISTS (SELECT 1 FROM mesVar AS v2 WHERE v2.oidref = b.oid "
                f"AND v2.vartyp IN ({_quote(sorted(vartyp_codes))}))")
        for code in raw_codes:
            type_clauses.append(
                f"EXISTS (SELECT 1 FROM mesVar AS v2 WHERE v2.oidref = b.oid "
                f"AND v2.vartyp LIKE '{code}%')")

    where = name_filter
    if type_clauses:
        where += " AND (" + " OR ".join(type_clauses) + ")"

    # LEFT JOIN mesVar for the max/min brightness of every returned star.
    # Note: ORDER BY must use the unqualified column name (SIMBAD ADQL quirk).
    adql = (
        f"SELECT TOP {max_records} b.main_id, b.ra, b.dec, b.otype_txt, b.sp_type, "
        f"MIN(v.vmax) AS vmax, MAX(v.vmin) AS vmin "
        f"FROM basic AS b LEFT OUTER JOIN mesVar AS v ON v.oidref = b.oid "
        f"WHERE {where} "
        f"GROUP BY b.main_id, b.ra, b.dec, b.otype_txt, b.sp_type "
        f"ORDER BY main_id")

    # mesVar EXISTS scans are slow, so allow a longer timeout when used
    needs_mesvar = bool(vartyp_codes or raw_codes)
    return run_tap_query(adql, max_records, timeout=90 if needs_mesvar else 45)


def find_existing_object(name, main_id=None):
    """Return an already-imported Object matching this SIMBAD result, or None.

    Mirrors the duplicate check in import_simbad_object so the UI can disable
    the Add button for objects that are already in the database.
    """
    from models import Object
    existing = Object.query.filter_by(name=name).first()
    if not existing and main_id and main_id != name:
        existing = Object.query.filter_by(name=main_id).first()
    if not existing and main_id:
        existing = Object.query.filter_by(desination=main_id).first()
    return existing


def ra_deg_to_hms(ra_deg):
    """Convert RA from degrees to HH:MM:SS.ss format"""
    if ra_deg is None:
        return ''
    ra_h = ra_deg / 15.0
    h = int(ra_h)
    m = int((ra_h - h) * 60)
    s = ((ra_h - h) * 60 - m) * 60
    return f"{h:02d}:{m:02d}:{s:05.2f}"


def dec_deg_to_dms(dec_deg):
    """Convert Dec from degrees to DD:MM:SS.s format"""
    if dec_deg is None:
        return ''
    sign = '+' if dec_deg >= 0 else '-'
    dec_abs = abs(dec_deg)
    d = int(dec_abs)
    m = int((dec_abs - d) * 60)
    s = ((dec_abs - d) * 60 - m) * 60
    return f"{sign}{d:02d}:{m:02d}:{s:04.1f}"


def search_simbad(query, search_type='name', max_records=50,
                  var_type=None, constellation=None):
    """
    Search SIMBAD for astronomical objects.

    Args:
        query: Search term (object name, coordinates, etc.)
        search_type: 'name', 'wildcard', 'type_variable', or
            'variable_constellation' (variable type within a constellation)
        max_records: Maximum results to return
        var_type: Variable-star type (used with 'variable_constellation')
        constellation: Constellation name or abbreviation (used with
            'variable_constellation')

    Returns:
        List of object dictionaries or None on error
    """
    results = []

    if search_type == 'variable_constellation':
        return search_variables_by_constellation(var_type, constellation, max_records)

    if search_type == 'name':
        # Direct identifier lookup via sim-id
        result = lookup_simbad_object(query)
        if result:
            results.append(result)
        return results

    elif search_type == 'wildcard':
        # Use basic table for wildcard search
        safe_query = query.replace("'", "''")
        # If query already has %, use as-is; otherwise wrap with %
        if '%' not in safe_query:
            safe_query = f'%{safe_query}%'
        adql = (
            f"SELECT TOP {max_records} "
            f"main_id, ra, dec, otype_txt, sp_type "
            f"FROM basic "
            f"WHERE main_id LIKE '{safe_query}' "
            f"ORDER BY main_id"
        )
        return run_tap_query(adql, max_records)

    elif search_type == 'type_variable':
        # Search for variable stars using TAP
        safe_query = query.replace("'", "''") if query else ''
        adql = (
            f"SELECT TOP {max_records} "
            f"main_id, ra, dec, otype_txt, sp_type "
            f"FROM basic "
            f"WHERE otype_txt = 'Variable Star' "
        )
        if safe_query:
            adql += f"AND main_id LIKE '%{safe_query}%' "
        adql += "ORDER BY main_id"
        return run_tap_query(adql, max_records)

    return results


def lookup_simbad_object(name):
    """
    Look up a single object by identifier using SIMBAD TAP service.

    Args:
        name: Object identifier (e.g., 'M31', 'Algol', 'NGC 7000')

    Returns:
        Dictionary with object data or None
    """
    safe_name = name.replace("'", "''")

    # Use TAP with ident table to resolve identifiers to main object
    adql = (
        f"SELECT TOP 1 b.main_id, b.ra, b.dec, b.otype_txt, b.sp_type "
        f"FROM ident AS i "
        f"JOIN basic AS b ON i.oidref = b.oid "
        f"WHERE i.id = '{safe_name}'"
    )

    results = run_tap_query(adql, 1)
    if results:
        return results[0]

    # Fallback: try direct main_id match
    adql2 = (
        f"SELECT TOP 1 main_id, ra, dec, otype_txt, sp_type "
        f"FROM basic "
        f"WHERE main_id = '{safe_name}'"
    )
    results = run_tap_query(adql2, 1)
    if results:
        return results[0]

    # Fallback: try LIKE match
    adql3 = (
        f"SELECT TOP 5 main_id, ra, dec, otype_txt, sp_type "
        f"FROM basic "
        f"WHERE main_id LIKE '%{safe_name}%' "
        f"ORDER BY main_id"
    )
    results = run_tap_query(adql3, 5)
    if results:
        return results[0]

    print(f"  No SIMBAD result for '{name}'")
    return None


def run_tap_query(adql, max_records=50, timeout=30):
    """
    Execute an ADQL query against SIMBAD TAP service.

    Args:
        adql: ADQL query string
        max_records: Maximum records
        timeout: HTTP timeout in seconds (raise for heavy joins, e.g. mesVar)

    Returns:
        List of object dictionaries
    """
    url = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"
    params = {
        'request': 'doQuery',
        'lang': 'adql',
        'format': 'json',
        'query': adql
    }

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        results = []
        # TAP JSON format has 'data' array with column values
        columns = [col['name'] for col in data.get('metadata', [])]
        rows = data.get('data', [])

        for row in rows[:max_records]:
            row_dict = dict(zip(columns, row))

            main_id = row_dict.get('main_id', '')
            ra_deg = row_dict.get('ra')
            dec_deg = row_dict.get('dec')
            otype = row_dict.get('otype_txt', '') or ''
            sp_type = row_dict.get('sp_type', '') or ''
            flux = row_dict.get('flux', '') or ''

            ra_hms = ra_deg_to_hms(ra_deg) if ra_deg else ''
            dec_dms = dec_deg_to_dms(dec_deg) if dec_deg else ''

            # Maximum / minimum brightness (GCVS Vmax/Vmin) when present
            def _fmt_mag(val):
                try:
                    return f"{float(val):.1f}" if val is not None else ''
                except (TypeError, ValueError):
                    return ''
            mag_max = _fmt_mag(row_dict.get('vmax'))
            mag_min = _fmt_mag(row_dict.get('vmin'))

            # Strip SIMBAD prefixes like "V* ", "* ", "** " from display name
            display_name = re.sub(r'^(V\*|NAME|\*\*|\*)\s+', '', main_id).strip() or main_id

            results.append({
                'main_id': main_id,
                'name': display_name,
                'ra_deg': ra_deg,
                'dec_deg': dec_deg,
                'ra_hms': ra_hms,
                'dec_dms': dec_dms,
                'otype_short': otype,
                'otype_long': otype,
                'spectral_type': sp_type,
                'magnitude_v': str(flux) if flux else '',
                'mag_max': mag_max,
                'mag_min': mag_min,
                'alt_names': '',
            })

        return results

    except Exception as e:
        print(f"  SIMBAD TAP query error: {str(e)}")
        return []


def get_our_type_name(simbad_otype):
    """Map SIMBAD object type to our type name"""
    if not simbad_otype:
        return 'Star'

    # Try direct match first
    otype = simbad_otype.strip().rstrip('*').strip()
    if simbad_otype.strip() in SIMBAD_TYPE_MAP:
        return SIMBAD_TYPE_MAP[simbad_otype.strip()]

    # Try partial matches
    for key, val in SIMBAD_TYPE_MAP.items():
        if key in simbad_otype:
            return val

    # Check description for variable star keywords
    lower = simbad_otype.lower()
    if 'var' in lower or 'eclips' in lower or 'cephe' in lower or 'mira' in lower:
        return 'Variable Star'
    if 'galax' in lower or 'qso' in lower or 'agn' in lower:
        return 'Galaxy'
    if 'nebul' in lower or 'hii' in lower:
        return 'Nebula'
    if 'cluster' in lower:
        return 'Cluster'

    return 'Star'


def import_simbad_object(obj_data):
    """
    Import a single SIMBAD object into the database.

    Args:
        obj_data: Dictionary from search_simbad/lookup_simbad_object

    Returns:
        Dictionary with import result
    """
    from sqlalchemy import func

    name = obj_data['name']
    main_id = obj_data['main_id']

    # Check if already exists
    existing = Object.query.filter_by(name=name).first()
    if not existing and main_id != name:
        existing = Object.query.filter_by(name=main_id).first()
    if not existing:
        existing = Object.query.filter_by(desination=main_id).first()

    if existing:
        return {'status': 'exists', 'name': name, 'id': existing.id}

    # Determine our type
    type_name = get_our_type_name(obj_data.get('otype_short', ''))

    # Get or create the type
    obj_type = Type.query.filter_by(name=type_name).first()
    if not obj_type:
        max_type_id = db.session.query(func.max(Type.id)).scalar()
        new_type_id = (max_type_id or 0) + 1
        obj_type = Type(id=new_type_id, name=type_name)
        db.session.add(obj_type)
        db.session.commit()
        print(f"  Created type '{type_name}' with ID {new_type_id}")

    # Build properties
    props = {
        'source': 'SIMBAD',
        'simbad_id': main_id,
    }

    if obj_data.get('ra_hms'):
        props['ra_2000'] = obj_data['ra_hms']
    if obj_data.get('dec_dms'):
        props['dec_2000'] = obj_data['dec_dms']
    if obj_data.get('ra_deg') is not None:
        props['ra_deg'] = obj_data['ra_deg']
    if obj_data.get('dec_deg') is not None:
        props['dec_deg'] = obj_data['dec_deg']
    if obj_data.get('otype_short'):
        props['object_type'] = obj_data['otype_short']
    if obj_data.get('otype_long'):
        props['object_type_long'] = obj_data['otype_long']
    if obj_data.get('spectral_type'):
        props['spectral_type'] = obj_data['spectral_type']
    if obj_data.get('magnitude_v'):
        props['magnitude_v'] = obj_data['magnitude_v']
    if obj_data.get('alt_names'):
        props['alt_names'] = obj_data['alt_names']

    # Get next object ID
    max_obj_id = db.session.query(func.max(Object.id)).scalar()
    next_id = (max_obj_id or 0) + 1

    new_obj = Object(
        id=next_id,
        name=name,
        desination=main_id,
        type=obj_type.id,
        props=json.dumps(props)
    )
    db.session.add(new_obj)
    db.session.commit()

    return {'status': 'added', 'name': name, 'id': next_id, 'type': type_name}
