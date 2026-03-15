"""
Import variable stars from AAVSO Variable Star Index (VSX)
Source: https://www.aavso.org/vsx/index.php?view=api.object

Uses the VSX api.object endpoint for individual star lookups,
and a built-in catalog of well-known variable stars for
constellation/type-based browsing.
"""

import requests
import json
from models import Object, Type
from database import db


# Well-known variable stars organized by type and constellation
# Used when searching by constellation or type (since api.list is unavailable)
VARIABLE_STAR_CATALOG = [
    # Cepheids (CEP/DCEP)
    "Delta Cep", "Eta Aql", "Zeta Gem", "Beta Dor", "l Car",
    "T Vul", "S Sge", "FF Aql", "RT Aur", "SU Cas",
    "DT Cyg", "SZ Tau", "V473 Lyr", "U Sgr", "W Sgr",
    "X Sgr", "Y Sgr", "S Nor", "V340 Nor", "AH Vel",
    "T Mon", "SV Vul", "RS Pup", "GY Sge", "S Vul",
    # Mira (M)
    "Mira", "Chi Cyg", "R Leo", "R Hya", "R Cas",
    "R And", "R Aql", "R Boo", "R Cen", "R Dra",
    "R Hor", "R Lep", "R Ser", "R Tri", "R UMa",
    "R Vir", "S CrB", "T Cep", "U Ori", "W And",
    "W Hya", "X Oph", "R Car", "R Gem", "R Lyn",
    "R Oct", "R Peg", "R Sct", "S Ori", "T Cas",
    "U Her", "V Mon", "X Cam", "R Cyg", "S Her",
    # Eclipsing (EA/EB/EW)
    "Algol", "Beta Lyr", "W UMa", "U Cep", "RS CVn",
    "AR Lac", "V505 Sgr", "TX UMa", "AI Dra", "RZ Cas",
    "U Sge", "S Equ", "TV Cas", "TW Dra", "WW Aur",
    "YY Gem", "RT And", "SV Cam", "V471 Tau", "AW UMa",
    # RR Lyrae (RR/RRAB/RRC)
    "RR Lyr", "SW And", "SU Dra", "RV UMa", "XZ Cyg",
    "DM Cyg", "AR Per", "TU UMa", "AV Peg", "ST Boo",
    "TV Boo", "UY Cyg", "RV Oct", "X Ari", "SS For",
    # Delta Scuti (DSCT)
    "Delta Sct", "AI Vel", "SX Phe", "CY Aqr", "DQ Cep",
    "V703 Sco", "VZ Cnc", "AD CMi", "BS Aqr", "YZ Boo",
    # Semi-Regular (SR/SRA/SRB)
    "Z UMa", "RR CrB", "Y CVn", "V CVn", "g Her",
    "AF Cyg", "W Cyg", "EU Del", "UW Her", "SV Peg",
    "TX Psc", "RX Boo", "ST Her", "TU CVn", "EP Aqr",
    # Dwarf Novae (UG/UGSS)
    "SS Cyg", "U Gem", "Z Cam", "SU UMa", "VW Hyi",
    "T Leo", "AB Dra", "SS Aur", "AH Her", "RU Peg",
    "WZ Sge", "EX Hya", "AM Her", "AN UMa", "VY Scl",
    # Irregular/Slow Irregular (L/LB)
    "TW Hor", "W Ori", "RX Lep", "CO Cyg", "UU Aur",
    # Rotating (BY/RS/ROT)
    "BY Dra", "V833 Tau", "EV Lac", "YY Gem", "AU Mic",
    # Gamma Doradus (GDOR)
    "Gamma Dor", "9 Aur", "HR 8799",
    # T Tauri
    "T Tau", "RU Lup", "S CrA",
    # R CrB type
    "R CrB", "RY Sgr", "SU Tau",
    # Novae
    "T CrB", "RS Oph", "T Pyx", "U Sco", "V2491 Cyg",
]


