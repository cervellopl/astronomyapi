"""
Create COMPLETE template files with FULL COBS and AAVSO support
All templates in one file
"""

import os

def create_complete_templates():
    """Create all complete template files"""
    print("Creating COMPLETE template files with COBS comet and AAVSO variable star support...")
    
    # Ensure directories exist
    for dir_name in ['objects', 'observations', 'instruments', 'places', 'types', 'properties', 'comets', 'vsx', 'sessions', 'auth']:
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
            color: #e0e0e0 !important;
            --bs-table-color: #e0e0e0;
            --bs-table-striped-color: #e0e0e0;
            --bs-table-hover-color: #ffffff;
            --bs-table-bg: transparent;
            --bs-table-striped-bg: rgba(255,255,255,0.04);
            --bs-table-hover-bg: rgba(77, 171, 247, 0.15);
        }
        .table td,
        .table th {
            color: #e0e0e0 !important;
        }
        .table td:nth-child(even),
        .table th:nth-child(even) {
            color: #8ec8f0 !important;
            background-color: rgba(50, 100, 160, 0.18) !important;
        }
        .table thead th {
            border-bottom: 2px solid rgba(77, 171, 247, 0.5) !important;
            color: #ffffff !important;
        }
        .table thead th:nth-child(even) {
            background-color: rgba(50, 100, 160, 0.25) !important;
            color: #a0d4ff !important;
        }
        .table-striped > tbody > tr:nth-of-type(odd) > td {
            color: #e0e0e0 !important;
            background-color: rgba(255,255,255,0.04) !important;
        }
        .table-striped > tbody > tr:nth-of-type(odd) > td:nth-child(even) {
            color: #8ec8f0 !important;
            background-color: rgba(50, 100, 160, 0.25) !important;
        }
        .table-hover > tbody > tr:hover > td {
            color: #ffffff !important;
            background-color: rgba(77, 171, 247, 0.15) !important;
        }
        .table-hover > tbody > tr:hover > td:nth-child(even) {
            color: #b8dcff !important;
            background-color: rgba(77, 171, 247, 0.28) !important;
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
            <span class="navbar-text">
                {% if current_user.is_authenticated %}
                <a href="{{ url_for('web.user_settings') }}" class="text-light text-decoration-none me-3">
                    <i class="bi bi-person-circle me-1"></i>{{ current_user.username }}
                </a>
                <a href="{{ url_for('web.logout') }}" class="btn btn-outline-light btn-sm">
                    <i class="bi bi-box-arrow-right me-1"></i>Logout
                </a>
                {% endif %}
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
                            <a class="nav-link" href="{{ url_for('web.list_sessions') }}">
                                <i class="bi bi-calendar-event me-2"></i> Sessions
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

                    <h6 class="sidebar-heading mt-4">Account</h6>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.user_settings') }}">
                                <i class="bi bi-gear me-2"></i> Settings
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
    
    create_auth_templates()
    create_observations_templates()
    create_objects_templates()
    create_instruments_templates()
    create_places_templates()
    create_types_templates()
    create_properties_templates()
    create_search_template()
    create_sessions_templates()

    print("=" * 60)
    print("✓ ALL COMPLETE TEMPLATES CREATED SUCCESSFULLY!")
    print("=" * 60)

def create_auth_templates():
    """Create authentication templates"""

    # Login template
    with open('templates/auth/login.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Astronomy Observations</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body {
            background-color: #0a0e27;
            color: #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .login-card {
            background-color: #1a1f3a;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            max-width: 420px;
            width: 100%;
            padding: 2.5rem;
        }
        .login-card h2 {
            color: #4dabf7;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .login-card .subtitle {
            color: rgba(255,255,255,0.5);
            text-align: center;
            margin-bottom: 2rem;
        }
        .form-control {
            background-color: #252b4a;
            border-color: rgba(255,255,255,0.2);
            color: #e0e0e0;
        }
        .form-control:focus {
            background-color: #2d3561;
            border-color: #4dabf7;
            color: #e0e0e0;
            box-shadow: 0 0 0 0.25rem rgba(77, 171, 247, 0.25);
        }
        .btn-primary {
            background-color: #4dabf7;
            border-color: #4dabf7;
            width: 100%;
            padding: 0.6rem;
        }
        .btn-primary:hover {
            background-color: #339af0;
            border-color: #339af0;
        }
        .form-label { color: #b0b0b0; }
        a { color: #4dabf7; }
        a:hover { color: #74c0fc; }
        .alert { border: none; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2><i class="bi bi-stars"></i> Astronomy</h2>
        <p class="subtitle">Observation Database</p>

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

        <form method="POST">
            <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" class="form-control" id="username" name="username" required autofocus>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary mb-3">
                <i class="bi bi-box-arrow-in-right me-2"></i>Log In
            </button>
        </form>
        <p class="text-center mb-0">
            <small>Don't have an account? <a href="{{ url_for('web.register') }}">Register</a></small>
        </p>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''')

    print("✓ Login template created")

    # Register template
    with open('templates/auth/register.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - Astronomy Observations</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body {
            background-color: #0a0e27;
            color: #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .login-card {
            background-color: #1a1f3a;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            max-width: 420px;
            width: 100%;
            padding: 2.5rem;
        }
        .login-card h2 {
            color: #4dabf7;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .login-card .subtitle {
            color: rgba(255,255,255,0.5);
            text-align: center;
            margin-bottom: 2rem;
        }
        .form-control {
            background-color: #252b4a;
            border-color: rgba(255,255,255,0.2);
            color: #e0e0e0;
        }
        .form-control:focus {
            background-color: #2d3561;
            border-color: #4dabf7;
            color: #e0e0e0;
            box-shadow: 0 0 0 0.25rem rgba(77, 171, 247, 0.25);
        }
        .btn-primary {
            background-color: #4dabf7;
            border-color: #4dabf7;
            width: 100%;
            padding: 0.6rem;
        }
        .btn-primary:hover {
            background-color: #339af0;
            border-color: #339af0;
        }
        .form-label { color: #b0b0b0; }
        a { color: #4dabf7; }
        a:hover { color: #74c0fc; }
        .alert { border: none; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2><i class="bi bi-person-plus"></i> Register</h2>
        <p class="subtitle">Create your account</p>

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

        <form method="POST">
            <div class="mb-3">
                <label for="username" class="form-label">Username <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="username" name="username" required autofocus>
            </div>
            <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" name="email">
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password <span class="text-danger">*</span></label>
                <input type="password" class="form-control" id="password" name="password" required>
                <div class="form-text" style="color:rgba(255,255,255,0.4);">Minimum 4 characters</div>
            </div>
            <div class="mb-3">
                <label for="password2" class="form-label">Confirm Password <span class="text-danger">*</span></label>
                <input type="password" class="form-control" id="password2" name="password2" required>
            </div>
            <button type="submit" class="btn btn-primary mb-3">
                <i class="bi bi-person-plus me-2"></i>Register
            </button>
        </form>
        <p class="text-center mb-0">
            <small>Already have an account? <a href="{{ url_for('web.login') }}">Log in</a></small>
        </p>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''')

    print("✓ Register template created")

    # Settings template
    with open('templates/auth/settings.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Settings{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-gear me-2"></i>User Settings</h1>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-person me-2"></i>Profile Information
            </div>
            <div class="card-body">
                <form method="POST">
                    <input type="hidden" name="action" value="update_profile">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Username</label>
                            <input type="text" class="form-control" value="{{ current_user.username }}" disabled>
                            <div class="form-text">Username cannot be changed</div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" name="email" value="{{ current_user.email or ''}}">
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="postal_address" class="form-label">Postal Address</label>
                        <textarea class="form-control" id="postal_address" name="postal_address" rows="2">{{ current_user.postal_address or ''}}</textarea>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label for="aavso_code" class="form-label">AAVSO Observer Code</label>
                            <input type="text" class="form-control" id="aavso_code" name="aavso_code" value="{{ current_user.aavso_code or ''  }}" maxlength="20" style="text-transform: uppercase;">
                            <div class="form-text">e.g., "XYZ"</div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="icq_code" class="form-label">ICQ Observer Code</label>
                            <input type="text" class="form-control" id="icq_code" name="icq_code" value="{{ current_user.icq_code or ''  }}" maxlength="20">
                            <div class="form-text">e.g., "ICQxxx"</div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="default_timezone" class="form-label">Default Timezone</label>
                            <select class="form-select" id="default_timezone" name="default_timezone">
                                <option value="">Select timezone...</option>
                                {% set timezones = [
                                    'Pacific/Midway', 'Pacific/Honolulu', 'America/Anchorage',
                                    'America/Los_Angeles', 'America/Denver', 'America/Chicago',
                                    'America/New_York', 'America/Halifax', 'America/Sao_Paulo',
                                    'Atlantic/Azores', 'Europe/London', 'Europe/Paris',
                                    'Europe/Berlin', 'Europe/Helsinki', 'Europe/Moscow',
                                    'Asia/Dubai', 'Asia/Karachi', 'Asia/Kolkata',
                                    'Asia/Dhaka', 'Asia/Bangkok', 'Asia/Shanghai',
                                    'Asia/Tokyo', 'Australia/Sydney', 'Pacific/Auckland'
                                ] %}
                                {% for tz in timezones %}
                                <option value="{{ tz }}" {{ 'selected' if current_user.default_timezone == tz else ''  }}>{{ tz }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-check-circle me-1"></i>Save Profile
                    </button>
                </form>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <i class="bi bi-shield-lock me-2"></i>Change Password
            </div>
            <div class="card-body">
                <form method="POST">
                    <input type="hidden" name="action" value="change_password">
                    <div class="mb-3">
                        <label for="current_password" class="form-label">Current Password <span class="text-danger">*</span></label>
                        <input type="password" class="form-control" id="current_password" name="current_password" required>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="new_password" class="form-label">New Password <span class="text-danger">*</span></label>
                            <input type="password" class="form-control" id="new_password" name="new_password" required>
                            <div class="form-text">Minimum 4 characters</div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="new_password2" class="form-label">Confirm New Password <span class="text-danger">*</span></label>
                            <input type="password" class="form-control" id="new_password2" name="new_password2" required>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-warning">
                        <i class="bi bi-key me-1"></i>Change Password
                    </button>
                </form>
            </div>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <i class="bi bi-info-circle me-2"></i>Account Info
            </div>
            <div class="card-body">
                <p><strong>Username:</strong> {{ current_user.username }}</p>
                <p><strong>Email:</strong> {{ current_user.email or 'Not set' }}</p>
                <p><strong>AAVSO Code:</strong> {{ current_user.aavso_code or 'Not set' }}</p>
                <p><strong>ICQ Code:</strong> {{ current_user.icq_code or 'Not set' }}</p>
                <p><strong>Member since:</strong> {{ current_user.created_at.strftime('%Y-%m-%d') if current_user.created_at else 'N/A' }}</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')

    print("✓ Settings template created")


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

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="session" class="form-label">Session</label>
                    <select class="form-select" id="session" name="session">
                        <option value="">No session</option>
                        {% for s in sessions %}
                        <option value="{{ s.id }}">{{ s.number }} ({{ s.start_datetime.strftime('%Y-%m-%d') if s.start_datetime else '?' }})</option>
                        {% endfor %}
                    </select>
                    <div class="form-text">Optionally assign this observation to a session</div>
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

                <!-- VSP Locally Available Charts -->
                <div id="vsp-charts-section" class="mb-4" style="display:none;">
                    <div class="card" style="background:#151a33; border-color:rgba(77,171,247,0.3);">
                        <div class="card-header d-flex justify-content-between align-items-center" style="background:#1a2040;">
                            <span><i class="bi bi-map me-2 text-info"></i><strong>Available Finder Charts</strong>
                            <small class="text-muted ms-2">Click thumbnail for full size</small></span>
                            <a id="vsp-all-charts-link" href="#" class="btn btn-sm btn-outline-info">
                                <i class="bi bi-cloud-arrow-down me-1"></i>Download Charts
                            </a>
                        </div>
                        <div class="card-body p-2">
                            <div id="vsp-thumbs" class="d-flex flex-wrap gap-2 justify-content-center">
                                <div class="text-muted p-2 small">No charts downloaded yet. Click "Download Charts" above.</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- VSP Full-size modal -->
                <div class="modal fade" id="vspModal" tabindex="-1">
                    <div class="modal-dialog modal-xl modal-dialog-centered">
                        <div class="modal-content" style="background:#111; border:1px solid rgba(255,255,255,0.2);">
                            <div class="modal-header" style="background:#1a1f3a; border-bottom:1px solid rgba(255,255,255,0.1);">
                                <h5 class="modal-title" id="vspModalLabel">Chart</h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body p-0 text-center" style="background:#000;">
                                <img id="vspModalImg" src="" style="max-width:100%;max-height:80vh;" alt="Chart">
                            </div>
                            <div class="modal-footer" style="background:#1a1f3a; border-top:1px solid rgba(255,255,255,0.1);">
                                <button type="button" class="btn btn-sm btn-outline-secondary" id="vspUseChartBtn">
                                    <i class="bi bi-clipboard-check me-1"></i>Use this Chart ID
                                </button>
                                <span id="vspChartIdText" class="text-muted ms-2 small"></span>
                            </div>
                        </div>
                    </div>
                </div>

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

var _currentVspChartId = '';

// Check object type and load locally stored VSP charts
function checkObjectType() {
    const sel = document.getElementById('object');
    const opt = sel.options[sel.selectedIndex];
    const type = opt.getAttribute('data-type');
    const starName = opt.getAttribute('data-name') || '';
    const nameLower = starName.toLowerCase();

    const isComet = type === '6' || nameLower.includes('comet') || nameLower.match(/\\b[cp]\\/\\d{4}/i);
    const isVarStar = type === '7' || nameLower.match(/^[a-z]{1,2}\\s+[a-z]{3}$/) || nameLower.includes('variable');

    document.getElementById('comet-fields').style.display = isComet ? 'block' : 'none';
    document.getElementById('varstar-fields').style.display = isVarStar ? 'block' : 'none';

    // Load locally stored VSP charts
    if (isVarStar && starName) {
        loadLocalCharts(starName);
    } else {
        document.getElementById('vsp-charts-section').style.display = 'none';
    }
}

function loadLocalCharts(starName) {
    var section = document.getElementById('vsp-charts-section');
    var thumbs = document.getElementById('vsp-thumbs');
    section.style.display = 'block';

    // Set the "Download Charts" link to the full charts page
    document.getElementById('vsp-all-charts-link').href = '/web/vsp/view/' + encodeURIComponent(starName);

    // Fetch locally available charts
    fetch('/web/vsp/local/' + encodeURIComponent(starName))
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (!data.charts || data.charts.length === 0) {
                thumbs.innerHTML = '<div class="text-muted p-2 small">No charts downloaded yet. Click "Download Charts" to get finder charts from AAVSO VSP.</div>';
                return;
            }
            var html = '';
            data.charts.forEach(function(chart) {
                html += '<div class="text-center" style="flex:0 0 auto; width:130px;">';
                html += '<img src="' + chart.image_url + '?t=' + Date.now() + '" ';
                html += 'style="width:120px;height:120px;object-fit:cover;border:2px solid rgba(255,255,255,0.1);border-radius:6px;cursor:pointer;transition:all 0.2s;" ';
                html += 'onmouseover="this.style.borderColor=\\\'#4dabf7\\\';this.style.transform=\\\'scale(1.05)\\\'" ';
                html += 'onmouseout="this.style.borderColor=\\\'rgba(255,255,255,0.1)\\\';this.style.transform=\\\'scale(1)\\\'" ';
                html += 'onclick="showVspChart(\\\'' + chart.image_url + '\\\',\\\'' + chart.scale + '\\\',\\\'' + chart.chartid + '\\\')" ';
                html += 'loading="lazy" alt="Scale ' + chart.scale + '" title="Scale ' + chart.scale + '">';
                html += '<div class="mt-1"><span class="badge bg-info" style="font-size:0.7rem;">' + chart.scale + '</span></div>';
                html += '<div><small class="text-muted" style="font-size:0.65rem;">' + chart.chartid + '</small></div>';
                html += '</div>';
            });
            thumbs.innerHTML = html;
        })
        .catch(function(err) {
            thumbs.innerHTML = '<div class="text-danger p-2 small">Error loading local charts</div>';
        });
}

function showVspChart(url, scale, chartid) {
    _currentVspChartId = chartid;
    document.getElementById('vspModalImg').src = url + '?t=' + Date.now();
    document.getElementById('vspModalLabel').textContent = 'Scale ' + scale;
    document.getElementById('vspChartIdText').textContent = 'Chart ID: ' + chartid;
    new bootstrap.Modal(document.getElementById('vspModal')).show();
}

// "Use this Chart ID" button
document.getElementById('vspUseChartBtn').addEventListener('click', function() {
    var chartField = document.getElementById('vs_chart');
    if (chartField && _currentVspChartId) {
        chartField.value = _currentVspChartId;
        chartField.style.borderColor = '#4dabf7';
        setTimeout(function() { chartField.style.borderColor = ''; }, 2000);
    }
    bootstrap.Modal.getInstance(document.getElementById('vspModal')).hide();
});

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
                    <th>Actions</th>
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
                    <td>
                        {% if obj.type == 7 %}
                        <a href="{{ url_for('web.vsp_view', star_name=obj.name) }}" class="btn btn-sm btn-outline-info" title="AAVSO Finder Charts">
                            <i class="bi bi-map"></i> Charts
                        </a>
                        {% endif %}
                    </td>
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
                    <th>Type</th>
                    <th>Aperture</th>
                    <th>Power/Focal Length</th>
                    <th>Eyepiece</th>
                </tr>
            </thead>
            <tbody>
                {% for instrument in instruments %}
                <tr>
                    <td>{{ instrument.id }}</td>
                    <td>{{ instrument.name }}</td>
                    <td>
                        {% if instrument.instrument_type %}
                            <span class="badge bg-{% if instrument.instrument_type == 'Binoculars' %}success{% elif instrument.instrument_type == 'Reflector' %}primary{% elif instrument.instrument_type == 'Refractor' %}info{% elif instrument.instrument_type == 'SCT' %}warning{% else %}secondary{% endif %}">{{ instrument.instrument_type }}</span>
                        {% else %}
                            N/A
                        {% endif %}
                    </td>
                    <td>{{ instrument.aperture or 'N/A' }}</td>
                    <td>{{ instrument.power or 'N/A' }}</td>
                    <td>{{ instrument.eyepiece or 'N/A' }}</td>
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
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" id="name" name="name" required>
                    <div class="form-text">e.g., "Celestron NexStar 8SE", "Nikon 10x50"</div>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="instrument_type" class="form-label">Instrument Type</label>
                    <select class="form-select" id="instrument_type" name="instrument_type">
                        <option value="">Select type...</option>
                        <option value="Binoculars">Binoculars</option>
                        <option value="Refractor">Refractor</option>
                        <option value="Reflector">Reflector (Newtonian)</option>
                        <option value="SCT">Schmidt-Cassegrain (SCT)</option>
                        <option value="Maksutov">Maksutov-Cassegrain</option>
                        <option value="Dobsonian">Dobsonian</option>
                        <option value="RCT">Ritchey-Chretien (RCT)</option>
                        <option value="Camera">Camera / DSLR</option>
                        <option value="Naked Eye">Naked Eye</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
            </div>
            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="aperture" class="form-label">Aperture</label>
                    <input type="text" class="form-control" id="aperture" name="aperture">
                    <div class="form-text">e.g., "203.2mm", "8 inches", "50mm"</div>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="power" class="form-label">Power / Focal Length</label>
                    <input type="text" class="form-control" id="power" name="power">
                    <div class="form-text">e.g., "2032mm", "f/10", "10x"</div>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="eyepiece" class="form-label">Eyepiece</label>
                    <input type="text" class="form-control" id="eyepiece" name="eyepiece">
                    <div class="form-text">e.g., "25mm Plossl", "10mm BST", "32mm Wide"</div>
                </div>
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
{% block extra_css %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
    #placesMap { height: 400px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }
</style>
{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-geo-alt me-2"></i>Observation Places</h1>
    <a href="{{ url_for('web.add_place') }}" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i> Add Place
    </a>
</div>

<div class="card mb-4">
    <div class="card-header">
        <i class="bi bi-map me-2"></i>Map
    </div>
    <div class="card-body p-0">
        <div id="placesMap"></div>
    </div>
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
{% endblock %}
{% block extra_js %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
var map = L.map('placesMap').setView([30, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
}).addTo(map);

var places = [
    {% for place in places %}
    {% if place.lat and place.lon %}
    { name: "{{ place.name }}", lat: {{ place.lat }}, lon: {{ place.lon }}, alt: "{{ place.alt or 'N/A' }}", tz: "{{ place.timezone or 'N/A' }}" },
    {% endif %}
    {% endfor %}
];

var bounds = [];
places.forEach(function(p) {
    var marker = L.marker([p.lat, p.lon]).addTo(map);
    marker.bindPopup('<strong>' + p.name + '</strong><br>Lat: ' + p.lat + '<br>Lon: ' + p.lon + '<br>Alt: ' + p.alt + '<br>TZ: ' + p.tz);
    bounds.push([p.lat, p.lon]);
});

if (bounds.length > 0) {
    if (bounds.length === 1) {
        map.setView(bounds[0], 10);
    } else {
        map.fitBounds(bounds, { padding: [30, 30] });
    }
}
</script>
{% endblock %}''')

    with open('templates/places/add.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Add Place{% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
    #pickMap { height: 400px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); cursor: crosshair; }
    .leaflet-container { background: #1a1f3a; }
</style>
{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-plus-circle me-2"></i>Add Observation Place</h1>
    <a href="{{ url_for('web.list_places') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>

<div class="card mb-4">
    <div class="card-header">
        <i class="bi bi-map me-2"></i>Click on map to set coordinates
    </div>
    <div class="card-body p-0">
        <div id="pickMap"></div>
    </div>
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
                    <div class="form-text">Click map or enter manually, e.g. "51.4778"</div>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="lon" class="form-label">Longitude <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" id="lon" name="lon" required>
                    <div class="form-text">Click map or enter manually, e.g. "0.0015"</div>
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
                    <div class="form-text">Auto-detected from map click, or enter manually</div>
                </div>
            </div>
            <button type="submit" class="btn btn-primary">Add Place</button>
            <a href="{{ url_for('web.list_places') }}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</div>
{% endblock %}
{% block extra_js %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
var map = L.map('pickMap').setView([50, 15], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
}).addTo(map);

var marker = null;

// Timezone lookup from coordinates
function guessTimezone(lat, lon) {
    var offset = Math.round(lon / 15);
    var tzMap = {
        '-12': 'Etc/GMT+12', '-11': 'Pacific/Midway', '-10': 'Pacific/Honolulu',
        '-9': 'America/Anchorage', '-8': 'America/Los_Angeles', '-7': 'America/Denver',
        '-6': 'America/Chicago', '-5': 'America/New_York', '-4': 'America/Halifax',
        '-3': 'America/Sao_Paulo', '-2': 'Atlantic/South_Georgia', '-1': 'Atlantic/Azores',
        '0': 'Europe/London', '1': 'Europe/Paris', '2': 'Europe/Helsinki',
        '3': 'Europe/Moscow', '4': 'Asia/Dubai', '5': 'Asia/Karachi',
        '6': 'Asia/Dhaka', '7': 'Asia/Bangkok', '8': 'Asia/Shanghai',
        '9': 'Asia/Tokyo', '10': 'Australia/Sydney', '11': 'Pacific/Noumea',
        '12': 'Pacific/Auckland'
    };
    return tzMap[String(offset)] || 'UTC';
}

map.on('click', function(e) {
    var lat = e.latlng.lat.toFixed(5);
    var lon = e.latlng.lng.toFixed(5);

    document.getElementById('lat').value = lat;
    document.getElementById('lon').value = lon;

    var tz = guessTimezone(parseFloat(lat), parseFloat(lon));
    document.getElementById('timezone').value = tz;

    if (marker) {
        marker.setLatLng(e.latlng);
    } else {
        marker = L.marker(e.latlng).addTo(map);
    }
    marker.bindPopup('Lat: ' + lat + '<br>Lon: ' + lon + '<br>TZ: ' + tz).openPopup();
});

// If lat/lon already filled, show marker
function syncMarker() {
    var lat = parseFloat(document.getElementById('lat').value);
    var lon = parseFloat(document.getElementById('lon').value);
    if (!isNaN(lat) && !isNaN(lon)) {
        var latlng = L.latLng(lat, lon);
        if (marker) {
            marker.setLatLng(latlng);
        } else {
            marker = L.marker(latlng).addTo(map);
        }
        map.setView(latlng, 12);
    }
}
document.getElementById('lat').addEventListener('change', syncMarker);
document.getElementById('lon').addEventListener('change', syncMarker);
</script>
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

def create_sessions_templates():
    """Create session templates"""

    os.makedirs('templates/sessions', exist_ok=True)

    with open('templates/sessions/list.html', 'w') as f:
        f.write('''{% extends "layout.html" %}

{% block title %}Sessions - Astronomy Observations{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2"><i class="bi bi-calendar-event me-2"></i>Sessions</h1>
    <a href="{{ url_for('web.add_session') }}" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i> Add Session
    </a>
</div>

{% if sessions %}
<div class="table-responsive">
    <table class="table table-striped table-hover">
        <thead>
            <tr>
                <th>Number</th>
                <th>Start</th>
                <th>End</th>
                <th>Clouds</th>
                <th>Light Pollution</th>
                <th>Lim. Mag.</th>
                <th>Moon</th>
                <th>Instrument</th>
                <th>Observations</th>
            </tr>
        </thead>
        <tbody>
            {% for session in sessions %}
            <tr>
                <td><a href="{{ url_for('web.view_session', session_id=session.id) }}">{{ session.number or '-' }}</a></td>
                <td>{{ session.start_datetime.strftime('%Y-%m-%d %H:%M') if session.start_datetime else '-' }}</td>
                <td>{{ session.end_datetime.strftime('%Y-%m-%d %H:%M') if session.end_datetime else '-' }}</td>
                <td>{{ session.cloud_percentage }}%{% if session.cloud_type %} ({{ session.cloud_type }}){% endif %}</td>
                <td>{{ session.light_pollution or '-' }}/10</td>
                <td>{{ session.limiting_magnitude or '-' }}</td>
                <td>{{ session.moon_phase or '-' }}{% if session.moon_altitude %} ({{ session.moon_altitude }}&deg;){% endif %}</td>
                <td>{{ session.session_instrument.name if session.session_instrument else '-' }}</td>
                <td>{{ session.observations|length }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="alert alert-info">
    No sessions found. <a href="{{ url_for('web.add_session') }}">Add your first session</a>.
</div>
{% endif %}
{% endblock %}''')

    with open('templates/sessions/add.html', 'w') as f:
        f.write('''{% extends "layout.html" %}

{% block title %}Add Session - Astronomy Observations{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2"><i class="bi bi-plus-circle me-2"></i>Add Session</h1>
    <a href="{{ url_for('web.list_sessions') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back to Sessions
    </a>
</div>

<div class="card">
    <div class="card-body">
        <form method="POST">
            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="number" class="form-label">Session Number</label>
                    <input type="text" class="form-control" id="number" name="number" placeholder="e.g. 1/2026" required>
                    <div class="form-text">Format: n/yyyy</div>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="start_datetime" class="form-label">Start Date & Time</label>
                    <input type="datetime-local" class="form-control" id="start_datetime" name="start_datetime" required>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="end_datetime" class="form-label">End Date & Time</label>
                    <input type="datetime-local" class="form-control" id="end_datetime" name="end_datetime">
                </div>
            </div>

            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="cloud_percentage" class="form-label">Cloud Percentage (%)</label>
                    <input type="number" class="form-control" id="cloud_percentage" name="cloud_percentage" min="0" max="100">
                </div>
                <div class="col-md-4 mb-3">
                    <label for="cloud_type" class="form-label">Cloud Type</label>
                    <select class="form-select" id="cloud_type" name="cloud_type">
                        <option value="">-- Select --</option>
                        <option value="Cirrus">Cirrus</option>
                        <option value="Cirrostratus">Cirrostratus</option>
                        <option value="Cirrocumulus">Cirrocumulus</option>
                        <option value="Altostratus">Altostratus</option>
                        <option value="Altocumulus">Altocumulus</option>
                        <option value="Stratus">Stratus</option>
                        <option value="Stratocumulus">Stratocumulus</option>
                        <option value="Cumulus">Cumulus</option>
                        <option value="Cumulonimbus">Cumulonimbus</option>
                        <option value="Nimbostratus">Nimbostratus</option>
                    </select>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="light_pollution" class="form-label">Light Pollution (1-10)</label>
                    <input type="number" class="form-control" id="light_pollution" name="light_pollution" min="1" max="10">
                    <div class="form-text">1 = darkest sky, 10 = brightest</div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="limiting_magnitude" class="form-label">Limiting Magnitude</label>
                    <input type="number" class="form-control" id="limiting_magnitude" name="limiting_magnitude" step="0.1">
                </div>
                <div class="col-md-4 mb-3">
                    <label for="moon_phase" class="form-label">Moon Phase</label>
                    <select class="form-select" id="moon_phase" name="moon_phase">
                        <option value="">-- Select --</option>
                        <option value="New Moon">New Moon</option>
                        <option value="Waxing Crescent">Waxing Crescent</option>
                        <option value="First Quarter">First Quarter</option>
                        <option value="Waxing Gibbous">Waxing Gibbous</option>
                        <option value="Full Moon">Full Moon</option>
                        <option value="Waning Gibbous">Waning Gibbous</option>
                        <option value="Last Quarter">Last Quarter</option>
                        <option value="Waning Crescent">Waning Crescent</option>
                    </select>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="moon_altitude" class="form-label">Moon Altitude (&deg;)</label>
                    <input type="number" class="form-control" id="moon_altitude" name="moon_altitude" step="0.1" min="-90" max="90">
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="instrument" class="form-label">Instrument</label>
                    <select class="form-select" id="instrument" name="instrument">
                        <option value="">-- Select --</option>
                        {% for inst in instruments %}
                        <option value="{{ inst.id }}">{{ inst.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>

            <button type="submit" class="btn btn-primary">
                <i class="bi bi-plus-circle me-1"></i> Add Session
            </button>
        </form>
    </div>
</div>
{% endblock %}''')

    with open('templates/sessions/view.html', 'w') as f:
        f.write('''{% extends "layout.html" %}

{% block title %}Session {{ session.number }} - Astronomy Observations{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2"><i class="bi bi-calendar-event me-2"></i>Session {{ session.number }}</h1>
    <a href="{{ url_for('web.list_sessions') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back to Sessions
    </a>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card mb-3">
            <div class="card-header"><strong>Session Details</strong></div>
            <div class="card-body">
                <table class="table table-sm">
                    <tr><th>Number</th><td>{{ session.number or '-' }}</td></tr>
                    <tr><th>Start</th><td>{{ session.start_datetime.strftime('%Y-%m-%d %H:%M') if session.start_datetime else '-' }}</td></tr>
                    <tr><th>End</th><td>{{ session.end_datetime.strftime('%Y-%m-%d %H:%M') if session.end_datetime else '-' }}</td></tr>
                    <tr><th>Instrument</th><td>{{ session.session_instrument.name if session.session_instrument else '-' }}</td></tr>
                </table>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card mb-3">
            <div class="card-header"><strong>Conditions</strong></div>
            <div class="card-body">
                <table class="table table-sm">
                    <tr><th>Clouds</th><td>{{ session.cloud_percentage or '-' }}%{% if session.cloud_type %} ({{ session.cloud_type }}){% endif %}</td></tr>
                    <tr><th>Light Pollution</th><td>{{ session.light_pollution or '-' }}/10</td></tr>
                    <tr><th>Limiting Magnitude</th><td>{{ session.limiting_magnitude or '-' }}</td></tr>
                    <tr><th>Moon Phase</th><td>{{ session.moon_phase or '-' }}</td></tr>
                    <tr><th>Moon Altitude</th><td>{{ session.moon_altitude or '-' }}&deg;</td></tr>
                </table>
            </div>
        </div>
    </div>
</div>

<h3 class="mt-4">Observations in this session</h3>
{% if observations %}
<div class="table-responsive">
    <table class="table table-striped table-hover">
        <thead>
            <tr>
                <th>ID</th>
                <th>Object</th>
                <th>Date/Time</th>
                <th>Place</th>
                <th>Instrument</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
            {% for obs in observations %}
            <tr>
                <td>{{ obs.id }}</td>
                <td>{{ obs.observed_object.name if obs.observed_object else obs.object }}</td>
                <td>{{ obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '-' }}</td>
                <td>{{ obs.observation_place.name if obs.observation_place else '-' }}</td>
                <td>{{ obs.observation_instrument.name if obs.observation_instrument else '-' }}</td>
                <td>{{ obs.observation or '-' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="alert alert-info">No observations in this session yet.</div>
{% endif %}
{% endblock %}''')

    print("✓ Sessions templates created")

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

def create_vsx_charts_template():
    """Create the AAVSO VSP charts viewing template - download & local storage"""

    content = (
        '{% extends "layout.html" %}\n'
        '{% block title %}AAVSO Charts - {{ star_name }}{% endblock %}\n'
        '{% block extra_css %}\n'
        '<style>\n'
        '  .chart-card{background:#1a1f3a;border:1px solid rgba(255,255,255,0.1);border-radius:10px;overflow:hidden}\n'
        '  .chart-card .card-header{background:#252b4a;padding:.5rem 1rem}\n'
        '  .chart-thumb{cursor:pointer;border:2px solid rgba(255,255,255,0.1);border-radius:6px;transition:all .3s;max-width:100%;background:#151a33}\n'
        '  .chart-thumb:hover{border-color:#4dabf7;box-shadow:0 4px 15px rgba(77,171,247,.3);transform:scale(1.02)}\n'
        '  .dl-btn:hover{transform:scale(1.1)}\n'
        '  #chartModal .modal-dialog{max-width:95vw}\n'
        '  #chartModal .modal-body{padding:0;background:#000;text-align:center}\n'
        '  #chartModal .modal-body img{max-width:100%;max-height:85vh}\n'
        '  #chartModal .modal-content{background:#111;border:1px solid rgba(255,255,255,.2)}\n'
        '  #chartModal .modal-header{background:#1a1f3a;border-bottom:1px solid rgba(255,255,255,.1)}\n'
        '</style>\n'
        '{% endblock %}\n'
        '{% block content %}\n'
        '<div class="d-flex justify-content-between mb-4">\n'
        '  <h1><i class="bi bi-map me-2"></i>AAVSO Finder Charts</h1>\n'
        '  <div>\n'
        '    <button class="btn btn-info me-2" onclick="downloadAll()" id="dlAllBtn">\n'
        '      <i class="bi bi-cloud-arrow-down me-1"></i>Download All Scales\n'
        '    </button>\n'
        '    <a href="{{ url_for(\'web.list_objects\') }}" class="btn btn-secondary">\n'
        '      <i class="bi bi-arrow-left me-1"></i> Back\n'
        '    </a>\n'
        '  </div>\n'
        '</div>\n'
        '<div class="card mb-4">\n'
        '  <div class="card-header"><i class="bi bi-star me-2 text-warning"></i><strong>{{ star_name }}</strong>\n'
        '    <span class="text-muted ms-2">- AAVSO Variable Star Plotter</span></div>\n'
        '  <div class="card-body"><p class="mb-0">Click <i class="bi bi-cloud-arrow-down"></i> to download a chart from AAVSO. '
        'Downloaded charts are stored locally. Click thumbnails for full size.</p></div>\n'
        '</div>\n'
        '<div class="row g-3" id="chartsGrid">\n'
        '{% for s in scales %}\n'
        '<div class="col-md-4 col-lg-3" id="card-{{ s.key }}">\n'
        '  <div class="chart-card h-100">\n'
        '    <div class="card-header d-flex justify-content-between align-items-center">\n'
        '      <span class="badge bg-info">{{ s.key }}</span>\n'
        '      <small class="text-muted">{{ s.label }}</small>\n'
        '    </div>\n'
        '    <div class="p-2 text-center" id="body-{{ s.key }}">\n'
        '      {% if s.downloaded %}\n'
        '        {% for c in local_charts if c.scale == s.key %}\n'
        '        <img src="{{ c.image_url }}?t={{ range(99999)|random }}" class="chart-thumb"\n'
        '             onclick="showFull(\'{{ c.image_url }}\',\'{{ s.key }}\',\'{{ c.chartid }}\',{{ s.fov }})"\n'
        '             alt="Scale {{ s.key }}" loading="lazy" style="max-height:200px;">\n'
        '        <div class="mt-1"><small class="text-muted">{{ c.chartid }}</small></div>\n'
        '        {% endfor %}\n'
        '      {% else %}\n'
        '        <div class="py-4">\n'
        '          <button class="btn btn-outline-info dl-btn" onclick="downloadOne(\'{{ s.key }}\')">\n'
        '            <i class="bi bi-cloud-arrow-down" style="font-size:2rem;"></i>\n'
        '            <div class="small mt-1">Download</div>\n'
        '          </button>\n'
        '          <div class="mt-2" id="spin-{{ s.key }}" style="display:none">\n'
        '            <div class="spinner-border spinner-border-sm text-info"></div>\n'
        '            <small class="ms-1">Downloading...</small>\n'
        '          </div>\n'
        '        </div>\n'
        '      {% endif %}\n'
        '    </div>\n'
        '  </div>\n'
        '</div>\n'
        '{% endfor %}\n'
        '</div>\n'
        '\n'
        '<div class="modal fade" id="chartModal" tabindex="-1">\n'
        '  <div class="modal-dialog modal-xl modal-dialog-centered">\n'
        '    <div class="modal-content">\n'
        '      <div class="modal-header">\n'
        '        <h5 class="modal-title" id="chartModalLabel">Chart</h5>\n'
        '        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>\n'
        '      </div>\n'
        '      <div class="modal-body"><img id="chartModalImg" src="" alt="Chart"></div>\n'
        '      <div class="modal-footer" style="background:#1a1f3a;border-top:1px solid rgba(255,255,255,.1)">\n'
        '        <span id="chartIdBadge" class="text-muted"></span>\n'
        '      </div>\n'
        '    </div>\n'
        '  </div>\n'
        '</div>\n'
        '{% endblock %}\n'
        '{% block extra_js %}\n'
        '<script>\n'
        'var starName = "{{ star_name }}";\n'
        'function showFull(url,scale,chartid,fov){\n'
        '  document.getElementById("chartModalImg").src=url+"?t="+Date.now();\n'
        '  document.getElementById("chartModalLabel").textContent=starName+" - Scale "+scale+" (FOV "+fov+"\')";\n'
        '  document.getElementById("chartIdBadge").textContent="Chart ID: "+chartid;\n'
        '  new bootstrap.Modal(document.getElementById("chartModal")).show();\n'
        '}\n'
        'function downloadOne(scale){\n'
        '  var spin=document.getElementById("spin-"+scale);\n'
        '  if(spin) spin.style.display="block";\n'
        '  var fd=new FormData();fd.append("star_name",starName);fd.append("scale",scale);\n'
        '  fetch("/web/vsp/download",{method:"POST",body:fd})\n'
        '    .then(function(r){return r.json();})\n'
        '    .then(function(d){\n'
        '      if(d.error){alert("Error: "+d.error);if(spin)spin.style.display="none";return;}\n'
        '      var b=document.getElementById("body-"+scale);\n'
        '      b.innerHTML=\'<img src="\'+d.image_url+"?t="+Date.now()+\'" class="chart-thumb" \'+\n'
        '        \'onclick="showFull(\\\'\'+d.image_url+\'\\\',\\\'\'+scale+\'\\\',\\\'\'+d.chartid+\'\\\',0)" \'+\n'
        '        \'alt="Scale \'+scale+\'" style="max-height:200px;">\'+\n'
        '        \'<div class="mt-1"><small class="text-muted">\'+d.chartid+\'</small></div>\';\n'
        '    }).catch(function(e){alert("Failed: "+e.message);if(spin)spin.style.display="none";});\n'
        '}\n'
        'function downloadAll(){\n'
        '  var btn=document.getElementById("dlAllBtn");\n'
        '  btn.disabled=true;btn.innerHTML=\'<span class="spinner-border spinner-border-sm me-1"></span>Downloading...\';\n'
        '  var fd=new FormData();fd.append("star_name",starName);\n'
        '  fetch("/web/vsp/download-all",{method:"POST",body:fd})\n'
        '    .then(function(r){return r.json();})\n'
        '    .then(function(data){\n'
        '      if(data.results)data.results.forEach(function(r){\n'
        '        if(r.success){\n'
        '          var b=document.getElementById("body-"+r.scale);\n'
        '          if(b) b.innerHTML=\'<img src="\'+r.image_url+"?t="+Date.now()+\'" class="chart-thumb" \'+\n'
        '            \'onclick="showFull(\\\'\'+r.image_url+\'\\\',\\\'\'+r.scale+\'\\\',\\\'\'+r.chartid+\'\\\',0)" \'+\n'
        '            \'alt="Scale \'+r.scale+\'" style="max-height:200px;">\'+\n'
        '            \'<div class="mt-1"><small class="text-muted">\'+r.chartid+\'</small></div>\';\n'
        '        }\n'
        '      });\n'
        '      btn.disabled=false;btn.innerHTML=\'<i class="bi bi-cloud-arrow-down me-1"></i>Download All Scales\';\n'
        '    }).catch(function(e){\n'
        '      alert("Error: "+e.message);\n'
        '      btn.disabled=false;btn.innerHTML=\'<i class="bi bi-cloud-arrow-down me-1"></i>Download All Scales\';\n'
        '    });\n'
        '}\n'
        '</script>\n'
        '{% endblock %}\n'
    )

    with open('templates/vsx/charts.html', 'w') as f:
        f.write(content)

    print("✓ VSP charts template created")

if __name__ == '__main__':
    create_complete_templates()
    create_comet_import_template()
    create_vsx_import_template()
    create_vsx_charts_template()