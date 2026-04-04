"""
Astronomy API Web Interface
==========================
HTML interface for interacting with the Astronomy Observations API.

This module provides a web-based interface for:
- Viewing all data (objects, observations, instruments, etc.)
- Adding new data through forms
- Searching observations with filters
"""

import os
import sys
from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app, Response
import json
import requests
from datetime import datetime
from models import Object, Type, Session, Instrument, Observation, Place, Property
from database import db
from import_comets_mpc import import_comets_from_mpc, sync_comets_from_mpc
from import_vsx import import_vsx_stars, sync_vsx_stars

# Create a Blueprint for the web interface
web = Blueprint('web', __name__, template_folder='templates')

# Print debug info
print(f"Web routes initialized")
print(f"Blueprint template folder: {web.template_folder}")
print(f"Current working directory: {os.getcwd()}")
if os.path.exists('templates'):
    print(f"Templates directory found: {os.listdir('templates')}")
else:
    print("Templates directory not found!")
    
# Base URL for API endpoints
API_BASE_URL = ''  # Empty for local API access


# =========================================================================
# Helper Functions
# =========================================================================

def get_api_url(endpoint):
    """Get the full URL for an API endpoint."""
    return f"{API_BASE_URL}{endpoint}"


def api_request(method, endpoint, data=None, params=None):
    """Make a request to the API."""
    url = get_api_url(endpoint)
    
    if method == 'GET':
        response = requests.get(url, params=params)
    elif method == 'POST':
        response = requests.post(url, json=data)
    elif method == 'PUT':
        response = requests.put(url, json=data)
    elif method == 'DELETE':
        response = requests.delete(url)
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    return response


# =========================================================================
# Dashboard Route
# =========================================================================

@web.route('/')
def dashboard():
    """Render the dashboard page."""
    try:
        print("Rendering dashboard")
        
        # Print template path information
        template_path = os.path.join(current_app.root_path, web.template_folder, 'dashboard.html')
        print(f"Looking for template at: {template_path}")
        print(f"Template exists: {os.path.exists(template_path)}")
        
        # Get counts of different entities
        try:
            types = api_request('GET', '/api/types').json()
            print(f"Found {len(types)} types")
        except Exception as e:
            print(f"Error getting types: {str(e)}")
            types = []
            
        try:
            properties = api_request('GET', '/api/properties').json()
            print(f"Found {len(properties)} properties")
        except Exception as e:
            print(f"Error getting properties: {str(e)}")
            properties = []
            
        try:
            places = api_request('GET', '/api/places').json()
            print(f"Found {len(places)} places")
        except Exception as e:
            print(f"Error getting places: {str(e)}")
            places = []
            
        try:
            instruments = api_request('GET', '/api/instruments').json()
            print(f"Found {len(instruments)} instruments")
        except Exception as e:
            print(f"Error getting instruments: {str(e)}")
            instruments = []
            
        try:
            objects = api_request('GET', '/api/objects').json()
            print(f"Found {len(objects)} objects")
        except Exception as e:
            print(f"Error getting objects: {str(e)}")
            objects = []
            
        try:
            observations = api_request('GET', '/api/observations').json()
            print(f"Found {len(observations)} observations")
        except Exception as e:
            print(f"Error getting observations: {str(e)}")
            observations = []
        
        counts = {
            'types': len(types),
            'properties': len(properties),
            'places': len(places),
            'instruments': len(instruments),
            'objects': len(objects),
            'observations': len(observations)
        }
        
        # Get recent observations
        recent_observations = observations[-5:] if observations else []
        
        # Enrich observations with related data
        for obs in recent_observations:
            for obj in objects:
                if obj['id'] == obs['object']:
                    obs['object_name'] = obj['name']
                    break
            else:
                obs['object_name'] = f"Object {obs['object']}"
            
            for place in places:
                if place['id'] == obs['place']:
                    obs['place_name'] = place['name']
                    break
            else:
                obs['place_name'] = f"Place {obs['place']}"
            
            for instrument in instruments:
                if instrument['id'] == obs['instrument']:
                    obs['instrument_name'] = instrument['name']
                    break
            else:
                obs['instrument_name'] = f"Instrument {obs['instrument']}"
            
            # Format datetime
            if obs.get('datetime'):
                try:
                    dt = datetime.fromisoformat(obs['datetime'].replace('Z', '+00:00'))
                    obs['formatted_date'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    obs['formatted_date'] = obs['datetime']
            else:
                obs['formatted_date'] = 'Unknown'
        
        return render_template('dashboard.html', counts=counts, 
                              recent_observations=recent_observations)
    
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", 'danger')
        return render_template('dashboard.html', counts={}, recent_observations=[])


# =========================================================================
# Type Routes
# =========================================================================

@web.route('/types')
def list_types():
    """List all types."""
    try:
        types = api_request('GET', '/api/types').json()
        return render_template('types/list.html', types=types)
    except Exception as e:
        flash(f"Error loading types: {str(e)}", 'danger')
        return render_template('types/list.html', types=[])


@web.route('/types/add', methods=['GET', 'POST'])
def add_type():
    """Add a new type."""
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name']
            }
            
            response = api_request('POST', '/api/types', data=data)
            
            if response.status_code == 201:
                flash('Type added successfully!', 'success')
                return redirect(url_for('web.list_types'))
            else:
                flash(f"Error adding type: {response.json().get('message', 'Unknown error')}", 'danger')
        except Exception as e:
            flash(f"Error adding type: {str(e)}", 'danger')
    
    return render_template('types/add.html')