def lookup_vsx_star(name):
    """
    Look up a single variable star using the VSX api.object endpoint.

    Args:
        name: Star name or identifier

    Returns:
        Dictionary from VSX API or None
    """
    url = "https://www.aavso.org/vsx/index.php"

    params = {
        'view': 'api.object',
        'format': 'json',
        'ident': name
    }

    try:
        response = requests.get(url, params=params, timeout=15,
                                allow_redirects=True)
        response.raise_for_status()

        data = response.json()

        vsx_obj = data.get('VSXObject')
        if vsx_obj and vsx_obj.get('Name'):
            return vsx_obj

        return None

    except Exception as e:
        print(f"  Error looking up {name}: {str(e)}")
        return None


def parse_vsx_object(obj):
    """
    Parse a VSX API object into our standard format.

    Args:
        obj: Dictionary from VSX API response

    Returns:
        Dictionary with name, designation, props
    """
    try:
        name = obj.get('Name', '').strip()
        if not name:
            return None

        auid = obj.get('AUID', '')

        # Build designation from AUID or name
        designation = auid if auid else name

        # Extract coordinates
        ra = obj.get('RA2000', '')
        dec = obj.get('Declination2000', '')

        # Extract variability info
        var_type = obj.get('VariabilityType', '')
        period = obj.get('Period', '')
        epoch = obj.get('Epoch', '')

        # Extract magnitude info
        max_mag = obj.get('MaxMag', '')
        min_mag = obj.get('MinMag', '')

        # Extract spectral type and constellation
        spectral = obj.get('SpectralType', '')
        constellation = obj.get('Constellation', '')

        # Build properties
        props = {
            'source': 'AAVSO VSX',
            'variability_type': var_type
        }

        if auid:
            props['auid'] = auid

        if ra:
            props['ra_2000'] = ra

        if dec:
            props['dec_2000'] = dec

        if period:
            props['period_days'] = period

        if epoch:
            props['epoch'] = epoch

        if max_mag:
            props['max_magnitude'] = max_mag

        if min_mag:
            props['min_magnitude'] = min_mag

        if max_mag and min_mag:
            props['magnitude_range'] = f"{max_mag} to {min_mag}"

        if spectral:
            props['spectral_type'] = spectral

        if constellation:
            props['constellation'] = constellation

        # OID from VSX
        oid = obj.get('OID', '')
        if oid:
            props['vsx_oid'] = oid

        return {
            'name': name,
            'designation': designation,
            'props': props
        }

    except Exception as e:
        print(f"Error parsing VSX object: {str(e)}")
        return None


def search_vsx(name=None, constellation=None, var_type=None, max_records=100):
    """
    Search VSX for variable stars using api.object endpoint.

    When a name is provided, looks up that specific star.
    When constellation or type filters are provided, searches the
    built-in catalog and looks up matching stars from VSX.

    Args:
        name: Star name to look up directly via VSX
        constellation: Constellation abbreviation filter (e.g. 'Cep', 'Ori')
        var_type: Variable type filter (e.g. 'CEP', 'M', 'EA')
        max_records: Maximum number of records to return

    Returns:
        List of variable star dictionaries or None on error
    """

    results = []

    if name:
        # Direct lookup by name
        print(f"Looking up '{name}' in VSX...")
        vsx_obj = lookup_vsx_star(name)
        if vsx_obj:
            star = parse_vsx_object(vsx_obj)
            if star:
                results.append(star)
                print(f"  Found: {star['name']}")
            else:
                print(f"  Could not parse result for '{name}'")
        else:
            print(f"  '{name}' not found in VSX")

        return results

    # Browse catalog by constellation/type
    print(f"Browsing variable star catalog...")
    if constellation:
        print(f"  Constellation filter: {constellation}")
    if var_type:
        print(f"  Type filter: {var_type}")

    candidates = VARIABLE_STAR_CATALOG[:max_records * 2]
    fetched = 0

    for star_name in candidates:
        if fetched >= max_records:
            break

        vsx_obj = lookup_vsx_star(star_name)
        if not vsx_obj:
            continue

        # Apply constellation filter
        if constellation and vsx_obj.get('Constellation', '') != constellation:
            continue

        # Apply type filter
        if var_type:
            obj_type = vsx_obj.get('VariabilityType', '')
            # Match if the filter is contained in the type
            # e.g. 'M' matches 'M', 'CEP' matches 'DCEP', 'EA' matches 'EA/SD'
            if var_type not in obj_type and obj_type not in var_type:
                continue

        star = parse_vsx_object(vsx_obj)
        if star:
            results.append(star)
            fetched += 1
            print(f"  [{fetched}/{max_records}] {star['name']} "
                  f"({vsx_obj.get('VariabilityType', '?')}, "
                  f"{vsx_obj.get('Constellation', '?')})")

    print(f"\nFound {len(results)} variable stars")
    return results


