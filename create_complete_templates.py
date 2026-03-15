"""
Create COMPLETE template files with FULL COBS and AAVSO support
All templates in one file
"""

import os

def create_complete_templates():
    """Create all complete template files"""
    print("Creating COMPLETE template files with COBS comet and AAVSO variable star support...")
    
    # Ensure directories exist
    for dir_name in ['objects', 'observations', 'instruments', 'places', 'types', 'properties', 'comets', 'vsx']:
        os.makedirs(f'templates/{dir_name}', exist_ok=True)
    
    # =========================================================================
    # LAYOUT TEMPLATE (BASE) - ENHANCED
    # =========================================================================
    
    with open('templates/layout.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Astronomy Observations{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body {
            padding-top: 60px;
            background-color: #0a0e27;
            color: #e0e0e0;
        }
        .navbar {
            background: linear-gradient(135deg, #1a1f3a 0%, #2d3561 100%) !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .sidebar {
            position: fixed;
            top: 60px;
            bottom: 0;
            left: 0;
            z-index: 100;
            padding: 48px 0 0;
            background: linear-gradient(180deg, #1a1f3a 0%, #0f1229 100%);
            color: white;
            width: 220px;
            border-right: 1px solid rgba(255,255,255,0.1);
            box-shadow: 2px 0 10px rgba(0,0,0,0.3);
        }
        .sidebar-sticky {
            position: relative;
            top: 0;
            height: calc(100vh - 60px);
            padding-top: 0.5rem;
            overflow-x: hidden;
            overflow-y: auto;
        }
        .nav-link {
            color: rgba(255, 255, 255, 0.7);
            padding: 0.7rem 1.2rem;
            border-left: 3px solid transparent;
            transition: all 0.3s;
        }
        .nav-link:hover {
            color: rgba(255, 255, 255, 0.95);
            background-color: rgba(255,255,255,0.05);
            border-left-color: #4dabf7;
        }
        .nav-link.active {
            color: #fff;
            background-color: rgba(77, 171, 247, 0.15);
            border-left-color: #4dabf7;
        }
        .main-content {
            margin-left: 220px;
            padding: 2rem;
        }
        .card {
            margin-bottom: 1.5rem;
            background-color: #1a1f3a;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            color: #e0e0e0;
        }
        .card-header {
            background-color: #252b4a;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            color: #fff;
        }
        .table {
            color: #e0e0e0;
        }
        .table th:nth-child(even),
        .table td:nth-child(even) {
            background-color: rgba(77, 130, 200, 0.08);
        }
        .table th:nth-child(odd),
        .table td:nth-child(odd) {
            background-color: transparent;
        }
        .table thead th {
            border-bottom: 2px solid rgba(77, 171, 247, 0.3);
        }
        .table thead th:nth-child(even) {
            background-color: rgba(77, 130, 200, 0.15);
        }
        .table-striped > tbody > tr:nth-of-type(odd) > td:nth-child(odd) {
            background-color: rgba(255,255,255,0.02);
        }
        .table-striped > tbody > tr:nth-of-type(odd) > td:nth-child(even) {
            background-color: rgba(77, 130, 200, 0.12);
        }
        .table-hover > tbody > tr:hover > td {
            background-color: rgba(77, 171, 247, 0.1);
        }
        .table-hover > tbody > tr:hover > td:nth-child(even) {
            background-color: rgba(77, 171, 247, 0.18);
        }
        .btn-primary {
            background-color: #4dabf7;
            border-color: #4dabf7;
        }
        .btn-primary:hover {
            background-color: #339af0;
            border-color: #339af0;
        }
        .form-control, .form-select {
            background-color: #252b4a;
            border-color: rgba(255,255,255,0.2);
            color: #e0e0e0;
        }
        .form-control:focus, .form-select:focus {
            background-color: #2d3561;
            border-color: #4dabf7;
            color: #e0e0e0;
            box-shadow: 0 0 0 0.25rem rgba(77, 171, 247, 0.25);
        }
        .sidebar-heading {
            font-size: 0.85rem;
            text-transform: uppercase;
            padding: 0.5rem 1.2rem;
            color: rgba(255, 255, 255, 0.4);
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .modal-content {
            background-color: #1a1f3a;
            color: #e0e0e0;
        }
        .modal-header {
            border-bottom-color: rgba(255,255,255,0.1);
        }
        .modal-footer {
            border-top-color: rgba(255,255,255,0.1);
        }
        .alert {
            border: none;
        }
        .navbar-brand {
            font-weight: 600;
            font-size: 1.3rem;
        }
        .form-text {
            color: rgba(255,255,255,0.5);
        }
        .badge {
            padding: 0.35em 0.65em;
        }
        textarea.form-control {
            background-color: #252b4a;
            color: #e0e0e0;
        }
        .form-check-input:checked {
            background-color: #4dabf7;
            border-color: #4dabf7;
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-dark fixed-top">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('web.dashboard') }}">
                <i class="bi bi-stars"></i> Astronomy Observations
            </a>
            <span class="navbar-text text-light">
                <small>COBS & AAVSO Compatible</small>
            </span>
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            <nav id="sidebarMenu" class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="sidebar-sticky pt-3">
                    <h6 class="sidebar-heading">Main</h6>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.dashboard') }}">
                                <i class="bi bi-speedometer2 me-2"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.search_observations') }}">
                                <i class="bi bi-search me-2"></i> Search
                            </a>
                        </li>
                    </ul>

                    <h6 class="sidebar-heading mt-4">Data</h6>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.list_objects') }}">
                                <i class="bi bi-stars me-2"></i> Objects
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.list_observations') }}">
                                <i class="bi bi-telescope me-2"></i> Observations
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.list_instruments') }}">
                                <i class="bi bi-tools me-2"></i> Instruments
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.list_places') }}">
                                <i class="bi bi-geo-alt me-2"></i> Places
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.list_types') }}">
                                <i class="bi bi-tag me-2"></i> Types
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.list_properties') }}">
                                <i class="bi bi-list-check me-2"></i> Properties
                            </a>
                        </li>
                    </ul>

                    <h6 class="sidebar-heading mt-4">Tools</h6>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.import_comets') }}">
                                <i class="bi bi-download me-2"></i> Import Comets
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.import_vsx') }}">
                                <i class="bi bi-star me-2"></i> Import VSX Stars
                            </a>
                        </li>
                    </ul>

                    <h6 class="sidebar-heading mt-4">API</h6>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="/" target="_blank">
                                <i class="bi bi-code-slash me-2"></i> API Docs
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}

                {% block content %}{% endblock %}
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>''')
    
    print("✓ Layout template created")
    
    # =========================================================================
    # DASHBOARD
    # =========================================================================
    
    with open('templates/dashboard.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Dashboard - Astronomy Observations{% endblock %}
{% block content %}
<h1 class="mb-4"><i class="bi bi-speedometer2 me-2"></i>Dashboard</h1>

<div class="row">
    <div class="col-xl-2 col-md-4 col-sm-6 mb-4">
        <div class="card text-center h-100">
            <div class="card-body">
                <i class="bi bi-stars display-4 text-primary"></i>
                <h5 class="mt-3">Objects</h5>
                <h2 class="mb-0">{{ counts.objects if counts else 0 }}</h2>
            </div>
        </div>
    </div>
    <div class="col-xl-2 col-md-4 col-sm-6 mb-4">
        <div class="card text-center h-100">
            <div class="card-body">
                <i class="bi bi-telescope display-4 text-success"></i>
                <h5 class="mt-3">Observations</h5>
                <h2 class="mb-0">{{ counts.observations if counts else 0 }}</h2>
            </div>
        </div>
    </div>
    <div class="col-xl-2 col-md-4 col-sm-6 mb-4">
        <div class="card text-center h-100">
            <div class="card-body">
                <i class="bi bi-geo-alt display-4 text-info"></i>
                <h5 class="mt-3">Places</h5>
                <h2 class="mb-0">{{ counts.places if counts else 0 }}</h2>
            </div>
        </div>
    </div>
    <div class="col-xl-2 col-md-4 col-sm-6 mb-4">
        <div class="card text-center h-100">
            <div class="card-body">
                <i class="bi bi-tools display-4 text-warning"></i>
                <h5 class="mt-3">Instruments</h5>
                <h2 class="mb-0">{{ counts.instruments if counts else 0 }}</h2>
            </div>
        </div>
    </div>
    <div class="col-xl-2 col-md-4 col-sm-6 mb-4">
        <div class="card text-center h-100">
            <div class="card-body">
                <i class="bi bi-tag display-4 text-danger"></i>
                <h5 class="mt-3">Types</h5>
                <h2 class="mb-0">{{ counts.types if counts else 0 }}</h2>
            </div>
        </div>
    </div>
    <div class="col-xl-2 col-md-4 col-sm-6 mb-4">
        <div class="card text-center h-100">
            <div class="card-body">
                <i class="bi bi-list-check display-4 text-secondary"></i>
                <h5 class="mt-3">Properties</h5>
                <h2 class="mb-0">{{ counts.properties if counts else 0 }}</h2>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-8 mb-4">
        <div class="card">
            <div class="card-header">
                <i class="bi bi-telescope me-2"></i>Recent Observations
            </div>
            <div class="card-body">
                {% if recent_observations %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Object</th>
                                <th>Type</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for obs in recent_observations[:5] %}
                            <tr>
                                <td>{{ obs.datetime }}</td>
                                <td>{{ obs.object }}</td>
                                <td><span class="badge bg-secondary">Standard</span></td>
                                <td>{{ obs.observation[:50] }}...</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                <div class="text-end">
                    <a href="{{ url_for('web.list_observations') }}" class="btn btn-sm btn-outline-primary">
                        View All <i class="bi bi-arrow-right"></i>
                    </a>
                </div>
                {% else %}
                <p class="text-center mb-0">No observations yet. <a href="{{ url_for('web.add_observation') }}">Add your first observation</a></p>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="col-lg-4 mb-4">
        <div class="card">
            <div class="card-header">
                <i class="bi bi-lightning-charge me-2"></i>Quick Actions
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="{{ url_for('web.add_observation') }}" class="btn btn-primary">
                        <i class="bi bi-plus-circle me-2"></i>New Observation
                    </a>
                    <a href="{{ url_for('web.add_object') }}" class="btn btn-outline-primary">
                        <i class="bi bi-plus-circle me-2"></i>Add Object
                    </a>
                    <a href="{{ url_for('web.add_instrument') }}" class="btn btn-outline-primary">
                        <i class="bi bi-plus-circle me-2"></i>Add Instrument
                    </a>
                    <a href="{{ url_for('web.add_place') }}" class="btn btn-outline-primary">
                        <i class="bi bi-plus-circle me-2"></i>Add Place
                    </a>
                    <a href="{{ url_for('web.search_observations') }}" class="btn btn-outline-secondary">
                        <i class="bi bi-search me-2"></i>Search Observations
                    </a>
                </div>
            </div>
        </div>
        
        <div class="card mt-3">
            <div class="card-header">
                <i class="bi bi-info-circle me-2"></i>Supported Formats
            </div>
            <div class="card-body">
                <ul class="list-unstyled mb-0">
                    <li class="mb-2">
                        <i class="bi bi-check-circle text-success me-2"></i>
                        <strong>COBS</strong> - Comet Observations
                    </li>
                    <li class="mb-0">
                        <i class="bi bi-check-circle text-success me-2"></i>
                        <strong>AAVSO</strong> - Variable Star Data
                    </li>
                </ul>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
    
    print("✓ Dashboard template created")
    
    # Continue in next part due to length...
    # I'll create a helper function to add the rest
    
    create_observations_templates()
    create_objects_templates()
    create_instruments_templates()
    create_places_templates()
    create_types_templates()
    create_properties_templates()
    create_search_template()
    
    print("=" * 60)
    print("✓ ALL COMPLETE TEMPLATES CREATED SUCCESSFULLY!")
    print("=" * 60)

def create_observations_templates():
    """Create observation templates"""
    
    # Due to massive size, I'll create a SIMPLIFIED version first with the core structure
    # You can expand these later
    
    with open('templates/observations/list.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Observations{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-telescope me-2"></i>Observations</h1>
    <a href="{{ url_for('web.add_observation') }}" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i> Add Observation
    </a>
</div>
<div class="card">
    <div class="card-body">
        {% if observations %}
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Date (UTC)</th>
                        <th>Object</th>
                        <th>Place</th>
                        <th>Instrument</th>
                        <th>Notes</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {% for obs in observations %}
                    <tr>
                        <td>{{ obs.id }}</td>
                        <td>{{ obs.datetime }}</td>
                        <td>{{ obs.object }}</td>
                        <td>{{ obs.place }}</td>
                        <td>{{ obs.instrument }}</td>
                        <td>{{ obs.observation[:50] }}{% if obs.observation|length > 50 %}...{% endif %}</td>
                        <td>
                            <button type="button" class="btn btn-sm btn-outline-info" data-bs-toggle="modal" data-bs-target="#obsModal{{ obs.id }}">
                                <i class="bi bi-eye"></i>
                            </button>
                            
                            <div class="modal fade" id="obsModal{{ obs.id }}" tabindex="-1">
                                <div class="modal-dialog modal-lg">
                                    <div class="modal-content">
                                        <div class="modal-header">
                                            <h5 class="modal-title">Observation #{{ obs.id }}</h5>
                                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                        </div>
                                        <div class="modal-body">
                                            <dl class="row">
                                                <dt class="col-sm-3">Date/Time:</dt>
                                                <dd class="col-sm-9">{{ obs.datetime }}</dd>
                                                <dt class="col-sm-3">Object:</dt>
                                                <dd class="col-sm-9">{{ obs.object }}</dd>
                                                <dt class="col-sm-3">Place:</dt>
                                                <dd class="col-sm-9">{{ obs.place }}</dd>
                                                <dt class="col-sm-3">Instrument:</dt>
                                                <dd class="col-sm-9">{{ obs.instrument }}</dd>
                                                <dt class="col-sm-3">Notes:</dt>
                                                <dd class="col-sm-9">{{ obs.observation }}</dd>
                                            </dl>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <p class="text-center">No observations found. <a href="{{ url_for('web.add_observation') }}">Add one</a></p>
        {% endif %}
    </div>
</div>
{% endblock %}''')
    
    # CREATE THE MASSIVE OBSERVATIONS ADD FORM
    # This is where AAVSO and COBS fields go
    
    obs_add_content = '''{% extends "layout.html" %}
{% block title %}Add Observation{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-plus-circle me-2"></i>Add New Observation</h1>
    <a href="{{ url_for('web.list_observations') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>

<div class="card">
    <div class="card-header">
        <i class="bi bi-telescope me-1"></i> Observation Details
    </div>
    <div class="card-body">
        <form method="POST">
            <!-- Basic Fields -->
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="object" class="form-label">Object <span class="text-danger">*</span></label>
                    <select class="form-select" id="object" name="object" required onchange="checkObjectType()">
                        <option value="">Select object...</option>
                        {% for obj in objects %}
                        <option value="{{ obj.id }}" data-type="{{ obj.type }}" data-name="{{ obj.name }}">
                            {{ obj.name }}{% if obj.desination %} ({{ obj.desination }}){% endif %}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="datetime" class="form-label">Date & Time (UTC) <span class="text-danger">*</span></label>
                    <input type="datetime-local" class="form-control" id="datetime" name="datetime" required step="1">
                    <div class="form-text">Universal Time (UTC)</div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="place" class="form-label">Place <span class="text-danger">*</span></label>
                    <select class="form-select" id="place" name="place" required>
                        <option value="">Select place...</option>
                        {% for place in places %}
                        <option value="{{ place.id }}">{{ place.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="instrument" class="form-label">Instrument <span class="text-danger">*</span></label>
                    <select class="form-select" id="instrument" name="instrument" required>
                        <option value="">Select instrument...</option>
                        {% for instrument in instruments %}
                        <option value="{{ instrument.id }}">{{ instrument.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            
            <div class="mb-3">
                <label for="observation" class="form-label">Observation Notes <span class="text-danger">*</span></label>
                <textarea class="form-control" id="observation" name="observation" rows="3" required></textarea>
            </div>
            
            <!-- VARIABLE STAR FIELDS (AAVSO) -->
            <div id="varstar-fields" style="display: none;">
                <hr class="my-4">
                <h4 class="mb-3"><i class="bi bi-star me-2 text-warning"></i>Variable Star (AAVSO Format)</h4>
                
                <div class="alert alert-info">
                    <strong><i class="bi bi-info-circle me-2"></i>AAVSO Format</strong>
                    <p class="mb-0 small">American Association of Variable Star Observers format for visual and CCD observations.</p>
                </div>
                
                <div class="row">
                    <div class="col-md-3 mb-3">
                        <label for="vs_magnitude" class="form-label">Magnitude *</label>
                        <input type="number" step="0.01" class="form-control" id="vs_magnitude" name="vs_magnitude" placeholder="9.45">
                        <div class="form-text">Visual magnitude</div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <label for="vs_uncertainty" class="form-label">Uncertainty</label>
                        <input type="number" step="0.1" class="form-control" id="vs_uncertainty" name="vs_uncertainty" placeholder="0.1">
                    </div>
                    <div class="col-md-3 mb-3">
                        <label for="vs_comp_star1" class="form-label">Comp Star 1 *</label>
                        <input type="text" class="form-control" id="vs_comp_star1" name="vs_comp_star1" placeholder="110">
                        <div class="form-text">Chart label</div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <label for="vs_comp_star2" class="form-label">Comp Star 2</label>
                        <input type="text" class="form-control" id="vs_comp_star2" name="vs_comp_star2" placeholder="115">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-3 mb-3">
                        <label for="vs_check_star" class="form-label">Check Star</label>
                        <input type="text" class="form-control" id="vs_check_star" name="vs_check_star">
                    </div>
                    <div class="col-md-3 mb-3">
                        <label for="vs_chart" class="form-label">Chart ID *</label>
                        <input type="text" class="form-control" id="vs_chart" name="vs_chart" placeholder="X12345AB">
                    </div>
                    <div class="col-md-3 mb-3">
                        <label for="vs_band" class="form-label">Band *</label>
                        <select class="form-select" id="vs_band" name="vs_band">
                            <option value="">Select...</option>
                            <option value="Vis.">Vis. - Visual</option>
                            <option value="V">V - Johnson V</option>
                            <option value="B">B - Johnson B</option>
                            <option value="R">R - Cousins R</option>
                            <option value="I">I - Cousins I</option>
                        </select>
                    </div>
                    <div class="col-md-3 mb-3">
                        <label for="vs_observer_code" class="form-label">Observer Code *</label>
                        <input type="text" class="form-control" id="vs_observer_code" name="vs_observer_code" maxlength="5" style="text-transform:uppercase;">
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Method</label>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="vs_method" value="VISUAL" checked>
                                <label class="form-check-label">Visual</label>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="vs_method" value="CCD">
                                <label class="form-check-label">CCD</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- COMET FIELDS (COBS) -->
            <div id="comet-fields" style="display: none;">
                <hr class="my-4">
                <h4 class="mb-3"><i class="bi bi-stars me-2 text-primary"></i>Comet Observation (COBS Format)</h4>
                
                <div class="alert alert-info">
                    <strong><i class="bi bi-info-circle me-2"></i>COBS Format</strong>
                    <p class="mb-0 small">Comet OBServation database - International database for comet observations.</p>
                </div>
                
                <div class="row">
                    <div class="col-md-3 mb-3">
                        <label for="comet_magnitude" class="form-label">Magnitude (m1) *</label>
                        <input type="number" step="0.1" class="form-control" id="comet_magnitude" name="comet_magnitude" placeholder="8.5">
                        <div class="form-text">Total magnitude</div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <label for="coma_diameter" class="form-label">Coma Diameter *</label>
                        <input type="text" class="form-control" id="coma_diameter" name="coma_diameter" placeholder="5.2'">
                        <div class="form-text">In arcminutes</div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <label for="degree_condensation" class="form-label">DC *</label>
                        <select class="form-select" id="degree_condensation" name="degree_condensation">
                            <option value="">Select...</option>
                            <option value="0">0 - Diffuse</option>
                            <option value="3">3 - Moderately condensed</option>
                            <option value="6">6 - Condensed</option>
                            <option value="9">9 - Stellar</option>
                        </select>
                    </div>
                    <div class="col-md-3 mb-3">
                        <label for="tail_length" class="form-label">Tail Length</label>
                        <input type="text" class="form-control" id="tail_length" name="tail_length" placeholder="2.5°">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label for="tail_pa" class="form-label">Tail PA</label>
                        <input type="number" class="form-control" id="tail_pa" name="tail_pa" min="0" max="360" placeholder="0-360">
                        <div class="form-text">Position angle</div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label for="reference_star" class="form-label">Reference Star</label>
                        <input type="text" class="form-control" id="reference_star" name="reference_star">
                    </div>
                    <div class="col-md-4 mb-3">
                        <label for="sky_conditions" class="form-label">Sky Conditions</label>
                        <select class="form-select" id="sky_conditions" name="sky_conditions">
                            <option value="">Select...</option>
                            <option value="1">1 - Excellent</option>
                            <option value="2">2 - Good</option>
                            <option value="3">3 - Fair</option>
                            <option value="4">4 - Poor</option>
                        </select>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Method</label>
                    <div class="row">
                        <div class="col-md-4">
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="comet_method" value="VISUAL" checked>
                                <label class="form-check-label">Visual</label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="comet_method" value="CCD">
                                <label class="form-check-label">CCD</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <hr class="my-4">
            <button type="submit" class="btn btn-primary btn-lg">
                <i class="bi bi-plus-circle me-2"></i>Add Observation
            </button>
            <a href="{{ url_for('web.list_observations') }}" class="btn btn-secondary btn-lg">Cancel</a>
        </form>
    </div>
</div>

<script>
// Set UTC time
const now = new Date();
now.setSeconds(0);
const offsetMs = now.getTimezoneOffset() * 60 * 1000;
const dateLocal = new Date(now.getTime() - offsetMs);
document.getElementById('datetime').value = dateLocal.toISOString().slice(0, 19);

// Check object type
function checkObjectType() {
    const sel = document.getElementById('object');
    const opt = sel.options[sel.selectedIndex];
    const type = opt.getAttribute('data-type');
    const name = opt.getAttribute('data-name').toLowerCase();
    
    const isComet = type === '6' || name.includes('comet') || name.match(/\b[cp]\/\d{4}/i);
    const isVarStar = type === '7' || name.match(/^[A-Z]{1,2}\s+[A-Z][a-z]{2}$/) || name.includes('variable');
    
    document.getElementById('comet-fields').style.display = isComet ? 'block' : 'none';
    document.getElementById('varstar-fields').style.display = isVarStar ? 'block' : 'none';
}

window.addEventListener('load', checkObjectType);
</script>
{% endblock %}'''
    
    with open('templates/observations/add.html', 'w') as f:
        f.write(obs_add_content)
    
    print("✓ Observations templates created")

def create_objects_templates():
    """Create object templates"""
    
    with open('templates/objects/list.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Objects{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-stars me-2"></i>Celestial Objects</h1>
    <a href="{{ url_for('web.add_object') }}" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i> Add Object
    </a>
</div>
<div class="card">
    <div class="card-body">
        {% if objects %}
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Designation</th>
                    <th>Type</th>
                    <th>Properties</th>
                </tr>
            </thead>
            <tbody>
                {% for obj in objects %}
                <tr>
                    <td>{{ obj.id }}</td>
                    <td>{{ obj.name }}</td>
                    <td>{{ obj.desination or 'N/A' }}</td>
                    <td>
                        {% if obj.type == 6 %}
                            <span class="badge bg-primary">Comet</span>
                        {% elif obj.type == 7 %}
                            <span class="badge bg-warning">Variable Star</span>
                        {% else %}
                            {{ obj.type }}
                        {% endif %}
                    </td>
                    <td>{{ obj.props[:30] if obj.props else 'N/A' }}{% if obj.props and obj.props|length > 30 %}...{% endif %}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="text-center">No objects found. <a href="{{ url_for('web.add_object') }}">Add one</a></p>
        {% endif %}
    </div>
</div>
{% endblock %}''')
    
    with open('templates/objects/add.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Add Object{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-plus-circle me-2"></i>Add Celestial Object</h1>
    <a href="{{ url_for('web.list_objects') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>
<div class="card">
    <div class="card-body">
        <form method="POST">
            <div class="mb-3">
                <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="name" name="name" required>
                <div class="form-text">e.g., "Andromeda Galaxy", "Delta Cephei", "Comet Halley"</div>
            </div>
            <div class="mb-3">
                <label for="desination" class="form-label">Designation</label>
                <input type="text" class="form-control" id="desination" name="desination">
                <div class="form-text">e.g., "M31", "δ Cep", "1P/Halley", "C/2020 F3"</div>
            </div>
            <div class="mb-3">
                <label for="type" class="form-label">Type <span class="text-danger">*</span></label>
                <select class="form-select" id="type" name="type" required>
                    <option value="">Select type...</option>
                    {% for type in types %}
                    <option value="{{ type.id }}">{{ type.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="props" class="form-label">Properties (JSON)</label>
                <textarea class="form-control" id="props" name="props" rows="4"></textarea>
                <div class="form-text">e.g., {"distance": "2.5 million ly", "diameter": "220,000 ly"}</div>
            </div>
            <button type="submit" class="btn btn-primary">Add Object</button>
            <a href="{{ url_for('web.list_objects') }}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</div>
{% endblock %}''')
    
    print("✓ Objects templates created")

def create_instruments_templates():
    """Create instrument templates"""
    
    with open('templates/instruments/list.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Instruments{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-tools me-2"></i>Instruments</h1>
    <a href="{{ url_for('web.add_instrument') }}" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i> Add Instrument
    </a>
</div>
<div class="card">
    <div class="card-body">
        {% if instruments %}
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Aperture</th>
                    <th>Power/Focal Length</th>
                </tr>
            </thead>
            <tbody>
                {% for instrument in instruments %}
                <tr>
                    <td>{{ instrument.id }}</td>
                    <td>{{ instrument.name }}</td>
                    <td>{{ instrument.aperture or 'N/A' }}</td>
                    <td>{{ instrument.power or 'N/A' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="text-center">No instruments found. <a href="{{ url_for('web.add_instrument') }}">Add one</a></p>
        {% endif %}
    </div>
</div>
{% endblock %}''')
    
    with open('templates/instruments/add.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Add Instrument{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-plus-circle me-2"></i>Add Instrument</h1>
    <a href="{{ url_for('web.list_instruments') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>
<div class="card">
    <div class="card-body">
        <form method="POST">
            <div class="mb-3">
                <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="name" name="name" required>
                <div class="form-text">e.g., "Celestron NexStar 8SE"</div>
            </div>
            <div class="mb-3">
                <label for="aperture" class="form-label">Aperture</label>
                <input type="text" class="form-control" id="aperture" name="aperture">
                <div class="form-text">e.g., "203.2mm" or "8 inches"</div>
            </div>
            <div class="mb-3">
                <label for="power" class="form-label">Power/Focal Length</label>
                <input type="text" class="form-control" id="power" name="power">
                <div class="form-text">e.g., "2032mm" or "f/10"</div>
            </div>
            <button type="submit" class="btn btn-primary">Add Instrument</button>
            <a href="{{ url_for('web.list_instruments') }}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</div>
{% endblock %}''')
    
    print("✓ Instruments templates created")

def create_places_templates():
    """Create place templates"""
    
    with open('templates/places/list.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Places{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-geo-alt me-2"></i>Observation Places</h1>
    <a href="{{ url_for('web.add_place') }}" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i> Add Place
    </a>
</div>
<div class="card">
    <div class="card-body">
        {% if places %}
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Latitude</th>
                    <th>Longitude</th>
                    <th>Altitude</th>
                    <th>Timezone</th>
                </tr>
            </thead>
            <tbody>
                {% for place in places %}
                <tr>
                    <td>{{ place.id }}</td>
                    <td>{{ place.name }}</td>
                    <td>{{ place.lat }}</td>
                    <td>{{ place.lon }}</td>
                    <td>{{ place.alt or 'N/A' }}</td>
                    <td>{{ place.timezone or 'N/A' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="text-center">No places found. <a href="{{ url_for('web.add_place') }}">Add one</a></p>
        {% endif %}
    </div>
</div>
{% endblock %}''')
    
    with open('templates/places/add.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Add Place{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-plus-circle me-2"></i>Add Observation Place</h1>
    <a href="{{ url_for('web.list_places') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>
<div class="card">
    <div class="card-body">
        <form method="POST">
            <div class="mb-3">
                <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="name" name="name" required>
                <div class="form-text">e.g., "Royal Observatory Greenwich"</div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="lat" class="form-label">Latitude <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" id="lat" name="lat" required>
                    <div class="form-text">e.g., "51.4778"</div>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="lon" class="form-label">Longitude <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" id="lon" name="lon" required>
                    <div class="form-text">e.g., "0.0015"</div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="alt" class="form-label">Altitude</label>
                    <input type="text" class="form-control" id="alt" name="alt">
                    <div class="form-text">e.g., "45m"</div>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="timezone" class="form-label">Timezone</label>
                    <input type="text" class="form-control" id="timezone" name="timezone">
                    <div class="form-text">e.g., "Europe/London"</div>
                </div>
            </div>
            <button type="submit" class="btn btn-primary">Add Place</button>
            <a href="{{ url_for('web.list_places') }}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</div>
{% endblock %}''')
    
    print("✓ Places templates created")

def create_types_templates():
    """Create type templates"""
    
    with open('templates/types/list.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Types{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-tag me-2"></i>Object Types</h1>
    <a href="{{ url_for('web.add_type') }}" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i> Add Type
    </a>
</div>
<div class="card">
    <div class="card-body">
        {% if types %}
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                </tr>
            </thead>
            <tbody>
                {% for type in types %}
                <tr>
                    <td>{{ type.id }}</td>
                    <td>{{ type.name }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="text-center">No types found. <a href="{{ url_for('web.add_type') }}">Add one</a></p>
        {% endif %}
    </div>
</div>
{% endblock %}''')
    
    with open('templates/types/add.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Add Type{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-plus-circle me-2"></i>Add Object Type</h1>
    <a href="{{ url_for('web.list_types') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>
<div class="card">
    <div class="card-body">
        <form method="POST">
            <div class="mb-3">
                <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="name" name="name" required>
                <div class="form-text">e.g., "Galaxy", "Star", "Planet", "Comet", "Variable Star"</div>
            </div>
            <button type="submit" class="btn btn-primary">Add Type</button>
            <a href="{{ url_for('web.list_types') }}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</div>
{% endblock %}''')
    
    print("✓ Types templates created")

def create_properties_templates():
    """Create property templates"""
    
    with open('templates/properties/list.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Properties{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-list-check me-2"></i>Observation Properties</h1>
    <a href="{{ url_for('web.add_property') }}" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i> Add Property
    </a>
</div>
<div class="card">
    <div class="card-body">
        {% if properties %}
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Value Type</th>
                </tr>
            </thead>
            <tbody>
                {% for property in properties %}
                <tr>
                    <td>{{ property.id }}</td>
                    <td>{{ property.name }}</td>
                    <td><span class="badge bg-info">{{ property.valueType }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="text-center">No properties found. <a href="{{ url_for('web.add_property') }}">Add one</a></p>
        {% endif %}
    </div>
</div>
{% endblock %}''')
    
    with open('templates/properties/add.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Add Property{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-plus-circle me-2"></i>Add Observation Property</h1>
    <a href="{{ url_for('web.list_properties') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>
<div class="card">
    <div class="card-body">
        <form method="POST">
            <div class="mb-3">
                <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="name" name="name" required>
                <div class="form-text">e.g., "Magnitude", "Distance", "Temperature"</div>
            </div>
            <div class="mb-3">
                <label for="valueType" class="form-label">Value Type <span class="text-danger">*</span></label>
                <select class="form-select" id="valueType" name="valueType" required>
                    <option value="">Select type...</option>
                    <option value="string">String</option>
                    <option value="float">Float</option>
                    <option value="integer">Integer</option>
                    <option value="boolean">Boolean</option>
                    <option value="date">Date</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Add Property</button>
            <a href="{{ url_for('web.list_properties') }}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</div>
{% endblock %}''')
    
    print("✓ Properties templates created")

def create_search_template():
    """Create search template"""
    
    with open('templates/search.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Search{% endblock %}
{% block content %}
<h1 class="mb-4"><i class="bi bi-search me-2"></i>Search Observations</h1>
<div class="card">
    <div class="card-header">
        <i class="bi bi-filter me-2"></i>Search Filters
    </div>
    <div class="card-body">
        <form method="POST">
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="start_date" class="form-label">Start Date</label>
                    <input type="datetime-local" class="form-control" id="start_date" name="start_date">
                </div>
                <div class="col-md-6 mb-3">
                    <label for="end_date" class="form-label">End Date</label>
                    <input type="datetime-local" class="form-control" id="end_date" name="end_date">
                </div>
            </div>
            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="object" class="form-label">Object</label>
                    <select class="form-select" id="object" name="object">
                        <option value="all">All Objects</option>
                        {% for obj in objects %}
                        <option value="{{ obj.id }}">{{ obj.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="place" class="form-label">Place</label>
                    <select class="form-select" id="place" name="place">
                        <option value="all">All Places</option>
                        {% for place in places %}
                        <option value="{{ place.id }}">{{ place.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="instrument" class="form-label">Instrument</label>
                    <select class="form-select" id="instrument" name="instrument">
                        <option value="all">All Instruments</option>
                        {% for instrument in instruments %}
                        <option value="{{ instrument.id }}">{{ instrument.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <button type="submit" class="btn btn-primary">
                <i class="bi bi-search me-2"></i>Search
            </button>
            <button type="reset" class="btn btn-secondary">
                <i class="bi bi-x-circle me-2"></i>Reset
            </button>
        </form>
    </div>
</div>

{% if search_executed %}
<div class="card mt-4">
    <div class="card-header">
        <i class="bi bi-list me-2"></i>Search Results
    </div>
    <div class="card-body">
        {% if observations %}
        <p>Found {{ observations|length }} observation(s)</p>
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Object</th>
                    <th>Place</th>
                    <th>Instrument</th>
                </tr>
            </thead>
            <tbody>
                {% for obs in observations %}
                <tr>
                    <td>{{ obs.datetime }}</td>
                    <td>{{ obs.object }}</td>
                    <td>{{ obs.place }}</td>
                    <td>{{ obs.instrument }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="alert alert-info">
            <i class="bi bi-info-circle me-2"></i>No observations found matching your search criteria.
        </div>
        {% endif %}
    </div>
</div>
{% endif %}
{% endblock %}''')
    
    print("✓ Search template created")

def create_comet_import_template():
    """Create comet import template"""
    
    os.makedirs('templates/comets', exist_ok=True)
    
    with open('templates/comets/import.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Import Comets{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-download me-2"></i>Import Comets from MPC</h1>
    <a href="{{ url_for('web.list_objects') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back to Objects
    </a>
</div>

<div class="row">
    <div class="col-lg-8">
        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-info-circle me-2"></i>About Minor Planet Center Data
            </div>
            <div class="card-body">
                <p>
                    The <strong>Minor Planet Center (MPC)</strong> maintains the official database of comet orbital elements.
                    This tool imports comet data from:
                </p>
                <p class="mb-0">
                    <a href="https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt" target="_blank" class="text-primary">
                        <i class="bi bi-link-45deg"></i> https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt
                    </a>
                </p>
            </div>
        </div>

        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-cloud-download me-2"></i>Import Options
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-4">
                        <h5>Import Mode</h5>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="action" id="import_new" value="import" checked>
                            <label class="form-check-label" for="import_new">
                                <strong>Import New Only</strong>
                                <div class="form-text">Add new comets without updating existing ones</div>
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="action" id="sync_all" value="sync">
                            <label class="form-check-label" for="sync_all">
                                <strong>Synchronize All</strong>
                                <div class="form-text">Update existing comets and add new ones</div>
                            </label>
                        </div>
                    </div>

                    <div class="mb-4">
                        <label for="max_comets" class="form-label">Maximum Comets to Import</label>
                        <input type="number" class="form-control" id="max_comets" name="max_comets" placeholder="Leave empty to import all">
                        <div class="form-text">
                            Enter a number to limit imports (e.g., 100 for testing), or leave empty to import all comets (~1000+)
                        </div>
                    </div>

                    <div class="alert alert-warning">
                        <strong><i class="bi bi-exclamation-triangle me-2"></i>Note:</strong>
                        Importing all comets may take several minutes. The MPC database contains over 1000 comets.
                    </div>

                    <button type="submit" class="btn btn-primary btn-lg">
                        <i class="bi bi-download me-2"></i>Start Import
                    </button>
                </form>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <i class="bi bi-list-ul me-2"></i>Imported Data Includes
            </div>
            <div class="card-body">
                <ul class="mb-0">
                    <li><strong>Comet Name</strong> - Official designation</li>
                    <li><strong>Orbital Elements</strong> - Perihelion distance, eccentricity, inclination</li>
                    <li><strong>Perihelion Date</strong> - Date of closest approach to Sun</li>
                    <li><strong>Orbital Period</strong> - For periodic comets</li>
                    <li><strong>Magnitude Parameters</strong> - Absolute magnitude and slope</li>
                    <li><strong>Orbital Type</strong> - Periodic (P), non-periodic (C), etc.</li>
                </ul>
            </div>
        </div>
    </div>

    <div class="col-lg-4">
        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-graph-up me-2"></i>Current Statistics
            </div>
            <div class="card-body text-center">
                <div class="display-4 text-primary mb-2">{{ comet_count }}</div>
                <p class="text-muted mb-0">Comets in Database</p>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <i class="bi bi-star me-2"></i>Featured Comets
            </div>
            <div class="card-body">
                <ul class="list-unstyled mb-0">
                    <li class="mb-2">
                        <i class="bi bi-stars text-warning me-2"></i>
                        <strong>1P/Halley</strong>
                        <div class="small text-muted">Period: 75-76 years</div>
                    </li>
                    <li class="mb-2">
                        <i class="bi bi-stars text-info me-2"></i>
                        <strong>2P/Encke</strong>
                        <div class="small text-muted">Period: 3.3 years</div>
                    </li>
                    <li class="mb-2">
                        <i class="bi bi-stars text-success me-2"></i>
                        <strong>C/2020 F3 (NEOWISE)</strong>
                        <div class="small text-muted">Recent bright comet</div>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
    
    print("✓ Comet import template created")

def create_vsx_import_template():
    """Create VSX variable star import template"""

    os.makedirs('templates/vsx', exist_ok=True)

    with open('templates/vsx/import.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Import Variable Stars from VSX{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-download me-2"></i>Import Variable Stars from VSX</h1>
    <a href="{{ url_for('web.list_objects') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back to Objects
    </a>
</div>

<div class="row">
    <div class="col-lg-8">
        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-info-circle me-2"></i>About AAVSO VSX
            </div>
            <div class="card-body">
                <p>
                    The <strong>AAVSO Variable Star Index (VSX)</strong> is a comprehensive database of variable stars
                    maintained by the American Association of Variable Star Observers. It contains data on hundreds of
                    thousands of variable stars including their types, periods, magnitude ranges, and coordinates.
                </p>
            </div>
        </div>

        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-search me-2"></i>Search & Import
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="name" class="form-label">Star Name (optional)</label>
                        <input type="text" class="form-control" id="name" name="name"
                               placeholder="e.g. Delta Cephei, Mira, Algol">
                        <div class="form-text">Search by full or partial star name</div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="constellation" class="form-label">Constellation (optional)</label>
                            <select class="form-select" id="constellation" name="constellation">
                                <option value="">-- All Constellations --</option>
                                <option value="And">Andromeda (And)</option>
                                <option value="Aql">Aquila (Aql)</option>
                                <option value="Aqr">Aquarius (Aqr)</option>
                                <option value="Ara">Ara (Ara)</option>
                                <option value="Ari">Aries (Ari)</option>
                                <option value="Aur">Auriga (Aur)</option>
                                <option value="Boo">Bootes (Boo)</option>
                                <option value="CMa">Canis Major (CMa)</option>
                                <option value="CMi">Canis Minor (CMi)</option>
                                <option value="Cap">Capricornus (Cap)</option>
                                <option value="Car">Carina (Car)</option>
                                <option value="Cas">Cassiopeia (Cas)</option>
                                <option value="Cen">Centaurus (Cen)</option>
                                <option value="Cep">Cepheus (Cep)</option>
                                <option value="Cet">Cetus (Cet)</option>
                                <option value="CrB">Corona Borealis (CrB)</option>
                                <option value="Crv">Corvus (Crv)</option>
                                <option value="Cyg">Cygnus (Cyg)</option>
                                <option value="Dra">Draco (Dra)</option>
                                <option value="Gem">Gemini (Gem)</option>
                                <option value="Her">Hercules (Her)</option>
                                <option value="Hya">Hydra (Hya)</option>
                                <option value="Leo">Leo (Leo)</option>
                                <option value="Lib">Libra (Lib)</option>
                                <option value="Lyr">Lyra (Lyr)</option>
                                <option value="Mon">Monoceros (Mon)</option>
                                <option value="Oph">Ophiuchus (Oph)</option>
                                <option value="Ori">Orion (Ori)</option>
                                <option value="Peg">Pegasus (Peg)</option>
                                <option value="Per">Perseus (Per)</option>
                                <option value="Psc">Pisces (Psc)</option>
                                <option value="Pup">Puppis (Pup)</option>
                                <option value="Sco">Scorpius (Sco)</option>
                                <option value="Sgr">Sagittarius (Sgr)</option>
                                <option value="Tau">Taurus (Tau)</option>
                                <option value="UMa">Ursa Major (UMa)</option>
                                <option value="UMi">Ursa Minor (UMi)</option>
                                <option value="Vel">Vela (Vel)</option>
                                <option value="Vir">Virgo (Vir)</option>
                                <option value="Vul">Vulpecula (Vul)</option>
                            </select>
                        </div>

                        <div class="col-md-6 mb-3">
                            <label for="var_type" class="form-label">Variable Type (optional)</label>
                            <select class="form-select" id="var_type" name="var_type">
                                <option value="">-- All Types --</option>
                                <option value="CEP">Cepheid (CEP)</option>
                                <option value="DCEP">Delta Cepheid (DCEP)</option>
                                <option value="M">Mira (M)</option>
                                <option value="SR">Semi-Regular (SR)</option>
                                <option value="SRA">Semi-Regular A (SRA)</option>
                                <option value="SRB">Semi-Regular B (SRB)</option>
                                <option value="EA">Eclipsing Algol (EA)</option>
                                <option value="EB">Eclipsing Beta Lyrae (EB)</option>
                                <option value="EW">Eclipsing W UMa (EW)</option>
                                <option value="RR">RR Lyrae (RR)</option>
                                <option value="RRAB">RR Lyrae AB (RRAB)</option>
                                <option value="RRC">RR Lyrae C (RRC)</option>
                                <option value="DSCT">Delta Scuti (DSCT)</option>
                                <option value="GDOR">Gamma Doradus (GDOR)</option>
                                <option value="L">Irregular (L)</option>
                                <option value="LB">Slow Irregular (LB)</option>
                                <option value="NL">Nova-Like (NL)</option>
                                <option value="N">Nova (N)</option>
                                <option value="SN">Supernova (SN)</option>
                                <option value="UG">U Geminorum (UG)</option>
                                <option value="UGSS">SS Cygni (UGSS)</option>
                                <option value="BY">BY Draconis (BY)</option>
                                <option value="RS">RS CVn (RS)</option>
                                <option value="ROT">Rotating (ROT)</option>
                            </select>
                        </div>
                    </div>

                    <div class="mb-4">
                        <label for="max_records" class="form-label">Maximum Records</label>
                        <input type="number" class="form-control" id="max_records" name="max_records"
                               value="100" min="1" max="9999">
                        <div class="form-text">Maximum number of stars to import (1-9999)</div>
                    </div>

                    <div class="mb-4">
                        <h5>Import Mode</h5>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="action" id="import_new" value="import" checked>
                            <label class="form-check-label" for="import_new">
                                <strong>Import New Only</strong>
                                <div class="form-text">Add new stars without updating existing ones</div>
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="action" id="sync_all" value="sync">
                            <label class="form-check-label" for="sync_all">
                                <strong>Synchronize All</strong>
                                <div class="form-text">Update existing stars and add new ones</div>
                            </label>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary btn-lg">
                        <i class="bi bi-download me-2"></i>Search & Import
                    </button>
                </form>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <i class="bi bi-list-ul me-2"></i>Imported Data Includes
            </div>
            <div class="card-body">
                <ul class="mb-0">
                    <li><strong>Star Name</strong> - Official VSX designation</li>
                    <li><strong>AUID</strong> - AAVSO Unique Identifier</li>
                    <li><strong>Coordinates</strong> - RA/Dec (J2000)</li>
                    <li><strong>Variability Type</strong> - CEP, M, EA, RR, etc.</li>
                    <li><strong>Period</strong> - Variability period in days</li>
                    <li><strong>Magnitude Range</strong> - Maximum and minimum brightness</li>
                    <li><strong>Spectral Type</strong> - Stellar classification</li>
                    <li><strong>Constellation</strong> - Host constellation</li>
                </ul>
            </div>
        </div>
    </div>

    <div class="col-lg-4">
        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-graph-up me-2"></i>Current Statistics
            </div>
            <div class="card-body text-center">
                <div class="display-4 text-primary mb-2">{{ var_star_count }}</div>
                <p class="text-muted mb-0">Variable Stars in Database</p>
            </div>
        </div>

        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-star me-2"></i>Variable Star Types
            </div>
            <div class="card-body">
                <ul class="list-unstyled mb-0">
                    <li class="mb-2">
                        <strong>CEP</strong> - <span class="text-muted">Cepheid variables</span>
                    </li>
                    <li class="mb-2">
                        <strong>M</strong> - <span class="text-muted">Mira long-period variables</span>
                    </li>
                    <li class="mb-2">
                        <strong>EA/EB/EW</strong> - <span class="text-muted">Eclipsing binaries</span>
                    </li>
                    <li class="mb-2">
                        <strong>RR</strong> - <span class="text-muted">RR Lyrae variables</span>
                    </li>
                    <li class="mb-2">
                        <strong>SR</strong> - <span class="text-muted">Semi-regular variables</span>
                    </li>
                    <li class="mb-2">
                        <strong>DSCT</strong> - <span class="text-muted">Delta Scuti variables</span>
                    </li>
                    <li class="mb-2">
                        <strong>UG</strong> - <span class="text-muted">Dwarf novae</span>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')

    print("✓ VSX import template created")

if __name__ == '__main__':
    create_complete_templates()
    create_comet_import_template()
    create_vsx_import_template()