# =========================================================================
# Property Routes
# =========================================================================

@web.route('/properties')
def list_properties():
    """List all properties."""
    try:
        properties = api_request('GET', '/api/properties').json()
        return render_template('properties/list.html', properties=properties)
    except Exception as e:
        flash(f"Error loading properties: {str(e)}", 'danger')
        return render_template('properties/list.html', properties=[])


@web.route('/properties/add', methods=['GET', 'POST'])
def add_property():
    """Add a new property."""
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name'],
                'valueType': request.form['valueType']
            }
            
            response = api_request('POST', '/api/properties', data=data)
            
            if response.status_code == 201:
                flash('Property added successfully!', 'success')
                return redirect(url_for('web.list_properties'))
            else:
                flash(f"Error adding property: {response.json().get('message', 'Unknown error')}", 'danger')
        except Exception as e:
            flash(f"Error adding property: {str(e)}", 'danger')
    
    return render_template('properties/add.html')


# =========================================================================
# Place Routes
# =========================================================================

@web.route('/places')
def list_places():
    """List all places."""
    try:
        places = api_request('GET', '/api/places').json()
        return render_template('places/list.html', places=places)
    except Exception as e:
        flash(f"Error loading places: {str(e)}", 'danger')
        return render_template('places/list.html', places=[])


@web.route('/places/add', methods=['GET', 'POST'])
def add_place():
    """Add a new place."""
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name'],
                'lat': request.form['lat'],
                'lon': request.form['lon'],
                'alt': request.form['alt'],
                'timezone': request.form['timezone']
            }
            
            response = api_request('POST', '/api/places', data=data)
            
            if response.status_code == 201:
                flash('Place added successfully!', 'success')
                return redirect(url_for('web.list_places'))
            else:
                flash(f"Error adding place: {response.json().get('message', 'Unknown error')}", 'danger')
        except Exception as e:
            flash(f"Error adding place: {str(e)}", 'danger')
    
    return render_template('places/add.html')


# =========================================================================
# Instrument Routes
# =========================================================================

@web.route('/instruments')
def list_instruments():
    """List all instruments."""
    try:
        instruments = api_request('GET', '/api/instruments').json()
        return render_template('instruments/list.html', instruments=instruments)
    except Exception as e:
        flash(f"Error loading instruments: {str(e)}", 'danger')
        return render_template('instruments/list.html', instruments=[])


@web.route('/instruments/add', methods=['GET', 'POST'])
def add_instrument():
    """Add a new instrument."""
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name'],
                'aperture': request.form['aperture'],
                'power': request.form['power']
            }
            
            response = api_request('POST', '/api/instruments', data=data)
            
            if response.status_code == 201:
                flash('Instrument added successfully!', 'success')
                return redirect(url_for('web.list_instruments'))
            else:
                flash(f"Error adding instrument: {response.json().get('message', 'Unknown error')}", 'danger')
        except Exception as e:
            flash(f"Error adding instrument: {str(e)}", 'danger')
    
    return render_template('instruments/add.html')