def import_vsx_stars(name=None, constellation=None, var_type=None,
                     max_records=100, update_existing=False):
    """
    Search VSX and import variable stars into the database.

    Args:
        name: Star name to look up directly
        constellation: Constellation abbreviation filter
        var_type: Variable star type filter
        max_records: Maximum records to fetch
        update_existing: Whether to update existing entries

    Returns:
        Dictionary with import statistics
    """

    print("=" * 70)
    print("IMPORTING VARIABLE STARS FROM AAVSO VSX")
    print("=" * 70)

    # Search VSX
    results = search_vsx(name=name, constellation=constellation,
                         var_type=var_type, max_records=max_records)

    if results is None:
        return {'error': 'Failed to search VSX'}

    if not results:
        return {
            'total_found': 0,
            'parsed': 0,
            'added': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

    # Get or create Variable Star type
    var_star_type = Type.query.filter_by(name='Variable Star').first()
    if not var_star_type:
        from sqlalchemy import func
        max_id = db.session.query(func.max(Type.id)).scalar()
        new_id = (max_id or 0) + 1

        var_star_type = Type(id=new_id, name='Variable Star')
        db.session.add(var_star_type)
        db.session.commit()
        print(f"Created Variable Star type with ID {new_id}")

    stats = {
        'total_found': len(results),
        'parsed': len(results),
        'added': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }

    # Get max object ID
    from sqlalchemy import func
    max_obj_id = db.session.query(func.max(Object.id)).scalar()
    next_id = (max_obj_id or 0) + 1

    # Import to database
    for star_data in results:
        try:
            star_name = star_data['name']
            designation = star_data['designation']

            # Check if star exists
            existing = None
            if designation:
                existing = Object.query.filter_by(desination=designation).first()

            if not existing:
                existing = Object.query.filter_by(name=star_name).first()

            if existing:
                if update_existing:
                    existing.props = json.dumps(star_data['props'])
                    stats['updated'] += 1
                    print(f"  Updated: {star_name}")
                else:
                    stats['skipped'] += 1
            else:
                new_star = Object(
                    id=next_id,
                    name=star_name,
                    desination=designation,
                    type=var_star_type.id,
                    props=json.dumps(star_data['props'])
                )

                db.session.add(new_star)
                stats['added'] += 1
                next_id += 1

        except Exception as e:
            stats['errors'] += 1
            print(f"  Error importing {star_data.get('name', 'unknown')}: {str(e)}")

    # Commit all changes
    try:
        db.session.commit()
        print("\n" + "=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        print(f"Stars found: {stats['total_found']}")
        print(f"Stars added: {stats['added']}")
        print(f"Stars updated: {stats['updated']}")
        print(f"Stars skipped: {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        print("=" * 70)
    except Exception as e:
        db.session.rollback()
        print(f"Error committing to database: {str(e)}")
        stats['error'] = str(e)

    return stats


def sync_vsx_stars(name=None, constellation=None, var_type=None, max_records=100):
    """Synchronize variable stars (update existing and add new)"""
    return import_vsx_stars(name=name, constellation=constellation,
                            var_type=var_type, max_records=max_records,
                            update_existing=True)


if __name__ == '__main__':
    # Example: look up a specific star
    import_vsx_stars(name='Mira')
