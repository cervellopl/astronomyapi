"""
Create a complete new web_routes.py with proper ID handling
"""

def create_new_web_routes():
    """Create a complete new web_routes.py"""
    print("Creating new web_routes.py...")
    
    content = '''"""
Web interface routes for Astronomy Observations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import (Type, Property, Place, Instrument, Object, Observation, Session,
                    User, Plan, ObservationProperty, StarList)
from aavso_recent import fetch_recent, fetch_star_info, fetch_light_curve
from database import db
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
import json
import math
import os
import time
import hashlib
import base64
import requests as http_requests
from urllib.parse import quote
from import_comets_mpc import import_comets_from_mpc, sync_comets_from_mpc
from import_vsx import import_vsx_stars, sync_vsx_stars
from import_simbad import (search_simbad, lookup_simbad_object, import_simbad_object,
                           find_existing_object, CONSTELLATIONS, VARIABLE_TYPE_QUERIES,
                           _run_tap_raw)

web = Blueprint('web', __name__)

BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups')

# ============================================================================
# BACKUP ENCRYPTION HELPERS
# ============================================================================

def _derive_fernet_key(password, salt):
    """Derive a 32-byte Fernet-compatible key from a password and salt."""
    key_material = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100_000, dklen=32
    )
    return base64.urlsafe_b64encode(key_material)

def _encrypt_backup(json_str, password):
    """Encrypt backup JSON string with a password. Returns binary bytes."""
    from cryptography.fernet import Fernet
    import secrets
    salt = secrets.token_bytes(16)
    key = _derive_fernet_key(password, salt)
    token = Fernet(key).encrypt(json_str.encode('utf-8'))
    # Layout: magic(8) + salt(16) + ciphertext
    return b'ASTROV1\\n' + salt + token

def _decrypt_backup(data, password):
    """Decrypt backup bytes with a password. Returns JSON string."""
    from cryptography.fernet import Fernet, InvalidToken
    MAGIC = b'ASTROV1\\n'
    if not data.startswith(MAGIC):
        raise ValueError('Not an encrypted astronomy backup file (missing header).')
    salt = data[len(MAGIC):len(MAGIC)+16]
    ciphertext = data[len(MAGIC)+16:]
    key = _derive_fernet_key(password, salt)
    try:
        return Fernet(key).decrypt(ciphertext).decode('utf-8')
    except InvalidToken:
        raise ValueError('Incorrect password or corrupted backup file.')

def _is_encrypted_backup(data):
    return data[:8] == b'ASTROV1\\n'

def _save_local_backup(json_str, password=None, prefix='auto'):
    """Save a backup to the internal backups/ directory. Returns filename."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    if password:
        filename = f'astronomy_{prefix}_{ts}.astroenc'
        content = _encrypt_backup(json_str, password)
        mode = 'wb'
    else:
        filename = f'astronomy_{prefix}_{ts}.json'
        content = json_str.encode('utf-8')
        mode = 'wb'
    path = os.path.join(BACKUP_DIR, filename)
    with open(path, mode) as fh:
        fh.write(content)
    return filename

def _list_local_backups():
    """Return list of dicts describing local backup files, newest first."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    result = []
    for name in os.listdir(BACKUP_DIR):
        if not (name.endswith('.json') or name.endswith('.astroenc')):
            continue
        path = os.path.join(BACKUP_DIR, name)
        stat = os.stat(path)
        result.append({
            'filename': name,
            'size_kb': round(stat.st_size / 1024, 1),
            'modified': datetime.utcfromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            'encrypted': name.endswith('.astroenc'),
        })
    result.sort(key=lambda x: x['modified'], reverse=True)
    return result

# ============================================================================
# AUTO-BACKUP SCHEDULER
# ============================================================================

_scheduler = None

def _do_auto_backups(app):
    """Run auto-backups for all users with auto-backup enabled."""
    from datetime import timedelta
    with app.app_context():
        try:
            users = User.query.filter_by(backup_auto_enabled=True).all()
            for user in users:
                interval = user.backup_auto_interval or 'weekly'
                thresholds = {'daily': timedelta(hours=23), 'weekly': timedelta(days=6, hours=23), 'monthly': timedelta(days=29)}
                threshold = thresholds.get(interval, timedelta(days=6, hours=23))
                now = datetime.utcnow()
                if user.backup_last_auto and (now - user.backup_last_auto) < threshold:
                    continue
                data = _build_backup_data()
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                pw = user.backup_password or None
                _save_local_backup(json_str, password=pw, prefix='auto')
                user.backup_last_auto = now
                db.session.commit()
        except Exception:
            pass

def _start_auto_backup_scheduler(app):
    """Start the APScheduler background scheduler (safe against double-start)."""
    global _scheduler
    if _scheduler is not None:
        return
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        import atexit
        _scheduler = BackgroundScheduler(daemon=True)
        _scheduler.add_job(
            _do_auto_backups, 'interval', args=[app],
            hours=1, id='auto_backup', replace_existing=True,
            misfire_grace_time=300,
        )
        _scheduler.start()
        atexit.register(lambda: _scheduler.shutdown(wait=False))
    except Exception:
        pass  # APScheduler not available; auto-backup won't run

# ============================================================================
# AUTHENTICATION
# ============================================================================

@web.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('web.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')

@web.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            flash('Passwords do not match.', 'danger')
        elif len(password) < 4:
            flash('Password must be at least 4 characters.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('web.login'))

    return render_template('auth/register.html')

@web.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('web.login'))

@web.route('/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    """User settings page"""
    if request.method == 'POST':
        try:
            action = request.form.get('action')

            if action == 'update_profile':
                current_user.email = request.form.get('email', '').strip() or None
                current_user.postal_address = request.form.get('postal_address', '').strip() or None
                current_user.aavso_code = request.form.get('aavso_code', '').strip() or None
                current_user.icq_code = request.form.get('icq_code', '').strip() or None
                current_user.default_timezone = request.form.get('default_timezone', '').strip() or None
                current_user.cobs_username = request.form.get('cobs_username', '').strip() or None
                cobs_pw = request.form.get('cobs_password', '').strip()
                if cobs_pw:
                    current_user.cobs_password = cobs_pw
                current_user.aavso_email = request.form.get('aavso_email', '').strip() or None
                aavso_pw = request.form.get('aavso_password', '').strip()
                if aavso_pw:
                    current_user.aavso_password = aavso_pw
                # Token for the v2 API; blank the field to clear it
                if 'aavso_api_key' in request.form:
                    current_user.aavso_api_key = (
                        request.form.get('aavso_api_key', '').strip() or None)
                db.session.commit()
                flash('Profile updated successfully!', 'success')

            elif action == 'update_backup':
                backup_pw = request.form.get('backup_password', '').strip()
                if backup_pw:
                    current_user.backup_password = backup_pw
                elif request.form.get('clear_backup_password'):
                    current_user.backup_password = None
                current_user.backup_auto_enabled = bool(request.form.get('backup_auto_enabled'))
                current_user.backup_auto_interval = request.form.get('backup_auto_interval', 'weekly')
                db.session.commit()
                flash('Backup settings saved!', 'success')

            elif action == 'change_password':
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                new_password2 = request.form.get('new_password2')

                if not current_user.check_password(current_password):
                    flash('Current password is incorrect.', 'danger')
                elif new_password != new_password2:
                    flash('New passwords do not match.', 'danger')
                elif len(new_password) < 4:
                    flash('New password must be at least 4 characters.', 'danger')
                else:
                    current_user.set_password(new_password)
                    db.session.commit()
                    flash('Password changed successfully!', 'success')

            return redirect(url_for('web.user_settings'))
        except Exception as e:
            flash(f'Error updating settings: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('auth/settings.html')

# ============================================================================
# DASHBOARD
# ============================================================================

@web.route('/')
@login_required
def dashboard():
    """Dashboard view"""
    try:
        # Get counts
        counts = {
            'types': Type.query.count(),
            'properties': Property.query.count(),
            'places': Place.query.count(),
            'instruments': Instrument.query.count(),
            'objects': Object.query.count(),
            'observations': Observation.query.count(),
            'sessions': Session.query.count()
        }
        
        # Get recent observations
        recent_observations = Observation.query.order_by(Observation.datetime.desc()).limit(10).all()
        
        return render_template('dashboard.html', counts=counts, recent_observations=recent_observations)
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return render_template('dashboard.html', counts={}, recent_observations=[])

# ============================================================================
# OBJECTS
# ============================================================================

@web.route('/objects')
@login_required
def list_objects():
    """List all objects"""
    try:
        objects = Object.query.all()
        return render_template('objects/list.html', objects=objects)
    except Exception as e:
        flash(f'Error loading objects: {str(e)}', 'danger')
        return render_template('objects/list.html', objects=[])

@web.route('/objects/add', methods=['GET', 'POST'])
@login_required
def add_object():
    """Add a new object"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            desination = request.form.get('desination')
            object_type = request.form.get('type')
            props = request.form.get('props')
            
            # Find the highest existing ID and add 1
            max_id = db.session.query(func.max(Object.id)).scalar()
            new_id = (max_id or 0) + 1
            
            # Create new object with explicit ID
            new_object = Object(
                id=new_id,
                name=name,
                desination=desination,
                type=int(object_type),
                props=props if props else None
            )
            
            db.session.add(new_object)
            db.session.commit()
            
            flash(f'Object "{name}" added successfully!', 'success')
            return redirect(url_for('web.list_objects'))
        except Exception as e:
            flash(f'Error adding object: {str(e)}', 'danger')
            db.session.rollback()
    
    # Get types for the form
    try:
        types = Type.query.all()
    except:
        types = []
    
    return render_template('objects/add.html', types=types)

@web.route('/objects/<int:object_id>')
@login_required
def view_object(object_id):
    """View object details"""
    try:
        obj = Object.query.get(object_id)
        if not obj:
            flash('Object not found', 'danger')
            return redirect(url_for('web.list_objects'))

        # Parse props JSON
        props = {}
        if obj.props:
            try:
                import json
                props = json.loads(obj.props)
            except:
                props = {'raw': obj.props}

        # Get type name
        obj_type = Type.query.get(obj.type) if obj.type else None

        return render_template('objects/view.html', obj=obj, props=props, obj_type=obj_type)
    except Exception as e:
        flash(f'Error loading object: {str(e)}', 'danger')
        return redirect(url_for('web.list_objects'))

@web.route('/objects/<int:object_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_object(object_id):
    """Edit an existing object"""
    obj = Object.query.get(object_id)
    if not obj:
        flash('Object not found', 'danger')
        return redirect(url_for('web.list_objects'))

    if request.method == 'POST':
        try:
            obj.name = request.form.get('name')
            obj.desination = request.form.get('desination')
            obj.type = int(request.form.get('type'))

            # Handle properties - merge individual fields with JSON
            import json
            props = {}
            if obj.props:
                try:
                    props = json.loads(obj.props)
                except:
                    props = {}

            # Update individual property fields
            ra_2000 = request.form.get('ra_2000', '').strip()
            dec_2000 = request.form.get('dec_2000', '').strip()
            constellation = request.form.get('constellation', '').strip()
            magnitude_v = request.form.get('magnitude_v', '').strip()
            spectral_type = request.form.get('spectral_type', '').strip()
            variability_type = request.form.get('variability_type', '').strip()
            period_days = request.form.get('period_days', '').strip()
            max_magnitude = request.form.get('max_magnitude', '').strip()
            min_magnitude = request.form.get('min_magnitude', '').strip()

            if ra_2000:
                props['ra_2000'] = ra_2000
            elif 'ra_2000' in props:
                del props['ra_2000']

            if dec_2000:
                props['dec_2000'] = dec_2000
            elif 'dec_2000' in props:
                del props['dec_2000']

            if constellation:
                props['constellation'] = constellation
            elif 'constellation' in props:
                del props['constellation']

            if magnitude_v:
                props['magnitude_v'] = magnitude_v
            elif 'magnitude_v' in props:
                del props['magnitude_v']

            if spectral_type:
                props['spectral_type'] = spectral_type
            elif 'spectral_type' in props:
                del props['spectral_type']

            if variability_type:
                props['variability_type'] = variability_type
            elif 'variability_type' in props:
                del props['variability_type']

            if period_days:
                props['period_days'] = period_days
            elif 'period_days' in props:
                del props['period_days']

            if max_magnitude:
                props['max_magnitude'] = max_magnitude
            elif 'max_magnitude' in props:
                del props['max_magnitude']

            if min_magnitude:
                props['min_magnitude'] = min_magnitude
            elif 'min_magnitude' in props:
                del props['min_magnitude']

            # Also allow raw JSON override
            extra_props_json = request.form.get('extra_props', '').strip()
            if extra_props_json:
                try:
                    extra = json.loads(extra_props_json)
                    props.update(extra)
                except:
                    pass

            obj.props = json.dumps(props) if props else None

            db.session.commit()
            flash(f'Object "{obj.name}" updated successfully!', 'success')
            return redirect(url_for('web.view_object', object_id=obj.id))
        except Exception as e:
            flash(f'Error updating object: {str(e)}', 'danger')
            db.session.rollback()

    # Parse current props
    import json
    props = {}
    if obj.props:
        try:
            props = json.loads(obj.props)
        except:
            props = {}

    types = Type.query.all()
    return render_template('objects/edit.html', obj=obj, types=types, props=props)

@web.route('/objects/<int:object_id>/delete', methods=['POST'])
@login_required
def delete_object(object_id):
    """Delete an object"""
    try:
        obj = Object.query.get(object_id)
        if not obj:
            flash('Object not found', 'danger')
            return redirect(url_for('web.list_objects'))

        name = obj.name
        db.session.delete(obj)
        db.session.commit()
        flash(f'Object "{name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting object: {str(e)}', 'danger')
        db.session.rollback()

    return redirect(url_for('web.list_objects'))

# ============================================================================
# OBSERVATIONS
# ============================================================================

@web.route('/observations')
@login_required
def list_observations():
    """List all observations"""
    try:
        observations = Observation.query.order_by(Observation.datetime.desc()).all()
        objects_lookup = {o.id: o.name for o in Object.query.all()}
        places_lookup = {p.id: (p.alias or p.name) for p in Place.query.all()}
        instruments_lookup = {i.id: i.name for i in Instrument.query.all()}
        properties_lookup = {p.id: p.name for p in Property.query.all()}
    except Exception as e:
        flash(f'Error loading observations: {str(e)}', 'danger')
        observations = []
        objects_lookup = places_lookup = instruments_lookup = properties_lookup = {}

    # Rendering stays outside the try: a template error must not be swallowed
    # into an empty "No observations found" page.
    return render_template('observations/list.html', observations=observations,
                         objects_lookup=objects_lookup, places_lookup=places_lookup,
                         instruments_lookup=instruments_lookup,
                         properties_lookup=properties_lookup)

AAVSO_FORM_FIELDS = [
    ('vs_magnitude', 'Magnitude'),
    ('vs_uncertainty', 'Uncertainty'),
    ('vs_comp_star1', 'Comp1'),
    ('vs_comp_star2', 'Comp2'),
    ('vs_check_star', 'Check'),
    ('vs_chart', 'Chart'),
    ('vs_band', 'Band'),
    ('vs_observer_code', 'Observer'),
    ('vs_method', 'Method'),
]


def _build_aavso_block(form):
    """Render the '[AAVSO: ...]' block from the variable-star form fields.

    Returns '' when no magnitude was given, since magnitude is what makes an
    observation reportable.
    """
    if not (form.get('vs_magnitude') or '').strip():
        return ''
    parts = []
    for field, key in AAVSO_FORM_FIELDS:
        value = (form.get(field) or '').strip()
        if value:
            parts.append(f"{key}: {value}")
    return " [AAVSO: " + ", ".join(parts) + "]" if parts else ''


def _strip_aavso_block(text):
    """Remove any existing '[AAVSO: ...]' block from observation text."""
    import re as _re_local
    return _re_local.sub(r'\\s*\\[AAVSO:[^\\]]*\\]', '', text or '').strip()


def _aavso_fields_from_text(text):
    """Parse a stored '[AAVSO: ...]' block back into form-field values.

    Lets the edit form show the same fields the add form captured, instead of
    making the observer hand-edit the raw text.
    """
    import re as _re_local
    values = {}
    match = _re_local.search(r'\\[AAVSO:\\s*(.+?)\\]', text or '')
    if not match:
        return values
    by_key = {}
    for part in match.group(1).split(','):
        part = part.strip()
        if ':' in part:
            key, val = part.split(':', 1)
            by_key[key.strip().lower()] = val.strip()
    for field, key in AAVSO_FORM_FIELDS:
        if key.lower() in by_key:
            values[field] = by_key[key.lower()]
    return values


def _parse_observation_properties(form):
    """Build ObservationProperty rows from the add/edit form's parallel
    prop_id[]/prop_value[] fields. Rows with an empty property are skipped."""
    rows = []
    ids = form.getlist('prop_id')
    values = form.getlist('prop_value')
    for i, pid in enumerate(ids):
        pid = (pid or '').strip()
        if not pid:
            continue
        val = values[i].strip() if i < len(values) else ''
        try:
            rows.append(ObservationProperty(property_id=int(pid), value=val or None))
        except (TypeError, ValueError):
            continue
    return rows


@web.route('/observations/add', methods=['GET', 'POST'])
@login_required
def add_observation():
    """Add a new observation"""
    if request.method == 'POST':
        try:
            # Get basic form data
            object_id = request.form.get('object')
            place_id = request.form.get('place')
            instrument_id = request.form.get('instrument')
            session_id = request.form.get('session')
            datetime_str = request.form.get('datetime')
            observation_text = request.form.get('observation')

            # Parse datetime
            obs_datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))

            # Create new observation (id is AUTO_INCREMENT)
            new_observation = Observation(
                object=int(object_id),
                place=int(place_id),
                instrument=int(instrument_id),
                session_id=int(session_id) if session_id else None,
                datetime=obs_datetime,
                observation=observation_text
            )
            
            # Handle properties (multiple property/value pairs)
            obs_props = _parse_observation_properties(request.form)
            new_observation.properties = obs_props
            if obs_props:
                new_observation.prop1 = obs_props[0].property_id
                new_observation.prop1value = obs_props[0].value
            
            # Handle AAVSO variable star fields
            vs_magnitude = request.form.get('vs_magnitude')
            if vs_magnitude:
                # Store AAVSO data in observation text or separate fields
                aavso_data = []
                aavso_data.append(f"Magnitude: {vs_magnitude}")
                
                vs_uncertainty = request.form.get('vs_uncertainty')
                if vs_uncertainty:
                    aavso_data.append(f"Uncertainty: {vs_uncertainty}")
                
                vs_comp1 = request.form.get('vs_comp_star1')
                if vs_comp1:
                    aavso_data.append(f"Comp1: {vs_comp1}")
                
                vs_comp2 = request.form.get('vs_comp_star2')
                if vs_comp2:
                    aavso_data.append(f"Comp2: {vs_comp2}")
                
                vs_check = request.form.get('vs_check_star')
                if vs_check:
                    aavso_data.append(f"Check: {vs_check}")
                
                vs_chart = request.form.get('vs_chart')
                if vs_chart:
                    aavso_data.append(f"Chart: {vs_chart}")
                
                vs_band = request.form.get('vs_band')
                if vs_band:
                    aavso_data.append(f"Band: {vs_band}")
                
                vs_observer = request.form.get('vs_observer_code')
                if vs_observer:
                    aavso_data.append(f"Observer: {vs_observer}")
                
                vs_method = request.form.get('vs_method')
                if vs_method:
                    aavso_data.append(f"Method: {vs_method}")
                
                # Append AAVSO data to observation text
                if aavso_data:
                    new_observation.observation += " [AAVSO: " + ", ".join(aavso_data) + "]"
            
            # Handle COBS comet fields
            comet_magnitude = request.form.get('comet_magnitude')
            if comet_magnitude:
                # Store COBS data in observation text
                cobs_data = []
                cobs_data.append(f"m1: {comet_magnitude}")
                
                coma_diameter = request.form.get('coma_diameter')
                if coma_diameter:
                    cobs_data.append(f"Coma: {coma_diameter}")
                
                dc = request.form.get('degree_condensation')
                if dc:
                    cobs_data.append(f"DC: {dc}")
                
                tail_length = request.form.get('tail_length')
                if tail_length:
                    cobs_data.append(f"Tail: {tail_length}")
                
                tail_pa = request.form.get('tail_pa')
                if tail_pa:
                    cobs_data.append(f"PA: {tail_pa}")
                
                ref_star = request.form.get('reference_star')
                if ref_star:
                    cobs_data.append(f"Ref: {ref_star}")
                
                sky = request.form.get('sky_conditions')
                if sky:
                    cobs_data.append(f"Sky: {sky}")
                
                comet_method = request.form.get('comet_method')
                if comet_method:
                    cobs_data.append(f"Method: {comet_method}")
                
                # Append COBS data to observation text
                if cobs_data:
                    new_observation.observation += " [COBS: " + ", ".join(cobs_data) + "]"
            
            db.session.add(new_observation)
            db.session.commit()
            
            flash('Observation added successfully!', 'success')
            # Came from a session page: go back there rather than to the
            # global list. Prefer the session actually saved on the
            # observation, in case it was changed on the form.
            if request.form.get('return_to_session'):
                back_to = new_observation.session_id or request.form.get('return_to_session')
                return redirect(url_for('web.view_session', session_id=int(back_to)))
            return redirect(url_for('web.list_observations'))
        except Exception as e:
            flash(f'Error adding observation: {str(e)}', 'danger')
            db.session.rollback()
    
    # Get data for the form
    try:
        objects = Object.query.all()
        places = Place.query.all()
        instruments = Instrument.query.all()
        properties = Property.query.all()
        sessions = Session.query.order_by(Session.start_datetime.desc()).all()
    except:
        objects = []
        places = []
        instruments = []
        properties = []
        sessions = []

    # Build session metadata for auto-fill
    import json as _json
    session_meta = {}
    for s in sessions:
        meta = {
            'instrument': s.instrument,
            'start_datetime': s.start_datetime.strftime('%Y-%m-%dT%H:%M:%S') if s.start_datetime else '',
            'limiting_magnitude': s.limiting_magnitude,
        }
        # Find place from most recent observation in this session
        last_obs = Observation.query.filter_by(session_id=s.id).order_by(Observation.datetime.desc()).first()
        meta['place'] = last_obs.place if last_obs else None
        session_meta[s.id] = meta

    # ?session=<id> preselects that session so the form opens pre-filled with
    # its date/time, instrument, place and limiting magnitude (used by the
    # "Add Observation" button on the session view page).
    # Falls back to the posted value so a failed submit keeps the context.
    try:
        prefill_session_id = int(request.args.get('session')
                                 or request.form.get('return_to_session') or '')
    except (TypeError, ValueError):
        prefill_session_id = None

    return render_template('observations/add.html',
                         objects=objects,
                         places=places,
                         instruments=instruments,
                         properties=properties,
                         sessions=sessions,
                         prefill_session_id=prefill_session_id,
                         session_meta_json=_json.dumps(session_meta))

@web.route('/observations/<int:obs_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_observation(obs_id):
    """Edit an existing observation"""
    obs = Observation.query.get(obs_id)
    if not obs:
        flash('Observation not found', 'danger')
        return redirect(url_for('web.list_observations'))

    if request.method == 'POST':
        try:
            obs.object = int(request.form.get('object'))
            obs.place = int(request.form.get('place'))
            obs.instrument = int(request.form.get('instrument'))
            session_id = request.form.get('session')
            obs.session_id = int(session_id) if session_id else None
            datetime_str = request.form.get('datetime')
            if datetime_str:
                obs.datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            # The AAVSO fields are edited as fields, not as raw text: drop any
            # block the notes still carry and rebuild it from the form, so
            # saving twice can't stack duplicate blocks.
            notes = _strip_aavso_block(request.form.get('observation'))
            obs.observation = (notes + _build_aavso_block(request.form)).strip()

            # Replace the property set with the submitted rows
            obs_props = _parse_observation_properties(request.form)
            obs.properties = obs_props
            if obs_props:
                obs.prop1 = obs_props[0].property_id
                obs.prop1value = obs_props[0].value
            else:
                obs.prop1 = None
                obs.prop1value = None

            db.session.commit()
            flash('Observation updated successfully!', 'success')
            return redirect(url_for('web.list_observations'))
        except Exception as e:
            flash(f'Error updating observation: {str(e)}', 'danger')
            db.session.rollback()

    try:
        objects = Object.query.all()
        places = Place.query.all()
        instruments = Instrument.query.all()
        properties = Property.query.all()
        sessions = Session.query.order_by(Session.start_datetime.desc()).all()
    except:
        objects = []
        places = []
        instruments = []
        properties = []
        sessions = []

    # Variable-star observations get the full AAVSO fieldset, pre-filled from
    # the stored block; the notes box shows the text without it.
    aavso_values = _aavso_fields_from_text(obs.observation)
    return render_template('observations/edit.html', obs=obs,
                         objects=objects, places=places,
                         instruments=instruments, properties=properties,
                         sessions=sessions,
                         aavso=aavso_values,
                         notes_text=_strip_aavso_block(obs.observation),
                         observer_code=current_user.aavso_code or '')

@web.route('/observations/<int:obs_id>/delete', methods=['POST'])
@login_required
def delete_observation(obs_id):
    """Delete an observation"""
    try:
        obs = Observation.query.get(obs_id)
        if not obs:
            flash('Observation not found', 'danger')
            return redirect(url_for('web.list_observations'))
        db.session.delete(obs)
        db.session.commit()
        flash('Observation deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting observation: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_observations'))

@web.route('/observations/<int:obs_id>/duplicate', methods=['POST'])
@login_required
def duplicate_observation(obs_id):
    """Duplicate an existing observation"""
    from sqlalchemy import func
    try:
        obs = Observation.query.get(obs_id)
        if not obs:
            flash('Observation not found', 'danger')
            return redirect(url_for('web.list_observations'))

        max_id = db.session.query(func.max(Observation.id)).scalar()
        new_id = (max_id or 0) + 1

        new_obs = Observation(
            id=new_id,
            object=obs.object,
            place=obs.place,
            instrument=obs.instrument,
            session_id=obs.session_id,
            datetime=obs.datetime,
            observation=obs.observation,
            prop1=obs.prop1,
            prop1value=obs.prop1value,
        )
        db.session.add(new_obs)
        db.session.commit()
        flash('Observation duplicated successfully!', 'success')
        return redirect(url_for('web.edit_observation', obs_id=new_id))
    except Exception as e:
        flash(f'Error duplicating observation: {str(e)}', 'danger')
        db.session.rollback()
        return redirect(url_for('web.list_observations'))

# ============================================================================
# INSTRUMENTS
# ============================================================================

@web.route('/instruments')
@login_required
def list_instruments():
    """List all instruments"""
    try:
        instruments = Instrument.query.all()
        return render_template('instruments/list.html', instruments=instruments)
    except Exception as e:
        flash(f'Error loading instruments: {str(e)}', 'danger')
        return render_template('instruments/list.html', instruments=[])

@web.route('/instruments/add', methods=['GET', 'POST'])
@login_required
def add_instrument():
    """Add a new instrument"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            instrument_type = request.form.get('instrument_type')
            aperture = request.form.get('aperture')
            power = request.form.get('power')
            eyepiece = request.form.get('eyepiece')

            # Find the highest existing ID and add 1
            max_id = db.session.query(func.max(Instrument.id)).scalar()
            new_id = (max_id or 0) + 1

            # Create new instrument with explicit ID
            new_instrument = Instrument(
                id=new_id,
                name=name,
                instrument_type=instrument_type if instrument_type else None,
                aperture=aperture if aperture else None,
                power=power if power else None,
                eyepiece=eyepiece if eyepiece else None
            )
            
            db.session.add(new_instrument)
            db.session.commit()
            
            flash(f'Instrument "{name}" added successfully!', 'success')
            return redirect(url_for('web.list_instruments'))
        except Exception as e:
            flash(f'Error adding instrument: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('instruments/add.html')

@web.route('/instruments/<int:inst_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_instrument(inst_id):
    """Edit an existing instrument"""
    inst = Instrument.query.get(inst_id)
    if not inst:
        flash('Instrument not found', 'danger')
        return redirect(url_for('web.list_instruments'))

    if request.method == 'POST':
        try:
            inst.name = request.form.get('name')
            inst.instrument_type = request.form.get('instrument_type') or None
            inst.aperture = request.form.get('aperture') or None
            inst.power = request.form.get('power') or None
            inst.eyepiece = request.form.get('eyepiece') or None

            db.session.commit()
            flash(f'Instrument "{inst.name}" updated successfully!', 'success')
            return redirect(url_for('web.list_instruments'))
        except Exception as e:
            flash(f'Error updating instrument: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('instruments/edit.html', inst=inst)

@web.route('/instruments/<int:inst_id>/delete', methods=['POST'])
@login_required
def delete_instrument(inst_id):
    """Delete an instrument"""
    try:
        inst = Instrument.query.get(inst_id)
        if not inst:
            flash('Instrument not found', 'danger')
            return redirect(url_for('web.list_instruments'))
        name = inst.name
        db.session.delete(inst)
        db.session.commit()
        flash(f'Instrument "{name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting instrument: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_instruments'))

# ============================================================================
# PLACES
# ============================================================================

@web.route('/places')
@login_required
def list_places():
    """List all places"""
    try:
        places = Place.query.all()
        return render_template('places/list.html', places=places)
    except Exception as e:
        flash(f'Error loading places: {str(e)}', 'danger')
        return render_template('places/list.html', places=[])

@web.route('/places/add', methods=['GET', 'POST'])
@login_required
def add_place():
    """Add a new place"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            alias = request.form.get('alias')
            lat = request.form.get('lat')
            lon = request.form.get('lon')
            alt = request.form.get('alt')
            timezone = request.form.get('timezone')

            # Create new place (id is AUTO_INCREMENT)
            new_place = Place(
                name=name,
                alias=alias if alias else None,
                lat=lat,
                lon=lon,
                alt=alt if alt else None,
                timezone=timezone if timezone else None
            )
            
            db.session.add(new_place)
            db.session.commit()
            
            flash(f'Place "{name}" added successfully!', 'success')
            return redirect(url_for('web.list_places'))
        except Exception as e:
            flash(f'Error adding place: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('places/add.html')

@web.route('/places/<int:place_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_place(place_id):
    """Edit an existing place"""
    place = Place.query.get(place_id)
    if not place:
        flash('Place not found', 'danger')
        return redirect(url_for('web.list_places'))

    if request.method == 'POST':
        try:
            place.name = request.form.get('name')
            place.alias = request.form.get('alias') or None
            place.lat = request.form.get('lat')
            place.lon = request.form.get('lon')
            place.alt = request.form.get('alt') or None
            place.timezone = request.form.get('timezone') or None

            db.session.commit()
            flash(f'Place "{place.name}" updated successfully!', 'success')
            return redirect(url_for('web.list_places'))
        except Exception as e:
            flash(f'Error updating place: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('places/edit.html', place=place)

@web.route('/places/<int:place_id>/delete', methods=['POST'])
@login_required
def delete_place(place_id):
    """Delete a place"""
    try:
        place = Place.query.get(place_id)
        if not place:
            flash('Place not found', 'danger')
            return redirect(url_for('web.list_places'))
        name = place.name
        db.session.delete(place)
        db.session.commit()
        flash(f'Place "{name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting place: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_places'))

@web.route('/places/<int:place_id>/set-default', methods=['POST'])
@login_required
def set_default_place(place_id):
    """Mark a place as the default observing site (clearing any previous one)."""
    try:
        place = Place.query.get(place_id)
        if not place:
            flash('Place not found', 'danger')
            return redirect(url_for('web.list_places'))
        Place.query.update({Place.is_default: False})
        place.is_default = True
        db.session.commit()
        flash(f'"{place.alias or place.name}" is now the default site.', 'success')
    except Exception as e:
        flash(f'Error setting default site: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_places'))

# ============================================================================
# WEATHER
# ============================================================================

# Naked-eye limit of the bundled star catalogue (see create_star_catalog.py)
SKY_MAG_LIMIT = 5.5


def get_default_place():
    """The place marked as default, else the only place, else None."""
    try:
        place = Place.query.filter_by(is_default=True).first()
        if place:
            return place
        places = Place.query.all()
        return places[0] if len(places) == 1 else None
    except Exception:
        return None


def _coord(value):
    """Parse a stored lat/lon string to float, or None if unusable."""
    try:
        return float(str(value).strip().replace(',', '.'))
    except (TypeError, ValueError):
        return None


def build_weather_services(place):
    """Build the external weather services for an observing site.

    One entry per provider, each carrying every viewpoint that provider offers
    for a fixed location. Services that accept coordinates are centred on the
    site. ``embeddable`` is False where the provider sends X-Frame-Options and
    refuses to render in an iframe.
    """
    lat = _coord(getattr(place, 'lat', None)) if place else None
    lon = _coord(getattr(place, 'lon', None)) if place else None
    has_coords = lat is not None and lon is not None
    ll_lat = lat if has_coords else 52.0
    ll_lon = lon if has_coords else 19.0

    # wxcharts wants a forecast timestamp; use today's 06:00Z run window.
    dtg = datetime.utcnow().strftime('%Y-%m-%dT06:00:00Z')
    today = datetime.utcnow().strftime('%Y-%m-%d')
    imgw_loc = f'{ll_lat},{ll_lon},8.25'

    wxcharts_url = ('https://www.wxcharts.com/?dataset=ecmwf_op&region=poland'
                    '&element=overview&run=00&dtg=' + quote(dtg, safe='') +
                    '&meteoModel=ecop&ensModel=eceps&chartRun=0'
                    + (f'&lat={ll_lat}&lon={ll_lon}' if has_coords else ''))

    services = []

    services.append({
        'id': 'wxcharts',
        'short': 'WXCHARTS',
        'name': 'WXCHARTS - ECMWF operational',
        'icon': 'bi-cloud-haze2',
        'targeted': has_coords,
        'note': 'WXCHARTS refuses to be embedded, so this one opens in a new tab.',
        'views': [{
            'label': 'ECMWF overview (Poland)',
            'desc': 'Pressure, precipitation and cloud from the 00Z run.',
            'url': wxcharts_url,
            'embeddable': False,
        }],
    })

    # ICM/meteo.pl resolves lat/lon to its own grid point via mgram_search.
    if has_coords:
        um = f'https://old.meteo.pl/um/php/mgram_search.php?NALL={lat}&EALL={lon}'
        coamps = f'https://old.meteo.pl/php/mgram_search.php?NALL={lat}&EALL={lon}&lang=pl'
    else:
        um = coamps = 'https://old.meteo.pl/'
    services.append({
        'id': 'meteopl',
        'short': 'meteo.pl',
        'name': 'meteo.pl - ICM numerical forecasts',
        'icon': 'bi-graph-up',
        'targeted': has_coords,
        'note': None,
        'views': [
            {'label': 'UM model meteorogram',
             'desc': 'Hourly meteorogram for the UM grid point nearest the site.',
             'url': um, 'embeddable': True},
            {'label': 'COAMPS model meteorogram',
             'desc': 'The same location in the COAMPS model, for comparison.',
             'url': coamps, 'embeddable': True},
        ],
    })

    services.append({
        'id': 'wunderground',
        'short': 'Wunderground',
        'name': 'Weather Underground - PWS IGSAWY6',
        'icon': 'bi-thermometer-half',
        'targeted': has_coords,
        'note': None,
        'views': [
            {'label': 'Station dashboard',
             'desc': 'Live readings from the local personal weather station.',
             'url': 'https://www.wunderground.com/dashboard/pws/IGSAWY6',
             'embeddable': True},
            {'label': 'Today - graph',
             'desc': 'Temperature, humidity, pressure and wind through the day.',
             'url': ('https://www.wunderground.com/dashboard/pws/IGSAWY6/graph/'
                     f'{today}/{today}/daily'),
             'embeddable': True},
            {'label': 'Today - table',
             'desc': 'The same readings as a numeric log.',
             'url': ('https://www.wunderground.com/dashboard/pws/IGSAWY6/table/'
                     f'{today}/{today}/daily'),
             'embeddable': True},
            {'label': 'WunderMap',
             'desc': 'Radar and nearby stations around the site.',
             'url': f'https://www.wunderground.com/wundermap?lat={ll_lat}&lon={ll_lon}',
             'embeddable': True},
        ],
    })

    services.append({
        'id': 'imgw',
        'short': 'IMGW',
        'name': 'IMGW - radar and satellite',
        'icon': 'bi-radar',
        'targeted': has_coords,
        'note': None,
        'views': [
            {'label': 'Radar - maximum reflectivity (CMAX)',
             'desc': 'Precipitation echoes, centred on the site.',
             'url': f'https://meteo.imgw.pl/dyn/index.html#group=radar&param=cmax&loc={imgw_loc}',
             'embeddable': True},
            {'label': 'Satellite - MTG day/night microphysics',
             'desc': 'Cloud cover that stays readable after dark.',
             'url': ('https://meteo.imgw.pl/dyn/index.html#group=sat'
                     f'&param=mtg-day-night-microphysics&loc={imgw_loc}'),
             'embeddable': True},
        ],
    })

    services.append({
        'id': 'lightning',
        'short': 'Lightning',
        'name': 'LightningMaps - live strikes',
        'icon': 'bi-lightning',
        'targeted': has_coords,
        'note': 'LightningMaps refuses to be embedded, so this one opens in a new tab.',
        'views': [{
            'label': 'Live strike map',
            'desc': 'Real-time lightning detection around the site.',
            'url': ('https://www.lightningmaps.org/#m=ses;t=3;s=0;o=0;b=;ts=0;z=9;'
                    f'y={ll_lat};x={ll_lon};d=2;dl=2;dc=0;'),
            'embeddable': False,
        }],
    })

    return services


@web.route('/weather')
@login_required
def weather():
    """Weather services for the default observing site."""
    place = get_default_place()
    places = []
    try:
        places = Place.query.all()
    except Exception:
        pass
    return render_template('weather/index.html',
                           place=place,
                           places=places,
                           lat=_coord(getattr(place, 'lat', None)) if place else None,
                           lon=_coord(getattr(place, 'lon', None)) if place else None,
                           services=build_weather_services(place))

@web.route('/sky')
@login_required
def sky_map():
    """Live all-sky chart for the default observing site."""
    place = get_default_place()
    places = []
    try:
        places = Place.query.all()
    except Exception:
        pass
    return render_template('sky/index.html',
                           place=place,
                           places=places,
                           lat=_coord(getattr(place, 'lat', None)) if place else None,
                           lon=_coord(getattr(place, 'lon', None)) if place else None,
                           mag_limit=SKY_MAG_LIMIT)


@web.route('/sky/stars')
@login_required
def sky_stars():
    """The naked-eye star catalogue behind the sky map.

    Normally written at startup by create_star_catalog.py; rebuilt on demand
    if that download failed, so the page recovers without a restart.
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'stars.json')
    if not os.path.isfile(path):
        try:
            from create_star_catalog import build_catalog
            build_catalog()
        except Exception as e:
            return jsonify({'error': f'Star catalogue unavailable: {e}'}), 503
    try:
        with open(path) as f:
            return Response(f.read(), mimetype='application/json')
    except Exception as e:
        return jsonify({'error': f'Star catalogue unreadable: {e}'}), 500


# Drawn on the sky map with the stars. Colours are picked so each planet stays
# distinguishable against a dark chart.
SKY_BODIES = [
    ('Sun', 'sun', '#ffd24d'),
    ('Moon', 'moon', '#e8e8f0'),
    ('Mercury', 'planet', '#c9a37a'),
    ('Venus', 'planet', '#fff3c4'),
    ('Mars', 'planet', '#ff7a5c'),
    ('Jupiter', 'planet', '#ffcf8f'),
    ('Saturn', 'planet', '#e6d5a0'),
    ('Uranus', 'planet', '#a9e6f0'),
    ('Neptune', 'planet', '#8fb3ff'),
]


def _moon_phase_name(illumination, waxing):
    """'waxing gibbous' and friends, from percent illuminated."""
    if illumination < 2:
        return 'new'
    if illumination > 98:
        return 'full'
    if 48 <= illumination <= 52:
        return 'first quarter' if waxing else 'last quarter'
    shape = 'crescent' if illumination < 50 else 'gibbous'
    return ('waxing ' if waxing else 'waning ') + shape


@web.route('/sky/solar-system')
@login_required
def sky_solar_system():
    """Current Sun, Moon and planet positions for the default site.

    Computed with PyEphem rather than in the browser: the Moon in particular
    needs topocentric parallax, which is nearly a degree.
    """
    place = get_default_place()
    lat = _coord(getattr(place, 'lat', None)) if place else None
    lon = _coord(getattr(place, 'lon', None)) if place else None
    if lat is None or lon is None:
        return jsonify({'error': 'No default site with usable coordinates'}), 400

    try:
        import ephem
        import math as _math
    except Exception as e:
        return jsonify({'error': f'Ephemeris library unavailable: {e}'}), 503

    try:
        obs = ephem.Observer()
        obs.lat = str(lat)
        obs.lon = str(lon)
        # Altitude in metres, if the place records one ('75m' -> 75)
        try:
            obs.elevation = float(_re.sub(r'[^0-9.\-]', '', str(place.alt or '')) or 0)
        except Exception:
            obs.elevation = 0
        # Geometric positions, matching how the star chart is drawn
        obs.pressure = 0
        obs.date = ephem.now()

        bodies = []
        moon_info = None
        sun_alt = None
        for name, kind, colour in SKY_BODIES:
            body = getattr(ephem, name)()
            body.compute(obs)
            alt = _math.degrees(float(body.alt))
            entry = {
                'name': name,
                'kind': kind,
                'colour': colour,
                'alt': round(alt, 3),
                'az': round(_math.degrees(float(body.az)), 3),
                'mag': round(float(body.mag), 1),
            }
            if kind == 'moon':
                illum = float(body.moon_phase) * 100.0
                waxing = float(body.elong) > 0     # east of the Sun
                entry['illumination'] = round(illum, 1)
                entry['phase'] = _moon_phase_name(illum, waxing)
                moon_info = entry
            if name == 'Sun':
                sun_alt = alt
            bodies.append(entry)

        # Twilight state, the thing that decides whether observing is on
        if sun_alt is None:
            twilight = ''
        elif sun_alt > 0:
            twilight = 'daylight'
        elif sun_alt > -6:
            twilight = 'civil twilight'
        elif sun_alt > -12:
            twilight = 'nautical twilight'
        elif sun_alt > -18:
            twilight = 'astronomical twilight'
        else:
            twilight = 'astronomical night'

        return jsonify({
            'bodies': bodies,
            'sun_alt': round(sun_alt, 2) if sun_alt is not None else None,
            'twilight': twilight,
            'moon': moon_info,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ----------------------------------------------------------------------------
# COMET / PLANET PATH CHART
# ----------------------------------------------------------------------------
# The classic "path of comet X" finder chart: the track across the sky over a
# period, ticked with dates, drawn over the stars of that patch of sky.

PATH_MAX_POINTS = 400


VIZIER_TAP = "https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync"
# Beyond this, SIMBAD is no longer a useful star field: it is an object
# database, not a survey, so a deep chart comes from Gaia instead.
DEEP_MAG_THRESHOLD = 11.0
DEEP_MAX_STARS = 6000


def _gaia_star_field(ra, dec, radius_deg, maglimit):
    """Gaia DR3 stars in a circle, for a deep 'lens view' field.

    The positional constraint is written as CONTAINS/CIRCLE so VizieR can use
    its spatial index - the same query with RA/Dec BETWEEN takes two minutes
    instead of three seconds.
    """
    adql = (
        f'SELECT TOP {DEEP_MAX_STARS} RAJ2000, DEJ2000, Gmag FROM "I/355/gaiadr3" '
        f"WHERE 1=CONTAINS(POINT('ICRS',RAJ2000,DEJ2000), "
        f"CIRCLE('ICRS', {ra}, {dec}, {radius_deg})) AND Gmag <= {maglimit}")
    try:
        resp = http_requests.get(VIZIER_TAP, params={
            'request': 'doQuery', 'lang': 'adql', 'format': 'json', 'query': adql,
        }, timeout=120)
        resp.raise_for_status()
        rows = resp.json().get('data', [])
    except Exception as e:
        print(f'  path chart: Gaia field unavailable: {e}')
        return []
    stars = []
    for row in rows:
        try:
            stars.append([round(float(row[0]), 5), round(float(row[1]), 5),
                          round(float(row[2]), 2), ''])
        except (TypeError, ValueError, IndexError):
            continue
    stars.sort(key=lambda s: s[2])
    return stars


def _path_star_field(ra_min, ra_max, dec_min, dec_max, maglimit):
    """Stars in one patch of sky, from SIMBAD.

    Queried per chart rather than taken from the bundled catalogue: a small
    field can afford a much fainter limit than an all-sky file could.
    """
    dec_min = max(-90.0, dec_min)
    dec_max = min(90.0, dec_max)

    # An RA range crossing 0h has to be asked for as two pieces
    if ra_min < 0 or ra_max > 360:
        ra_clause = (f"(b.ra >= {ra_min % 360} OR b.ra <= {ra_max % 360})")
    else:
        ra_clause = f"b.ra BETWEEN {ra_min} AND {ra_max}"

    adql = (
        "SELECT TOP 3000 b.main_id, b.ra, b.dec, f.V "
        "FROM basic AS b JOIN allfluxes AS f ON f.oidref = b.oid "
        f"WHERE f.V <= {maglimit} AND {ra_clause} "
        f"AND b.dec BETWEEN {dec_min} AND {dec_max}")
    rows = _run_tap_raw(adql, timeout=90)
    stars = []
    for row in rows:
        ra, dec, v = row.get('ra'), row.get('dec'), row.get('V')
        if ra is None or dec is None or v is None:
            continue
        name = _re.sub(r'^(V\*|NAME|\*\*|\*)\s+', '', str(row.get('main_id') or '')).strip()
        stars.append([round(float(ra), 5), round(float(dec), 5), round(float(v), 2), name])
    stars.sort(key=lambda s: s[2])
    return stars


@web.route('/comet-path/data')
@login_required
def comet_path_data():
    """Sky track for a comet, planet or catalogue object, plus its star field."""
    try:
        import ephem
    except Exception as e:
        return jsonify({'error': f'Ephemeris library unavailable: {e}'}), 503

    try:
        start = datetime.fromisoformat(request.args.get('start'))
        end = datetime.fromisoformat(request.args.get('end'))
    except Exception:
        return jsonify({'error': 'start and end dates are required (YYYY-MM-DD)'}), 400
    if end < start:
        start, end = end, start

    try:
        step = max(1, int(request.args.get('step') or 2))
    except ValueError:
        step = 2
    try:
        maglimit = float(request.args.get('maglimit') or 8.0)
    except ValueError:
        maglimit = 8.0
    maglimit = max(4.0, min(maglimit, 16.0))

    try:
        fov = float(request.args.get('fov') or 0)
    except ValueError:
        fov = 0.0
    fov = max(0.0, min(fov, 20.0))
    center_date = (request.args.get('center_date') or '').strip()

    # A deep limit is only sensible over a small field; a whole-path chart at
    # mag 16 would be an unreadable smear of a million stars.
    if maglimit > DEEP_MAG_THRESHOLD and fov <= 0:
        return jsonify({'error': f'Stars fainter than mag {DEEP_MAG_THRESHOLD:.0f} need a '
                                 f'field of view - pick one instead of the whole path.'}), 400
    if fov > 5 and maglimit > 13:
        return jsonify({'error': f'A {fov:.0f}\u00b0 field to mag {maglimit:.0f} is too many '
                                 f'stars - narrow the field or lift the limit.'}), 400

    days = (end - start).days
    if days // step + 1 > PATH_MAX_POINTS:
        return jsonify({'error': f'Too many steps; widen the interval or shorten the period'}), 400

    # The moving object: a catalogue object (usually a comet) or a planet
    name = ''
    planet = (request.args.get('planet') or '').strip()
    object_id = request.args.get('object_id')
    if planet:
        if planet not in [b[0] for b in ALMANAC_BODIES] + ['Sun']:
            return jsonify({'error': 'Unknown planet'}), 400
        body = getattr(ephem, planet)()
        name = planet
    elif object_id and object_id.isdigit():
        obj = Object.query.get(int(object_id))
        if not obj:
            return jsonify({'error': 'Object not found'}), 404
        body, err = _ephem_body_for_object(obj, ephem)
        if body is None:
            return jsonify({'error': err}), 400
        name = obj.name
    else:
        return jsonify({'error': 'Choose a comet, object or planet'}), 400

    path = []
    day = start
    while day <= end:
        try:
            body.compute(ephem.Date(day.strftime('%Y/%m/%d 00:00:00')))
            path.append({
                'date': day.strftime('%Y-%m-%d'),
                'ra': round(math.degrees(float(body.a_ra)), 5),
                'dec': round(math.degrees(float(body.a_dec)), 5),
                'mag': round(float(body.mag), 1),
            })
        except Exception:
            pass
        day += timedelta(days=step)

    if len(path) < 2:
        return jsonify({'error': 'Could not compute a path for this object'}), 400

    # Unwrap RA across 0h so the track stays continuous, then frame it
    ras = [p['ra'] for p in path]
    unwrapped = [ras[0]]
    for value in ras[1:]:
        prev = unwrapped[-1]
        while value - prev > 180:
            value -= 360
        while prev - value > 180:
            value += 360
        unwrapped.append(value)
    for p, u in zip(path, unwrapped):
        p['ra_plot'] = round(u, 5)

    decs = [p['dec'] for p in path]

    # How far the object actually travels, as an angle on the sky. A finder
    # chart is a tangent-plane projection, so it only makes sense over a modest
    # field - a fast comet can cross a third of the sky in two months.
    def _sep(a, b):
        ra1, d1, ra2, d2 = (math.radians(x) for x in
                            (a['ra'], a['dec'], b['ra'], b['dec']))
        cos_sep = (math.sin(d1) * math.sin(d2) +
                   math.cos(d1) * math.cos(d2) * math.cos(ra1 - ra2))
        return math.degrees(math.acos(max(-1.0, min(1.0, cos_sep))))

    span_deg = max(_sep(path[0], p) for p in path)
    span_deg = max(span_deg, _sep(path[0], path[-1]))
    if span_deg > 70 and not (request.args.get('fov') or '').strip('0. '):
        return jsonify({
            'error': (f'{name} moves {span_deg:.0f}\u00b0 over this period - too far for one '
                      f'finder chart. Try a shorter period or a larger tick interval.'),
            'span_deg': round(span_deg, 1),
        }), 400

    ra_span = max(unwrapped) - min(unwrapped)
    dec_span = max(decs) - min(decs)
    dec_mid = (max(decs) + min(decs)) / 2.0
    # RA degrees compress towards the poles; margin in real sky degrees
    margin = max(2.0, dec_span * 0.25, ra_span * math.cos(math.radians(dec_mid)) * 0.25)
    ra_margin = margin / max(0.2, math.cos(math.radians(dec_mid)))

    lens = None
    if fov > 0:
        # Centre on the object's place on the chosen date (default: mid-period)
        centre = path[len(path) // 2]
        if center_date:
            for p in path:
                if p['date'] == center_date:
                    centre = p
                    break
        half = fov / 2.0
        ra_half = half / max(0.05, math.cos(math.radians(centre['dec'])))
        field = {
            'ra_min': centre['ra_plot'] - ra_half,
            'ra_max': centre['ra_plot'] + ra_half,
            'dec_min': max(-90.0, centre['dec'] - half),
            'dec_max': min(90.0, centre['dec'] + half),
        }
        lens = {'ra': centre['ra'], 'dec': centre['dec'], 'date': centre['date'], 'fov': fov}
    else:
        field = {
            'ra_min': min(unwrapped) - ra_margin,
            'ra_max': max(unwrapped) + ra_margin,
            'dec_min': max(-90.0, min(decs) - margin),
            'dec_max': min(90.0, max(decs) + margin),
        }

    stars = []
    try:
        if maglimit > DEEP_MAG_THRESHOLD and lens:
            # Gaia for the faint field, plus SIMBAD's bright stars so the chart
            # still carries recognisable names to orient by.
            stars = _gaia_star_field(lens['ra'], lens['dec'], fov * 0.75, maglimit)
            named = _path_star_field(field['ra_min'], field['ra_max'],
                                     field['dec_min'], field['dec_max'],
                                     min(DEEP_MAG_THRESHOLD, 9.0))
            seen = set()
            merged = []
            for star in named + stars:
                key = (round(star[0], 3), round(star[1], 3))
                if key in seen:
                    continue
                seen.add(key)
                merged.append(star)
            stars = sorted(merged, key=lambda x: x[2])
        else:
            stars = _path_star_field(field['ra_min'], field['ra_max'],
                                     field['dec_min'], field['dec_max'], maglimit)
    except Exception as e:
        stars = []
        print(f'  comet path: star field unavailable: {e}')

    return jsonify({
        'name': name,
        'span_deg': round(span_deg, 1),
        'lens': lens,
        'deep': bool(lens and maglimit > DEEP_MAG_THRESHOLD),
        'stars_capped': len(stars) >= (DEEP_MAX_STARS if lens else 3000),
        'start': start.strftime('%Y-%m-%d'),
        'end': end.strftime('%Y-%m-%d'),
        'step': step,
        'maglimit': maglimit,
        'path': path,
        'field': field,
        'stars': stars,
    })


@web.route('/comet-path')
@login_required
def comet_path():
    """Finder chart showing an object's path across the stars."""
    comets, others = [], []
    try:
        comet_type = Type.query.filter_by(name='Comet').first()
        if comet_type:
            comets = Object.query.filter_by(type=comet_type.id).order_by(Object.name).all()
        others = Object.query.order_by(Object.name).limit(2000).all()
    except Exception:
        pass
    return render_template('almanac/comet_path.html',
                           comets=comets, objects=others,
                           planets=[b[0] for b in ALMANAC_BODIES])


# ----------------------------------------------------------------------------
# ALMANAC / VISIBILITY CHART
# ----------------------------------------------------------------------------
# A night-by-night diagram: dates across, time of night up, twilight shaded,
# and a curve per body for its rising, setting and culmination.

ALMANAC_BODIES = [
    ('Moon', '#e8e8f0'),
    ('Mercury', '#c9a37a'),
    ('Venus', '#fff3c4'),
    ('Mars', '#ff7a5c'),
    ('Jupiter', '#ffcf8f'),
    ('Saturn', '#e6d5a0'),
    ('Uranus', '#a9e6f0'),
    ('Neptune', '#8fb3ff'),
]

# Twilight boundaries, darkest last. Sun altitudes in degrees.
ALMANAC_TWILIGHTS = [
    ('day', '-0:34'),
    ('civil', '-6'),
    ('nautical', '-12'),
    ('astronomical', '-18'),
]

ALMANAC_MAX_DAYS = 400


def _object_magnitude_range(obj):
    """[brightest, faintest] from a stored 'magnitude_range' like '3.48-4.37'."""
    try:
        props = json.loads(obj.props) if obj.props else {}
    except Exception:
        return None
    raw = props.get('magnitude_range') or props.get('magnitude_v')
    if not raw:
        return None
    nums = _re.findall(r'-?\d+(?:\.\d+)?', str(raw))
    if not nums:
        return None
    values = [float(n) for n in nums[:2]]
    if len(values) == 1:
        return [values[0], values[0]]
    return [min(values), max(values)]


def _almanac_observer(place, ephem):
    obs = ephem.Observer()
    obs.lat = str(_coord(place.lat))
    obs.lon = str(_coord(place.lon))
    try:
        obs.elevation = float(_re.sub(r'[^0-9.\-]', '', str(place.alt or '')) or 0)
    except Exception:
        obs.elevation = 0
    return obs


def _hours_since_noon(when, tzinfo, ephem):
    """Event time as hours after the local noon that starts its night.

    The chart's y axis runs from afternoon up through midnight to morning, so
    an evening event lands near 4-6 and a morning one near 16-20.
    """
    if when is None:
        return None
    dt = ephem.Date(when).datetime().replace(tzinfo=timezone.utc)
    if tzinfo is not None:
        dt = dt.astimezone(tzinfo)
    return dt.hour + dt.minute / 60.0 + dt.second / 3600.0


def _almanac_event(obs, body, kind, ephem):
    """Rising / setting / transit for the night that follows obs.date.

    Returns (event, status). A missing event is not always the same thing: a
    circumpolar target never sets and one below the horizon never rises, and an
    observer wants to be told which.
    """
    try:
        if kind == 'rise':
            return obs.next_rising(body), 'ok'
        if kind == 'set':
            return obs.next_setting(body), 'ok'
        return obs.next_transit(body), 'ok'
    except ephem.AlwaysUpError:
        return None, 'always_up'
    except ephem.NeverUpError:
        return None, 'never_up'
    except Exception:
        return None, 'none'


@web.route('/almanac/data')
@login_required
def almanac_data():
    """Rise/set/transit curves plus twilight bands for the chart."""
    try:
        import ephem
    except Exception as e:
        return jsonify({'error': f'Ephemeris library unavailable: {e}'}), 503

    place_id = request.args.get('place_id')
    place = None
    if place_id:
        place = Place.query.get(int(place_id)) if place_id.isdigit() else None
    if place is None:
        place = get_default_place()
    if place is None or _coord(place.lat) is None or _coord(place.lon) is None:
        return jsonify({'error': 'No place with usable coordinates'}), 400

    try:
        start = datetime.fromisoformat(request.args.get('start'))
        end = datetime.fromisoformat(request.args.get('end'))
    except Exception:
        return jsonify({'error': 'start and end dates are required (YYYY-MM-DD)'}), 400
    if end < start:
        start, end = end, start
    days = (end - start).days + 1
    if days > ALMANAC_MAX_DAYS:
        return jsonify({'error': f'Period too long: {days} days (max {ALMANAC_MAX_DAYS})'}), 400

    use_utc = request.args.get('tz') == 'utc'
    tzinfo = None
    tz_label = 'UTC'
    if not use_utc:
        try:
            from zoneinfo import ZoneInfo
            tzinfo = ZoneInfo(place.timezone) if place.timezone else timezone.utc
            tz_label = place.timezone or 'UTC'
        except Exception:
            tzinfo = timezone.utc
            tz_label = 'UTC'
    else:
        tzinfo = timezone.utc

    wanted = [b for b in (request.args.get('bodies') or '').split(',') if b]
    object_ids = [int(i) for i in (request.args.get('objects') or '').split(',') if i.isdigit()]

    obs = _almanac_observer(place, ephem)

    # Bodies to plot: solar-system by name, catalogue objects by id
    series = []
    for name, colour in ALMANAC_BODIES:
        if name in wanted:
            series.append({'name': name, 'colour': colour,
                           'make': (lambda n: (lambda: getattr(ephem, n)()))(name),
                           'magnitude': 'computed'})
    skipped = []
    palette = ['#7ee787', '#f778ba', '#a5d6ff', '#ffab70', '#d2a8ff']
    for idx, oid in enumerate(object_ids):
        obj = Object.query.get(oid)
        if not obj:
            continue
        body, err = _ephem_body_for_object(obj, ephem)
        if body is None:
            skipped.append(obj.name + (' (' + err + ')' if err else ''))
            continue
        # A comet's brightness follows from its orbit; a fixed object only has
        # whatever range the catalogue recorded, which is flat over the period.
        entry = {'name': obj.name, 'colour': palette[idx % len(palette)],
                 'make': (lambda b: (lambda: b))(body),
                 'magnitude': 'computed' if _is_comet(obj) else 'none'}
        if not _is_comet(obj):
            rng = _object_magnitude_range(obj)
            if rng:
                entry['magnitude'] = 'range'
                entry['range'] = rng
        series.append(entry)

    sun = ephem.Sun()
    dates, twilight, curves = [], [], {}
    statuses = {}
    for sp in series:
        curves[sp['name']] = {'colour': sp['colour'], 'rise': [], 'set': [],
                              'transit': [], 'mag': []}
        if sp.get('magnitude') == 'range':
            curves[sp['name']]['mag_range'] = sp['range']
        statuses[sp['name']] = set()

    day = start
    while day <= end:
        dates.append(day.strftime('%Y-%m-%d'))
        # Anchor each night at local noon so the window spans one night
        anchor = day.replace(hour=12, minute=0, second=0)
        if tzinfo is not None and tzinfo is not timezone.utc:
            anchor_utc = anchor.replace(tzinfo=tzinfo).astimezone(timezone.utc)
        else:
            anchor_utc = anchor.replace(tzinfo=timezone.utc)
        anchor_naive = anchor_utc.replace(tzinfo=None)

        night = {}
        for label, horizon in ALMANAC_TWILIGHTS:
            obs.date = anchor_naive
            obs.horizon = horizon
            obs.pressure = 0
            centre = label != 'day'
            try:
                dusk = obs.next_setting(sun, use_center=centre)
                dawn = obs.next_rising(sun, use_center=centre)
            except (ephem.AlwaysUpError, ephem.NeverUpError):
                dusk = dawn = None
            except Exception:
                dusk = dawn = None
            night[label + '_dusk'] = _hours_since_noon(dusk, tzinfo, ephem)
            night[label + '_dawn'] = _hours_since_noon(dawn, tzinfo, ephem)
        twilight.append(night)

        obs.horizon = '-0:34'
        for sp in series:
            body = sp['make']()
            for kind in ('rise', 'set', 'transit'):
                obs.date = anchor_naive
                ev, status = _almanac_event(obs, body, kind, ephem)
                curves[sp['name']][kind].append(_hours_since_noon(ev, tzinfo, ephem))
                if status in ('always_up', 'never_up'):
                    statuses[sp['name']].add(status)

            # Brightness at local midnight: it depends on the geometry of the
            # night, not on where the object happens to be in the sky.
            mag = None
            if sp.get('magnitude') == 'computed':
                try:
                    # anchor_naive is a datetime; half a day of ephem.Date is
                    # what moves it from local noon to local midnight.
                    obs.date = ephem.Date(anchor_naive) + 0.5
                    body.compute(obs)
                    mag = round(float(body.mag), 2)
                except Exception as exc:
                    print(f"  almanac: no magnitude for {sp['name']}: {exc}")
                    mag = None
            curves[sp['name']]['mag'].append(mag)

        day += timedelta(days=1)

    # Tell the reader why a rise/set line is missing rather than leaving a gap
    for name, flags in statuses.items():
        note = ''
        if 'always_up' in flags and 'never_up' in flags:
            note = 'circumpolar for part of the period'
        elif 'always_up' in flags:
            note = 'circumpolar - never sets'
        elif 'never_up' in flags:
            note = 'never rises from this site'
        if note:
            curves[name]['note'] = note

    return jsonify({
        'place': {'id': place.id, 'name': place.alias or place.name,
                  'lat': _coord(place.lat), 'lon': _coord(place.lon)},
        'timezone': tz_label,
        'start': start.strftime('%Y-%m-%d'),
        'end': end.strftime('%Y-%m-%d'),
        'dates': dates,
        'twilight': twilight,
        'curves': curves,
        'skipped': skipped,
    })


@web.route('/almanac')
@login_required
def almanac():
    """Visibility chart: twilight and rise/set curves over a period."""
    places = []
    objects = []
    try:
        places = Place.query.all()
        objects = Object.query.order_by(Object.name).all()
    except Exception:
        pass
    return render_template('almanac/index.html',
                           places=places,
                           objects=objects,
                           default_place=get_default_place(),
                           bodies=[{'name': n, 'colour': c} for n, c in ALMANAC_BODIES])


# ============================================================================
# TYPES
# ============================================================================

@web.route('/types')
@login_required
def list_types():
    """List all types"""
    try:
        types = Type.query.all()
        return render_template('types/list.html', types=types)
    except Exception as e:
        flash(f'Error loading types: {str(e)}', 'danger')
        return render_template('types/list.html', types=[])

@web.route('/types/add', methods=['GET', 'POST'])
@login_required
def add_type():
    """Add a new type"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            
            # Find the highest existing ID and add 1
            max_id = db.session.query(func.max(Type.id)).scalar()
            new_id = (max_id or 0) + 1
            
            # Create new type with explicit ID
            new_type = Type(
                id=new_id,
                name=name
            )
            
            db.session.add(new_type)
            db.session.commit()
            
            flash(f'Type "{name}" added successfully!', 'success')
            return redirect(url_for('web.list_types'))
        except Exception as e:
            flash(f'Error adding type: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('types/add.html')

@web.route('/types/<int:type_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_type(type_id):
    """Edit an existing type"""
    type_obj = Type.query.get(type_id)
    if not type_obj:
        flash('Type not found', 'danger')
        return redirect(url_for('web.list_types'))

    if request.method == 'POST':
        try:
            type_obj.name = request.form.get('name')
            db.session.commit()
            flash(f'Type "{type_obj.name}" updated successfully!', 'success')
            return redirect(url_for('web.list_types'))
        except Exception as e:
            flash(f'Error updating type: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('types/edit.html', type_obj=type_obj)

@web.route('/types/<int:type_id>/delete', methods=['POST'])
@login_required
def delete_type(type_id):
    """Delete a type"""
    try:
        type_obj = Type.query.get(type_id)
        if not type_obj:
            flash('Type not found', 'danger')
            return redirect(url_for('web.list_types'))
        name = type_obj.name
        db.session.delete(type_obj)
        db.session.commit()
        flash(f'Type "{name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting type: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_types'))

# ============================================================================
# PROPERTIES
# ============================================================================

@web.route('/properties')
@login_required
def list_properties():
    """List all properties"""
    try:
        properties = Property.query.all()
        return render_template('properties/list.html', properties=properties)
    except Exception as e:
        flash(f'Error loading properties: {str(e)}', 'danger')
        return render_template('properties/list.html', properties=[])

@web.route('/properties/add', methods=['GET', 'POST'])
@login_required
def add_property():
    """Add a new property"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            value_type = request.form.get('valueType')
            
            # Find the highest existing ID and add 1
            max_id = db.session.query(func.max(Property.id)).scalar()
            new_id = (max_id or 0) + 1
            
            # Create new property with explicit ID
            new_property = Property(
                id=new_id,
                name=name,
                valueType=value_type
            )
            
            db.session.add(new_property)
            db.session.commit()
            
            flash(f'Property "{name}" added successfully!', 'success')
            return redirect(url_for('web.list_properties'))
        except Exception as e:
            flash(f'Error adding property: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('properties/add.html')

@web.route('/properties/<int:prop_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(prop_id):
    """Edit an existing property"""
    prop = Property.query.get(prop_id)
    if not prop:
        flash('Property not found', 'danger')
        return redirect(url_for('web.list_properties'))

    if request.method == 'POST':
        try:
            prop.name = request.form.get('name')
            prop.valueType = request.form.get('valueType')
            db.session.commit()
            flash(f'Property "{prop.name}" updated successfully!', 'success')
            return redirect(url_for('web.list_properties'))
        except Exception as e:
            flash(f'Error updating property: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('properties/edit.html', prop=prop)

@web.route('/properties/<int:prop_id>/delete', methods=['POST'])
@login_required
def delete_property(prop_id):
    """Delete a property"""
    try:
        prop = Property.query.get(prop_id)
        if not prop:
            flash('Property not found', 'danger')
            return redirect(url_for('web.list_properties'))
        name = prop.name
        db.session.delete(prop)
        db.session.commit()
        flash(f'Property "{name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting property: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_properties'))

# ============================================================================
# SESSIONS
# ============================================================================

@web.route('/sessions')
@login_required
def list_sessions():
    """List all sessions"""
    try:
        sessions = Session.query.order_by(Session.start_datetime.desc()).all()
        return render_template('sessions/list.html', sessions=sessions)
    except Exception as e:
        flash(f'Error loading sessions: {str(e)}', 'danger')
        return render_template('sessions/list.html', sessions=[])

@web.route('/sessions/<int:session_id>')
@login_required
def view_session(session_id):
    """View a single session with its observations"""
    try:
        session = Session.query.get_or_404(session_id)
        observations = Observation.query.filter_by(session_id=session_id).order_by(Observation.datetime).all()
        return render_template('sessions/view.html', session=session, observations=observations)
    except Exception as e:
        flash(f'Error loading session: {str(e)}', 'danger')
        return redirect(url_for('web.list_sessions'))

@web.route('/sessions/add', methods=['GET', 'POST'])
@login_required
def add_session():
    """Add a new session"""
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
    except:
        instruments = []

    # Auto-generate next session number in format n/YYYY for current year
    current_year = datetime.now().year
    year_suffix = f'/{current_year}'
    max_num = 0
    try:
        for s in Session.query.all():
            if s.number and s.number.endswith(year_suffix):
                try:
                    n = int(s.number.split('/')[0])
                    if n > max_num:
                        max_num = n
                except (ValueError, IndexError):
                    pass
    except Exception:
        pass
    next_number = f'{max_num + 1}/{current_year}'

    return render_template('sessions/add.html', instruments=instruments, next_number=next_number)

@web.route('/sessions/<int:session_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_session(session_id):
    """Edit an existing session"""
    sess = Session.query.get(session_id)
    if not sess:
        flash('Session not found', 'danger')
        return redirect(url_for('web.list_sessions'))

    if request.method == 'POST':
        try:
            sess.number = request.form.get('number')
            start_str = request.form.get('start_datetime')
            end_str = request.form.get('end_datetime')
            sess.start_datetime = datetime.fromisoformat(start_str.replace('Z', '+00:00')) if start_str else None
            sess.end_datetime = datetime.fromisoformat(end_str.replace('Z', '+00:00')) if end_str else None
            cloud_pct = request.form.get('cloud_percentage')
            sess.cloud_percentage = int(cloud_pct) if cloud_pct else None
            sess.cloud_type = request.form.get('cloud_type') or None
            lp = request.form.get('light_pollution')
            sess.light_pollution = int(lp) if lp else None
            lm = request.form.get('limiting_magnitude')
            sess.limiting_magnitude = float(lm) if lm else None
            sess.moon_phase = request.form.get('moon_phase') or None
            ma = request.form.get('moon_altitude')
            sess.moon_altitude = float(ma) if ma else None
            inst = request.form.get('instrument')
            sess.instrument = int(inst) if inst else None

            db.session.commit()
            flash(f'Session "{sess.number}" updated successfully!', 'success')
            return redirect(url_for('web.view_session', session_id=sess.id))
        except Exception as e:
            flash(f'Error updating session: {str(e)}', 'danger')
            db.session.rollback()

    try:
        instruments = Instrument.query.all()
    except:
        instruments = []

    return render_template('sessions/edit.html', sess=sess, instruments=instruments)

@web.route('/sessions/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_session(session_id):
    """Delete a session"""
    try:
        sess = Session.query.get(session_id)
        if not sess:
            flash('Session not found', 'danger')
            return redirect(url_for('web.list_sessions'))
        number = sess.number
        db.session.delete(sess)
        db.session.commit()
        flash(f'Session "{number}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting session: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('web.list_sessions'))

# ============================================================================
# SEARCH
# ============================================================================

@web.route('/search', methods=['GET', 'POST'])
@login_required
def search_observations():
    """Search observations"""
    search_executed = False
    observations = []
    
    if request.method == 'POST':
        search_executed = True
        try:
            # Get search parameters
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            object_id = request.form.get('object')
            place_id = request.form.get('place')
            instrument_id = request.form.get('instrument')
            
            # Build query
            query = Observation.query
            
            if start_date:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(Observation.datetime >= start_dt)
            
            if end_date:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(Observation.datetime <= end_dt)
            
            if object_id and object_id != 'all':
                query = query.filter(Observation.object == int(object_id))
            
            if place_id and place_id != 'all':
                query = query.filter(Observation.place == int(place_id))
            
            if instrument_id and instrument_id != 'all':
                query = query.filter(Observation.instrument == int(instrument_id))
            
            observations = query.order_by(Observation.datetime.desc()).all()
        except Exception as e:
            flash(f'Error searching: {str(e)}', 'danger')
    
    # Get data for filters
    try:
        objects = Object.query.all()
        places = Place.query.all()
        instruments = Instrument.query.all()
    except:
        objects = []
        places = []
        instruments = []
    
    return render_template('search.html', 
                         search_executed=search_executed,
                         observations=observations,
                         objects=objects,
                         places=places,
                         instruments=instruments)

# ============================================================================
# VARIABLE STAR OBSERVING PLANS
# ============================================================================

def _variable_star_objects():
    """Return all objects whose type is 'Variable Star', ordered by name."""
    vs_type = Type.query.filter_by(name='Variable Star').first()
    if not vs_type:
        return []
    return Object.query.filter_by(type=vs_type.id).order_by(Object.name).all()


def _comet_objects():
    """Return all objects whose type is 'Comet', ordered by name."""
    comet_type = Type.query.filter_by(name='Comet').first()
    if not comet_type:
        return []
    return Object.query.filter_by(type=comet_type.id).order_by(Object.name).all()


def _is_comet(obj):
    """True if the given object's type is 'Comet'."""
    comet_type = Type.query.filter_by(name='Comet').first()
    return comet_type is not None and obj is not None and obj.type == comet_type.id


def _ephem_body_for_object(obj, ephem):
    """Build an ephem body for a catalogue object.

    Comets are built from their stored MPC orbital elements - a fixed position
    is meaningless for something that moves several degrees a week - and other
    objects from stored J2000 coordinates, falling back to a SIMBAD lookup.
    Returns (body, error_message); exactly one is set.
    """
    props = {}
    try:
        props = json.loads(obj.props) if obj.props else {}
    except Exception:
        props = {}

    if _is_comet(obj):
        q = props.get('perihelion_distance_au')
        e = props.get('eccentricity')
        tp = props.get('perihelion_date')
        inc = props.get('inclination_deg')
        node = props.get('longitude_ascending_node_deg')
        argp = props.get('argument_perihelion_deg')
        if None in (q, e, tp, inc, node, argp):
            return None, 'Comet is missing orbital elements needed for a position.'
        parts = str(tp).split('-')
        if len(parts) < 3:
            return None, 'Comet has an invalid perihelion date.'
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        tp_str = f"{month:02d}/{day:02d}/{year}"
        mag_h = props.get('absolute_magnitude', 8.0)
        mag_g = props.get('slope_parameter', 4.0)
        try:
            if float(e) < 1.0:
                # XEphem's elliptical format wants a and the mean anomaly at an
                # epoch; anchoring the epoch at perihelion makes that anomaly 0.
                a = float(q) / (1.0 - float(e))
                n = 0.9856076686 / (a ** 1.5)
                # 'g<value>' (no separator) selects the comet g/k magnitude
                # model; writing 'g,<value>' shifts the fields and lands mag on 0.
                line = f"{obj.name},e,{inc},{node},{argp},{a},{n},{e},0,{tp_str},2000,g{mag_h},{mag_g}"
            else:
                line = f"{obj.name},h,{tp_str},{inc},{node},{argp},{e},{q},2000,g{mag_h},{mag_g}"
            return ephem.readdb(line), None
        except Exception as exc:
            return None, f'Could not read comet elements: {exc}'

    # Stored coordinates use either naming, depending on the importer
    ra = props.get('ra_2000') or props.get('ra')
    dec = props.get('dec_2000') or props.get('dec')
    if ra in (None, '') or dec in (None, ''):
        try:
            found = lookup_simbad_object(obj.name)
            if found:
                ra, dec = found.get('ra_hms'), found.get('dec_dms')
        except Exception:
            pass
    if ra in (None, '') or dec in (None, ''):
        return None, 'Object has no stored J2000 coordinates.'
    try:
        body = ephem.FixedBody()
        body._ra = ephem.hours(str(ra)) if ':' in str(ra) else math.radians(float(ra))
        body._dec = ephem.degrees(str(dec).replace('+', '')) if ':' in str(dec) else math.radians(float(dec))
        body._epoch = ephem.J2000
        body.name = obj.name
        return body, None
    except Exception as exc:
        return None, f'Could not read coordinates: {exc}'


def _parse_lat_lon(value):
    """Parse a Place lat/lon string into a signed decimal-degree float, or None."""
    if value is None:
        return None
    v = str(value).strip().upper()
    if not v:
        return None
    sign = -1.0 if ('S' in v or 'W' in v or v.startswith('-')) else 1.0
    for ch in 'NSEW+-':
        v = v.replace(ch, '')
    v = v.strip()
    try:
        return sign * float(v)
    except ValueError:
        return None


_COMPASS_16 = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
               'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']


def _object_position(obj, place, when=None):
    """Compute an object's current altitude/azimuth from an observing place.

    Handles variable stars (fixed RA/Dec from props) and comets (orbital
    elements from props). Returns a dict with alt, az, compass, ra, dec and
    SVG sky-dome coordinates, or a dict with an 'error' key when it cannot be
    computed (missing place, missing data, or the ephem library not installed).
    """
    if place is None:
        return {'error': 'No place set on this plan - edit the plan to add one.'}
    lat = _parse_lat_lon(place.lat)
    lon = _parse_lat_lon(place.lon)
    if lat is None or lon is None:
        return {'error': 'This place has no usable coordinates.'}

    try:
        import ephem
    except Exception:
        return {'error': 'Position library (ephem) is not installed.'}

    import math
    import json as _json

    try:
        props = _json.loads(obj.props) if obj.props else {}
    except Exception:
        props = {}

    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.pressure = 0
    elev = 0.0
    if place.alt:
        digits = ''.join(c for c in str(place.alt) if c.isdigit() or c in '.-')
        try:
            elev = float(digits) if digits else 0.0
        except ValueError:
            elev = 0.0
    observer.elevation = elev
    observer.date = ephem.Date(when) if when else ephem.now()

    body, err = _ephem_body_for_object(obj, ephem)
    if body is None:
        return {'error': err}
    try:
        body.compute(observer)
    except Exception as exc:
        return {'error': f'Could not compute position: {exc}'}

    alt = math.degrees(float(body.alt))
    az = math.degrees(float(body.az)) % 360.0
    compass = _COMPASS_16[int((az + 11.25) % 360 / 22.5)]

    # SVG sky-dome: zenith at centre (110,110), horizon at radius 95
    cx, cy, radius = 110.0, 110.0, 95.0
    r = (90.0 - alt) / 90.0 * radius
    r = min(r, radius)
    x = cx + r * math.sin(math.radians(az))
    y = cy - r * math.cos(math.radians(az))

    return {
        'alt': round(alt, 1),
        'az': round(az, 1),
        'compass': compass,
        'ra': str(body.ra),
        'dec': str(body.dec),
        'x': round(x, 1),
        'y': round(y, 1),
        'below_horizon': alt < 0,
    }


def _comet_packed_designation(obj):
    """Best-effort MPC packed designation for a comet, used as the In-The-Sky.org
    object code (e.g. 10P -> "0010P", C/2025 A6 -> "CK25A060").

    Comets imported from the MPC store the packed provisional designation in
    ``desination`` (e.g. "C/K25A060"), so provisional comets only need the slash
    removed; numbered periodic comets are zero-padded to four digits. Returns
    None when no code can be derived.
    """
    import re as _re
    d = (getattr(obj, 'desination', None) or getattr(obj, 'name', None) or '').strip()
    if not d:
        return None
    # Numbered periodic comet: "10P", "29P/...", "73P" -> "0010P"
    m = _re.match(r'^\s*(\d+)([PDCIA])\b', d)
    if m:
        return f"{int(m.group(1)):04d}{m.group(2)}"
    # Provisional (designation already packed): "C/K25A060" -> "CK25A060"
    m = _re.match(r'^\s*([CPDXAI])/([A-Za-z0-9]+)\s*$', d)
    if m:
        return (m.group(1) + m.group(2)).upper()
    return None


def _comet_finderchart_url(obj, when=None):
    """Build an In-The-Sky.org finder-chart URL for a comet at a given date.

    Returns None when a packed designation cannot be derived.
    """
    packed = _comet_packed_designation(obj)
    if not packed:
        return None
    dt = when or datetime.utcnow()
    return ("https://in-the-sky.org/findercharts.php?"
            f"obj={packed}&year={dt.year}&month={dt.month}&day={dt.day}")


@web.route('/plan')
@login_required
def plan_start():
    """List saved observing plans."""
    plans = Plan.query.order_by(Plan.created_at.desc()).all()
    # Precompute a star count for each plan for display
    plan_rows = []
    for p in plans:
        plan_rows.append({'plan': p, 'count': len(p.star_id_list())})
    return render_template('plan/list.html', plan_rows=plan_rows)


@web.route('/plan/new')
@login_required
def plan_new():
    """Build a new observing plan: pick variable stars and/or comets and settings."""
    stars = _variable_star_objects()
    comets = _comet_objects()
    places = Place.query.all()
    instruments = Instrument.query.all()
    sessions = Session.query.order_by(Session.start_datetime.desc()).all()
    # Object ids to pre-select, e.g. carried over from the Magnitude Check page
    preselected = set()
    for v in request.args.getlist('star'):
        try:
            preselected.add(int(v))
        except (TypeError, ValueError):
            pass
    return render_template('plan/start.html', stars=stars, comets=comets, places=places,
                           instruments=instruments, sessions=sessions,
                           preselected=preselected)


@web.route('/plan/create', methods=['POST'])
@login_required
def plan_create():
    """Save a new observing plan, then either run it or return to the list."""
    try:
        name = (request.form.get('name') or '').strip() or 'Untitled plan'
        star_ids = request.form.getlist('star')
        if not star_ids:
            flash('Please select at least one variable star.', 'warning')
            return redirect(url_for('web.plan_new'))

        def _int_or_none(v):
            return int(v) if v else None

        plan = Plan(
            name=name,
            star_ids=','.join(star_ids),
            place_id=_int_or_none(request.form.get('place')),
            instrument_id=_int_or_none(request.form.get('instrument')),
            session_id=_int_or_none(request.form.get('session')),
        )
        db.session.add(plan)
        db.session.commit()
        flash(f'Plan "{name}" saved.', 'success')

        if request.form.get('action') == 'run':
            return redirect(url_for('web.plan_run', plan_id=plan.id))
        return redirect(url_for('web.plan_start'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving plan: {str(e)}', 'danger')
        return redirect(url_for('web.plan_new'))


@web.route('/plan/<int:plan_id>/run')
@login_required
def plan_run(plan_id):
    """Start the observing wizard for a saved plan."""
    plan = db.session.get(Plan, plan_id)
    if not plan:
        flash('Plan not found.', 'danger')
        return redirect(url_for('web.plan_start'))
    if not plan.star_id_list():
        flash('This plan has no stars.', 'warning')
        return redirect(url_for('web.plan_start'))
    return redirect(url_for('web.plan_observe',
                            ids=plan.star_ids, i=0,
                            place=plan.place_id or '',
                            instrument=plan.instrument_id or '',
                            session=plan.session_id or '',
                            plan=plan.id))


@web.route('/plan/<int:plan_id>/delete', methods=['POST'])
@login_required
def plan_delete(plan_id):
    """Delete a saved plan."""
    plan = db.session.get(Plan, plan_id)
    if plan:
        try:
            db.session.delete(plan)
            db.session.commit()
            flash('Plan deleted.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting plan: {str(e)}', 'danger')
    return redirect(url_for('web.plan_start'))


@web.route('/plan/observe', methods=['GET', 'POST'])
@login_required
def plan_observe():
    """Step through a variable star observing plan one plan item at a time."""
    if request.method == 'POST':
        action = request.form.get('action', 'next')
        ids_raw = request.form.get('ids', '')
        try:
            index = int(request.form.get('index', '0') or 0)
        except ValueError:
            index = 0
        place_id = request.form.get('place')
        instrument_id = request.form.get('instrument')
        session_id = request.form.get('session')

        # Save the observation for this plan item (unless the user chose to skip)
        if action != 'skip':
            try:
                object_id = request.form.get('object')
                datetime_str = request.form.get('datetime')
                observation_text = request.form.get('observation') or ''
                obs_datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))

                new_observation = Observation(
                    object=int(object_id),
                    place=int(place_id) if place_id else None,
                    instrument=int(instrument_id) if instrument_id else None,
                    session_id=int(session_id) if session_id else None,
                    datetime=obs_datetime,
                    observation=observation_text
                )

                # Append AAVSO variable star data, mirroring the Add Observation form
                vs_magnitude = request.form.get('vs_magnitude')
                if vs_magnitude:
                    aavso_data = [f"Magnitude: {vs_magnitude}"]
                    aavso_fields = [
                        ('vs_uncertainty', 'Uncertainty'),
                        ('vs_comp_star1', 'Comp1'),
                        ('vs_comp_star2', 'Comp2'),
                        ('vs_check_star', 'Check'),
                        ('vs_chart', 'Chart'),
                        ('vs_band', 'Band'),
                        ('vs_observer_code', 'Observer'),
                        ('vs_method', 'Method'),
                    ]
                    for field_name, label in aavso_fields:
                        value = request.form.get(field_name)
                        if value:
                            aavso_data.append(f"{label}: {value}")
                    new_observation.observation += " [AAVSO: " + ", ".join(aavso_data) + "]"

                # Append COBS comet data, mirroring the Add Observation form
                comet_magnitude = request.form.get('comet_magnitude')
                if comet_magnitude:
                    cobs_data = [f"m1: {comet_magnitude}"]
                    cobs_fields = [
                        ('coma_diameter', 'Coma'),
                        ('degree_condensation', 'DC'),
                        ('tail_length', 'Tail'),
                        ('tail_pa', 'PA'),
                        ('reference_star', 'Ref'),
                        ('sky_conditions', 'Sky'),
                        ('comet_method', 'Method'),
                    ]
                    for field_name, label in cobs_fields:
                        value = request.form.get(field_name)
                        if value:
                            cobs_data.append(f"{label}: {value}")
                    new_observation.observation += " [COBS: " + ", ".join(cobs_data) + "]"

                db.session.add(new_observation)
                db.session.commit()
                flash(f'Observation saved for plan item {index + 1}.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error saving observation: {str(e)}', 'danger')
                return redirect(url_for('web.plan_observe', ids=ids_raw, i=index,
                                        place=place_id, instrument=instrument_id,
                                        session=session_id))

        # Advance to the next plan item
        ids_list = [x for x in ids_raw.split(',') if x]
        next_index = index + 1
        if next_index >= len(ids_list):
            flash('Observing plan complete!', 'success')
            return redirect(url_for('web.list_observations'))
        return redirect(url_for('web.plan_observe', ids=ids_raw, i=next_index,
                                place=place_id, instrument=instrument_id,
                                session=session_id))

    # GET: render the current plan item
    ids_raw = request.args.get('ids', '')
    ids_list = [x for x in ids_raw.split(',') if x]
    if not ids_list:
        flash('No variable stars selected for the plan.', 'warning')
        return redirect(url_for('web.plan_start'))

    try:
        index = int(request.args.get('i', '0') or 0)
    except ValueError:
        index = 0
    if index < 0 or index >= len(ids_list):
        index = 0

    current_obj = db.session.get(Object, int(ids_list[index]))
    if not current_obj:
        flash('Plan item not found.', 'danger')
        return redirect(url_for('web.plan_start'))

    place_id = request.args.get('place')
    instrument_id = request.args.get('instrument')
    session_id = request.args.get('session')

    # Build the list of plan items for the progress display
    plan_items = []
    for position, obj_id in enumerate(ids_list):
        obj = db.session.get(Object, int(obj_id))
        plan_items.append({'index': position, 'name': obj.name if obj else f'Object {obj_id}'})

    observer_code = getattr(current_user, 'aavso_code', '') or ''

    # Object type + current sky position (altitude/azimuth) for this plan item
    is_comet = _is_comet(current_obj)
    place_obj = db.session.get(Place, int(place_id)) if place_id else None
    position = _object_position(current_obj, place_obj)
    # Comets link out to an In-The-Sky.org finder chart for the current date
    comet_chart_url = _comet_finderchart_url(current_obj) if is_comet else None

    return render_template('plan/observe.html',
                           current_obj=current_obj,
                           index=index,
                           total=len(ids_list),
                           is_last=(index == len(ids_list) - 1),
                           ids_raw=ids_raw,
                           plan_items=plan_items,
                           sel_place=place_id,
                           sel_instrument=instrument_id,
                           sel_session=session_id,
                           observer_code=observer_code,
                           is_comet=is_comet,
                           position=position,
                           comet_chart_url=comet_chart_url,
                           place_name=place_obj.name if place_obj else None)


# ============================================================================
# AAVSO VSP CHARTS - Local download and storage
# ============================================================================

import os, re

CHARTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'charts')

VSP_SCALES = [
    {'key': 'A',  'fov': 180, 'label': 'A (3 deg)'},
    {'key': 'AB', 'fov': 120, 'label': 'AB (2 deg)'},
    {'key': 'B',  'fov': 60,  'label': 'B (1 deg)'},
    {'key': 'C',  'fov': 20,  'label': 'C (20 arcmin)'},
    {'key': 'D',  'fov': 10,  'label': 'D (10 arcmin)'},
    {'key': 'E',  'fov': 5,   'label': 'E (5 arcmin)'},
    {'key': 'F',  'fov': 2,   'label': 'F (2 arcmin)'},
]

# AAVSO's chart renderer (apps.aavso.org) intermittently returns 500 or stalls
# when a batch hits it in quick succession; those failures clear on a retry, so
# every VSP request goes through _vsp_get rather than a bare requests.get.
VSP_ATTEMPTS = 3
VSP_API_TIMEOUT = 30
VSP_IMAGE_TIMEOUT = 60

_vsp_session = None


def _vsp_http():
    """Shared session: connection reuse cuts handshake cost across a batch."""
    global _vsp_session
    if _vsp_session is None:
        s = http_requests.Session()
        s.headers.update({'User-Agent': 'astronomyapi (observation logger)'})
        _vsp_session = s
    return _vsp_session


def _vsp_get(url, params=None, timeout=VSP_API_TIMEOUT, attempts=VSP_ATTEMPTS):
    """GET a VSP URL, retrying transient failures.

    Retries 5xx responses and network timeouts with a growing pause; gives up
    immediately on 4xx, which won't fix itself. Returns (response, error) with
    exactly one of them set.
    """
    last_error = ''
    for attempt in range(1, attempts + 1):
        try:
            resp = _vsp_http().get(url, params=params, timeout=timeout)
            if resp.status_code == 200:
                return resp, ''
            last_error = f'HTTP {resp.status_code}'
            if resp.status_code < 500:
                break
        except Exception as e:
            last_error = str(e)
        if attempt < attempts:
            time.sleep(1.5 * attempt)
    return None, f'{last_error} (after {attempts} attempts)' if last_error else 'unknown error'


def _safe_dirname(star_name):
    """Convert star name to safe directory name"""
    return re.sub(r'[^a-zA-Z0-9_\\-]', '_', star_name.strip())

def _extract_comparisons(chart_data):
    """Reduce a VSP chart payload to the comparison stars we show in the form.

    Each entry keeps the AAVSO label (what goes in COMP1/COMP2 - it is the
    magnitude x10), the AUID, and the V magnitude when available, falling back
    to whatever band the chart carries.
    """
    comps = []
    for star in (chart_data or {}).get('photometry', []) or []:
        label = str(star.get('label') or '').strip()
        if not label:
            continue
        bands = star.get('bands') or []
        mag = None
        band_name = ''
        for b in bands:
            if b.get('band') == 'V':
                mag, band_name = b.get('mag'), 'V'
                break
        if mag is None and bands:
            mag, band_name = bands[0].get('mag'), bands[0].get('band') or ''
        comps.append({
            'label': label,
            'auid': star.get('auid') or '',
            'mag': mag,
            'band': band_name,
            'ra': star.get('ra') or '',
            'dec': star.get('dec') or '',
        })
    # Brightest first, so the list reads the way an observer brackets a star.
    comps.sort(key=lambda c: (c['mag'] is None, c['mag'] if c['mag'] is not None else 0))
    return comps


def _save_comparisons(star_dir, scale_key, chart_data):
    """Cache a chart's comparison stars next to its PNG (best effort)."""
    try:
        comps = _extract_comparisons(chart_data)
        if not comps:
            return
        path = os.path.join(star_dir, f"{scale_key}.comps.json")
        with open(path, 'w') as f:
            json.dump({'chartid': chart_data.get('chartid', ''),
                       'star': chart_data.get('star', ''),
                       'comparisons': comps}, f)
    except Exception as e:
        print(f"  Could not cache comparisons for {scale_key}: {e}")


def _find_cached_comparisons(chartid):
    """Look for a cached comparison list for this chart id, anywhere in CHARTS_DIR."""
    if not chartid or not os.path.isdir(CHARTS_DIR):
        return None
    for star_dir in os.listdir(CHARTS_DIR):
        full = os.path.join(CHARTS_DIR, star_dir)
        if not os.path.isdir(full):
            continue
        for name in os.listdir(full):
            if not name.endswith('.comps.json'):
                continue
            try:
                with open(os.path.join(full, name)) as f:
                    data = json.load(f)
                if data.get('chartid') == chartid:
                    return data
            except Exception:
                continue
    return None


def _get_local_charts(star_name):
    """Get list of locally stored charts for a star"""
    safe = _safe_dirname(star_name)
    star_dir = os.path.join(CHARTS_DIR, safe)
    charts = []
    if os.path.isdir(star_dir):
        for s in VSP_SCALES:
            png = os.path.join(star_dir, f"{s['key']}.png")
            meta = os.path.join(star_dir, f"{s['key']}.meta")
            if os.path.isfile(png):
                chartid = ''
                if os.path.isfile(meta):
                    with open(meta) as mf:
                        chartid = mf.read().strip()
                charts.append({
                    'scale': s['key'],
                    'label': s['label'],
                    'fov': s['fov'],
                    'chartid': chartid,
                    'image_url': f"/static/charts/{safe}/{s['key']}.png",
                    'local': True,
                    'size': os.path.getsize(png),
                })
    return charts

@web.route('/vsp/local/<path:star_name>')
@login_required
def vsp_local_charts(star_name):
    """Get locally stored charts for a star"""
    charts = _get_local_charts(star_name)
    return jsonify({'star': star_name, 'charts': charts})

@web.route('/vsp/charts-available')
@login_required
def vsp_charts_available():
    """Chart ids already downloaded on this system.

    With ?star=<name> only that star's charts are returned (what the
    observation form wants); without it, every chart held locally.
    """
    star = (request.args.get('star') or '').strip()
    charts = []
    if star:
        stars = [star]
    else:
        stars = sorted(os.listdir(CHARTS_DIR)) if os.path.isdir(CHARTS_DIR) else []

    for name in stars:
        if star:
            local = _get_local_charts(name)
            display = name
        else:
            star_dir = os.path.join(CHARTS_DIR, name)
            if not os.path.isdir(star_dir):
                continue
            local = _get_local_charts(name)
            display = name.replace('_', ' ')
        for c in local:
            if not c.get('chartid'):
                continue
            charts.append({
                'chartid': c['chartid'],
                'scale': c['scale'],
                'label': c['label'],
                'star': display,
                'has_comparisons': os.path.isfile(
                    os.path.join(CHARTS_DIR, _safe_dirname(name), f"{c['scale']}.comps.json")),
            })
    return jsonify({'star': star, 'charts': charts})

@web.route('/vsp/download', methods=['POST'])
@login_required
def vsp_download_chart():
    """Download a single chart from AAVSO VSP and store locally"""
    star_name = request.form.get('star_name', '').strip()
    scale_key = request.form.get('scale', '').strip()

    if not star_name or not scale_key:
        return jsonify({'error': 'Missing star_name or scale'}), 400

    # Find scale info
    scale_info = None
    for s in VSP_SCALES:
        if s['key'] == scale_key:
            scale_info = s
            break
    if not scale_info:
        return jsonify({'error': f'Invalid scale: {scale_key}'}), 400

    maglimit = request.form.get('maglimit', '').strip()
    try:
        maglimit = float(maglimit) if maglimit else 14.5
    except ValueError:
        maglimit = 14.5

    try:
        # Get chart metadata from VSP API
        resp, err = _vsp_get(
            'https://app.aavso.org/vsp/api/chart/',
            params={'format': 'json', 'star': star_name, 'fov': scale_info['fov'], 'maglimit': maglimit})
        if resp is None:
            return jsonify({'error': f'VSP API error: {err}'}), 502

        data = resp.json()
        chartid = data.get('chartid', '')
        image_url = data.get('image_uri', '').replace('?format=json', '')

        if not image_url:
            return jsonify({'error': 'No image URL from VSP'}), 502

        # Download the image
        img_resp, err = _vsp_get(image_url, timeout=VSP_IMAGE_TIMEOUT)
        if img_resp is None:
            return jsonify({'error': f'Image download failed: {err}'}), 502

        # Save locally
        safe = _safe_dirname(star_name)
        star_dir = os.path.join(CHARTS_DIR, safe)
        os.makedirs(star_dir, exist_ok=True)

        png_path = os.path.join(star_dir, f"{scale_key}.png")
        with open(png_path, 'wb') as f:
            f.write(img_resp.content)

        # Save metadata
        meta_path = os.path.join(star_dir, f"{scale_key}.meta")
        with open(meta_path, 'w') as f:
            f.write(chartid)

        # Cache the comparison stars so the observation form can offer them
        # even when AAVSO is unreachable later.
        _save_comparisons(star_dir, scale_key, data)

        return jsonify({
            'success': True,
            'scale': scale_key,
            'chartid': chartid,
            'image_url': f"/static/charts/{safe}/{scale_key}.png",
            'size': len(img_resp.content),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web.route('/vsp/download-all', methods=['POST'])
@login_required
def vsp_download_all_charts():
    """Download all chart scales for a star"""
    star_name = request.form.get('star_name', '').strip()
    if not star_name:
        return jsonify({'error': 'Missing star_name'}), 400

    results = []
    for s in VSP_SCALES:
        try:
            resp, err = _vsp_get(
                'https://app.aavso.org/vsp/api/chart/',
                params={'format': 'json', 'star': star_name, 'fov': s['fov'], 'maglimit': 14.5})
            if resp is None:
                results.append({'scale': s['key'], 'error': f'API {err}'})
                continue

            data = resp.json()
            chartid = data.get('chartid', '')
            image_url = data.get('image_uri', '').replace('?format=json', '')
            if not image_url:
                results.append({'scale': s['key'], 'error': 'No image URL'})
                continue

            img_resp, err = _vsp_get(image_url, timeout=VSP_IMAGE_TIMEOUT)
            if img_resp is None:
                results.append({'scale': s['key'], 'error': f'Image download failed: {err}'})
                continue

            safe = _safe_dirname(star_name)
            star_dir = os.path.join(CHARTS_DIR, safe)
            os.makedirs(star_dir, exist_ok=True)

            with open(os.path.join(star_dir, f"{s['key']}.png"), 'wb') as f:
                f.write(img_resp.content)
            with open(os.path.join(star_dir, f"{s['key']}.meta"), 'w') as f:
                f.write(chartid)
            _save_comparisons(star_dir, s['key'], data)

            results.append({
                'scale': s['key'],
                'success': True,
                'chartid': chartid,
                'image_url': f"/static/charts/{safe}/{s['key']}.png",
            })
        except Exception as e:
            results.append({'scale': s['key'], 'error': str(e)})

    return jsonify({'star': star_name, 'results': results})

@web.route('/vsp/comparisons/<path:chartid>')
@login_required
def vsp_comparisons(chartid):
    """AJAX endpoint: comparison stars for a VSP chart id.

    Serves the copy cached when the chart was downloaded; falls back to the
    live VSP API (and caches nothing, since we don't know which star dir it
    belongs to) when there is no local copy.
    """
    chartid = (chartid or '').strip()
    if not chartid:
        return jsonify({'error': 'Missing chart id'}), 400

    cached = _find_cached_comparisons(chartid)
    if cached:
        return jsonify({'chartid': chartid, 'source': 'local',
                        'star': cached.get('star', ''),
                        'comparisons': cached.get('comparisons', [])})

    try:
        resp = http_requests.get(
            f'https://app.aavso.org/vsp/api/chart/{quote(chartid, safe="")}/',
            params={'format': 'json'}, timeout=15)
        if resp.status_code != 200:
            return jsonify({'error': f'VSP API error: HTTP {resp.status_code}'}), 502
        data = resp.json()
        comps = _extract_comparisons(data)
        if not comps:
            return jsonify({'error': 'No comparison stars on this chart',
                            'chartid': chartid, 'comparisons': []}), 404
        return jsonify({'chartid': data.get('chartid', chartid), 'source': 'aavso',
                        'star': data.get('star', ''), 'comparisons': comps})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web.route('/vsp/view/<path:star_name>')
@login_required
def vsp_view(star_name):
    """View all AAVSO VSP charts for a variable star"""
    local_charts = _get_local_charts(star_name)
    downloaded_scales = [c['scale'] for c in local_charts]
    scales = []
    for s in VSP_SCALES:
        entry = dict(s)
        entry['downloaded'] = s['key'] in downloaded_scales
        scales.append(entry)
    return render_template('vsx/charts.html', star_name=star_name, scales=scales, local_charts=local_charts)

@web.route('/vsp/batch')
@login_required
def vsp_batch_charts():
    """Batch-download AAVSO VSP finder charts for many variable stars at once.

    Lists every variable-star object with the scales already cached locally.
    The actual downloading is driven client-side, one (star, scale) at a time
    against the existing /vsp/download endpoint, so large batches show live
    progress and never time out a single request.
    """
    stars = []
    for obj in _variable_star_objects():
        local = _get_local_charts(obj.name)
        stars.append({
            'id': obj.id,
            'name': obj.name,
            'designation': obj.desination or '',
            'local_count': len(local),
            'local_scales': ','.join(c['scale'] for c in local),
        })
    return render_template('vsx/batch_charts.html',
                           stars=stars, scales=VSP_SCALES,
                           total_scales=len(VSP_SCALES))

@web.route('/aavso/magnitude-check')
@login_required
def magnitude_check():
    """Batch magnitude/tendency check for selected variable stars.

    Lists every variable-star object; the user selects some and the page
    fetches the latest AAVSO magnitude and tendency for each one, driven
    client-side against the existing /aavso/recent endpoint so large batches
    show a live progress bar and never time out a single request.
    """
    stars = []
    for obj in _variable_star_objects():
        stars.append({
            'id': obj.id,
            'name': obj.name,
            'designation': obj.desination or '',
        })
    return render_template('vsx/magnitude_check.html', stars=stars)


# ----------------------------------------------------------------------------
# SAVED STAR LISTS (magnitude check)
# ----------------------------------------------------------------------------

@web.route('/star-lists')
@login_required
def star_lists():
    """All saved star lists, newest first."""
    try:
        lists = StarList.query.order_by(StarList.updated_at.desc()).all()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'lists': [
        {'id': sl.id, 'name': sl.name, 'star_ids': sl.star_id_list(),
         'count': len(sl.star_id_list()),
         'updated': sl.updated_at.strftime('%Y-%m-%d %H:%M') if sl.updated_at else ''}
        for sl in lists]})


@web.route('/star-lists/save', methods=['POST'])
@login_required
def save_star_list():
    """Create a star list, or replace the contents of one with the same name."""
    name = (request.form.get('name') or '').strip()
    ids = [i for i in (request.form.get('star_ids') or '').split(',') if i.strip().isdigit()]
    if not name:
        return jsonify({'error': 'Give the list a name'}), 400
    if not ids:
        return jsonify({'error': 'Select at least one star'}), 400
    try:
        existing = StarList.query.filter_by(name=name).first()
        if existing:
            existing.star_ids = ','.join(ids)
            saved, created = existing, False
        else:
            saved = StarList(name=name, star_ids=','.join(ids))
            db.session.add(saved)
            created = True
        db.session.commit()
        return jsonify({'id': saved.id, 'name': saved.name,
                        'count': len(ids), 'created': created})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@web.route('/star-lists/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_star_list(list_id):
    """Remove a saved star list."""
    try:
        sl = StarList.query.get(list_id)
        if not sl:
            return jsonify({'error': 'List not found'}), 404
        db.session.delete(sl)
        db.session.commit()
        return jsonify({'deleted': list_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def _pdf_text(value):
    """Core PDF fonts are latin-1: drop anything they cannot render."""
    return str(value or '').encode('latin-1', 'replace').decode('latin-1')


@web.route('/aavso/magnitude-check/pdf', methods=['POST'])
@login_required
def magnitude_check_pdf():
    """A printable two-column observing form from the magnitude check.

    Each star gets its latest AAVSO reading and an empty box to write the
    estimate in at the telescope, which is the point of taking it outside.
    """
    try:
        from fpdf import FPDF
    except Exception as e:
        return jsonify({'error': f'PDF support unavailable: {e}'}), 503

    payload = request.get_json(silent=True) or {}
    rows = payload.get('rows') or []
    if not rows:
        return jsonify({'error': 'No stars to put on the list'}), 400
    title = _pdf_text(payload.get('title') or 'Variable Star Observing List')

    # A4 portrait, two columns of entry blocks
    PAGE_W, PAGE_H = 210.0, 297.0
    MARGIN = 12.0
    COL_GAP = 6.0
    COL_W = (PAGE_W - 2 * MARGIN - COL_GAP) / 2
    ROW_H = 15.0
    BOX_W, BOX_H = 26.0, 9.0
    HEADER_H = 23.0

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(False)
    pdf.set_title(title)

    generated = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    observer = _pdf_text(getattr(current_user, 'aavso_code', '') or '')

    def start_page():
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_xy(MARGIN, MARGIN)
        pdf.cell(0, 7, title, ln=1)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(90, 90, 90)
        line = f'Generated {generated}'
        if observer:
            line += f'   Observer: {observer}'
        line += f'   {len(rows)} stars'
        pdf.cell(0, 5, _pdf_text(line), ln=1)
        pdf.set_text_color(0, 0, 0)

        # Blank fields for the session details, since this is filled in by hand
        pdf.set_font('Helvetica', '', 8)
        pdf.set_xy(MARGIN, MARGIN + 11)
        usable = PAGE_W - 2 * MARGIN
        for label, width in (('Date', 0.26), ('Place', 0.30), ('Instrument', 0.26), ('Lim. mag', 0.18)):
            w = usable * width
            pdf.cell(pdf.get_string_width(label + ' '), 4, label, ln=0)
            x0 = pdf.get_x()
            rule = w - pdf.get_string_width(label + ' ') - 4
            pdf.set_draw_color(150, 150, 150)
            pdf.line(x0, MARGIN + 14.5, x0 + rule, MARGIN + 14.5)
            pdf.set_x(x0 + rule + 4)
        pdf.ln(6)
        pdf.set_draw_color(0, 0, 0)
        pdf.line(MARGIN, MARGIN + 17, PAGE_W - MARGIN, MARGIN + 17)

    rows_per_col = int((PAGE_H - MARGIN - HEADER_H - MARGIN) // ROW_H)
    per_page = rows_per_col * 2

    for index, row in enumerate(rows):
        slot = index % per_page
        if slot == 0:
            start_page()
        column = 0 if slot < rows_per_col else 1
        line_no = slot % rows_per_col
        x = MARGIN + column * (COL_W + COL_GAP)
        y = MARGIN + HEADER_H + line_no * ROW_H

        name = _pdf_text(row.get('name'))
        designation = _pdf_text(row.get('designation'))
        mag = _pdf_text(row.get('mag'))
        date = _pdf_text(row.get('date'))
        tendency = _pdf_text(row.get('tendency'))

        pdf.set_xy(x, y)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(COL_W - BOX_W - 3, 5, name, ln=0)

        # The empty box the observer writes the estimate into
        pdf.set_draw_color(60, 60, 60)
        pdf.rect(x + COL_W - BOX_W, y, BOX_W, BOX_H)
        pdf.set_font('Helvetica', '', 6)
        pdf.set_text_color(140, 140, 140)
        pdf.set_xy(x + COL_W - BOX_W + 1, y + BOX_H - 3)
        pdf.cell(BOX_W - 2, 2.5, 'estimate', ln=0)

        pdf.set_text_color(90, 90, 90)
        pdf.set_font('Helvetica', '', 7)
        pdf.set_xy(x, y + 5)
        if designation:
            pdf.cell(COL_W - BOX_W - 3, 3.5, designation, ln=0)
        bits = []
        if mag and mag != '-':
            bits.append(f'AAVSO {mag}')
        if date and date != '-':
            bits.append(date)
        if tendency and tendency != '-':
            bits.append(tendency)
        pdf.set_xy(x, y + 8.5)
        pdf.cell(COL_W - BOX_W - 3, 3.5, _pdf_text('  '.join(bits) or 'no recent AAVSO data'), ln=0)

        # Faint rule under each entry, so the columns read as a list
        pdf.set_draw_color(200, 200, 200)
        pdf.line(x, y + ROW_H - 2, x + COL_W, y + ROW_H - 2)
        pdf.set_text_color(0, 0, 0)

    out = pdf.output()
    if not isinstance(out, (bytes, bytearray)):
        out = str(out).encode('latin-1')
    filename = 'magnitude_check_' + datetime.utcnow().strftime('%Y%m%d') + '.pdf'
    return Response(bytes(out), mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment; filename={filename}'})


@web.route('/aavso/light-curve')
@login_required
def light_curve_page():
    """Standalone AAVSO light-curve viewer.

    Lists every variable-star object; the user picks one and the page renders
    its AAVSO light curve client-side via the /aavso/lightcurve/<star> endpoint.
    """
    stars = []
    for obj in _variable_star_objects():
        stars.append({
            'id': obj.id,
            'name': obj.name,
            'designation': obj.desination or '',
        })
    return render_template('vsx/light_curve.html', stars=stars)


# ============================================================================
# API DOCUMENTATION PAGE
# ============================================================================

# Human-readable catalog of the API/tool endpoints, grouped for the docs page.
# The machine-readable version lives at the root "/" JSON endpoint (server.py).
API_DOC_GROUPS = [
    {
        'name': 'Types', 'icon': 'bi-tag',
        'desc': 'Observation classification types.',
        'endpoints': [
            {'method': 'GET',    'path': '/api/types',           'desc': 'List all types'},
            {'method': 'POST',   'path': '/api/types',           'desc': 'Create a type'},
            {'method': 'GET',    'path': '/api/types/<id>',      'desc': 'Get a type'},
            {'method': 'PUT',    'path': '/api/types/<id>',      'desc': 'Update a type'},
            {'method': 'DELETE', 'path': '/api/types/<id>',      'desc': 'Delete a type'},
        ],
    },
    {
        'name': 'Properties', 'icon': 'bi-list-check',
        'desc': 'Custom observation properties.',
        'endpoints': [
            {'method': 'GET',    'path': '/api/properties',      'desc': 'List all properties'},
            {'method': 'POST',   'path': '/api/properties',      'desc': 'Create a property'},
            {'method': 'GET',    'path': '/api/properties/<id>', 'desc': 'Get a property'},
            {'method': 'PUT',    'path': '/api/properties/<id>', 'desc': 'Update a property'},
            {'method': 'DELETE', 'path': '/api/properties/<id>', 'desc': 'Delete a property'},
        ],
    },
    {
        'name': 'Places', 'icon': 'bi-geo-alt',
        'desc': 'Observing locations.',
        'endpoints': [
            {'method': 'GET',    'path': '/api/places',                    'desc': 'List all places'},
            {'method': 'POST',   'path': '/api/places',                    'desc': 'Create a place'},
            {'method': 'GET',    'path': '/api/places/<id>',               'desc': 'Get a place'},
            {'method': 'PUT',    'path': '/api/places/<id>',               'desc': 'Update a place'},
            {'method': 'DELETE', 'path': '/api/places/<id>',               'desc': 'Delete a place'},
            {'method': 'GET',    'path': '/api/places/<id>/observations',  'desc': 'Observations made at a place'},
        ],
    },
    {
        'name': 'Instruments', 'icon': 'bi-tools',
        'desc': 'Telescopes and optical instruments.',
        'endpoints': [
            {'method': 'GET',    'path': '/api/instruments',                    'desc': 'List all instruments'},
            {'method': 'POST',   'path': '/api/instruments',                    'desc': 'Create an instrument'},
            {'method': 'GET',    'path': '/api/instruments/<id>',               'desc': 'Get an instrument'},
            {'method': 'PUT',    'path': '/api/instruments/<id>',               'desc': 'Update an instrument'},
            {'method': 'DELETE', 'path': '/api/instruments/<id>',               'desc': 'Delete an instrument'},
            {'method': 'GET',    'path': '/api/instruments/<id>/observations',  'desc': 'Observations made with an instrument'},
        ],
    },
    {
        'name': 'Objects', 'icon': 'bi-star',
        'desc': 'Celestial objects (stars, comets, deep-sky, ...).',
        'endpoints': [
            {'method': 'GET',    'path': '/api/objects',                    'desc': 'List all objects'},
            {'method': 'POST',   'path': '/api/objects',                    'desc': 'Create an object'},
            {'method': 'GET',    'path': '/api/objects/<id>',               'desc': 'Get an object'},
            {'method': 'PUT',    'path': '/api/objects/<id>',               'desc': 'Update an object'},
            {'method': 'DELETE', 'path': '/api/objects/<id>',               'desc': 'Delete an object'},
            {'method': 'GET',    'path': '/api/objects/<id>/observations',  'desc': 'Observations of an object'},
        ],
    },
    {
        'name': 'Observations', 'icon': 'bi-binoculars',
        'desc': 'Individual observation records.',
        'endpoints': [
            {'method': 'GET',    'path': '/api/observations',         'desc': 'List all observations'},
            {'method': 'POST',   'path': '/api/observations',         'desc': 'Create an observation'},
            {'method': 'GET',    'path': '/api/observations/<id>',    'desc': 'Get an observation'},
            {'method': 'PUT',    'path': '/api/observations/<id>',    'desc': 'Update an observation'},
            {'method': 'DELETE', 'path': '/api/observations/<id>',    'desc': 'Delete an observation'},
            {'method': 'GET',    'path': '/api/observations/search',  'desc': 'Search with filters: start_date, end_date, object_id, place_id, instrument_id'},
        ],
    },
    {
        'name': 'Sessions', 'icon': 'bi-calendar-event',
        'desc': 'Observing sessions (conditions, sky, instrument).',
        'endpoints': [
            {'method': 'GET',    'path': '/api/sessions',                    'desc': 'List all sessions'},
            {'method': 'POST',   'path': '/api/sessions',                    'desc': 'Create a session'},
            {'method': 'GET',    'path': '/api/sessions/<id>',               'desc': 'Get a session'},
            {'method': 'PUT',    'path': '/api/sessions/<id>',               'desc': 'Update a session'},
            {'method': 'DELETE', 'path': '/api/sessions/<id>',               'desc': 'Delete a session'},
            {'method': 'GET',    'path': '/api/sessions/<id>/observations',  'desc': 'Observations recorded in a session'},
        ],
    },
    {
        'name': 'Plans', 'icon': 'bi-card-checklist',
        'desc': 'Saved variable-star observing plans.',
        'endpoints': [
            {'method': 'GET',    'path': '/api/plans',       'desc': 'List all plans'},
            {'method': 'POST',   'path': '/api/plans',       'desc': 'Create a plan (name required; stars=[object_ids] or star_ids="1,2,3")'},
            {'method': 'GET',    'path': '/api/plans/<id>',  'desc': 'Get a plan'},
            {'method': 'PUT',    'path': '/api/plans/<id>',  'desc': 'Update a plan'},
            {'method': 'DELETE', 'path': '/api/plans/<id>',  'desc': 'Delete a plan'},
        ],
    },
    {
        'name': 'AAVSO Recent', 'icon': 'bi-activity',
        'desc': 'Latest AAVSO magnitude / tendency for variable stars. Public (no login).',
        'endpoints': [
            {'method': 'GET', 'path': '/api/aavso/recent/<star_name>',            'desc': 'Latest magnitude, last-observation date and tendency (past year). Same JSON as /web/aavso/recent/<star>'},
            {'method': 'GET', 'path': '/api/aavso/recent?stars=R+Leo,Mira,AC+Her',  'desc': 'Batch: array of per-star summaries in one request (max 50 stars)'},
        ],
    },
    {
        'name': 'SIMBAD & Charts', 'icon': 'bi-globe',
        'desc': 'External-data integrations: SIMBAD object search and AAVSO VSP finder charts.',
        'endpoints': [
            {'method': 'GET', 'path': '/api/simbad/search',      'desc': 'Search SIMBAD. Params: q (required), type=name|wildcard|type_variable|variable_constellation, max=1..2000 (up to 5000 for variable_constellation), var_type, constellation'},
            {'method': 'GET', 'path': '/api/charts/vsp',         'desc': 'Resolve an AAVSO VSP finder chart. Params: star (required), scale=A..F or fov=<deg>, maglimit. Returns chartid, image_uri, comparison_stars'},
            {'method': 'GET', 'path': '/api/charts/vsp/scales',  'desc': 'List the available VSP chart scales (A-F)'},
        ],
    },
    {
        'name': 'Variable Stars (AAVSO)', 'icon': 'bi-graph-up',
        'desc': 'AAVSO magnitude, tendency and light-curve data (JSON; served under /web).',
        'endpoints': [
            {'method': 'GET', 'path': '/web/aavso/recent/<star_name>',            'desc': 'Latest AAVSO magnitude, date and brightness tendency (past year)'},
            {'method': 'GET', 'path': '/web/aavso/lightcurve/<star_name>?days=N',  'desc': 'Full AAVSO observation time series as light-curve points, grouped by band (days=1..3650, default 365)'},
            {'method': 'GET', 'path': '/web/observations/lightcurve/<star_name>',  'desc': 'Your own recorded observations of a star as light-curve points'},
        ],
    },
    {
        'name': 'Web Tools', 'icon': 'bi-window',
        'desc': 'Interactive pages in the web interface.',
        'endpoints': [
            {'method': 'GET', 'path': '/web/aavso/magnitude-check',  'desc': 'Batch magnitude/tendency check; can start an observing plan from selected stars'},
            {'method': 'GET', 'path': '/web/aavso/light-curve',      'desc': 'Interactive AAVSO light-curve viewer'},
            {'method': 'GET', 'path': '/web/plan/new',               'desc': 'Build an observing plan; ?star=<object_id> (repeatable) pre-selects stars'},
        ],
    },
]


@web.route('/api-docs')
@login_required
def api_docs_page():
    """Human-readable HTML documentation of the REST API and tool endpoints."""
    return render_template('api/docs.html', groups=API_DOC_GROUPS, api_version='1.2.0')

# ============================================================================
# COMET IMPORT
# ============================================================================

@web.route('/comets/import', methods=['GET', 'POST'])
@login_required
def import_comets():
    """Import comets from Minor Planet Center"""
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            max_comets = request.form.get('max_comets')
            
            # Convert max_comets to int or None
            if max_comets:
                try:
                    max_comets = int(max_comets)
                except:
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
    except:
        comet_count = 0
    
    return render_template('comets/import.html', comet_count=comet_count)

# ============================================================================
# VSX VARIABLE STAR IMPORT
# ============================================================================

@web.route('/vsx/import', methods=['GET', 'POST'])
@login_required
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
            except:
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
    except:
        var_star_count = 0

    return render_template('vsx/import.html', var_star_count=var_star_count)

# ============================================================================
# SIMBAD SEARCH & IMPORT
# ============================================================================

@web.route('/simbad/search', methods=['GET', 'POST'])
@login_required
def search_simbad_page():
    """Search SIMBAD and import objects"""
    results = None
    query_text = ''
    search_type = 'name'
    max_records = 50
    var_type = []
    constellation = ''
    import_message = None

    if request.method == 'POST':
        action = request.form.get('action', 'search')
        # var_type is a multi-select: collect all chosen types
        var_type = [v.strip() for v in request.form.getlist('var_type') if v.strip()]
        constellation = request.form.get('constellation', '').strip()

        if action == 'import_one':
            # Import a single object from search results
            import_name = request.form.get('import_name', '').strip()
            if import_name:
                try:
                    obj_data = lookup_simbad_object(import_name)
                    if obj_data:
                        result = import_simbad_object(obj_data)
                        if result['status'] == 'added':
                            flash(f"Added {result['name']} as {result.get('type', 'object')} (ID: {result['id']})", 'success')
                        elif result['status'] == 'exists':
                            flash(f"{result['name']} already exists in database (ID: {result['id']})", 'warning')
                    else:
                        flash(f"Could not find '{import_name}' in SIMBAD", 'danger')
                except Exception as e:
                    flash(f"Error importing: {str(e)}", 'danger')

            # Restore previous search
            query_text = request.form.get('query', '').strip()
            search_type = request.form.get('search_type', 'name')
            max_records = int(request.form.get('max_records', '50') or '50')
            if search_type == 'variable_constellation':
                if constellation:
                    try:
                        results = search_simbad(query_text, search_type=search_type,
                                                max_records=max_records,
                                                var_type=var_type, constellation=constellation)
                    except:
                        results = []
            elif query_text:
                try:
                    results = search_simbad(query_text, search_type=search_type, max_records=max_records)
                except:
                    results = []

        elif action == 'import_all':
            # Import all results from search
            query_text = request.form.get('query', '').strip()
            search_type = request.form.get('search_type', 'name')
            max_records = int(request.form.get('max_records', '50') or '50')
            do_search = constellation if search_type == 'variable_constellation' else query_text
            if do_search:
                try:
                    results = search_simbad(query_text, search_type=search_type, max_records=max_records,
                                            var_type=var_type, constellation=constellation)
                    if results:
                        added = 0
                        skipped = 0
                        for obj_data in results:
                            try:
                                r = import_simbad_object(obj_data)
                                if r['status'] == 'added':
                                    added += 1
                                else:
                                    skipped += 1
                            except:
                                skipped += 1
                        flash(f"Imported {added} objects, {skipped} skipped/already exist", 'success')
                except Exception as e:
                    flash(f"Error: {str(e)}", 'danger')
                    results = []

        elif action == 'import_selected':
            # Import only the checked rows, then re-run the search for display
            selected = set(request.form.getlist('import_names'))
            query_text = request.form.get('query', '').strip()
            search_type = request.form.get('search_type', 'name')
            max_records = int(request.form.get('max_records', '50') or '50')
            do_search = constellation if search_type == 'variable_constellation' else query_text
            if do_search:
                try:
                    results = search_simbad(query_text, search_type=search_type, max_records=max_records,
                                            var_type=var_type, constellation=constellation)
                except Exception as e:
                    flash(f"Error: {str(e)}", 'danger')
                    results = []
            if not selected:
                flash("No stars were selected to import", 'warning')
            elif results:
                added = 0
                skipped = 0
                for obj_data in results:
                    if obj_data.get('main_id') not in selected:
                        continue
                    try:
                        r = import_simbad_object(obj_data)
                        if r['status'] == 'added':
                            added += 1
                        else:
                            skipped += 1
                    except:
                        skipped += 1
                flash(f"Imported {added} selected objects, {skipped} skipped/already exist",
                      'success' if added else 'warning')

        else:
            # Regular search
            query_text = request.form.get('query', '').strip()
            search_type = request.form.get('search_type', 'name')
            max_records = int(request.form.get('max_records', '50') or '50')
            if search_type == 'variable_constellation':
                if not constellation:
                    flash("Please choose a constellation", 'warning')
                else:
                    try:
                        results = search_simbad(query_text, search_type=search_type,
                                                max_records=max_records,
                                                var_type=var_type, constellation=constellation)
                        if not results:
                            label = ', '.join(var_type) if var_type else 'variable'
                            flash(f"No {label} stars found in {constellation}", 'warning')
                    except Exception as e:
                        flash(f"SIMBAD query error: {str(e)}", 'danger')
                        results = []
            elif query_text:
                try:
                    results = search_simbad(query_text, search_type=search_type, max_records=max_records)
                    if not results:
                        flash(f"No results found for '{query_text}'", 'warning')
                except Exception as e:
                    flash(f"SIMBAD query error: {str(e)}", 'danger')
                    results = []
            else:
                flash("Please enter a search query", 'warning')

    # Flag which results are already in the database so the template can
    # disable their Add button (covers both just-added and pre-existing records)
    if results:
        for r in results:
            try:
                r['exists'] = find_existing_object(r.get('name', ''), r.get('main_id')) is not None
            except Exception:
                r['exists'] = False

    # Get current object count
    try:
        obj_count = Object.query.count()
    except:
        obj_count = 0

    # Sort constellations by full name for the dropdown
    constellation_list = sorted(CONSTELLATIONS.items(), key=lambda kv: kv[1])
    variable_types = list(VARIABLE_TYPE_QUERIES.keys())

    return render_template('simbad/search.html',
                          results=results,
                          query=query_text,
                          search_type=search_type,
                          max_records=max_records,
                          var_type=var_type,
                          constellation=constellation,
                          constellation_list=constellation_list,
                          variable_types=variable_types,
                          obj_count=obj_count)

@web.route('/simbad/api/search')
@login_required
def simbad_api_search():
    """AJAX endpoint for SIMBAD quick search"""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])

    try:
        results = search_simbad(query, search_type='name', max_records=10)
        return jsonify(results or [])
    except:
        return jsonify([])


@web.route('/aavso/recent/<path:star_name>')
@login_required
def aavso_recent_obs(star_name):
    """AJAX endpoint: fetch recent AAVSO observations for a variable star.
    Returns JSON with last_date, last_mag, tendency, days_span, obs_count.

    Shares its logic with the public /api/aavso/recent endpoint via
    aavso_recent.fetch_recent, so both return identical JSON.
    """
    star_name = (star_name or '').strip()
    if not star_name:
        return jsonify({'error': 'No star name provided'}), 400
    data = fetch_recent(star_name, current_user.aavso_api_key)
    if data.get('auth'):
        return jsonify(data), 401
    status = 500 if str(data.get('error', '')).startswith('Failed to fetch') else 200
    return jsonify(data), status


@web.route('/aavso/current/<path:star_name>')
@login_required
def aavso_current_magnitude(star_name):
    """AJAX endpoint: what is this star doing right now?

    Pairs the newest AAVSO observation with the star's VSX range, which is
    what you want next to the magnitude box while entering an observation:
    a value to sanity-check your estimate against.
    """
    star_name = (star_name or '').strip()
    if not star_name:
        return jsonify({'error': 'No star name provided'}), 400

    key = current_user.aavso_api_key
    recent = fetch_recent(star_name, key, days=90, max_pages=3)
    if recent.get('auth'):
        return jsonify(recent), 401
    info = fetch_star_info(star_name, key)

    payload = {
        'star': star_name,
        'last_mag': recent.get('last_mag'),
        'last_date': recent.get('last_date'),
        'last_jd': recent.get('last_jd'),
        'last_observer': recent.get('last_observer'),
        'band': recent.get('band'),
        'tendency': recent.get('tendency'),
        'obs_count': recent.get('obs_count', 0),
    }
    if recent.get('error'):
        payload['error'] = recent['error']
    if not info.get('error'):
        payload.update({
            'vsx_name': info.get('name'),
            'auid': info.get('auid'),
            'mag_max': info.get('mag_max'),
            'mag_min': info.get('mag_min'),
            'vartype': info.get('vartype'),
        })
    return jsonify(payload)


@web.route('/aavso/lightcurve/<path:star_name>')
@login_required
def aavso_lightcurve(star_name):
    """AJAX endpoint: AAVSO observation time series for a light curve.

    Points come back ready for the Chart.js scatter plot
    ({x: unix_ms, y: mag, date, band, uncert}); limit observations are left
    out since they have no plottable magnitude. The v2 API paginates ten rows
    at a time, so long windows are capped and reported as truncated rather
    than fetched forever.
    """
    star_name = star_name.strip()
    if not star_name:
        return jsonify({'error': 'No star name provided', 'points': []}), 400

    try:
        days = max(1, min(int(request.args.get('days', '365')), 3650))
    except (TypeError, ValueError):
        days = 365

    data = fetch_light_curve(star_name, current_user.aavso_api_key, days=days)
    if data.get('error'):
        return jsonify({'error': data['error'], 'points': [], 'obs_count': 0}), \
            (401 if data.get('auth') else 200)

    # Flatten the per-band series into the shape the chart expects
    import calendar as _calendar
    points = []
    for band, rows in (data.get('points') or {}).items():
        for row in rows:
            try:
                y, m, d = (int(part) for part in row['date'].split('-'))
                x_ms = _calendar.timegm((y, m, d, 12, 0, 0, 0, 0, 0)) * 1000
            except Exception:
                continue
            points.append({
                'x': x_ms,
                'y': row['mag'],
                'date': row['date'],
                'jd': row['jd'],
                'band': band,
                'uncert': row.get('uncertainty'),
            })
    points.sort(key=lambda p: p['x'])

    return jsonify({
        'star': star_name,
        'days': days,
        'obs_count': data.get('obs_count', len(points)),
        'total_available': data.get('total_available'),
        'truncated': data.get('truncated', False),
        'mag_min': data.get('mag_min'),
        'mag_max': data.get('mag_max'),
        'points': points,
    })


@web.route('/observations/lightcurve/<path:star_name>')
@login_required
def obs_lightcurve(star_name):
    """AJAX endpoint: return own observations for a variable star as JSON for scatter plot.
    Parses [AAVSO: Magnitude: X.X, Band: ..., Uncertainty: ...] from the observation text.
    """
    import re as _lc_re

    star_name = star_name.strip()
    if not star_name:
        return jsonify({'error': 'No star name provided', 'points': []}), 400

    try:
        # Find object(s) matching the name (case-insensitive)
        obj = Object.query.filter(
            db.func.lower(Object.name) == star_name.lower()
        ).first()

        # Also try partial / AUID match if not found by exact name
        if not obj:
            # Try to find by any object whose name contains the star_name
            obj = Object.query.filter(
                Object.name.ilike('%{}%'.format(star_name))
            ).first()

        if not obj:
            return jsonify({'error': 'Star "{}" not found in your objects'.format(star_name), 'points': []})

        # Get all observations for this object, ordered by date
        obs_list = Observation.query.filter_by(object=obj.id).order_by(
            Observation.datetime.asc()
        ).all()

        # Parse AAVSO magnitude data from each observation text
        aavso_re = _lc_re.compile(
            r'\[AAVSO:\s*(.+?)\]', _lc_re.IGNORECASE
        )
        mag_re = _lc_re.compile(r'Magnitude:\s*([\d.]+)', _lc_re.IGNORECASE)
        band_re = _lc_re.compile(r'Band:\s*([^,\]]+)', _lc_re.IGNORECASE)
        uncert_re = _lc_re.compile(r'Uncertainty:\s*([\d.]+)', _lc_re.IGNORECASE)

        points = []
        for obs in obs_list:
            if not obs.observation:
                continue
            m = aavso_re.search(obs.observation)
            if not m:
                continue
            aavso_block = m.group(1)
            mag_m = mag_re.search(aavso_block)
            if not mag_m:
                continue
            try:
                mag = float(mag_m.group(1))
            except ValueError:
                continue

            band_m = band_re.search(aavso_block)
            band = band_m.group(1).strip() if band_m else 'Vis.'

            uncert_m = uncert_re.search(aavso_block)
            uncert = float(uncert_m.group(1)) if uncert_m else None

            dt = obs.datetime
            date_str = dt.strftime('%Y-%m-%d') if dt else None
            datetime_str = dt.strftime('%Y-%m-%d %H:%M') if dt else None
            # Timestamp in ms for Chart.js time scale
            ts = int(dt.timestamp() * 1000) if dt else None

            if date_str and ts:
                points.append({
                    'x': ts,
                    'date': datetime_str,
                    'y': mag,
                    'band': band,
                    'uncert': uncert,
                    'obs_id': obs.id,
                })

        return jsonify({
            'star': obj.name,
            'obs_count': len(points),
            'points': points,
        })

    except Exception as e:
        return jsonify({'error': 'Failed to load observations: {}'.format(str(e)), 'points': []}), 500


# ============================================================================
# ICQ FORMAT EXPORT
# ============================================================================

import re as _re

def _parse_cobs_data(observation_text):
    """Parse COBS data block from observation text field.
    Returns dict with keys: m1, Coma, DC, Tail, PA, Ref, Sky, Method
    """
    result = {}
    if not observation_text:
        return result
    match = _re.search(r'\\[COBS:\\s*(.+?)\\]', observation_text)
    if not match:
        return result
    for part in match.group(1).split(','):
        part = part.strip()
        if ':' in part:
            key, val = part.split(':', 1)
            result[key.strip()] = val.strip()
    return result


def _parse_comet_designation(designation):
    """Parse comet designation into ICQ columns 1-11.
    Returns (sp_number, year, halfmonth_letter, halfmonth_num, component).
    Examples: '1P/Halley' -> ('  1', '', '', '', '  ')
              'C/2020 F3' -> ('   ', '2020', 'F', '3', '  ')
              '29P/Schwassmann-Wachmann' -> (' 29', '', '', '', '  ')
    """
    sp_number = '   '
    year = '    '
    halfmonth_letter = ' '
    halfmonth_num = ' '
    component = '  '

    if not designation:
        return sp_number, year, halfmonth_letter, halfmonth_num, component

    designation = designation.strip()

    # Periodic comet: "1P/...", "29P/..."
    m = _re.match(r'^(\\d+)[PpDd]/', designation)
    if m:
        num = m.group(1)
        sp_number = num.rjust(3)[:3]
        return sp_number, year, halfmonth_letter, halfmonth_num, component

    # Non-periodic: "C/2020 F3", "C/2024 A1b"
    m = _re.match(r'^[CPDXAI]/(\\d{4})\\s+([A-Z])(\\d+)([a-z])?', designation)
    if m:
        year = m.group(1)
        halfmonth_letter = m.group(2)
        halfmonth_num = m.group(3)[0] if m.group(3) else ' '
        comp = m.group(4) if m.group(4) else '  '
        if len(comp) == 1:
            comp = comp + ' '
        component = comp[:2]
        return sp_number, year, halfmonth_letter, halfmonth_num, component

    return sp_number, year, halfmonth_letter, halfmonth_num, component


def _format_icq_magnitude(mag_str):
    """Format magnitude for ICQ columns 28-33.
    Format: ' mm.m ' with decimal in column 31 (position 4 within field).
    """
    if not mag_str:
        return '      '
    try:
        mag = float(mag_str)
        # Format as right-justified with one decimal: ' mm.m '
        formatted = f'{mag:5.1f}'
        return formatted + ' '
    except (ValueError, TypeError):
        return '      '


def _format_icq_aperture(aperture_str):
    """Format instrument aperture for ICQ columns 36-40.
    Should be in cm, significant figures only.
    """
    if not aperture_str:
        return '     '
    try:
        ap = float(aperture_str)
        if ap == int(ap):
            formatted = f'{int(ap):>5}'
        else:
            formatted = f'{ap:5.1f}'
        return formatted[:5]
    except (ValueError, TypeError):
        # Try to extract number
        m = _re.search(r'([\\d.]+)', str(aperture_str))
        if m:
            return _format_icq_aperture(m.group(1))
        return '     '


def _format_icq_coma(coma_str):
    """Format coma diameter for ICQ columns 49-54.
    In arcminutes, significant figures.
    """
    if not coma_str:
        return '      '
    # Strip unit suffixes like ' or arcmin
    cleaned = _re.sub(r"['\\"arcmin\\s]", '', str(coma_str))
    try:
        coma = float(cleaned)
        if coma >= 100:
            formatted = f'{coma:6.1f}'
        elif coma >= 10:
            formatted = f'{coma:6.2f}'
        else:
            formatted = f'{coma:6.2f}'
        return formatted[:6]
    except (ValueError, TypeError):
        return '      '


def _format_icq_tail(tail_str):
    """Format tail length for ICQ columns 59-64.
    In degrees, or with 'm' suffix for arcminutes.
    """
    if not tail_str:
        return '      '
    cleaned = str(tail_str).strip()
    # Check for degree symbol or 'd'
    is_arcmin = "'" in cleaned or 'arcmin' in cleaned.lower() or 'm' in cleaned.lower()
    cleaned = _re.sub(r"[°'\\"darcmin\\s]", '', cleaned)
    try:
        val = float(cleaned)
        if is_arcmin:
            formatted = f'{val:5.1f}m'
        else:
            formatted = f'{val:5.2f} '
        return formatted[:6]
    except (ValueError, TypeError):
        return '      '


def _format_icq_line(obs, obj, instrument, place, observer_code):
    """Format a single observation into an 80-character ICQ line."""
    cobs = _parse_cobs_data(obs.observation)
    if not cobs:
        return None  # Skip non-comet observations

    # Columns 1-11: Comet designation
    sp, yr, hl, hn, comp = _parse_comet_designation(obj.desination if obj else '')

    # Columns 12-23: Date of observation
    dt = obs.datetime
    if not dt:
        return None
    obs_year = f'{dt.year:4d}'
    obs_month = f'{dt.month:02d}'
    day_frac = dt.day + dt.hour / 24.0 + dt.minute / 1440.0
    obs_day = f'{day_frac:06.2f}'  # DD.DD with leading zero

    # Column 24-25: spaces
    # Column 26: extinction notes (blank)
    # Column 27: magnitude method
    method = cobs.get('Method', '').upper()
    if method == 'CCD':
        mag_method = 'Z'
    elif method == 'VISUAL':
        mag_method = 'B'  # Bobrovnikoff method (default for visual)
    else:
        mag_method = ' '

    # Columns 28-33: magnitude
    magnitude = _format_icq_magnitude(cobs.get('m1'))

    # Columns 34-35: reference stars catalog
    ref = cobs.get('Ref', '')[:2].ljust(2)

    # Columns 36-40: aperture (cm)
    aperture = _format_icq_aperture(instrument.aperture if instrument else '')

    # Column 41: instrument type
    inst_type = ' '
    if instrument and instrument.instrument_type:
        itype = instrument.instrument_type.upper()
        if 'REFRACT' in itype:
            inst_type = 'R'
        elif 'REFLECT' in itype or 'NEWT' in itype:
            inst_type = 'N'
        elif 'CASSEGRAIN' in itype or 'SCT' in itype or 'SCHMIDT' in itype:
            inst_type = 'S'
        elif 'BINOC' in itype:
            inst_type = 'B'
        elif 'NAKED' in itype or 'EYE' in itype:
            inst_type = 'E'
        elif 'CCD' in itype or 'CAMERA' in itype:
            inst_type = 'L'
        else:
            inst_type = 'L'

    # Columns 42-43: focal ratio
    focal_ratio = '  '

    # Columns 44-47: power/magnification
    power = '    '
    if instrument and instrument.power:
        try:
            p = int(float(instrument.power))
            power = f'{p:>4}'[:4]
        except (ValueError, TypeError):
            pass

    # Column 48: space
    # Columns 49-54: coma diameter
    coma = _format_icq_coma(cobs.get('Coma'))

    # Column 55: central condensation appearance (blank)
    cond_appearance = ' '

    # Columns 56-57: degree of condensation
    dc = cobs.get('DC', '')
    if dc:
        try:
            dc_val = int(float(dc))
            dc_str = f'{dc_val:>1} '
        except (ValueError, TypeError):
            dc_str = '  '
    else:
        dc_str = '  '

    # Column 58: space
    # Columns 59-64: tail length
    tail = _format_icq_tail(cobs.get('Tail'))

    # Columns 65-67: position angle
    pa = cobs.get('PA', '')
    if pa:
        try:
            pa_val = int(float(pa))
            pa_str = f'{pa_val:>3}'[:3]
        except (ValueError, TypeError):
            pa_str = '   '
    else:
        pa_str = '   '

    # Column 68: space
    # Columns 69-74: publication reference (blank)
    pub_ref = '      '

    # Column 75: revision indicator
    revision = ' '

    # Columns 76-80: observer code
    obs_code = (observer_code or '').ljust(5)[:5]

    # Assemble the 80-character line
    line = (
        f'{sp}'               # 1-3
        f'{yr}'               # 4-7
        f'{hl}'               # 8
        f'{hn}'               # 9
        f'{comp}'             # 10-11
        f'{obs_year}'         # 12-15
        f'{obs_month}'        # 16-17
        f'{obs_day}'          # 18-23
        f'  '                 # 24-25
        f' '                  # 26
        f'{mag_method}'       # 27
        f'{magnitude}'        # 28-33
        f'{ref}'              # 34-35
        f'{aperture}'         # 36-40
        f'{inst_type}'        # 41
        f'{focal_ratio}'      # 42-43
        f'{power}'            # 44-47
        f' '                  # 48
        f'{coma}'             # 49-54
        f'{cond_appearance}'  # 55
        f'{dc_str}'           # 56-57
        f' '                  # 58
        f'{tail}'             # 59-64
        f'{pa_str}'           # 65-67
        f' '                  # 68
        f'{pub_ref}'          # 69-74
        f'{revision}'         # 75
        f'{obs_code}'         # 76-80
    )

    return line[:80]


@web.route('/export/icq', methods=['GET', 'POST'])
@login_required
def export_icq():
    """Export comet observations in ICQ format."""
    comet_observations = []
    icq_lines = []
    exported = False

    try:
        # Get comet type
        comet_type = Type.query.filter_by(name='Comet').first()

        # Get all comet objects
        comet_objects = []
        if comet_type:
            comet_objects = Object.query.filter_by(type=comet_type.id).all()
        comet_ids = [c.id for c in comet_objects]
        comet_lookup = {c.id: c for c in comet_objects}

        # Get all instruments lookup
        instruments = {i.id: i for i in Instrument.query.all()}

        # Get all places lookup
        places = {p.id: p for p in Place.query.all()}

        # Get observer code from current user
        observer_code = current_user.icq_code or ''

        if request.method == 'POST':
            exported = True
            # Filter parameters
            comet_id = request.form.get('comet_id')
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')

            # Build query
            query = Observation.query.filter(Observation.object.in_(comet_ids))

            if comet_id and comet_id != 'all':
                query = query.filter(Observation.object == int(comet_id))
            if date_from:
                query = query.filter(Observation.datetime >= datetime.fromisoformat(date_from))
            if date_to:
                query = query.filter(Observation.datetime <= datetime.fromisoformat(date_to + 'T23:59:59'))

            query = query.order_by(Observation.datetime)
            comet_observations = query.all()

            # Generate ICQ lines
            for obs in comet_observations:
                obj = comet_lookup.get(obs.object)
                inst = instruments.get(obs.instrument)
                line = _format_icq_line(obs, obj, inst, places.get(obs.place), observer_code)
                if line:
                    icq_lines.append({
                        'line': line,
                        'obs_id': obs.id,
                        'comet_name': obj.name if obj else 'Unknown',
                        'date': obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '',
                    })

    except Exception as e:
        flash(f'Error loading comet observations: {str(e)}', 'danger')

    return render_template('export/icq.html',
                         comet_objects=comet_objects if 'comet_objects' in dir() else [],
                         icq_lines=icq_lines,
                         total_observations=len(comet_observations),
                         exported=exported)


@web.route('/export/icq/download', methods=['POST'])
@login_required
def export_icq_download():
    """Download comet observations as ICQ format text file."""
    try:
        comet_type = Type.query.filter_by(name='Comet').first()
        comet_objects = Object.query.filter_by(type=comet_type.id).all() if comet_type else []
        comet_ids = [c.id for c in comet_objects]
        comet_lookup = {c.id: c for c in comet_objects}
        instruments = {i.id: i for i in Instrument.query.all()}
        places = {p.id: p for p in Place.query.all()}
        observer_code = current_user.icq_code or ''

        # Filter parameters
        comet_id = request.form.get('comet_id')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')

        query = Observation.query.filter(Observation.object.in_(comet_ids))
        if comet_id and comet_id != 'all':
            query = query.filter(Observation.object == int(comet_id))
        if date_from:
            query = query.filter(Observation.datetime >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(Observation.datetime <= datetime.fromisoformat(date_to + 'T23:59:59'))

        query = query.order_by(Observation.datetime)
        observations = query.all()

        lines = []
        for obs in observations:
            obj = comet_lookup.get(obs.object)
            inst = instruments.get(obs.instrument)
            line = _format_icq_line(obs, obj, inst, places.get(obs.place), observer_code)
            if line:
                lines.append(line)

        content = '\\n'.join(lines) + '\\n' if lines else ''
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'comet_observations_icq_{timestamp}.txt'

        return Response(
            content,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        flash(f'Error exporting ICQ data: {str(e)}', 'danger')
        return redirect(url_for('web.export_icq'))


# ============================================================================
# AAVSO VISUAL FORMAT EXPORT
# ============================================================================

def _parse_aavso_data(observation_text):
    """Parse AAVSO data block from observation text field.
    Returns dict with keys: Magnitude, Uncertainty, Comp1, Comp2, Check,
    Chart, Band, Observer, Method
    """
    result = {}
    if not observation_text:
        return result
    match = _re.search(r'\\[AAVSO:\\s*(.+?)\\]', observation_text)
    if not match:
        return result
    for part in match.group(1).split(','):
        part = part.strip()
        if ':' in part:
            key, val = part.split(':', 1)
            result[key.strip()] = val.strip()
    return result


def _aavso_reportable_objects():
    """Objects that can appear in an AAVSO report.

    Object type is not a reliable filter here: plenty of genuine variables
    (U Del, CH Cyg, AC Her ...) were created or imported with type 'Star', and
    filtering on type 'Variable Star' silently dropped their observations from
    the export. Anything carrying an [AAVSO: ...] block is reportable, so the
    marker in the observation text is the real criterion - the type is only
    used to keep stars with no observations yet in the star picker.

    Returns (objects, ids, lookup).
    """
    ids = set()
    try:
        vs_type = Type.query.filter_by(name='Variable Star').first()
        if vs_type:
            ids.update(o.id for o in Object.query.filter_by(type=vs_type.id).all())
    except Exception:
        pass
    try:
        rows = db.session.query(Observation.object).filter(
            Observation.observation.like('%[AAVSO:%')).distinct().all()
        ids.update(r[0] for r in rows if r[0] is not None)
    except Exception:
        pass
    if not ids:
        return [], [], {}
    objects = Object.query.filter(Object.id.in_(ids)).order_by(Object.name).all()
    return objects, [o.id for o in objects], {o.id: o for o in objects}


def _datetime_to_jd(dt):
    """Convert a Python datetime to Julian Date."""
    if not dt:
        return None
    # Julian Date formula
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    jd = jdn + (dt.hour - 12) / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
    return jd


def _build_aavso_visual_file(observations, objects_lookup, observer_code):
    """Build a complete AAVSO Visual Format file string.

    AAVSO Visual File Format:
    Header:
        #TYPE=Visual
        #OBSCODE=<observer_code>
        #SOFTWARE=Astronomy Observations App
        #DELIM=,
        #DATE=JD
        #OBSTYPE=Visual
    Data (one per line, comma-separated):
        NAME,DATE,MAG,COMMENTCODE,COMP1,COMP2,CHART,NOTES
    """
    lines = []
    # Header
    lines.append('#TYPE=Visual')
    lines.append(f'#OBSCODE={observer_code or "na"}')
    lines.append('#SOFTWARE=Astronomy Observations App')
    lines.append('#DELIM=,')
    lines.append('#DATE=JD')
    lines.append('#OBSTYPE=Visual')

    for obs in observations:
        aavso = _parse_aavso_data(obs.observation)
        if not aavso:
            continue

        obj = objects_lookup.get(obs.object)
        # NAME: star name or designation
        name = ''
        if obj:
            name = obj.desination or obj.name or ''
        name = name.strip() or 'na'

        # DATE: Julian Date
        jd = _datetime_to_jd(obs.datetime)
        date_str = f'{jd:.4f}' if jd else 'na'

        # MAG: magnitude, may include < for fainter-than
        mag = aavso.get('Magnitude', 'na')
        if mag:
            mag = mag.strip()
        if not mag:
            mag = 'na'

        # COMMENTCODE: na unless special circumstances
        # B=cloudy, D=poor seeing, I=identification uncertain,
        # K=non-AAVSO chart, U=discrepant, W=uncertain, Y=outburst, Z=magnitude corrected
        comment_code = 'na'

        # COMP1: comparison star 1
        comp1 = aavso.get('Comp1', 'na')
        if not comp1:
            comp1 = 'na'

        # COMP2: comparison star 2
        comp2 = aavso.get('Comp2', 'na')
        if not comp2:
            comp2 = 'na'

        # CHART: chart id
        chart = aavso.get('Chart', 'na')
        if not chart:
            chart = 'na'

        # NOTES: additional notes (strip out the [AAVSO:...] block itself)
        notes_text = obs.observation or ''
        notes_text = _re.sub(r'\\s*\\[AAVSO:.*?\\]', '', notes_text).strip()
        if not notes_text:
            notes_text = 'na'
        # Commas in notes must be removed since comma is our delimiter
        notes_text = notes_text.replace(',', ';')

        line = f'{name},{date_str},{mag},{comment_code},{comp1},{comp2},{chart},{notes_text}'
        lines.append(line)

    return '\\n'.join(lines) + '\\n'


@web.route('/export/aavso', methods=['GET', 'POST'])
@login_required
def export_aavso():
    """Export variable star observations in AAVSO Visual format."""
    vs_observations = []
    aavso_lines = []
    exported = False

    try:
        # Everything with AAVSO data, whatever the object's type is
        vs_objects, vs_ids, vs_lookup = _aavso_reportable_objects()

        # Observer code from user settings
        observer_code = current_user.aavso_code or ''

        if request.method == 'POST':
            exported = True
            star_id = request.form.get('star_id')
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')

            query = Observation.query.filter(Observation.object.in_(vs_ids))
            if star_id and star_id != 'all':
                query = query.filter(Observation.object == int(star_id))
            if date_from:
                query = query.filter(Observation.datetime >= datetime.fromisoformat(date_from))
            if date_to:
                query = query.filter(Observation.datetime <= datetime.fromisoformat(date_to + 'T23:59:59'))

            query = query.order_by(Observation.datetime)
            vs_observations = query.all()

            # Build preview lines
            for obs in vs_observations:
                aavso = _parse_aavso_data(obs.observation)
                if not aavso:
                    continue
                obj = vs_lookup.get(obs.object)
                jd = _datetime_to_jd(obs.datetime)
                aavso_lines.append({
                    'obs_id': obs.id,
                    'star_name': obj.name if obj else 'Unknown',
                    'designation': obj.desination if obj else '',
                    'date': obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '',
                    'jd': f'{jd:.4f}' if jd else '',
                    'magnitude': aavso.get('Magnitude', ''),
                    'comp1': aavso.get('Comp1', ''),
                    'comp2': aavso.get('Comp2', ''),
                    'chart': aavso.get('Chart', ''),
                })

    except Exception as e:
        flash(f'Error loading variable star observations: {str(e)}', 'danger')

    return render_template('export/aavso.html',
                         vs_objects=vs_objects if 'vs_objects' in dir() else [],
                         aavso_lines=aavso_lines,
                         total_observations=len(vs_observations),
                         exported=exported,
                         observer_code=observer_code if 'observer_code' in dir() else '')


@web.route('/export/aavso/download', methods=['POST'])
@login_required
def export_aavso_download():
    """Download variable star observations as AAVSO Visual format text file."""
    try:
        vs_objects, vs_ids, vs_lookup = _aavso_reportable_objects()
        observer_code = current_user.aavso_code or ''

        star_id = request.form.get('star_id')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')

        query = Observation.query.filter(Observation.object.in_(vs_ids))
        if star_id and star_id != 'all':
            query = query.filter(Observation.object == int(star_id))
        if date_from:
            query = query.filter(Observation.datetime >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(Observation.datetime <= datetime.fromisoformat(date_to + 'T23:59:59'))

        query = query.order_by(Observation.datetime)
        observations = query.all()

        content = _build_aavso_visual_file(observations, vs_lookup, observer_code)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'variable_stars_aavso_{timestamp}.txt'

        return Response(
            content,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        flash(f'Error exporting AAVSO data: {str(e)}', 'danger')
        return redirect(url_for('web.export_aavso'))


# ============================================================================
# COBS SUBMISSION (cobs.si)
# ============================================================================

def _cobs_login(session, username, password):
    """Login to COBS and return True on success."""
    r = session.get('https://www.cobs.si/accounts/login/', timeout=15)
    csrf_match = _re.search(r'csrfmiddlewaretoken.*?value=["\\'](.*?)["\\'\\s]', r.text)
    if not csrf_match:
        return False, 'Could not get COBS CSRF token'
    csrf = csrf_match.group(1)
    r2 = session.post('https://www.cobs.si/accounts/login/', data={
        'csrfmiddlewaretoken': csrf,
        'username': username,
        'password': password,
    }, headers={'Referer': 'https://www.cobs.si/accounts/login/'}, allow_redirects=True, timeout=15)
    if 'login' in r2.url:
        return False, 'COBS login failed. Check your credentials in Settings.'
    return True, 'OK'


def _cobs_get_form_csrf(session):
    """Get the observation form CSRF token."""
    r = session.get('https://www.cobs.si/obs/form/vis/', timeout=15)
    if 'login' in r.url:
        return None, None
    csrf_match = _re.search(r'csrfmiddlewaretoken.*?value=["\\'](.*?)["\\'\\s]', r.text)
    if not csrf_match:
        return None, None
    return csrf_match.group(1), r.text


def _aperture_mm_to_cm(aperture_str):
    """Convert aperture from mm to cm for COBS submission.
    Parses strings like '70mm', '200.0mm', '70', extracting the number and dividing by 10.
    """
    if not aperture_str:
        return ''
    import re as _re_local
    m = _re_local.search(r'([\\d.]+)', str(aperture_str))
    if not m:
        return aperture_str
    mm_val = float(m.group(1))
    cm_val = mm_val / 10.0
    # Return as clean number: 7.0 -> '7.0', 20.0 -> '20.0'
    if cm_val == int(cm_val):
        return f'{cm_val:.1f}'
    return str(cm_val)


def _clean_power_for_cobs(power_str):
    """Extract integer magnification from power string for COBS.
    COBS requires a whole number. '15x' -> '15', '10X' -> '10', '200' -> '200'.
    """
    if not power_str:
        return ''
    import re as _re_local
    m = _re_local.search(r'(\\d+)', str(power_str))
    return m.group(1) if m else ''


def _map_instrument_type_to_cobs(instrument):
    """Map local instrument type to COBS instrument_type select value."""
    if not instrument or not instrument.instrument_type:
        return ''
    itype = instrument.instrument_type.upper()
    mapping = {
        'REFRACT': '20', 'NEWT': '12', 'REFLECT': '12',
        'CASSEGRAIN': '3', 'SCT': '22', 'SCHMIDT-CASSEGRAIN': '22',
        'MAKSUTOV': '13', 'BINOC': '2', 'NAKED': '5', 'EYE': '5',
        'CAMERA': '1', 'LENS': '1', 'SCHMIDT': '4',
    }
    for key, val in mapping.items():
        if key in itype:
            return val
    return ''


def _map_obs_method_to_cobs(method_str):
    """Map COBS method field from our app to cobs.si obs_method value."""
    if not method_str:
        return ''
    m = method_str.upper().strip()
    if m == 'VISUAL' or m == 'B':
        return '2'   # B - Simple Out-Out method
    elif m == 'CCD':
        return '47'  # Z - CCD Visual equivalent
    return ''


def _submit_obs_to_cobs(session, csrf, obs, obj, instrument, place, cobs_data):
    """Submit a single observation to COBS. Returns (success, message)."""
    # Find comet in COBS by designation — we pass the COBS comet ID if known,
    # otherwise the user must select it in the preview step.
    form_data = {
        'csrfmiddlewaretoken': csrf,
        'comet': cobs_data.get('cobs_comet_id', ''),
        'obs_date': obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '',
        'magnitude': cobs_data.get('magnitude', ''),
        'obs_method': cobs_data.get('obs_method', ''),
        'extinction': '',
        'comet_visibility': '',
        'conditions': '',
        'ref_catalog': cobs_data.get('ref_catalog', '144'),
        'instrument_type': cobs_data.get('instrument_type', ''),
        'instrument_aperture': cobs_data.get('aperture', ''),
        'instrument_focal_ratio': '',
        'instrument_power': cobs_data.get('power', ''),
        'coma_diameter': cobs_data.get('coma', ''),
        'coma_dc': cobs_data.get('dc', ''),
        'coma_visibility': '',
        'coma_notes': '',
        'tail_length': cobs_data.get('tail', ''),
        'tail_pa': cobs_data.get('pa', ''),
        'tail_visibility': '',
        'tail_length_unit': cobs_data.get('tail_unit', 'd'),
        'location': cobs_data.get('location', ''),
        'icq_reference': '',
        'icq_revision': 'unknown',
        'obs_sky_quality': '',
        'obs_sky_quality_method': '',
        'reference_star_names': cobs_data.get('ref', ''),
        'obs_comment': cobs_data.get('comment', ''),
    }

    r = session.post('https://www.cobs.si/obs/form/vis/', data=form_data,
                     headers={'Referer': 'https://www.cobs.si/obs/form/vis/'},
                     allow_redirects=True, timeout=15)

    # Success: COBS redirects to /obs/done/<id>/
    if '/obs/done/' in r.url:
        obs_num = _re.search(r'/obs/done/(\d+)/', r.url)
        obs_id_str = obs_num.group(1) if obs_num else ''
        return True, f'Submitted (COBS #{obs_id_str})'

    # Check for form validation errors - look for is-invalid fields with their error messages
    errors = []
    for m in _re.finditer(r'<div id="div_id_(\\w+)"[^>]*>(.*?)</div>\\s*</div>', r.text, _re.DOTALL):
        if 'is-invalid' in m.group(2):
            field_name = m.group(1)
            err_match = _re.search(r'invalid-feedback[^>]*>(.*?)</div>', m.group(2), _re.DOTALL)
            err_text = _re.sub(r'<[^>]+>', '', err_match.group(1)).strip() if err_match else 'required'
            errors.append(f'{field_name}: {err_text}')

    # Also check for strong tags in invalid-feedback (older format)
    if not errors:
        for m in _re.finditer(r'invalid-feedback["\\'\\s][^>]*>.*?<strong>(.*?)</strong>', r.text, _re.DOTALL):
            errors.append(m.group(1).strip())

    if errors:
        return False, '; '.join(errors)

    # Check for Django errorlist
    for m in _re.finditer(r'errorlist[^>]*>(.*?)</ul>', r.text, _re.DOTALL):
        clean = _re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
        if clean:
            return False, clean

    # If still on the form page, something went wrong
    if '/obs/form/' in r.url:
        return False, 'Form submission failed (unknown error)'

    return True, 'Submitted successfully'


@web.route('/cobs/submit', methods=['GET', 'POST'])
@login_required
def cobs_submit():
    """Submit comet observations to COBS."""
    # Check credentials
    if not current_user.cobs_username or not current_user.cobs_password:
        flash('Please set your COBS credentials in Settings first.', 'warning')
        return redirect(url_for('web.user_settings'))

    comet_observations = []
    preview_data = []
    cobs_comets = []
    submitted_results = []
    step = request.form.get('step', 'filter')

    try:
        comet_type = Type.query.filter_by(name='Comet').first()
        comet_objects = Object.query.filter_by(type=comet_type.id).all() if comet_type else []
        comet_ids = [c.id for c in comet_objects]
        comet_lookup = {c.id: c for c in comet_objects}
        instruments = {i.id: i for i in Instrument.query.all()}
        places = {p.id: p for p in Place.query.all()}

        if request.method == 'POST' and step == 'preview':
            # Build query with filters
            comet_id = request.form.get('comet_id')
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')

            query = Observation.query.filter(Observation.object.in_(comet_ids))
            if comet_id and comet_id != 'all':
                query = query.filter(Observation.object == int(comet_id))
            if date_from:
                query = query.filter(Observation.datetime >= datetime.fromisoformat(date_from))
            if date_to:
                query = query.filter(Observation.datetime <= datetime.fromisoformat(date_to + 'T23:59:59'))

            comet_observations = query.order_by(Observation.datetime).all()

            # Login to COBS to get comet list
            cobs_session = http_requests.Session()
            ok, msg = _cobs_login(cobs_session, current_user.cobs_username, current_user.cobs_password)
            if not ok:
                flash(msg, 'danger')
            else:
                csrf, form_html = _cobs_get_form_csrf(cobs_session)
                if form_html:
                    # Extract COBS comet options from the comet select element only
                    comet_select = _re.search(r'<select[^>]*\\bname=["\\'\\s]comet["\\'\\s][^>]*>(.*?)</select>', form_html, _re.DOTALL)
                    if not comet_select:
                        comet_select = _re.search(r'<select[^>]*\\bid=["\\'\\s]id_comet["\\'\\s][^>]*>(.*?)</select>', form_html, _re.DOTALL)
                    comet_html = comet_select.group(1) if comet_select else form_html
                    for m in _re.finditer(r'<option value=["\\'](\\d+)["\\'](.*?)>(.*?)</option>', comet_html):
                        cobs_comets.append({'id': m.group(1), 'name': m.group(3).strip()})
                    if not cobs_comets:
                        flash(f'Warning: Could not extract comet list from COBS form. The form structure may have changed.', 'warning')

            # Build preview data
            for obs in comet_observations:
                cobs = _parse_cobs_data(obs.observation)
                if not cobs:
                    continue
                obj = comet_lookup.get(obs.object)
                inst = instruments.get(obs.instrument)
                place = places.get(obs.place)

                # Try to auto-match COBS comet by name and designation
                matched_cobs_id = ''
                if obj:
                    obj_name = (obj.name or '').strip()
                    obj_des = (obj.desination or '').strip()
                    for cc in cobs_comets:
                        cobs_name = cc['name']
                        # Direct match on designation or name
                        if obj_des and (obj_des in cobs_name or cobs_name in obj_des):
                            matched_cobs_id = cc['id']
                            break
                        if obj_name and (obj_name in cobs_name or cobs_name in obj_name):
                            matched_cobs_id = cc['id']
                            break
                        # Match readable designation from name, e.g. 'C/2025 R3 (PANSTARRS)'
                        # against our name 'C/2025 R3 (PANSTARRS)'
                        # Also handle MPC packed format: C/K25R030 -> C/2025 R3
                        name_parts = obj_name.split('(')[0].strip() if obj_name else ''
                        cobs_parts = cobs_name.split('(')[0].strip()
                        if name_parts and cobs_parts and name_parts == cobs_parts:
                            matched_cobs_id = cc['id']
                            break

                preview_data.append({
                    'obs_id': obs.id,
                    'comet_name': obj.name if obj else 'Unknown',
                    'designation': obj.desination if obj else '',
                    'date': obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '',
                    'magnitude': cobs.get('m1', ''),
                    'coma': cobs.get('Coma', ''),
                    'dc': cobs.get('DC', ''),
                    'tail': cobs.get('Tail', ''),
                    'pa': cobs.get('PA', ''),
                    'method': cobs.get('Method', ''),
                    'aperture': _aperture_mm_to_cm(inst.aperture) if inst else '',
                    'power': _clean_power_for_cobs(inst.power) if inst else '',
                    'instrument_type': _map_instrument_type_to_cobs(inst),
                    'obs_method': _map_obs_method_to_cobs(cobs.get('Method', '')),
                    'location': (place.alias or place.name) if place else '',
                    'ref': cobs.get('Ref', ''),
                    'matched_cobs_id': matched_cobs_id,
                })
            step = 'preview'

        elif request.method == 'POST' and step == 'submit':
            # Actually submit selected observations
            obs_ids = request.form.getlist('obs_ids')
            if not obs_ids:
                flash('No observations selected.', 'warning')
                return redirect(url_for('web.cobs_submit'))

            cobs_session = http_requests.Session()
            ok, msg = _cobs_login(cobs_session, current_user.cobs_username, current_user.cobs_password)
            if not ok:
                flash(msg, 'danger')
                return redirect(url_for('web.cobs_submit'))

            for obs_id in obs_ids:
                obs = Observation.query.get(int(obs_id))
                if not obs:
                    continue
                cobs = _parse_cobs_data(obs.observation)
                if not cobs:
                    continue

                obj = comet_lookup.get(obs.object)
                inst = instruments.get(obs.instrument)
                place = places.get(obs.place)

                # Get fresh CSRF for each submission
                csrf, _ = _cobs_get_form_csrf(cobs_session)
                if not csrf:
                    submitted_results.append({'obs_id': obs_id, 'success': False, 'msg': 'Could not get form'})
                    continue

                cobs_data = {
                    'cobs_comet_id': request.form.get(f'cobs_comet_{obs_id}', ''),
                    'magnitude': cobs.get('m1', ''),
                    'obs_method': _map_obs_method_to_cobs(cobs.get('Method', '')),
                    'instrument_type': _map_instrument_type_to_cobs(inst),
                    'aperture': _aperture_mm_to_cm(inst.aperture) if inst else '',
                    'power': _clean_power_for_cobs(inst.power) if inst else '',
                    'coma': cobs.get('Coma', '').replace("'", '').replace('"', '').strip(),
                    'dc': cobs.get('DC', ''),
                    'tail': cobs.get('Tail', '').replace("'", '').replace('"', '').replace('d', '').replace('m', '').strip(),
                    'pa': cobs.get('PA', ''),
                    'tail_unit': 'd',
                    'location': (place.alias or place.name) if place else '',
                    'ref': cobs.get('Ref', ''),
                    'comment': f'Submitted from Astronomy Observations App',
                }

                success, result_msg = _submit_obs_to_cobs(cobs_session, csrf, obs, obj, inst, place, cobs_data)
                comet_name = obj.name if obj else f'Obs #{obs_id}'
                submitted_results.append({
                    'obs_id': obs_id,
                    'comet_name': comet_name,
                    'date': obs.datetime.strftime('%Y-%m-%d') if obs.datetime else '',
                    'success': success,
                    'msg': result_msg,
                })

            successes = sum(1 for r in submitted_results if r['success'])
            failures = len(submitted_results) - successes
            if successes:
                flash(f'Successfully submitted {successes} observation(s) to COBS!', 'success')
            if failures:
                flash(f'{failures} observation(s) failed to submit.', 'danger')
            step = 'results'

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return render_template('cobs/submit.html',
                         comet_objects=comet_objects if 'comet_objects' in dir() else [],
                         preview_data=preview_data,
                         cobs_comets=cobs_comets,
                         submitted_results=submitted_results,
                         step=step)


# ============================================================================
# AAVSO SUBMISSION (aavso.org)
# ============================================================================

def _aavso_login(email, password):
    """Login to AAVSO via Auth0. Returns (session, success, message)."""
    s = http_requests.Session()
    try:
        # Step 1: Get the AAVSO login page (triggers CSRF)
        r = s.get('https://apps.aavso.org/v2/accounts/auth0/login/', timeout=15)
        csrf = _re.search(r'csrfmiddlewaretoken.*?value="(.*?)"', r.text)
        if not csrf:
            return None, False, 'Could not get AAVSO login page'

        # Step 2: POST to trigger Auth0 redirect
        r2 = s.post('https://apps.aavso.org/v2/accounts/auth0/login/', data={
            'csrfmiddlewaretoken': csrf.group(1)
        }, headers={'Referer': 'https://apps.aavso.org/v2/accounts/auth0/login/'},
           allow_redirects=True, timeout=15)

        if 'auth.aavso.org' not in r2.url:
            return None, False, 'Could not reach Auth0 login'

        # Step 3: Submit credentials to Auth0
        r3 = s.post(r2.url, data={
            'username': email,
            'password': password,
            'action': 'default',
        }, headers={'Referer': r2.url}, allow_redirects=True, timeout=15)

        if 'login' in r3.url.split('?')[0]:
            return None, False, 'AAVSO login failed. Check your email and password.'

        return s, True, 'Logged in'
    except Exception as e:
        return None, False, f'AAVSO login error: {str(e)}'


def _aavso_get_form_csrf(session):
    """Get the AAVSO photometry submission form CSRF token."""
    r = session.get('https://apps.aavso.org/v2/data/submit/photometry/', timeout=15)
    if 'login' in r.url.lower():
        return None
    csrf = _re.search(r'csrfmiddlewaretoken.*?value="(.*?)"', r.text)
    return csrf.group(1) if csrf else None


def _map_band_to_aavso(band_str):
    """Map our band string to AAVSO band value."""
    if not band_str:
        return '0'  # Visual
    mapping = {
        'VIS': '0', 'VIS.': '0', 'VISUAL': '0', 'V': '2',
        'B': '3', 'U': '7', 'R': '4', 'I': '5',
        'CV': '8', 'CR': '9', 'TG': '1',
    }
    return mapping.get(band_str.upper().strip(), '0')


def _map_obstype_to_aavso(method_str):
    """Map our method to AAVSO obstype value."""
    if not method_str:
        return '1'
    m = method_str.upper().strip()
    if m == 'CCD':
        return '2'
    if m == 'DSLR':
        return '6'
    if m == 'PEP':
        return '3'
    return '1'  # Visual


def _submit_obs_to_aavso(session, csrf, star_name, obs_datetime, aavso_data):
    """Submit a single observation to AAVSO using 2-step preview+confirm flow.
    Returns (success, message).
    obs_datetime should be a datetime string like '2026-04-12 04:23'.
    """
    form_data = {
        'csrfmiddlewaretoken': csrf,
        '_obscount': '1',
        'obstype': aavso_data.get('obstype', '1'),
        'auid': star_name,
        'jd': obs_datetime,
        'magnitude': aavso_data.get('magnitude', ''),
        'uncertainty': aavso_data.get('uncertainty', ''),
        'charts': aavso_data.get('chart', ''),
        'comp1_c': aavso_data.get('comp1', ''),
        'cmag': '',
        'comp2_k': aavso_data.get('comp2', ''),
        'kmag': '',
        'band': aavso_data.get('band', '0'),
        'comments': aavso_data.get('comments', ''),
    }

    url = 'https://apps.aavso.org/v2/data/submit/photometry/'
    referer = {'Referer': url}

    # Step 1: Preview with "Continue"
    form_data['continue'] = 'Continue'
    r_preview = session.post(url, data=form_data, headers=referer,
                            allow_redirects=True, timeout=15)

    # Check for validation errors on preview
    preview_errors = []
    for m in _re.finditer(r'alert[^"]*"[^>]*>(.*?)</div>', r_preview.text, _re.DOTALL):
        clean = _re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if clean and ('correct' in clean.lower() or 'error' in clean.lower()):
            preview_errors.append(clean)

    if preview_errors:
        return False, '; '.join(preview_errors[:3])

    # Step 2: Confirm with "Submit and Return"
    csrf2 = _re.search(r'csrfmiddlewaretoken.*?value="(.*?)"', r_preview.text)
    if not csrf2:
        return False, 'Could not get confirmation CSRF'

    form_data['csrfmiddlewaretoken'] = csrf2.group(1)
    del form_data['continue']
    form_data['submit'] = 'Submit and Return'

    r_submit = session.post(url, data=form_data, headers=referer,
                           allow_redirects=True, timeout=15)

    # Check for success: URL contains ?success=true
    if 'success=true' in r_submit.url:
        return True, 'Submitted successfully'

    if 'successfully' in r_submit.text.lower():
        return True, 'Submitted successfully'

    # Check for errors on submit
    errors = []
    for m in _re.finditer(r'alert[^"]*"[^>]*>(.*?)</div>', r_submit.text, _re.DOTALL):
        clean = _re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if clean and len(clean) > 3:
            errors.append(clean)

    for m in _re.finditer(r'is-invalid.*?<div[^>]*invalid-feedback[^>]*>(.*?)</div>', r_submit.text, _re.DOTALL):
        clean = _re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if clean:
            errors.append(clean)

    if errors:
        return False, '; '.join(errors[:3])

    if '/data/submit/' in r_submit.url and 'success' not in r_submit.url:
        return False, 'Submission may have failed (no success confirmation)'

    return True, 'Submitted'


@web.route('/aavso/submit', methods=['GET', 'POST'])
@login_required
def aavso_submit():
    """Submit variable star observations to AAVSO."""
    if not current_user.aavso_email or not current_user.aavso_password:
        flash('Please set your AAVSO email and password in Settings first.', 'warning')
        return redirect(url_for('web.user_settings'))

    varstar_observations = []
    preview_data = []
    submitted_results = []
    step = request.form.get('step', 'filter')

    try:
        varstar_objects, varstar_ids, varstar_lookup = _aavso_reportable_objects()

        if request.method == 'POST' and step == 'preview':
            star_id = request.form.get('star_id')
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')

            query = Observation.query.filter(Observation.object.in_(varstar_ids))
            if star_id and star_id != 'all':
                query = query.filter(Observation.object == int(star_id))
            if date_from:
                query = query.filter(Observation.datetime >= datetime.fromisoformat(date_from))
            if date_to:
                query = query.filter(Observation.datetime <= datetime.fromisoformat(date_to + 'T23:59:59'))

            varstar_observations = query.order_by(Observation.datetime).all()

            for obs in varstar_observations:
                aavso = _parse_aavso_data(obs.observation)
                if not aavso:
                    continue
                obj = varstar_lookup.get(obs.object)
                jd = _datetime_to_jd(obs.datetime)
                star_name = obj.name if obj else 'Unknown'

                # Get AUID from object props if available
                obj_auid = ''
                if obj and obj.props:
                    try:
                        import json as _json_mod
                        obj_props = _json_mod.loads(obj.props)
                        obj_auid = obj_props.get('auid', '')
                    except:
                        pass

                preview_data.append({
                    'obs_id': obs.id,
                    'star_name': star_name,
                    'auid': obj_auid,
                    'date': obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '',
                    'jd': f'{jd:.4f}' if jd else '',
                    'magnitude': aavso.get('Magnitude', ''),
                    'comp1': aavso.get('Comp1', ''),
                    'comp2': aavso.get('Comp2', ''),
                    'chart': aavso.get('Chart', ''),
                    'band': aavso.get('Band', 'Vis.'),
                    'method': aavso.get('Method', 'VISUAL'),
                    'observer': aavso.get('Observer', ''),
                })
            step = 'preview'

        elif request.method == 'POST' and step == 'submit':
            obs_ids = request.form.getlist('obs_ids')
            if not obs_ids:
                flash('No observations selected.', 'warning')
                return redirect(url_for('web.aavso_submit'))

            aavso_session, ok, msg = _aavso_login(current_user.aavso_email, current_user.aavso_password)
            if not ok:
                flash(msg, 'danger')
                return redirect(url_for('web.aavso_submit'))

            for obs_id in obs_ids:
                obs = Observation.query.get(int(obs_id))
                if not obs:
                    continue
                aavso = _parse_aavso_data(obs.observation)
                if not aavso:
                    continue

                obj = varstar_lookup.get(obs.object)
                jd = _datetime_to_jd(obs.datetime)
                star_name = obj.name if obj else 'Unknown'

                csrf = _aavso_get_form_csrf(aavso_session)
                if not csrf:
                    submitted_results.append({'obs_id': obs_id, 'star_name': star_name, 'success': False, 'msg': 'Could not get form'})
                    continue

                submit_data = {
                    'obstype': _map_obstype_to_aavso(aavso.get('Method', '')),
                    'magnitude': aavso.get('Magnitude', ''),
                    'uncertainty': aavso.get('Uncertainty', ''),
                    'chart': aavso.get('Chart', ''),
                    'comp1': aavso.get('Comp1', ''),
                    'comp2': aavso.get('Comp2', '') or aavso.get('Check', ''),
                    'band': _map_band_to_aavso(aavso.get('Band', '')),
                    'comments': '',
                }

                obs_datetime_str = obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else ''
                success, result_msg = _submit_obs_to_aavso(aavso_session, csrf, star_name, obs_datetime_str, submit_data)
                submitted_results.append({
                    'obs_id': obs_id,
                    'star_name': star_name,
                    'date': obs.datetime.strftime('%Y-%m-%d') if obs.datetime else '',
                    'success': success,
                    'msg': result_msg,
                })

            successes = sum(1 for r in submitted_results if r['success'])
            failures = len(submitted_results) - successes
            if successes:
                flash(f'Successfully submitted {successes} observation(s) to AAVSO!', 'success')
            if failures:
                flash(f'{failures} observation(s) failed to submit.', 'danger')
            step = 'results'

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return render_template('aavso/submit.html',
                         varstar_objects=varstar_objects if 'varstar_objects' in dir() else [],
                         preview_data=preview_data,
                         submitted_results=submitted_results,
                         step=step)


# ============================================================================
# BACKUP / EXPORT / IMPORT / RESTORE
# ============================================================================

def _serialize_datetime(dt):
    """Convert datetime to ISO string or None."""
    return dt.isoformat() if dt else None


def _build_backup_data():
    """Collect all user data into a serializable dict."""
    data = {
        'version': 3,
        'exported_at': datetime.utcnow().isoformat(),
        'user_settings': {
            'email': current_user.email,
            'postal_address': current_user.postal_address,
            'aavso_code': current_user.aavso_code,
            'icq_code': current_user.icq_code,
            'default_timezone': current_user.default_timezone,
            'cobs_username': current_user.cobs_username,
            'cobs_password': current_user.cobs_password,
            'aavso_email': current_user.aavso_email,
            'aavso_password': current_user.aavso_password,
            'backup_auto_enabled': current_user.backup_auto_enabled,
            'backup_auto_interval': current_user.backup_auto_interval,
        },
        'types': [],
        'properties': [],
        'places': [],
        'instruments': [],
        'objects': [],
        'sessions': [],
        'observations': [],
        'plans': [],
    }

    for t in Type.query.all():
        data['types'].append({'id': t.id, 'name': t.name})

    for p in Property.query.all():
        data['properties'].append({'id': p.id, 'name': p.name, 'valueType': p.valueType})

    for p in Place.query.all():
        data['places'].append({
            'id': p.id, 'name': p.name, 'alias': p.alias,
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

    for pl in Plan.query.all():
        data['plans'].append({
            'id': pl.id, 'name': pl.name,
            'star_ids': pl.star_ids,
            'place_id': pl.place_id,
            'instrument_id': pl.instrument_id,
            'session_id': pl.session_id,
            'created_at': _serialize_datetime(pl.created_at),
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


def _restore_user_settings(settings):
    """Apply backed-up user_settings dict to the currently logged-in user."""
    if not settings or not isinstance(settings, dict):
        return
    fields = [
        'email', 'postal_address', 'aavso_code', 'icq_code',
        'default_timezone', 'cobs_username', 'cobs_password',
        'aavso_email', 'aavso_password',
        'backup_auto_enabled', 'backup_auto_interval',
    ]
    for field in fields:
        if field in settings:
            setattr(current_user, field, settings[field])


def _import_backup_data(data, mode='merge', restore_settings=False):
    """Import data from a backup dict.

    mode='merge'           - skip records whose id already exists
    mode='restore'         - wipe all tables first, then insert everything
    restore_settings=True  - also apply user_settings to current_user
    """
    stats = {'added': {}, 'skipped': {}, 'settings_restored': False}

    if mode == 'restore':
        Plan.query.delete()
        Observation.query.delete()
        Session.query.delete()
        Object.query.delete()
        Instrument.query.delete()
        Place.query.delete()
        Property.query.delete()
        Type.query.delete()
        db.session.flush()

    table_configs = [
        ('types', Type, lambda r: Type(id=r['id'], name=r['name'])),
        ('properties', Property, lambda r: Property(id=r['id'], name=r['name'], valueType=r.get('valueType'))),
        ('places', Place, lambda r: Place(
            id=r['id'], name=r['name'], alias=r.get('alias'),
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
        ('plans', Plan, lambda r: Plan(
            id=r['id'], name=r.get('name'),
            star_ids=r.get('star_ids'),
            place_id=r.get('place_id'),
            instrument_id=r.get('instrument_id'),
            session_id=r.get('session_id'),
            created_at=_parse_datetime(r.get('created_at')),
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

    if restore_settings and 'user_settings' in data:
        _restore_user_settings(data['user_settings'])
        stats['settings_restored'] = True

    db.session.commit()
    return stats


@web.route('/backup')
@login_required
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
            'plans': Plan.query.count(),
        }
    except Exception as e:
        flash(f'Error loading counts: {str(e)}', 'danger')
    # Start scheduler lazily on first visit
    _start_auto_backup_scheduler(current_app._get_current_object())
    local_backups = _list_local_backups()
    return render_template('backup/index.html', counts=counts, local_backups=local_backups)


@web.route('/backup/export', methods=['POST'])
@login_required
def backup_export():
    """Export all data as a downloadable file, optionally encrypted."""
    try:
        password = request.form.get('export_password', '').strip()
        also_save = bool(request.form.get('also_save_local'))
        data = _build_backup_data()
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

        if password:
            file_bytes = _encrypt_backup(json_str, password)
            filename = f'astronomy_backup_{timestamp}.astroenc'
            mimetype = 'application/octet-stream'
        else:
            file_bytes = json_str.encode('utf-8')
            filename = f'astronomy_backup_{timestamp}.json'
            mimetype = 'application/json'

        if also_save:
            _save_local_backup(json_str, password=password or None, prefix='manual')

        return Response(
            file_bytes,
            mimetype=mimetype,
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'danger')
        return redirect(url_for('web.backup_page'))


def _load_backup_file(file, password):
    """Read and optionally decrypt an uploaded backup file. Returns parsed dict."""
    raw = file.read()
    if _is_encrypted_backup(raw):
        if not password:
            raise ValueError('This backup file is password-protected. Please enter the password.')
        json_str = _decrypt_backup(raw, password)
    else:
        json_str = raw.decode('utf-8')
    data = json.loads(json_str)
    if not isinstance(data, dict) or 'version' not in data:
        raise ValueError('Invalid backup file format.')
    return data


@web.route('/backup/import', methods=['POST'])
@login_required
def backup_import():
    """Import (merge) data from an uploaded backup file. Existing records are kept."""
    try:
        file = request.files.get('backup_file')
        if not file or file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(url_for('web.backup_page'))
        password = request.form.get('import_password', '').strip()
        restore_settings = bool(request.form.get('restore_user_settings'))
        data = _load_backup_file(file, password)
        stats = _import_backup_data(data, mode='merge', restore_settings=restore_settings)
        total_added = sum(stats['added'].values())
        total_skipped = sum(stats['skipped'].values())
        msg = f'Import complete! Added {total_added} records, skipped {total_skipped} existing.'
        if stats.get('settings_restored'):
            msg += ' Profile & account settings restored.'
        flash(msg, 'success')
    except (json.JSONDecodeError, UnicodeDecodeError):
        flash('File is not valid JSON or is corrupted.', 'danger')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error importing data: {str(e)}', 'danger')
    return redirect(url_for('web.backup_page'))


@web.route('/backup/restore', methods=['POST'])
@login_required
def backup_restore():
    """Restore data from an uploaded backup file. WARNING: replaces all existing data."""
    try:
        file = request.files.get('backup_file')
        if not file or file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(url_for('web.backup_page'))
        password = request.form.get('restore_password', '').strip()
        data = _load_backup_file(file, password)
        stats = _import_backup_data(data, mode='restore', restore_settings=True)
        total_added = sum(stats['added'].values())
        msg = f'Restore complete! All previous data replaced. Loaded {total_added} records.'
        if stats.get('settings_restored'):
            msg += ' Profile & account settings restored.'
        flash(msg, 'success')
    except (json.JSONDecodeError, UnicodeDecodeError):
        flash('File is not valid JSON or is corrupted.', 'danger')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error restoring data: {str(e)}', 'danger')
    return redirect(url_for('web.backup_page'))


@web.route('/backup/save-local', methods=['POST'])
@login_required
def backup_save_local():
    """Save a backup directly to the internal storage directory."""
    try:
        password = request.form.get('save_password', '').strip() or current_user.backup_password or None
        data = _build_backup_data()
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        filename = _save_local_backup(json_str, password=password, prefix='manual')
        flash(f'Backup saved to internal storage: {filename}', 'success')
    except Exception as e:
        flash(f'Error saving backup: {str(e)}', 'danger')
    return redirect(url_for('web.backup_page'))


@web.route('/backup/local/download/<path:filename>')
@login_required
def backup_local_download(filename):
    """Download a backup file from internal storage."""
    import re as _re_fn
    if not _re_fn.match(r'^astronomy_[\\w]+\\.(?:json|astroenc)$', filename):
        flash('Invalid filename.', 'danger')
        return redirect(url_for('web.backup_page'))
    path = os.path.join(BACKUP_DIR, filename)
    if not os.path.isfile(path):
        flash('Backup file not found.', 'danger')
        return redirect(url_for('web.backup_page'))
    with open(path, 'rb') as fh:
        data = fh.read()
    mimetype = 'application/json' if filename.endswith('.json') else 'application/octet-stream'
    return Response(data, mimetype=mimetype,
                    headers={'Content-Disposition': f'attachment; filename={filename}'})


@web.route('/backup/local/delete/<path:filename>', methods=['POST'])
@login_required
def backup_local_delete(filename):
    """Delete a backup file from internal storage."""
    import re as _re_fn
    if not _re_fn.match(r'^astronomy_[\\w]+\\.(?:json|astroenc)$', filename):
        flash('Invalid filename.', 'danger')
        return redirect(url_for('web.backup_page'))
    path = os.path.join(BACKUP_DIR, filename)
    try:
        os.remove(path)
        flash(f'Deleted: {filename}', 'success')
    except FileNotFoundError:
        flash('File not found.', 'warning')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'danger')
    return redirect(url_for('web.backup_page'))


@web.route('/backup/auto/run', methods=['POST'])
@login_required
def backup_auto_run():
    """Manually trigger an auto-backup to internal storage."""
    try:
        pw = current_user.backup_password or None
        data = _build_backup_data()
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        filename = _save_local_backup(json_str, password=pw, prefix='auto')
        current_user.backup_last_auto = datetime.utcnow()
        db.session.commit()
        flash(f'Auto-backup created: {filename}', 'success')
    except Exception as e:
        flash(f'Error running auto-backup: {str(e)}', 'danger')
    return redirect(url_for('web.backup_page'))
'''
    
    with open('web_routes.py', 'w') as f:
        f.write(content)
    
    print("Created new web_routes.py with proper ID handling!")
    return True

if __name__ == '__main__':
    create_new_web_routes()