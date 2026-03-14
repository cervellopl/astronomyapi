"""
Import comets from Minor Planet Center
Source: https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt
"""

import requests
import re
from datetime import datetime
from models import Object, Type
from database import db
import json

def parse_mpc_comet_line(line):
    """
    Parse a line from MPC Soft00Cmt.txt file
    Format documentation: https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
    
    Columns:
    1-4    Periodic comet number
    5      Orbit type (C, P, D, X, A, I)
    6-12   Provisional designation
    15-18  Year of perihelion passage
    20-21  Month of perihelion passage
    23-29  Day of perihelion passage (TT)
    31-39  Perihelion distance (AU)
    42-49  Orbital eccentricity
    52-59  Argument of perihelion (degrees)
    62-69  Longitude of ascending node (degrees)
    72-79  Inclination (degrees)
    82-85  Year of epoch for elements
    87-88  Month of epoch
    90-91  Day of epoch
    93-100 Absolute magnitude
    103-107 Slope parameter
    109-158 Designation and Name
    """
    
    try:
        # Check if line is long enough
        if len(line) < 100:
            return None
        
        # Extract comet number (periodic comets only)
        comet_num = line[0:4].strip()
        
        # Extract orbit type
        orbit_type = line[4:5].strip()
        
        # Extract provisional designation
        prov_desig = line[5:12].strip()
        
        # Extract perihelion data
        try:
            peri_year = int(line[14:18])
            peri_month = int(line[19:21])
            peri_day = float(line[22:29])
        except:
            peri_year = peri_month = peri_day = None
        
        # Extract orbital elements
        try:
            perihelion_dist = float(line[30:39])
        except:
            perihelion_dist = None
        
        try:
            eccentricity = float(line[41:49])
        except:
            eccentricity = None
        
        try:
            arg_perihelion = float(line[51:59])
        except:
            arg_perihelion = None
        
        try:
            long_asc_node = float(line[61:69])
        except:
            long_asc_node = None
        
        try:
            inclination = float(line[71:79])
        except:
            inclination = None
        
        # Extract magnitude data
        try:
            abs_magnitude = float(line[91:95])
        except:
            abs_magnitude = None
        
        try:
            slope_param = float(line[96:100])
        except:
            slope_param = None
        
        # Extract name (this is the most important part)
        name_part = line[102:158].strip() if len(line) > 102 else ""
        
        # Skip if no name
        if not name_part:
            return None
        
        # Build designation
        if comet_num:
            # Periodic comet
            designation = f"{comet_num}P/{prov_desig}" if prov_desig else f"{comet_num}P"
        elif prov_desig:
            # Non-periodic comet with provisional designation
            designation = f"{orbit_type}/{prov_desig}"
        else:
            designation = None
        
        # Create properties JSON
        props = {
            "orbit_type": orbit_type,
            "source": "Minor Planet Center"
        }
        
        if perihelion_dist:
            props["perihelion_distance_au"] = perihelion_dist
        
        if eccentricity:
            props["eccentricity"] = eccentricity
        
        if peri_year and peri_month:
            props["perihelion_date"] = f"{peri_year}-{peri_month:02d}-{int(peri_day):02d}"
        
        if arg_perihelion:
            props["argument_perihelion_deg"] = arg_perihelion
        
        if long_asc_node:
            props["longitude_ascending_node_deg"] = long_asc_node
        
        if inclination:
            props["inclination_deg"] = inclination
        
        if abs_magnitude:
            props["absolute_magnitude"] = abs_magnitude
        
        if slope_param:
            props["slope_parameter"] = slope_param
        
        # Calculate period for periodic comets
        if orbit_type == 'P' and perihelion_dist and eccentricity and eccentricity < 1.0:
            # Calculate semi-major axis
            a = perihelion_dist / (1 - eccentricity)
            # Calculate period in years (Kepler's third law)
            period = a ** 1.5
            props["period_years"] = round(period, 2)
        
        return {
            'name': name_part,
            'designation': designation,
            'props': props
        }
    
    except Exception as e:
        print(f"Error parsing line: {str(e)}")
        return None