# =========================================================================
# Object Routes
# =========================================================================

@web.route('/objects')
def list_objects():
    """List all objects."""
    try:
        objects = api_request('GET', '/api/objects').json()
        types = api_request('GET', '/api/types').json()
        
        # Create a type lookup dictionary
        type_lookup = {t['id']: t['name'] for t in types}
        
        # Add type name to each object
        for obj in objects:
            obj['type_name'] = type_lookup.get(obj['type'], f"Type {obj['type']}")
        
        return render_template('objects/list.html', objects=objects)
    except Exception as e:
        flash(f"Error loading objects: {str(e)}", 'danger')
        return render_template('objects/list.html', objects=[])


@web.route('/objects/add', methods=['GET', 'POST'])
def add_object():
    """Add a new object."""
    try:
        types = api_request('GET', '/api/types').json()
        
        if request.method == 'POST':
            try:
                # Parse props as JSON if provided
                props = None
                if request.form['props']:
                    try:
                        props = json.dumps(json.loads(request.form['props']))
                    except json.JSONDecodeError:
                        flash('Invalid JSON in props field', 'warning')
                        return render_template('objects/add.html', types=types)
                
                data = {
                    'name': request.form['name'],
                    'desination': request.form['desination'],
                    'type': int(request.form['type']),
                    'props': props
                }
                
                response = api_request('POST', '/api/objects', data=data)
                
                if response.status_code == 201:
                    flash('Object added successfully!', 'success')
                    return redirect(url_for('web.list_objects'))
                else:
                    flash(f"Error adding object: {response.json().get('message', 'Unknown error')}", 'danger')
            except Exception as e:
                flash(f"Error adding object: {str(e)}", 'danger')
        
        return render_template('objects/add.html', types=types)
    except Exception as e:
        flash(f"Error loading form: {str(e)}", 'danger')
        return redirect(url_for('web.list_objects'))


# =========================================================================
# Observation Routes
# =========================================================================

