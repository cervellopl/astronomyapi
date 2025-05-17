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
from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app
import json
import requests
from datetime import datetime

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