def download_mpc_comets():
    """Download comet data from Minor Planet Center"""
    url = "https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt"
    
    print(f"Downloading comet data from {url}...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        print(f"Downloaded {len(response.text)} bytes")
        return response.text
    except Exception as e:
        print(f"Error downloading: {str(e)}")
        return None

def import_comets_from_mpc(max_comets=None, update_existing=False):
    """
    Import comets from Minor Planet Center
    
    Args:
        max_comets: Maximum number of comets to import (None = all)
        update_existing: Whether to update existing comets
    
    Returns:
        Dictionary with import statistics
    """
    
    print("=" * 70)
    print("IMPORTING COMETS FROM MINOR PLANET CENTER")
    print("=" * 70)
    
    # Download data
    data = download_mpc_comets()
    if not data:
        return {'error': 'Failed to download data'}
    
    lines = data.split('\n')
    print(f"Processing {len(lines)} lines...")
    
    # Get or create Comet type
    comet_type = Type.query.filter_by(name='Comet').first()
    if not comet_type:
        # Find max ID
        from sqlalchemy import func
        max_id = db.session.query(func.max(Type.id)).scalar()
        new_id = (max_id or 0) + 1
        
        comet_type = Type(id=new_id, name='Comet')
        db.session.add(comet_type)
        db.session.commit()
        print(f"Created Comet type with ID {new_id}")
    
    stats = {
        'total_lines': len(lines),
        'parsed': 0,
        'added': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    comets_data = []
    
    # Parse all lines first
    for line in lines:
        # Skip header/comment lines
        if not line or line.startswith('#') or len(line) < 100:
            continue
        
        comet_data = parse_mpc_comet_line(line)
        if comet_data:
            comets_data.append(comet_data)
            stats['parsed'] += 1
            
            if max_comets and len(comets_data) >= max_comets:
                break
    
    print(f"\nParsed {stats['parsed']} comets")
    print(f"Importing to database...")
    
    # Get max object ID
    from sqlalchemy import func
    max_obj_id = db.session.query(func.max(Object.id)).scalar()
    next_id = (max_obj_id or 0) + 1
    
    # Import to database
    for comet_data in comets_data:
        try:
            name = comet_data['name']
            designation = comet_data['designation']
            
            # Check if comet exists
            existing = None
            if designation:
                existing = Object.query.filter_by(desination=designation).first()
            
            if not existing:
                existing = Object.query.filter_by(name=name).first()
            
            if existing:
                if update_existing:
                    # Update existing comet
                    existing.props = json.dumps(comet_data['props'])
                    stats['updated'] += 1
                    print(f"  Updated: {name} ({designation})")
                else:
                    stats['skipped'] += 1
            else:
                # Add new comet
                new_comet = Object(
                    id=next_id,
                    name=name,
                    desination=designation,
                    type=comet_type.id,
                    props=json.dumps(comet_data['props'])
                )
                
                db.session.add(new_comet)
                stats['added'] += 1
                next_id += 1
                
                if stats['added'] % 100 == 0:
                    print(f"  Imported {stats['added']} comets...")
        
        except Exception as e:
            stats['errors'] += 1
            print(f"  Error importing {comet_data.get('name', 'unknown')}: {str(e)}")
    
    # Commit all changes
    try:
        db.session.commit()
        print("\n" + "=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        print(f"Total lines processed: {stats['total_lines']}")
        print(f"Comets parsed: {stats['parsed']}")
        print(f"Comets added: {stats['added']}")
        print(f"Comets updated: {stats['updated']}")
        print(f"Comets skipped: {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        print("=" * 70)
    except Exception as e:
        db.session.rollback()
        print(f"Error committing to database: {str(e)}")
        stats['error'] = str(e)
    
    return stats

def sync_comets_from_mpc():
    """Synchronize comets (update existing and add new)"""
    return import_comets_from_mpc(update_existing=True)

if __name__ == '__main__':
    # Import first 100 comets for testing
    import_comets_from_mpc(max_comets=100)