@web.route('/observations')
def list_observations():
    """List all observations."""
    try:
        observations = api_request('GET', '/api/observations').json()
        objects = api_request('GET', '/api/objects').json()
        places = api_request('GET', '/api/places').json()
        instruments = api_request('GET', '/api/instruments').json()
        properties = api_request('GET', '/api/properties').json()
        
        # Create lookup dictionaries
        object_lookup = {o['id']: o['name'] for o in objects}
        place_lookup = {p['id']: p['name'] for p in places}
        instrument_lookup = {i['id']: i['name'] for i in instruments}
        property_lookup = {p['id']: p['name'] for p in properties}
        
        # Add related data to each observation
        for obs in observations:
            obs['object_name'] = object_lookup.get(obs['object'], f"Object {obs['object']}")
            obs['place_name'] = place_lookup.get(obs['place'], f"Place {obs['place']}")
            obs['instrument_name'] = instrument_lookup.get(obs['instrument'], f"Instrument {obs['instrument']}")
            
            if obs.get('prop1'):
                obs['property_name'] = property_lookup.get(obs['prop1'], f"Property {obs['prop1']}")
            else:
                obs['property_name'] = 'None'
            
            # Format datetime
            if obs.get('datetime'):
                try:
                    dt = datetime.fromisoformat(obs['datetime'].replace('Z', '+00:00'))
                    obs['formatted_date'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    obs['formatted_date'] = obs['datetime']
            else:
                obs['formatted_date'] = 'Unknown'
        
        return render_template('observations/list.html', observations=observations)
    except Exception as e:
        flash(f"Error loading observations: {str(e)}", 'danger')
        return render_template('observations/list.html', observations=[])


@web.route('/observations/add', methods=['GET', 'POST'])
def add_observation():
    """Add a new observation."""
    try:
        objects = api_request('GET', '/api/objects').json()
        places = api_request('GET', '/api/places').json()
        instruments = api_request('GET', '/api/instruments').json()
        properties = api_request('GET', '/api/properties').json()
        
        if request.method == 'POST':
            try:
                # Convert property to integer or None
                prop1 = request.form.get('prop1')
                if prop1 and prop1 != 'none':
                    prop1 = int(prop1)
                else:
                    prop1 = None
                
                data = {
                    'object': int(request.form['object']),
                    'place': int(request.form['place']),
                    'instrument': int(request.form['instrument']),
                    'datetime': request.form['datetime'],
                    'observation': request.form['observation'],
                    'prop1': prop1,
                    'prop1value': request.form.get('prop1value', '')
                }
                
                response = api_request('POST', '/api/observations', data=data)
                
                if response.status_code == 201:
                    flash('Observation added successfully!', 'success')
                    return redirect(url_for('web.list_observations'))
                else:
                    flash(f"Error adding observation: {response.json().get('message', 'Unknown error')}", 'danger')
            except Exception as e:
                flash(f"Error adding observation: {str(e)}", 'danger')
        
        return render_template('observations/add.html', 
                             objects=objects, 
                             places=places, 
                             instruments=instruments, 
                             properties=properties)
    except Exception as e:
        flash(f"Error loading form: {str(e)}", 'danger')
        return redirect(url_for('web.list_observations'))


# =========================================================================
# Session Routes
# =========================================================================

@web.route('/sessions')
def list_sessions():
    """List all sessions."""
    try:
        sessions = Session.query.order_by(Session.start_datetime.desc()).all()
        return render_template('sessions/list.html', sessions=sessions)
    except Exception as e:
        flash(f'Error loading sessions: {str(e)}', 'danger')
        return render_template('sessions/list.html', sessions=[])


@web.route('/sessions/<int:session_id>')
def view_session(session_id):
    """View a single session with its observations."""
    try:
        session = Session.query.get_or_404(session_id)
        observations = Observation.query.filter_by(session_id=session_id).order_by(Observation.datetime).all()
        return render_template('sessions/view.html', session=session, observations=observations)
    except Exception as e:
        flash(f'Error loading session: {str(e)}', 'danger')
        return redirect(url_for('web.list_sessions'))


@web.route('/sessions/add', methods=['GET', 'POST'])
def add_session():
    """Add a new session."""
    if request.method == 'POST':
        try:
            number = request.form.get('number')
            start_datetime_str = request.form.get('start_datetime')
            end_datetime_str = request.form.get('end_datetime')
            cloud_percentage = request.form.get('cloud_percentage')
            cloud_type = request.form.get('cloud_type')
            light_pollution = request.form.get('light_pollution')
            limiting_magnitude = request.form.get('limiting_magnitude')
            moon_phase = request.form.get('moon_phase')
            moon_altitude = request.form.get('moon_altitude')
            instrument_id = request.form.get('instrument')

            start_dt = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00')) if start_datetime_str else None
            end_dt = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00')) if end_datetime_str else None

            new_session = Session(
                number=number,
                start_datetime=start_dt,
                end_datetime=end_dt,
                cloud_percentage=int(cloud_percentage) if cloud_percentage else None,
                cloud_type=cloud_type if cloud_type else None,
                light_pollution=int(light_pollution) if light_pollution else None,
                limiting_magnitude=float(limiting_magnitude) if limiting_magnitude else None,
                moon_phase=moon_phase if moon_phase else None,
                moon_altitude=float(moon_altitude) if moon_altitude else None,
                instrument=int(instrument_id) if instrument_id else None
            )

            db.session.add(new_session)
            db.session.commit()

            flash(f'Session "{number}" added successfully!', 'success')
            return redirect(url_for('web.list_sessions'))
        except Exception as e:
            flash(f'Error adding session: {str(e)}', 'danger')
            db.session.rollback()

    try:
        instruments = Instrument.query.all()
    except Exception:
        instruments = []

    return render_template('sessions/add.html', instruments=instruments)


# =========================================================================
# Search Route
# =========================================================================

@web.route('/search', methods=['GET', 'POST'])
def search_observations():
    """Search observations."""
    try:
        objects = api_request('GET', '/api/objects').json()
        places = api_request('GET', '/api/places').json()
        instruments = api_request('GET', '/api/instruments').json()
        
        if request.method == 'POST':
            # Build query parameters
            params = {}
            
            if request.form.get('start_date'):
                params['start_date'] = request.form['start_date']
            
            if request.form.get('end_date'):
                params['end_date'] = request.form['end_date']
            
            if request.form.get('object') and request.form['object'] != 'all':
                params['object_id'] = request.form['object']
            
            if request.form.get('place') and request.form['place'] != 'all':
                params['place_id'] = request.form['place']
            
            if request.form.get('instrument') and request.form['instrument'] != 'all':
                params['instrument_id'] = request.form['instrument']
            
            # Execute search
            observations = api_request('GET', '/api/observations/search', params=params).json()
            
            # Create lookup dictionaries
            object_lookup = {o['id']: o['name'] for o in objects}
            place_lookup = {p['id']: p['name'] for p in places}
            instrument_lookup = {i['id']: i['name'] for i in instruments}
            
            # Add related data to each observation
            for obs in observations:
                obs['object_name'] = object_lookup.get(obs['object'], f"Object {obs['object']}")
                obs['place_name'] = place_lookup.get(obs['place'], f"Place {obs['place']}")
                obs['instrument_name'] = instrument_lookup.get(obs['instrument'], f"Instrument {obs['instrument']}")
                
                # Format datetime
                if obs.get('datetime'):
                    try:
                        dt = datetime.fromisoformat(obs['datetime'].replace('Z', '+00:00'))
                        obs['formatted_date'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        obs['formatted_date'] = obs['datetime']
                else:
                    obs['formatted_date'] = 'Unknown'
            
            return render_template('search.html', 
                                 objects=objects, 
                                 places=places, 
                                 instruments=instruments,
                                 observations=observations,
                                 search_executed=True)
        
        return render_template('search.html', 
                             objects=objects, 
                             places=places, 
                             instruments=instruments,
                             observations=[],
                             search_executed=False)
    except Exception as e:
        flash(f"Error during search: {str(e)}", 'danger')
        return render_template('search.html',
                             objects=[],
                             places=[],
                             instruments=[],
                             observations=[],
                             search_executed=False)


# =========================================================================
# Comet Import Route
# =========================================================================

@web.route('/comets/import', methods=['GET', 'POST'])
def import_comets():
    """Import comets from Minor Planet Center"""
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            max_comets = request.form.get('max_comets')

            if max_comets:
                try:
                    max_comets = int(max_comets)
                except ValueError:
                    max_comets = None
            else:
                max_comets = None

            if action == 'import':
                stats = import_comets_from_mpc(max_comets=max_comets, update_existing=False)
                flash(f"Import complete! Added {stats.get('added', 0)} comets, skipped {stats.get('skipped', 0)}", 'success')
            elif action == 'sync':
                stats = sync_comets_from_mpc()
                flash(f"Sync complete! Added {stats.get('added', 0)} comets, updated {stats.get('updated', 0)}", 'success')

            return redirect(url_for('web.list_objects'))
        except Exception as e:
            flash(f'Error importing comets: {str(e)}', 'danger')

    # Get current comet count
    try:
        comet_type = Type.query.filter_by(name='Comet').first()
        if comet_type:
            comet_count = Object.query.filter_by(type=comet_type.id).count()
        else:
            comet_count = 0
    except Exception:
        comet_count = 0

    return render_template('comets/import.html', comet_count=comet_count)


# =========================================================================
# VSX Variable Star Import Route
# =========================================================================

@web.route('/vsx/import', methods=['GET', 'POST'])
def import_vsx():
    """Search and import variable stars from AAVSO VSX"""
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            name = request.form.get('name', '').strip() or None
            constellation = request.form.get('constellation', '').strip() or None
            var_type = request.form.get('var_type', '').strip() or None
            max_records = request.form.get('max_records', '100')

            try:
                max_records = int(max_records)
                max_records = max(1, min(max_records, 9999))
            except ValueError:
                max_records = 100

            if action == 'import':
                stats = import_vsx_stars(
                    name=name, constellation=constellation,
                    var_type=var_type, max_records=max_records,
                    update_existing=False
                )
                if 'error' in stats:
                    flash(f"Error: {stats['error']}", 'danger')
                else:
                    flash(
                        f"Import complete! Found {stats.get('total_found', 0)}, "
                        f"added {stats.get('added', 0)}, "
                        f"skipped {stats.get('skipped', 0)}",
                        'success'
                    )
            elif action == 'sync':
                stats = sync_vsx_stars(
                    name=name, constellation=constellation,
                    var_type=var_type, max_records=max_records
                )
                if 'error' in stats:
                    flash(f"Error: {stats['error']}", 'danger')
                else:
                    flash(
                        f"Sync complete! Found {stats.get('total_found', 0)}, "
                        f"added {stats.get('added', 0)}, "
                        f"updated {stats.get('updated', 0)}",
                        'success'
                    )

            return redirect(url_for('web.list_objects'))
        except Exception as e:
            flash(f'Error importing from VSX: {str(e)}', 'danger')

    # Get current variable star count
    try:
        var_star_type = Type.query.filter_by(name='Variable Star').first()
        if var_star_type:
            var_star_count = Object.query.filter_by(type=var_star_type.id).count()
        else:
            var_star_count = 0
    except Exception:
        var_star_count = 0

    return render_template('vsx/import.html', var_star_count=var_star_count)


# =========================================================================
# Backup / Export / Import / Restore Routes
# =========================================================================

def _serialize_datetime(dt):
    """Convert datetime to ISO string or None."""
    return dt.isoformat() if dt else None


def _build_backup_data():
    """Collect all user data into a serializable dict."""
    data = {
        'version': 1,
        'exported_at': datetime.utcnow().isoformat(),
        'types': [],
        'properties': [],
        'places': [],
        'instruments': [],
        'objects': [],
        'sessions': [],
        'observations': [],
    }

    for t in Type.query.all():
        data['types'].append({'id': t.id, 'name': t.name})

    for p in Property.query.all():
        data['properties'].append({'id': p.id, 'name': p.name, 'valueType': p.valueType})

    for p in Place.query.all():
        data['places'].append({
            'id': p.id, 'name': p.name,
            'lat': p.lat, 'lon': p.lon, 'alt': p.alt,
            'timezone': p.timezone,
        })

    for i in Instrument.query.all():
        data['instruments'].append({
            'id': i.id, 'name': i.name,
            'instrument_type': i.instrument_type,
            'aperture': i.aperture, 'power': i.power,
            'eyepiece': i.eyepiece,
        })

    for o in Object.query.all():
        data['objects'].append({
            'id': o.id, 'name': o.name,
            'desination': o.desination, 'type': o.type,
            'props': o.props,
        })

    for s in Session.query.all():
        data['sessions'].append({
            'id': s.id, 'number': s.number,
            'start_datetime': _serialize_datetime(s.start_datetime),
            'end_datetime': _serialize_datetime(s.end_datetime),
            'cloud_percentage': s.cloud_percentage,
            'cloud_type': s.cloud_type,
            'light_pollution': s.light_pollution,
            'limiting_magnitude': s.limiting_magnitude,
            'moon_phase': s.moon_phase,
            'moon_altitude': s.moon_altitude,
            'instrument': s.instrument,
        })

    for obs in Observation.query.all():
        data['observations'].append({
            'id': obs.id, 'object': obs.object,
            'place': obs.place, 'instrument': obs.instrument,
            'session_id': obs.session_id,
            'datetime': _serialize_datetime(obs.datetime),
            'observation': obs.observation,
            'prop1': obs.prop1, 'prop1value': obs.prop1value,
        })

    return data


def _parse_datetime(s):
    """Parse an ISO datetime string, return None on failure."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None


def _import_backup_data(data, mode='merge'):
    """Import data from a backup dict.

    mode='merge'   – skip records whose id already exists
    mode='restore' – wipe all tables first, then insert everything
    """
    stats = {'added': {}, 'skipped': {}}

    if mode == 'restore':
        # Delete in reverse-dependency order
        Observation.query.delete()
        Session.query.delete()
        Object.query.delete()
        Instrument.query.delete()
        Place.query.delete()
        Property.query.delete()
        Type.query.delete()
        db.session.flush()

    # Import order follows foreign-key dependencies
    table_configs = [
        ('types', Type, lambda r: Type(id=r['id'], name=r['name'])),
        ('properties', Property, lambda r: Property(id=r['id'], name=r['name'], valueType=r.get('valueType'))),
        ('places', Place, lambda r: Place(
            id=r['id'], name=r['name'],
            lat=r.get('lat'), lon=r.get('lon'), alt=r.get('alt'),
            timezone=r.get('timezone'),
        )),
        ('instruments', Instrument, lambda r: Instrument(
            id=r['id'], name=r['name'],
            instrument_type=r.get('instrument_type'),
            aperture=r.get('aperture'), power=r.get('power'),
            eyepiece=r.get('eyepiece'),
        )),
        ('objects', Object, lambda r: Object(
            id=r['id'], name=r['name'],
            desination=r.get('desination'), type=r.get('type'),
            props=r.get('props'),
        )),
        ('sessions', Session, lambda r: Session(
            id=r['id'], number=r.get('number'),
            start_datetime=_parse_datetime(r.get('start_datetime')),
            end_datetime=_parse_datetime(r.get('end_datetime')),
            cloud_percentage=r.get('cloud_percentage'),
            cloud_type=r.get('cloud_type'),
            light_pollution=r.get('light_pollution'),
            limiting_magnitude=r.get('limiting_magnitude'),
            moon_phase=r.get('moon_phase'),
            moon_altitude=r.get('moon_altitude'),
            instrument=r.get('instrument'),
        )),
        ('observations', Observation, lambda r: Observation(
            id=r['id'], object=r.get('object'),
            place=r.get('place'), instrument=r.get('instrument'),
            session_id=r.get('session_id'),
            datetime=_parse_datetime(r.get('datetime')),
            observation=r.get('observation'),
            prop1=r.get('prop1'), prop1value=r.get('prop1value'),
        )),
    ]

    for key, model, factory in table_configs:
        added = 0
        skipped = 0
        for record in data.get(key, []):
            if mode == 'merge' and db.session.get(model, record['id']):
                skipped += 1
                continue
            db.session.add(factory(record))
            added += 1
        stats['added'][key] = added
        stats['skipped'][key] = skipped

    db.session.commit()
    return stats


@web.route('/backup')
def backup_page():
    """Render the backup management page."""
    counts = {}
    try:
        counts = {
            'types': Type.query.count(),
            'properties': Property.query.count(),
            'places': Place.query.count(),
            'instruments': Instrument.query.count(),
            'objects': Object.query.count(),
            'sessions': Session.query.count(),
            'observations': Observation.query.count(),
        }
    except Exception as e:
        flash(f'Error loading counts: {str(e)}', 'danger')
    return render_template('backup/index.html', counts=counts)


@web.route('/backup/export')
def backup_export():
    """Export all data as a downloadable JSON file."""
    try:
        data = _build_backup_data()
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'astronomy_backup_{timestamp}.json'
        return Response(
            json_str,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'danger')
        return redirect(url_for('web.backup_page'))


@web.route('/backup/import', methods=['POST'])
def backup_import():
    """Import (merge) data from an uploaded JSON file. Existing records are kept."""
    try:
        file = request.files.get('backup_file')
        if not file or file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(url_for('web.backup_page'))

        raw = file.read()
        data = json.loads(raw)

        if not isinstance(data, dict) or 'version' not in data:
            flash('Invalid backup file format.', 'danger')
            return redirect(url_for('web.backup_page'))

        stats = _import_backup_data(data, mode='merge')
        total_added = sum(stats['added'].values())
        total_skipped = sum(stats['skipped'].values())
        flash(f'Import complete! Added {total_added} records, skipped {total_skipped} existing.', 'success')
    except json.JSONDecodeError:
        flash('File is not valid JSON.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error importing data: {str(e)}', 'danger')
    return redirect(url_for('web.backup_page'))


@web.route('/backup/restore', methods=['POST'])
def backup_restore():
    """Restore data from an uploaded JSON file. WARNING: replaces all existing data."""
    try:
        file = request.files.get('backup_file')
        if not file or file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(url_for('web.backup_page'))

        raw = file.read()
        data = json.loads(raw)

        if not isinstance(data, dict) or 'version' not in data:
            flash('Invalid backup file format.', 'danger')
            return redirect(url_for('web.backup_page'))

        stats = _import_backup_data(data, mode='restore')
        total_added = sum(stats['added'].values())
        flash(f'Restore complete! All previous data replaced. Loaded {total_added} records.', 'success')
    except json.JSONDecodeError:
        flash('File is not valid JSON.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error restoring data: {str(e)}', 'danger')
    return redirect(url_for('web.backup_page'))
