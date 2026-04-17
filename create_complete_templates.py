"""
Create COMPLETE template files with FULL COBS and AAVSO support
All templates in one file
"""

import os

def create_complete_templates():
    """Create all complete template files"""
    print("Creating COMPLETE template files with COBS comet and AAVSO variable star support...")
    
    # Ensure directories exist
    for dir_name in ['objects', 'observations', 'instruments', 'places', 'types', 'properties', 'comets', 'vsx', 'sessions', 'auth', 'backup', 'export', 'cobs']:
        os.makedirs(f'templates/{dir_name}', exist_ok=True)
    
    # =========================================================================
    # LAYOUT TEMPLATE (BASE) - ENHANCED
    # =========================================================================
    
    with open('templates/layout.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#1a1f3a">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="description" content="Track and manage astronomical observations">
    <link rel="manifest" href="/manifest.json">
    <link rel="icon" type="image/svg+xml" href="/static/icons/icon.svg">
    <link rel="apple-touch-icon" href="/static/icons/icon-192.png">
    <title>{% block title %}Astronomy Observations{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link rel="stylesheet" href="/static/mobile.css">
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
            <button class="btn btn-outline-light me-2 mobile-menu-btn" type="button" id="sidebarToggle" style="display:none;">
                <i class="bi bi-list"></i>
            </button>
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
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.search_simbad_page') }}">
                                <i class="bi bi-globe me-2"></i> SIMBAD Search
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.export_icq') }}">
                                <i class="bi bi-file-earmark-text me-2"></i> Export ICQ
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.export_aavso') }}">
                                <i class="bi bi-file-earmark-ruled me-2"></i> Export AAVSO
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.cobs_submit') }}">
                                <i class="bi bi-cloud-upload me-2"></i> Submit to COBS
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.aavso_submit') }}">
                                <i class="bi bi-star me-2 text-warning"></i> Submit to AAVSO
                            </a>
                        </li>
                    </ul>

                    <h6 class="sidebar-heading mt-4">Backup</h6>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('web.backup_page') }}">
                                <i class="bi bi-cloud-arrow-down me-2"></i> Backup & Restore
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

    <!-- Sidebar backdrop for mobile -->
    <div class="sidebar-backdrop" id="sidebarBackdrop"></div>

    <!-- PWA Install Banner -->
    <div class="pwa-install-banner" id="pwaInstallBanner">
        <div>
            <strong><i class="bi bi-phone me-1"></i> Install App</strong><br>
            <small>Add Astronomy Observations to your home screen</small>
        </div>
        <div>
            <button class="btn-install" id="pwaInstallBtn">Install</button>
            <button class="btn-dismiss" id="pwaInstallDismiss">&times;</button>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <script>
    // --- Mobile sidebar toggle ---
    (function() {
        const toggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('sidebarMenu');
        const backdrop = document.getElementById('sidebarBackdrop');

        if (toggle && sidebar) {
            toggle.addEventListener('click', function() {
                sidebar.classList.toggle('show');
                backdrop.classList.toggle('show');
            });
            if (backdrop) {
                backdrop.addEventListener('click', function() {
                    sidebar.classList.remove('show');
                    backdrop.classList.remove('show');
                });
            }
            // Close sidebar when a link is clicked (mobile)
            sidebar.querySelectorAll('.nav-link').forEach(function(link) {
                link.addEventListener('click', function() {
                    if (window.innerWidth < 768) {
                        sidebar.classList.remove('show');
                        backdrop.classList.remove('show');
                    }
                });
            });
        }
    })();

    // --- PWA Service Worker Registration ---
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').then(function(reg) {
            console.log('Service Worker registered, scope:', reg.scope);
        }).catch(function(err) {
            console.log('Service Worker registration failed:', err);
        });
    }

    // --- PWA Install Prompt ---
    (function() {
        let deferredPrompt;
        const banner = document.getElementById('pwaInstallBanner');
        const installBtn = document.getElementById('pwaInstallBtn');
        const dismissBtn = document.getElementById('pwaInstallDismiss');

        window.addEventListener('beforeinstallprompt', function(e) {
            e.preventDefault();
            deferredPrompt = e;
            // Don't show if user previously dismissed
            if (localStorage.getItem('pwa-install-dismissed')) return;
            banner.classList.add('show');
        });

        if (installBtn) {
            installBtn.addEventListener('click', function() {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then(function(choice) {
                        deferredPrompt = null;
                        banner.classList.remove('show');
                    });
                }
            });
        }

        if (dismissBtn) {
            dismissBtn.addEventListener('click', function() {
                banner.classList.remove('show');
                localStorage.setItem('pwa-install-dismissed', '1');
            });
        }

        // Hide banner if already installed
        window.addEventListener('appinstalled', function() {
            banner.classList.remove('show');
        });
    })();
    </script>
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
                    <h6 class="mt-3 mb-2"><i class="bi bi-cloud-upload me-1"></i> COBS Integration (cobs.si)</h6>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label for="cobs_username" class="form-label">COBS Username</label>
                            <input type="text" class="form-control" id="cobs_username" name="cobs_username" value="{{ current_user.cobs_username or '' }}">
                            <div class="form-text">Your cobs.si login</div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="cobs_password" class="form-label">COBS Password</label>
                            <input type="password" class="form-control" id="cobs_password" name="cobs_password" placeholder="{{ '********' if current_user.cobs_password else '' }}">
                            <div class="form-text">Leave empty to keep current</div>
                        </div>
                    </div>
                    <h6 class="mt-3 mb-2"><i class="bi bi-star me-1"></i> AAVSO Integration (aavso.org)</h6>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label for="aavso_email" class="form-label">AAVSO Email</label>
                            <input type="email" class="form-control" id="aavso_email" name="aavso_email" value="{{ current_user.aavso_email or '' }}">
                            <div class="form-text">Your AAVSO login email</div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="aavso_password" class="form-label">AAVSO Password</label>
                            <input type="password" class="form-control" id="aavso_password" name="aavso_password" placeholder="{{ '********' if current_user.aavso_password else '' }}">
                            <div class="form-text">Leave empty to keep current</div>
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
                <p><strong>COBS Account:</strong> {{ current_user.cobs_username or 'Not set' }}</p>
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
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for obs in observations %}
                    <tr>
                        <td>{{ obs.id }}</td>
                        <td>{{ obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '' }}</td>
                        <td>{{ objects_lookup.get(obs.object, obs.object) }}</td>
                        <td>{{ places_lookup.get(obs.place, obs.place) }}</td>
                        <td>{{ instruments_lookup.get(obs.instrument, obs.instrument) }}</td>
                        <td>{{ obs.observation[:50] }}{% if obs.observation|length > 50 %}...{% endif %}</td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                <button type="button" class="btn btn-outline-info" data-bs-toggle="modal" data-bs-target="#obsModal{{ obs.id }}" title="View">
                                    <i class="bi bi-eye"></i>
                                </button>
                                <a href="{{ url_for('web.edit_observation', obs_id=obs.id) }}" class="btn btn-outline-warning" title="Edit">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                <form method="POST" action="{{ url_for('web.duplicate_observation', obs_id=obs.id) }}" style="display:inline">
                                    <button type="submit" class="btn btn-outline-success" title="Duplicate">
                                        <i class="bi bi-files"></i>
                                    </button>
                                </form>
                                <button type="button" class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deleteModal{{ obs.id }}" title="Delete">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>

                            <div class="modal fade" id="deleteModal{{ obs.id }}" tabindex="-1">
                                <div class="modal-dialog">
                                    <div class="modal-content">
                                        <div class="modal-header">
                                            <h5 class="modal-title">Confirm Delete</h5>
                                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                        </div>
                                        <div class="modal-body">Are you sure you want to delete observation #{{ obs.id }}?</div>
                                        <div class="modal-footer">
                                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                            <form method="POST" action="{{ url_for('web.delete_observation', obs_id=obs.id) }}" style="display:inline">
                                                <button type="submit" class="btn btn-danger">Delete</button>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                            </div>

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
                                                <dd class="col-sm-9">{{ obs.datetime.strftime('%Y-%m-%d %H:%M') if obs.datetime else '' }}</dd>
                                                <dt class="col-sm-3">Object:</dt>
                                                <dd class="col-sm-9">{{ objects_lookup.get(obs.object, obs.object) }}</dd>
                                                <dt class="col-sm-3">Place:</dt>
                                                <dd class="col-sm-9">{{ places_lookup.get(obs.place, obs.place) }}</dd>
                                                <dt class="col-sm-3">Instrument:</dt>
                                                <dd class="col-sm-9">{{ instruments_lookup.get(obs.instrument, obs.instrument) }}</dd>
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
                    <label for="object_search" class="form-label">Object <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" id="object_search" list="object_list" placeholder="Type to search..." autocomplete="off" oninput="onObjectSearchInput()">
                    <datalist id="object_list">
                        {% for obj in objects %}
                        <option value="{{ obj.name }}{% if obj.desination %} ({{ obj.desination }}){% endif %}" data-id="{{ obj.id }}"></option>
                        {% endfor %}
                    </datalist>
                    <input type="hidden" id="object" name="object" required>
                    <select id="object_data" style="display:none">
                        {% for obj in objects %}
                        <option value="{{ obj.id }}" data-type="{{ obj.type }}" data-name="{{ obj.name }}" data-props="{{ obj.props|default('{}', true)|e }}" data-label="{{ obj.name }}{% if obj.desination %} ({{ obj.desination }}){% endif %}"></option>
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
                    <select class="form-select" id="session" name="session" onchange="onSessionChange()">
                        <option value="">No session</option>
                        {% for s in sessions %}
                        <option value="{{ s.id }}">{{ s.number }} ({{ s.start_datetime.strftime('%Y-%m-%d') if s.start_datetime else '?' }})</option>
                        {% endfor %}
                    </select>
                    <div class="form-text">Selecting a session auto-fills date, place, instrument & limiting magnitude</div>
                </div>
            </div>

            <div class="mb-3">
                <label for="observation" class="form-label">Observation Notes <span class="text-danger">*</span></label>
                <textarea class="form-control" id="observation" name="observation" rows="3" required></textarea>
            </div>

            <!-- VARIABLE STAR FIELDS (AAVSO) -->
            <div id="varstar-fields" style="display: none;">
                <hr class="my-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="mb-0"><i class="bi bi-star me-2 text-warning"></i>Variable Star (AAVSO Format)</h4>
                    <div class="d-flex gap-2">
                        <button id="aavso-recent-obs-btn" type="button" class="btn btn-sm btn-outline-info" style="display:none;" onclick="loadAavsoRecent()">
                            <i class="bi bi-clock-history me-1"></i>Recent AAVSO Observations
                        </button>
                        <button id="lightcurve-btn" type="button" class="btn btn-sm btn-outline-warning" style="display:none;" onclick="loadLightCurve()">
                            <i class="bi bi-graph-up me-1"></i>My Light Curve
                        </button>
                    </div>
                </div>

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

                <!-- AAVSO Recent Observations Modal -->
                <div class="modal fade" id="aavsoRecentModal" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content" style="background:#1a1f3a; border:1px solid rgba(77,171,247,0.4);">
                            <div class="modal-header" style="background:#111827; border-bottom:1px solid rgba(77,171,247,0.3);">
                                <h5 class="modal-title text-info">
                                    <i class="bi bi-clock-history me-2"></i>Recent AAVSO Observations
                                    <small id="aavsoRecentStarLabel" class="ms-2 text-warning"></small>
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div id="aavsoRecentLoading" class="text-center py-4">
                                    <div class="spinner-border text-info" role="status"></div>
                                    <div class="text-muted mt-2 small">Fetching from AAVSO...</div>
                                </div>
                                <div id="aavsoRecentError" style="display:none;">
                                    <div class="alert alert-warning mb-0">
                                        <i class="bi bi-exclamation-triangle me-2"></i>
                                        <span id="aavsoRecentErrorMsg"></span>
                                    </div>
                                </div>
                                <div id="aavsoRecentData" style="display:none;">
                                    <div class="row g-3 text-center">
                                        <div class="col-6">
                                            <div class="p-3 rounded" style="background:#111827; border:1px solid rgba(255,255,255,0.1);">
                                                <div class="text-muted small mb-1">Last Observation</div>
                                                <div id="aavsoLastDate" class="fw-bold text-light fs-6"></div>
                                                <div id="aavsoLastMag" class="text-warning fs-4 fw-bold mt-1"></div>
                                                <div id="aavsoLastBand" class="text-muted small"></div>
                                            </div>
                                        </div>
                                        <div class="col-6">
                                            <div class="p-3 rounded" style="background:#111827; border:1px solid rgba(255,255,255,0.1);">
                                                <div class="text-muted small mb-1">Current Tendency</div>
                                                <div id="aavsoTendency" class="fs-5 fw-bold mt-2"></div>
                                                <div class="text-muted small mt-1">last 10 vs prior 10</div>
                                            </div>
                                        </div>
                                        <div class="col-6">
                                            <div class="p-3 rounded" style="background:#111827; border:1px solid rgba(255,255,255,0.1);">
                                                <div class="text-muted small mb-1">Observations (1 yr)</div>
                                                <div id="aavsoObsCount" class="fw-bold text-light fs-4"></div>
                                            </div>
                                        </div>
                                        <div class="col-6">
                                            <div class="p-3 rounded" style="background:#111827; border:1px solid rgba(255,255,255,0.1);">
                                                <div class="text-muted small mb-1">Date Span</div>
                                                <div id="aavsoDaysSpan" class="fw-bold text-light fs-5 mt-1"></div>
                                                <div id="aavsoFirstDate" class="text-muted small"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer" style="border-top:1px solid rgba(77,171,247,0.3);">
                                <a id="aavsoWebObsLink" href="#" target="_blank" class="btn btn-sm btn-outline-info">
                                    <i class="bi bi-box-arrow-up-right me-1"></i>Open on AAVSO
                                </a>
                                <button type="button" class="btn btn-sm btn-outline-secondary" data-bs-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Light Curve Modal (own observations) -->
                <div class="modal fade" id="lightcurveModal" tabindex="-1">
                    <div class="modal-dialog modal-xl modal-dialog-centered">
                        <div class="modal-content" style="background:#1a1f3a; border:1px solid rgba(255,193,7,0.4);">
                            <div class="modal-header" style="background:#111827; border-bottom:1px solid rgba(255,193,7,0.3);">
                                <h5 class="modal-title text-warning">
                                    <i class="bi bi-graph-up me-2"></i>My Light Curve &mdash;
                                    <small id="lcStarLabel" class="text-light"></small>
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body p-3">
                                <div id="lcLoading" class="text-center py-5">
                                    <div class="spinner-border text-warning" role="status"></div>
                                    <div class="text-muted mt-2 small">Loading observations...</div>
                                </div>
                                <div id="lcError" style="display:none;">
                                    <div class="alert alert-warning mb-0">
                                        <i class="bi bi-exclamation-triangle me-2"></i>
                                        <span id="lcErrorMsg"></span>
                                    </div>
                                </div>
                                <div id="lcContent" style="display:none;">
                                    <div class="row mb-2 text-center">
                                        <div class="col-4">
                                            <span class="text-muted small">Observations</span>
                                            <div id="lcCount" class="fw-bold text-warning fs-5"></div>
                                        </div>
                                        <div class="col-4">
                                            <span class="text-muted small">Magnitude range</span>
                                            <div id="lcMagRange" class="fw-bold text-light fs-6 mt-1"></div>
                                        </div>
                                        <div class="col-4">
                                            <span class="text-muted small">Date span</span>
                                            <div id="lcDateSpan" class="fw-bold text-light fs-6 mt-1"></div>
                                        </div>
                                    </div>
                                    <div style="position:relative; height:380px;">
                                        <canvas id="lcChart"></canvas>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer" style="border-top:1px solid rgba(255,193,7,0.3);">
                                <small class="text-muted me-auto">Y-axis inverted: brighter stars appear higher</small>
                                <button type="button" class="btn btn-sm btn-outline-secondary" data-bs-dismiss="modal">Close</button>
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
                        <input type="text" class="form-control" id="vs_observer_code" name="vs_observer_code" maxlength="5" style="text-transform:uppercase;" value="{{ current_user.aavso_code or '' }}">
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
                            <option value="0">0 - Diffuse, no condensation</option>
                            <option value="0.5">0.5</option>
                            <option value="1">1</option>
                            <option value="1.5">1.5</option>
                            <option value="2">2</option>
                            <option value="2.5">2.5</option>
                            <option value="3">3 - Moderately condensed</option>
                            <option value="3.5">3.5</option>
                            <option value="4">4</option>
                            <option value="4.5">4.5</option>
                            <option value="5">5</option>
                            <option value="5.5">5.5</option>
                            <option value="6">6 - Condensed</option>
                            <option value="6.5">6.5</option>
                            <option value="7">7</option>
                            <option value="7.5">7.5</option>
                            <option value="8">8</option>
                            <option value="8.5">8.5</option>
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

// Session auto-fill data
var _sessionMeta = {{ session_meta_json|safe }};

function onSessionChange() {
    var sessId = document.getElementById('session').value;
    if (!sessId || !_sessionMeta[sessId]) return;
    var m = _sessionMeta[sessId];

    // Auto-fill date/time from session start
    if (m.start_datetime) {
        document.getElementById('datetime').value = m.start_datetime;
    }

    // Auto-fill instrument
    if (m.instrument) {
        var instSel = document.getElementById('instrument');
        for (var i = 0; i < instSel.options.length; i++) {
            if (instSel.options[i].value == m.instrument) {
                instSel.selectedIndex = i;
                break;
            }
        }
    }

    // Auto-fill place
    if (m.place) {
        var placeSel = document.getElementById('place');
        for (var i = 0; i < placeSel.options.length; i++) {
            if (placeSel.options[i].value == m.place) {
                placeSel.selectedIndex = i;
                break;
            }
        }
    }

    // Add limiting magnitude to observation notes
    if (m.limiting_magnitude) {
        var obsField = document.getElementById('observation');
        var lmTag = 'Lim.mag: ' + m.limiting_magnitude;
        // Only add if not already present
        if (obsField.value.indexOf('Lim.mag:') === -1) {
            obsField.value = obsField.value ? obsField.value + ' ' + lmTag : lmTag;
        }
    }
}

var _currentVspChartId = '';

// Resolve searchable object input to hidden input with ID
function onObjectSearchInput() {
    var searchField = document.getElementById('object_search');
    var hidden = document.getElementById('object');
    var dataSel = document.getElementById('object_data');
    var typed = searchField.value;
    var matched = null;
    for (var i = 0; i < dataSel.options.length; i++) {
        var o = dataSel.options[i];
        if (o.getAttribute('data-label') === typed) {
            matched = o;
            break;
        }
    }
    if (matched) {
        hidden.value = matched.value;
        checkObjectType();
    } else {
        hidden.value = '';
        document.getElementById('comet-fields').style.display = 'none';
        document.getElementById('varstar-fields').style.display = 'none';
    }
}

// Check object type and load locally stored VSP charts
function checkObjectType() {
    const hidden = document.getElementById('object');
    const dataSel = document.getElementById('object_data');
    let opt = null;
    for (let i = 0; i < dataSel.options.length; i++) {
        if (dataSel.options[i].value === hidden.value) { opt = dataSel.options[i]; break; }
    }
    if (!opt) {
        document.getElementById('comet-fields').style.display = 'none';
        document.getElementById('varstar-fields').style.display = 'none';
        return;
    }
    const type = opt.getAttribute('data-type');
    const starName = opt.getAttribute('data-name') || '';
    const nameLower = starName.toLowerCase();

    const isComet = type === '6' || nameLower.includes('comet') || nameLower.match(/\\b[cp]\\/\\d{4}/i);
    const isVarStar = type === '7' || nameLower.match(/^[a-z]{1,2}\\s+[a-z]{3}$/) || nameLower.includes('variable');

    document.getElementById('comet-fields').style.display = isComet ? 'block' : 'none';
    document.getElementById('varstar-fields').style.display = isVarStar ? 'block' : 'none';

    // Show AAVSO recent observations button for variable stars
    var aavsoBtn = document.getElementById('aavso-recent-obs-btn');
    if (isVarStar && starName) {
        var propsStr = opt.getAttribute('data-props') || '{}';
        try { var props = JSON.parse(propsStr); } catch(e) { var props = {}; }
        var auid = props.auid || '';
        // Store star info on button for use by loadAavsoRecent()
        aavsoBtn.setAttribute('data-star', starName);
        aavsoBtn.setAttribute('data-auid', auid);
        aavsoBtn.style.display = '';
        // Also show light curve button
        var lcBtn = document.getElementById('lightcurve-btn');
        if (lcBtn) {
            lcBtn.setAttribute('data-star', starName);
            lcBtn.style.display = '';
        }
    } else {
        aavsoBtn.style.display = 'none';
        var lcBtn = document.getElementById('lightcurve-btn');
        if (lcBtn) lcBtn.style.display = 'none';
    }

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

var _lcChartInstance = null;

function loadLightCurve() {
    var btn = document.getElementById('lightcurve-btn');
    var starName = btn.getAttribute('data-star') || '';
    if (!starName) return;

    // Reset modal state
    document.getElementById('lcStarLabel').textContent = starName;
    document.getElementById('lcLoading').style.display = 'block';
    document.getElementById('lcError').style.display = 'none';
    document.getElementById('lcContent').style.display = 'none';

    // Destroy previous chart instance if any
    if (_lcChartInstance) {
        _lcChartInstance.destroy();
        _lcChartInstance = null;
    }

    new bootstrap.Modal(document.getElementById('lightcurveModal')).show();

    fetch('/web/observations/lightcurve/' + encodeURIComponent(starName))
        .then(function(r) { return r.json(); })
        .then(function(data) {
            document.getElementById('lcLoading').style.display = 'none';
            if (data.error || !data.points || data.points.length === 0) {
                document.getElementById('lcErrorMsg').textContent =
                    data.error || 'No variable star observations found for ' + starName + '.';
                document.getElementById('lcError').style.display = 'block';
                return;
            }

            var points = data.points;
            // Compute summary stats
            var mags = points.map(function(p) { return p.y; });
            var minMag = Math.min.apply(null, mags).toFixed(2);
            var maxMag = Math.max.apply(null, mags).toFixed(2);
            document.getElementById('lcCount').textContent = points.length;
            document.getElementById('lcMagRange').textContent = minMag + ' – ' + maxMag;
            // Date span
            var firstDate = points[0].date ? points[0].date.substring(0,10) : '-';
            var lastDate = points[points.length-1].date ? points[points.length-1].date.substring(0,10) : '-';
            document.getElementById('lcDateSpan').textContent =
                firstDate === lastDate ? firstDate : firstDate + ' → ' + lastDate;

            // Build chart datasets — group by band
            var bands = {};
            points.forEach(function(p) {
                var b = p.band || 'Vis.';
                if (!bands[b]) bands[b] = [];
                bands[b].push({x: p.x, y: p.y, date: p.date, uncert: p.uncert});
            });

            var bandColors = {
                'Vis.': '#ffd700', 'Visual': '#ffd700',
                'V': '#4ade80', 'B': '#60a5fa', 'R': '#f87171',
                'I': '#c084fc', 'U': '#818cf8',
            };
            var datasets = Object.keys(bands).map(function(b) {
                var color = bandColors[b] || '#94a3b8';
                return {
                    label: b,
                    data: bands[b],
                    backgroundColor: color,
                    borderColor: color,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    showLine: points.length < 100,
                    borderWidth: 1,
                    tension: 0.2,
                };
            });

            var ctx = document.getElementById('lcChart').getContext('2d');
            _lcChartInstance = new Chart(ctx, {
                type: 'scatter',
                data: { datasets: datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: { unit: 'month', tooltipFormat: 'yyyy-MM-dd HH:mm' },
                            grid: { color: 'rgba(255,255,255,0.08)' },
                            ticks: { color: '#9ca3af' },
                            title: { display: true, text: 'Date', color: '#9ca3af' },
                        },
                        y: {
                            reverse: true,
                            grid: { color: 'rgba(255,255,255,0.08)' },
                            ticks: { color: '#9ca3af' },
                            title: { display: true, text: 'Magnitude (brighter ↑)', color: '#9ca3af' },
                        },
                    },
                    plugins: {
                        legend: { labels: { color: '#e5e7eb' } },
                        tooltip: {
                            callbacks: {
                                label: function(ctx) {
                                    var p = ctx.raw;
                                    var s = 'Mag: ' + p.y.toFixed(2);
                                    if (p.date) s += '  |  ' + p.date;
                                    if (p.uncert) s += '  ±' + p.uncert;
                                    return s;
                                }
                            },
                            backgroundColor: 'rgba(17,24,39,0.95)',
                            titleColor: '#fbbf24',
                            bodyColor: '#e5e7eb',
                            borderColor: 'rgba(255,193,7,0.4)',
                            borderWidth: 1,
                        },
                    },
                    backgroundColor: 'rgba(0,0,0,0)',
                }
            });

            document.getElementById('lcContent').style.display = 'block';
        })
        .catch(function(err) {
            document.getElementById('lcLoading').style.display = 'none';
            document.getElementById('lcErrorMsg').textContent = 'Network error: ' + err;
            document.getElementById('lcError').style.display = 'block';
        });
}

function loadAavsoRecent() {
    var btn = document.getElementById('aavso-recent-obs-btn');
    var starName = btn.getAttribute('data-star') || '';
    var auid = btn.getAttribute('data-auid') || '';
    if (!starName) return;

    // Show modal immediately with loading state
    document.getElementById('aavsoRecentStarLabel').textContent = starName;
    document.getElementById('aavsoRecentLoading').style.display = 'block';
    document.getElementById('aavsoRecentError').style.display = 'none';
    document.getElementById('aavsoRecentData').style.display = 'none';

    // Set AAVSO webobs link
    var webLink = document.getElementById('aavsoWebObsLink');
    if (auid) {
        webLink.href = 'https://apps.aavso.org/webobs/results/?star=' + encodeURIComponent(auid) + '&num_results=200';
    } else {
        webLink.href = 'https://apps.aavso.org/webobs/results/?star=' + encodeURIComponent(starName) + '&num_results=200';
    }

    new bootstrap.Modal(document.getElementById('aavsoRecentModal')).show();

    // Use AUID if available for better matching, else star name
    var ident = auid || starName;
    fetch('/web/aavso/recent/' + encodeURIComponent(ident))
        .then(function(r) { return r.json(); })
        .then(function(data) {
            document.getElementById('aavsoRecentLoading').style.display = 'none';
            if (data.error) {
                document.getElementById('aavsoRecentErrorMsg').textContent = data.error;
                document.getElementById('aavsoRecentError').style.display = 'block';
                return;
            }
            // Populate data fields
            document.getElementById('aavsoLastDate').textContent = data.last_date || '-';
            document.getElementById('aavsoLastMag').textContent = data.last_mag || '-';
            document.getElementById('aavsoLastBand').textContent = data.band ? 'Band: ' + data.band : '';
            document.getElementById('aavsoObsCount').textContent = data.obs_count || 0;
            document.getElementById('aavsoDaysSpan').textContent = (data.days_span || 0) + ' days';
            document.getElementById('aavsoFirstDate').textContent = 'from ' + (data.first_date || '-');

            // Tendency with colour
            var tendEl = document.getElementById('aavsoTendency');
            if (data.tendency === 'brightening') {
                tendEl.innerHTML = '<span class="text-success"><i class="bi bi-arrow-up-circle-fill me-1"></i>Brightening</span>';
            } else if (data.tendency === 'fading') {
                tendEl.innerHTML = '<span class="text-danger"><i class="bi bi-arrow-down-circle-fill me-1"></i>Fading</span>';
            } else if (data.tendency === 'stable') {
                tendEl.innerHTML = '<span class="text-info"><i class="bi bi-dash-circle-fill me-1"></i>Stable</span>';
            } else {
                tendEl.innerHTML = '<span class="text-muted">-</span>';
            }
            document.getElementById('aavsoRecentData').style.display = 'block';
        })
        .catch(function(err) {
            document.getElementById('aavsoRecentLoading').style.display = 'none';
            document.getElementById('aavsoRecentErrorMsg').textContent = 'Network error: ' + err;
            document.getElementById('aavsoRecentError').style.display = 'block';
        });
}

window.addEventListener('load', checkObjectType);
</script>
{% endblock %}'''

    with open('templates/observations/add.html', 'w') as f:
        f.write(obs_add_content)

    with open('templates/observations/edit.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Edit Observation{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-pencil me-2"></i>Edit Observation #{{ obs.id }}</h1>
    <a href="{{ url_for('web.list_observations') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>

<div class="card">
    <div class="card-body">
        <form method="POST">
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="object" class="form-label">Object <span class="text-danger">*</span></label>
                    <select class="form-select" id="object" name="object" required>
                        <option value="">Select object...</option>
                        {% for obj in objects %}
                        <option value="{{ obj.id }}" {% if obj.id == obs.object %}selected{% endif %}>
                            {{ obj.name }}{% if obj.desination %} ({{ obj.desination }}){% endif %}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="datetime" class="form-label">Date & Time (UTC) <span class="text-danger">*</span></label>
                    <input type="datetime-local" class="form-control" id="datetime" name="datetime" required step="1"
                           value="{{ obs.datetime.strftime('%Y-%m-%dT%H:%M:%S') if obs.datetime else '' }}">
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="place" class="form-label">Place <span class="text-danger">*</span></label>
                    <select class="form-select" id="place" name="place" required>
                        <option value="">Select place...</option>
                        {% for place in places %}
                        <option value="{{ place.id }}" {% if place.id == obs.place %}selected{% endif %}>{{ place.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="instrument" class="form-label">Instrument <span class="text-danger">*</span></label>
                    <select class="form-select" id="instrument" name="instrument" required>
                        <option value="">Select instrument...</option>
                        {% for instrument in instruments %}
                        <option value="{{ instrument.id }}" {% if instrument.id == obs.instrument %}selected{% endif %}>{{ instrument.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="session" class="form-label">Session</label>
                    <select class="form-select" id="session" name="session">
                        <option value="">No session</option>
                        {% for session in sessions %}
                        <option value="{{ session.id }}" {% if session.id == obs.session_id %}selected{% endif %}>
                            {{ session.number }} ({{ session.start_datetime.strftime('%Y-%m-%d') if session.start_datetime else 'N/A' }})
                        </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="prop1" class="form-label">Property</label>
                    <select class="form-select" id="prop1" name="prop1">
                        <option value="">None</option>
                        {% for prop in properties %}
                        <option value="{{ prop.id }}" {% if prop.id == obs.prop1 %}selected{% endif %}>{{ prop.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="prop1value" class="form-label">Property Value</label>
                    <input type="text" class="form-control" id="prop1value" name="prop1value" value="{{ obs.prop1value or '' }}">
                </div>
            </div>

            <div class="mb-3">
                <label for="observation" class="form-label">Observation Notes</label>
                <textarea class="form-control" id="observation" name="observation" rows="5">{{ obs.observation or '' }}</textarea>
            </div>

            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-warning"><i class="bi bi-check-circle me-1"></i> Save Changes</button>
                <a href="{{ url_for('web.list_observations') }}" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>

<div class="card border-danger mt-4">
    <div class="card-header bg-danger bg-opacity-25"><i class="bi bi-exclamation-triangle me-2"></i>Danger Zone</div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('web.delete_observation', obs_id=obs.id) }}" onsubmit="return confirm('Are you sure you want to permanently delete this observation? This cannot be undone.')">
            <button type="submit" class="btn btn-outline-danger"><i class="bi bi-trash me-1"></i> Delete This Observation</button>
        </form>
    </div>
</div>
{% endblock %}''')

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
                        <a href="{{ url_for('web.view_object', object_id=obj.id) }}" class="btn btn-sm btn-outline-info me-1" title="View">
                            <i class="bi bi-eye"></i>
                        </a>
                        <a href="{{ url_for('web.edit_object', object_id=obj.id) }}" class="btn btn-sm btn-outline-warning me-1" title="Edit">
                            <i class="bi bi-pencil"></i>
                        </a>
                        {% if obj.type == 7 %}
                        <a href="{{ url_for('web.vsp_view', star_name=obj.name) }}" class="btn btn-sm btn-outline-success me-1" title="AAVSO Finder Charts">
                            <i class="bi bi-map"></i>
                        </a>
                        {% endif %}
                        <form method="POST" action="{{ url_for('web.delete_object', object_id=obj.id) }}" class="d-inline" onsubmit="return confirm('Delete {{ obj.name }}?')">
                            <button type="submit" class="btn btn-sm btn-outline-danger" title="Delete">
                                <i class="bi bi-trash"></i>
                            </button>
                        </form>
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

    with open('templates/objects/view.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}{{ obj.name }}{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-star me-2"></i>{{ obj.name }}</h1>
    <div>
        <a href="{{ url_for('web.edit_object', object_id=obj.id) }}" class="btn btn-warning">
            <i class="bi bi-pencil me-1"></i> Edit
        </a>
        {% if obj_type and obj_type.name == 'Variable Star' %}
        <a href="{{ url_for('web.vsp_view', star_name=obj.name) }}" class="btn btn-info">
            <i class="bi bi-map me-1"></i> Charts
        </a>
        {% endif %}
        <a href="{{ url_for('web.list_objects') }}" class="btn btn-secondary">
            <i class="bi bi-arrow-left me-1"></i> Back
        </a>
    </div>
</div>

<div class="row">
    <div class="col-lg-6">
        <div class="card mb-4">
            <div class="card-header"><i class="bi bi-info-circle me-2"></i>Basic Information</div>
            <div class="card-body">
                <table class="table table-dark mb-0">
                    <tr><th style="width:35%">ID</th><td>{{ obj.id }}</td></tr>
                    <tr><th>Name</th><td><strong>{{ obj.name }}</strong></td></tr>
                    <tr><th>Designation</th><td>{{ obj.desination or '-' }}</td></tr>
                    <tr><th>Type</th><td>
                        {% if obj_type %}
                            <span class="badge bg-primary">{{ obj_type.name }}</span>
                        {% else %}
                            {{ obj.type }}
                        {% endif %}
                    </td></tr>
                </table>
            </div>
        </div>

        {% if props.get('ra_2000') or props.get('dec_2000') or props.get('ra_deg') %}
        <div class="card mb-4">
            <div class="card-header"><i class="bi bi-compass me-2"></i>Coordinates (J2000)</div>
            <div class="card-body">
                <table class="table table-dark mb-0">
                    {% if props.get('ra_2000') %}<tr><th style="width:35%">RA</th><td>{{ props.ra_2000 }}</td></tr>{% endif %}
                    {% if props.get('dec_2000') %}<tr><th>Dec</th><td>{{ props.dec_2000 }}</td></tr>{% endif %}
                    {% if props.get('ra_deg') %}<tr><th>RA (deg)</th><td>{{ props.ra_deg }}</td></tr>{% endif %}
                    {% if props.get('dec_deg') %}<tr><th>Dec (deg)</th><td>{{ props.dec_deg }}</td></tr>{% endif %}
                    {% if props.get('constellation') %}<tr><th>Constellation</th><td>{{ props.constellation }}</td></tr>{% endif %}
                </table>
            </div>
        </div>
        {% endif %}
    </div>

    <div class="col-lg-6">
        {% if props.get('magnitude_v') or props.get('max_magnitude') or props.get('spectral_type') or props.get('variability_type') %}
        <div class="card mb-4">
            <div class="card-header"><i class="bi bi-bar-chart me-2"></i>Physical Properties</div>
            <div class="card-body">
                <table class="table table-dark mb-0">
                    {% if props.get('magnitude_v') %}<tr><th style="width:35%">Magnitude (V)</th><td>{{ props.magnitude_v }}</td></tr>{% endif %}
                    {% if props.get('max_magnitude') %}<tr><th>Max Magnitude</th><td>{{ props.max_magnitude }}</td></tr>{% endif %}
                    {% if props.get('min_magnitude') %}<tr><th>Min Magnitude</th><td>{{ props.min_magnitude }}</td></tr>{% endif %}
                    {% if props.get('magnitude_range') %}<tr><th>Mag Range</th><td>{{ props.magnitude_range }}</td></tr>{% endif %}
                    {% if props.get('spectral_type') %}<tr><th>Spectral Type</th><td>{{ props.spectral_type }}</td></tr>{% endif %}
                    {% if props.get('variability_type') %}<tr><th>Variability Type</th><td>{{ props.variability_type }}</td></tr>{% endif %}
                    {% if props.get('period_days') %}<tr><th>Period (days)</th><td>{{ props.period_days }}</td></tr>{% endif %}
                    {% if props.get('epoch') %}<tr><th>Epoch</th><td>{{ props.epoch }}</td></tr>{% endif %}
                </table>
            </div>
        </div>
        {% endif %}

        <div class="card mb-4">
            <div class="card-header"><i class="bi bi-database me-2"></i>Source & Identifiers</div>
            <div class="card-body">
                <table class="table table-dark mb-0">
                    {% if props.get('source') %}<tr><th style="width:35%">Source</th><td>{{ props.source }}</td></tr>{% endif %}
                    {% if props.get('simbad_id') %}<tr><th>SIMBAD ID</th><td>{{ props.simbad_id }}</td></tr>{% endif %}
                    {% if props.get('auid') %}<tr><th>AUID</th><td>{{ props.auid }}</td></tr>{% endif %}
                    {% if props.get('vsx_oid') %}<tr><th>VSX OID</th><td>{{ props.vsx_oid }}</td></tr>{% endif %}
                    {% if props.get('object_type') %}<tr><th>SIMBAD Type</th><td>{{ props.object_type }}</td></tr>{% endif %}
                    {% if props.get('alt_names') %}<tr><th>Alt Names</th><td>{{ props.alt_names }}</td></tr>{% endif %}
                </table>
            </div>
        </div>

        {% if props %}
        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-code me-2"></i>All Properties (JSON)
                <button class="btn btn-sm btn-outline-info float-end" type="button" data-bs-toggle="collapse" data-bs-target="#rawJson">
                    <i class="bi bi-eye"></i> Toggle
                </button>
            </div>
            <div class="collapse" id="rawJson">
                <div class="card-body">
                    <pre class="mb-0" style="color:#8ec8f0; white-space:pre-wrap;">{{ props|tojson(indent=2) }}</pre>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}''')

    with open('templates/objects/edit.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Edit {{ obj.name }}{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-pencil me-2"></i>Edit: {{ obj.name }}</h1>
    <div>
        <a href="{{ url_for('web.view_object', object_id=obj.id) }}" class="btn btn-info">
            <i class="bi bi-eye me-1"></i> View
        </a>
        <a href="{{ url_for('web.list_objects') }}" class="btn btn-secondary">
            <i class="bi bi-arrow-left me-1"></i> Back
        </a>
    </div>
</div>

<form method="POST">
<div class="row">
    <div class="col-lg-6">
        <div class="card mb-4">
            <div class="card-header"><i class="bi bi-info-circle me-2"></i>Basic Information</div>
            <div class="card-body">
                <div class="mb-3">
                    <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" id="name" name="name" value="{{ obj.name }}" required>
                </div>
                <div class="mb-3">
                    <label for="desination" class="form-label">Designation</label>
                    <input type="text" class="form-control" id="desination" name="desination" value="{{ obj.desination or '' }}">
                    <div class="form-text">e.g. M31, NGC 7000, 1P/Halley</div>
                </div>
                <div class="mb-3">
                    <label for="type" class="form-label">Type <span class="text-danger">*</span></label>
                    <select class="form-select" id="type" name="type" required>
                        <option value="">Select type...</option>
                        {% for t in types %}
                        <option value="{{ t.id }}" {% if t.id == obj.type %}selected{% endif %}>{{ t.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
        </div>

        <div class="card mb-4">
            <div class="card-header"><i class="bi bi-compass me-2"></i>Coordinates (J2000)</div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="ra_2000" class="form-label">Right Ascension</label>
                        <input type="text" class="form-control" id="ra_2000" name="ra_2000" value="{{ props.get('ra_2000', '') }}" placeholder="HH:MM:SS.ss">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="dec_2000" class="form-label">Declination</label>
                        <input type="text" class="form-control" id="dec_2000" name="dec_2000" value="{{ props.get('dec_2000', '') }}" placeholder="+DD:MM:SS.s">
                    </div>
                </div>
                <div class="mb-3">
                    <label for="constellation" class="form-label">Constellation</label>
                    <input type="text" class="form-control" id="constellation" name="constellation" value="{{ props.get('constellation', '') }}" placeholder="e.g. And, Cyg, Ori">
                </div>
            </div>
        </div>
    </div>

    <div class="col-lg-6">
        <div class="card mb-4">
            <div class="card-header"><i class="bi bi-bar-chart me-2"></i>Physical Properties</div>
            <div class="card-body">
                <div class="mb-3">
                    <label for="magnitude_v" class="form-label">Magnitude (V)</label>
                    <input type="text" class="form-control" id="magnitude_v" name="magnitude_v" value="{{ props.get('magnitude_v', '') }}">
                </div>
                <div class="mb-3">
                    <label for="spectral_type" class="form-label">Spectral Type</label>
                    <input type="text" class="form-control" id="spectral_type" name="spectral_type" value="{{ props.get('spectral_type', '') }}">
                </div>
                <div class="mb-3">
                    <label for="variability_type" class="form-label">Variability Type</label>
                    <input type="text" class="form-control" id="variability_type" name="variability_type" value="{{ props.get('variability_type', '') }}" placeholder="e.g. M, CEP, EA, RR">
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="max_magnitude" class="form-label">Max Magnitude</label>
                        <input type="text" class="form-control" id="max_magnitude" name="max_magnitude" value="{{ props.get('max_magnitude', '') }}">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="min_magnitude" class="form-label">Min Magnitude</label>
                        <input type="text" class="form-control" id="min_magnitude" name="min_magnitude" value="{{ props.get('min_magnitude', '') }}">
                    </div>
                </div>
                <div class="mb-3">
                    <label for="period_days" class="form-label">Period (days)</label>
                    <input type="text" class="form-control" id="period_days" name="period_days" value="{{ props.get('period_days', '') }}">
                </div>
            </div>
        </div>

        <div class="card mb-4">
            <div class="card-header"><i class="bi bi-code me-2"></i>Additional Properties (JSON)</div>
            <div class="card-body">
                <textarea class="form-control" id="extra_props" name="extra_props" rows="3" placeholder=\'{"key": "value"}\'></textarea>
                <div class="form-text">Add extra properties as JSON. These will be merged with existing properties.</div>
                {% if props %}
                <hr>
                <small class="text-muted">Current stored properties:</small>
                <pre class="mt-1 mb-0" style="color:#8ec8f0; font-size:0.8rem; white-space:pre-wrap;">{{ props|tojson(indent=2) }}</pre>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<div class="d-flex gap-2 mb-4">
    <button type="submit" class="btn btn-warning btn-lg">
        <i class="bi bi-check-circle me-1"></i> Save Changes
    </button>
    <a href="{{ url_for('web.view_object', object_id=obj.id) }}" class="btn btn-secondary btn-lg">Cancel</a>
</div>
</form>

<div class="card border-danger">
    <div class="card-header bg-danger bg-opacity-25"><i class="bi bi-exclamation-triangle me-2"></i>Danger Zone</div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('web.delete_object', object_id=obj.id) }}" onsubmit="return confirm('Are you sure you want to permanently delete {{ obj.name }}? This cannot be undone.')">
            <button type="submit" class="btn btn-outline-danger">
                <i class="bi bi-trash me-1"></i> Delete This Object
            </button>
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
                    <th>Actions</th>
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
                    <td>
                        <div class="btn-group btn-group-sm">
                            <a href="{{ url_for('web.edit_instrument', inst_id=instrument.id) }}" class="btn btn-outline-warning" title="Edit">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button type="button" class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deleteInstModal{{ instrument.id }}" title="Delete">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        <div class="modal fade" id="deleteInstModal{{ instrument.id }}" tabindex="-1">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header"><h5 class="modal-title">Confirm Delete</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                                    <div class="modal-body">Are you sure you want to delete instrument "{{ instrument.name }}"?</div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                        <form method="POST" action="{{ url_for('web.delete_instrument', inst_id=instrument.id) }}" style="display:inline">
                                            <button type="submit" class="btn btn-danger">Delete</button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </td>
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
    
    with open('templates/instruments/edit.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Edit Instrument{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-pencil me-2"></i>Edit Instrument</h1>
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
                    <input type="text" class="form-control" id="name" name="name" value="{{ inst.name or '' }}" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="instrument_type" class="form-label">Instrument Type</label>
                    <select class="form-select" id="instrument_type" name="instrument_type">
                        <option value="">Select type...</option>
                        {% for opt in ['Binoculars','Refractor','Reflector','SCT','Maksutov','Dobsonian','RCT','Camera','Naked Eye','Other'] %}
                        <option value="{{ opt }}" {% if inst.instrument_type == opt %}selected{% endif %}>{{ opt }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="aperture" class="form-label">Aperture</label>
                    <input type="text" class="form-control" id="aperture" name="aperture" value="{{ inst.aperture or '' }}">
                    <div class="form-text">e.g., "203.2mm", "50mm"</div>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="power" class="form-label">Power / Focal Length</label>
                    <input type="text" class="form-control" id="power" name="power" value="{{ inst.power or '' }}">
                    <div class="form-text">e.g., "2032mm", "f/10", "10x"</div>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="eyepiece" class="form-label">Eyepiece</label>
                    <input type="text" class="form-control" id="eyepiece" name="eyepiece" value="{{ inst.eyepiece or '' }}">
                </div>
            </div>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-warning"><i class="bi bi-check-circle me-1"></i> Save Changes</button>
                <a href="{{ url_for('web.list_instruments') }}" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>

<div class="card border-danger mt-4">
    <div class="card-header bg-danger bg-opacity-25"><i class="bi bi-exclamation-triangle me-2"></i>Danger Zone</div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('web.delete_instrument', inst_id=inst.id) }}" onsubmit="return confirm('Are you sure you want to permanently delete this instrument?')">
            <button type="submit" class="btn btn-outline-danger"><i class="bi bi-trash me-1"></i> Delete This Instrument</button>
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
                    <th>Alias</th>
                    <th>Latitude</th>
                    <th>Longitude</th>
                    <th>Altitude</th>
                    <th>Timezone</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for place in places %}
                <tr>
                    <td>{{ place.id }}</td>
                    <td>{{ place.name }}</td>
                    <td>{{ place.alias or '' }}</td>
                    <td>{{ place.lat }}</td>
                    <td>{{ place.lon }}</td>
                    <td>{{ place.alt or 'N/A' }}</td>
                    <td>{{ place.timezone or 'N/A' }}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <a href="{{ url_for('web.edit_place', place_id=place.id) }}" class="btn btn-outline-warning" title="Edit">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button type="button" class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deletePlaceModal{{ place.id }}" title="Delete">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        <div class="modal fade" id="deletePlaceModal{{ place.id }}" tabindex="-1">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header"><h5 class="modal-title">Confirm Delete</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                                    <div class="modal-body">Are you sure you want to delete place "{{ place.name }}"?</div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                        <form method="POST" action="{{ url_for('web.delete_place', place_id=place.id) }}" style="display:inline">
                                            <button type="submit" class="btn btn-danger">Delete</button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </td>
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
            <div class="mb-3">
                <label for="alias" class="form-label">Alias</label>
                <input type="text" class="form-control" id="alias" name="alias">
                <div class="form-text">Readable name for external services, e.g., "Jastrowo, Poland"</div>
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

    with open('templates/places/edit.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Edit Place{% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
    #pickMap { height: 400px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); cursor: crosshair; }
    .leaflet-container { background: #1a1f3a; }
</style>
{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-pencil me-2"></i>Edit Place</h1>
    <a href="{{ url_for('web.list_places') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>

<div class="card mb-4">
    <div class="card-header"><i class="bi bi-map me-2"></i>Click on map to set coordinates</div>
    <div class="card-body p-0"><div id="pickMap"></div></div>
</div>

<div class="card">
    <div class="card-body">
        <form method="POST">
            <div class="mb-3">
                <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="name" name="name" value="{{ place.name or '' }}" required>
            </div>
            <div class="mb-3">
                <label for="alias" class="form-label">Alias</label>
                <input type="text" class="form-control" id="alias" name="alias" value="{{ place.alias or '' }}">
                <div class="form-text">Readable name for external services, e.g., "Jastrowo, Poland"</div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="lat" class="form-label">Latitude <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" id="lat" name="lat" value="{{ place.lat or '' }}" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="lon" class="form-label">Longitude <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" id="lon" name="lon" value="{{ place.lon or '' }}" required>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="alt" class="form-label">Altitude</label>
                    <input type="text" class="form-control" id="alt" name="alt" value="{{ place.alt or '' }}">
                </div>
                <div class="col-md-6 mb-3">
                    <label for="timezone" class="form-label">Timezone</label>
                    <input type="text" class="form-control" id="timezone" name="timezone" value="{{ place.timezone or '' }}">
                </div>
            </div>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-warning"><i class="bi bi-check-circle me-1"></i> Save Changes</button>
                <a href="{{ url_for('web.list_places') }}" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>

<div class="card border-danger mt-4">
    <div class="card-header bg-danger bg-opacity-25"><i class="bi bi-exclamation-triangle me-2"></i>Danger Zone</div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('web.delete_place', place_id=place.id) }}" onsubmit="return confirm('Are you sure you want to permanently delete this place?')">
            <button type="submit" class="btn btn-outline-danger"><i class="bi bi-trash me-1"></i> Delete This Place</button>
        </form>
    </div>
</div>
{% endblock %}
{% block extra_js %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
var map = L.map('pickMap').setView([50, 15], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors', maxZoom: 19
}).addTo(map);

var marker = null;

function guessTimezone(lat, lon) {
    var offset = Math.round(lon / 15);
    var tzMap = {'-12':'Etc/GMT+12','-11':'Pacific/Midway','-10':'Pacific/Honolulu','-9':'America/Anchorage','-8':'America/Los_Angeles','-7':'America/Denver','-6':'America/Chicago','-5':'America/New_York','-4':'America/Halifax','-3':'America/Sao_Paulo','-2':'Atlantic/South_Georgia','-1':'Atlantic/Azores','0':'Europe/London','1':'Europe/Paris','2':'Europe/Helsinki','3':'Europe/Moscow','4':'Asia/Dubai','5':'Asia/Karachi','6':'Asia/Dhaka','7':'Asia/Bangkok','8':'Asia/Shanghai','9':'Asia/Tokyo','10':'Australia/Sydney','11':'Pacific/Noumea','12':'Pacific/Auckland'};
    return tzMap[String(offset)] || 'UTC';
}

map.on('click', function(e) {
    var lat = e.latlng.lat.toFixed(5);
    var lon = e.latlng.lng.toFixed(5);
    document.getElementById('lat').value = lat;
    document.getElementById('lon').value = lon;
    var tz = guessTimezone(parseFloat(lat), parseFloat(lon));
    document.getElementById('timezone').value = tz;
    if (marker) { marker.setLatLng(e.latlng); } else { marker = L.marker(e.latlng).addTo(map); }
    marker.bindPopup('Lat: ' + lat + '<br>Lon: ' + lon + '<br>TZ: ' + tz).openPopup();
});

// Show existing marker on load
(function() {
    var lat = parseFloat(document.getElementById('lat').value);
    var lon = parseFloat(document.getElementById('lon').value);
    if (!isNaN(lat) && !isNaN(lon)) {
        var latlng = L.latLng(lat, lon);
        marker = L.marker(latlng).addTo(map);
        map.setView(latlng, 10);
    }
})();
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
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for type in types %}
                <tr>
                    <td>{{ type.id }}</td>
                    <td>{{ type.name }}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <a href="{{ url_for('web.edit_type', type_id=type.id) }}" class="btn btn-outline-warning" title="Edit">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button type="button" class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deleteTypeModal{{ type.id }}" title="Delete">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        <div class="modal fade" id="deleteTypeModal{{ type.id }}" tabindex="-1">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header"><h5 class="modal-title">Confirm Delete</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                                    <div class="modal-body">Are you sure you want to delete type "{{ type.name }}"?</div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                        <form method="POST" action="{{ url_for('web.delete_type', type_id=type.id) }}" style="display:inline">
                                            <button type="submit" class="btn btn-danger">Delete</button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </td>
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
    
    with open('templates/types/edit.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Edit Type{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-pencil me-2"></i>Edit Type</h1>
    <a href="{{ url_for('web.list_types') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>
<div class="card">
    <div class="card-body">
        <form method="POST">
            <div class="mb-3">
                <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="name" name="name" value="{{ type_obj.name or '' }}" required>
            </div>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-warning"><i class="bi bi-check-circle me-1"></i> Save Changes</button>
                <a href="{{ url_for('web.list_types') }}" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>

<div class="card border-danger mt-4">
    <div class="card-header bg-danger bg-opacity-25"><i class="bi bi-exclamation-triangle me-2"></i>Danger Zone</div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('web.delete_type', type_id=type_obj.id) }}" onsubmit="return confirm('Are you sure you want to permanently delete this type?')">
            <button type="submit" class="btn btn-outline-danger"><i class="bi bi-trash me-1"></i> Delete This Type</button>
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
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for property in properties %}
                <tr>
                    <td>{{ property.id }}</td>
                    <td>{{ property.name }}</td>
                    <td><span class="badge bg-info">{{ property.valueType }}</span></td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <a href="{{ url_for('web.edit_property', prop_id=property.id) }}" class="btn btn-outline-warning" title="Edit">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button type="button" class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deletePropModal{{ property.id }}" title="Delete">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        <div class="modal fade" id="deletePropModal{{ property.id }}" tabindex="-1">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header"><h5 class="modal-title">Confirm Delete</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                                    <div class="modal-body">Are you sure you want to delete property "{{ property.name }}"?</div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                        <form method="POST" action="{{ url_for('web.delete_property', prop_id=property.id) }}" style="display:inline">
                                            <button type="submit" class="btn btn-danger">Delete</button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </td>
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
    
    with open('templates/properties/edit.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Edit Property{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-pencil me-2"></i>Edit Property</h1>
    <a href="{{ url_for('web.list_properties') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>
<div class="card">
    <div class="card-body">
        <form method="POST">
            <div class="mb-3">
                <label for="name" class="form-label">Name <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="name" name="name" value="{{ prop.name or '' }}" required>
            </div>
            <div class="mb-3">
                <label for="valueType" class="form-label">Value Type <span class="text-danger">*</span></label>
                <select class="form-select" id="valueType" name="valueType" required>
                    <option value="">Select type...</option>
                    {% for vt in ['String', 'Integer', 'Float', 'Boolean', 'Date'] %}
                    <option value="{{ vt }}" {% if prop.valueType == vt %}selected{% endif %}>{{ vt }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-warning"><i class="bi bi-check-circle me-1"></i> Save Changes</button>
                <a href="{{ url_for('web.list_properties') }}" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>

<div class="card border-danger mt-4">
    <div class="card-header bg-danger bg-opacity-25"><i class="bi bi-exclamation-triangle me-2"></i>Danger Zone</div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('web.delete_property', prop_id=prop.id) }}" onsubmit="return confirm('Are you sure you want to permanently delete this property?')">
            <button type="submit" class="btn btn-outline-danger"><i class="bi bi-trash me-1"></i> Delete This Property</button>
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
                <th>Actions</th>
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
                <td>
                    <div class="btn-group btn-group-sm">
                        <a href="{{ url_for('web.edit_session', session_id=session.id) }}" class="btn btn-outline-warning" title="Edit">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <button type="button" class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deleteSessModal{{ session.id }}" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                    <div class="modal fade" id="deleteSessModal{{ session.id }}" tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header"><h5 class="modal-title">Confirm Delete</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                                <div class="modal-body">Are you sure you want to delete session "{{ session.number }}"?</div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                    <form method="POST" action="{{ url_for('web.delete_session', session_id=session.id) }}" style="display:inline">
                                        <button type="submit" class="btn btn-danger">Delete</button>
                                    </form>
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
                    <input type="text" class="form-control" id="number" name="number" value="{{ next_number or '' }}" placeholder="e.g. 1/2026" required>
                    <div class="form-text">Format: n/yyyy (auto-generated)</div>
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
                        <option value="None">None</option>
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

    with open('templates/sessions/edit.html', 'w') as f:
        f.write('''{% extends "layout.html" %}

{% block title %}Edit Session - Astronomy Observations{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2"><i class="bi bi-pencil me-2"></i>Edit Session</h1>
    <a href="{{ url_for('web.view_session', session_id=sess.id) }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back
    </a>
</div>

<div class="card">
    <div class="card-body">
        <form method="POST">
            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="number" class="form-label">Session Number</label>
                    <input type="text" class="form-control" id="number" name="number" value="{{ sess.number or '' }}" required>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="start_datetime" class="form-label">Start Date & Time</label>
                    <input type="datetime-local" class="form-control" id="start_datetime" name="start_datetime"
                           value="{{ sess.start_datetime.strftime('%Y-%m-%dT%H:%M') if sess.start_datetime else '' }}" required>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="end_datetime" class="form-label">End Date & Time</label>
                    <input type="datetime-local" class="form-control" id="end_datetime" name="end_datetime"
                           value="{{ sess.end_datetime.strftime('%Y-%m-%dT%H:%M') if sess.end_datetime else '' }}">
                </div>
            </div>

            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="cloud_percentage" class="form-label">Cloud Percentage (%)</label>
                    <input type="number" class="form-control" id="cloud_percentage" name="cloud_percentage" min="0" max="100"
                           value="{{ sess.cloud_percentage if sess.cloud_percentage is not none else '' }}">
                </div>
                <div class="col-md-4 mb-3">
                    <label for="cloud_type" class="form-label">Cloud Type</label>
                    <select class="form-select" id="cloud_type" name="cloud_type">
                        <option value="">-- Select --</option>
                        {% for ct in ['None','Cirrus','Cirrostratus','Cirrocumulus','Altostratus','Altocumulus','Stratus','Stratocumulus','Cumulus','Cumulonimbus','Nimbostratus'] %}
                        <option value="{{ ct }}" {% if sess.cloud_type == ct %}selected{% endif %}>{{ ct }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="light_pollution" class="form-label">Light Pollution (1-10)</label>
                    <input type="number" class="form-control" id="light_pollution" name="light_pollution" min="1" max="10"
                           value="{{ sess.light_pollution if sess.light_pollution is not none else '' }}">
                </div>
            </div>

            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="limiting_magnitude" class="form-label">Limiting Magnitude</label>
                    <input type="number" class="form-control" id="limiting_magnitude" name="limiting_magnitude" step="0.1"
                           value="{{ sess.limiting_magnitude if sess.limiting_magnitude is not none else '' }}">
                </div>
                <div class="col-md-4 mb-3">
                    <label for="moon_phase" class="form-label">Moon Phase</label>
                    <select class="form-select" id="moon_phase" name="moon_phase">
                        <option value="">-- Select --</option>
                        {% for mp in ['New Moon','Waxing Crescent','First Quarter','Waxing Gibbous','Full Moon','Waning Gibbous','Last Quarter','Waning Crescent'] %}
                        <option value="{{ mp }}" {% if sess.moon_phase == mp %}selected{% endif %}>{{ mp }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="moon_altitude" class="form-label">Moon Altitude (&deg;)</label>
                    <input type="number" class="form-control" id="moon_altitude" name="moon_altitude" step="0.1" min="-90" max="90"
                           value="{{ sess.moon_altitude if sess.moon_altitude is not none else '' }}">
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="instrument" class="form-label">Instrument</label>
                    <select class="form-select" id="instrument" name="instrument">
                        <option value="">-- None --</option>
                        {% for inst in instruments %}
                        <option value="{{ inst.id }}" {% if inst.id == sess.instrument %}selected{% endif %}>{{ inst.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>

            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-warning"><i class="bi bi-check-circle me-1"></i> Save Changes</button>
                <a href="{{ url_for('web.view_session', session_id=sess.id) }}" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>

<div class="card border-danger mt-4">
    <div class="card-header bg-danger bg-opacity-25"><i class="bi bi-exclamation-triangle me-2"></i>Danger Zone</div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('web.delete_session', session_id=sess.id) }}" onsubmit="return confirm('Are you sure you want to permanently delete this session?')">
            <button type="submit" class="btn btn-outline-danger"><i class="bi bi-trash me-1"></i> Delete This Session</button>
        </form>
    </div>
</div>
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

def create_simbad_search_template():
    """Create SIMBAD search and import template"""

    os.makedirs('templates/simbad', exist_ok=True)

    with open('templates/simbad/search.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}SIMBAD Search{% endblock %}
{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h1><i class="bi bi-globe me-2"></i>SIMBAD Search</h1>
    <a href="{{ url_for('web.list_objects') }}" class="btn btn-secondary">
        <i class="bi bi-arrow-left me-1"></i> Back to Objects
    </a>
</div>

<div class="row">
    <div class="col-lg-8">
        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-info-circle me-2"></i>About SIMBAD
            </div>
            <div class="card-body">
                <p>
                    <strong>SIMBAD</strong> (Set of Identifications, Measurements, and Bibliography for Astronomical Data)
                    is an astronomical database maintained by the <strong>Centre de Donn&eacute;es astronomiques de Strasbourg (CDS)</strong>.
                    It provides basic data, cross-identifications, bibliography and measurements for astronomical objects outside the solar system.
                </p>
                <p class="mb-0">
                    <a href="https://simbad.cds.unistra.fr/simbad/" target="_blank" class="text-primary">
                        <i class="bi bi-link-45deg"></i> https://simbad.cds.unistra.fr/simbad/
                    </a>
                </p>
            </div>
        </div>

        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-search me-2"></i>Search SIMBAD
            </div>
            <div class="card-body">
                <form method="POST" id="searchForm">
                    <input type="hidden" name="action" value="search" id="formAction">
                    <input type="hidden" name="import_name" value="" id="importName">

                    <div class="mb-3">
                        <label for="query" class="form-label">Search Query</label>
                        <input type="text" class="form-control" id="query" name="query"
                               value="{{ query or '' }}"
                               placeholder="e.g. R And, M31, NGC 7000, Algol, Betelgeuse">
                        <div class="form-text">Enter an object name, identifier, or wildcard pattern</div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="search_type" class="form-label">Search Type</label>
                            <select class="form-select" id="search_type" name="search_type">
                                <option value="name" {% if search_type == 'name' %}selected{% endif %}>Identifier (exact)</option>
                                <option value="wildcard" {% if search_type == 'wildcard' %}selected{% endif %}>Wildcard (pattern)</option>
                                <option value="type_variable" {% if search_type == 'type_variable' %}selected{% endif %}>Variable Stars</option>
                            </select>
                            <div class="form-text" id="searchTypeHelp">Search by exact name/identifier</div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="max_records" class="form-label">Max Results</label>
                            <input type="number" class="form-control" id="max_records" name="max_records"
                                   value="{{ max_records or 50 }}" min="1" max="200">
                        </div>
                    </div>

                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-primary" onclick="document.getElementById('formAction').value='search'">
                            <i class="bi bi-search me-1"></i> Search
                        </button>
                        {% if results %}
                        <button type="submit" class="btn btn-success" onclick="document.getElementById('formAction').value='import_all'">
                            <i class="bi bi-download me-1"></i> Import All Results ({{ results|length }})
                        </button>
                        {% endif %}
                    </div>
                </form>
            </div>
        </div>

        {% if results is not none %}
        <div class="card mb-4">
            <div class="card-header d-flex justify-content-between">
                <span><i class="bi bi-list-ul me-2"></i>Search Results</span>
                <span class="badge bg-info">{{ results|length }} found</span>
            </div>
            <div class="card-body p-0">
                {% if results %}
                <div class="table-responsive">
                    <table class="table table-dark table-hover mb-0">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Type</th>
                                <th>RA (J2000)</th>
                                <th>Dec (J2000)</th>
                                <th>Sp. Type</th>
                                <th>Mag V</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for obj in results %}
                            <tr>
                                <td>
                                    <strong>{{ obj.main_id }}</strong>
                                    {% if obj.alt_names %}
                                    <br><small class="text-muted">{{ obj.alt_names[:80] }}</small>
                                    {% endif %}
                                </td>
                                <td><span class="badge bg-secondary">{{ obj.otype_short or '?' }}</span></td>
                                <td><small>{{ obj.ra_hms }}</small></td>
                                <td><small>{{ obj.dec_dms }}</small></td>
                                <td><small>{{ obj.spectral_type or '-' }}</small></td>
                                <td>{{ obj.magnitude_v or '-' }}</td>
                                <td>
                                    <button class="btn btn-sm btn-success import-btn"
                                            onclick="importObject('{{ obj.main_id|e }}')">
                                        <i class="bi bi-plus-circle me-1"></i>Add
                                    </button>
                                </td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="p-4 text-center text-muted">
                    <i class="bi bi-search" style="font-size: 2rem;"></i>
                    <p class="mt-2">No results found. Try a different search query.</p>
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}
    </div>

    <div class="col-lg-4">
        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-graph-up me-2"></i>Database Statistics
            </div>
            <div class="card-body text-center">
                <div class="display-4 text-primary mb-2">{{ obj_count }}</div>
                <p class="text-muted mb-0">Objects in Database</p>
            </div>
        </div>

        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-lightbulb me-2"></i>Search Tips
            </div>
            <div class="card-body">
                <ul class="list-unstyled mb-0">
                    <li class="mb-2">
                        <strong>Identifier:</strong>
                        <span class="text-muted">Exact name lookup</span>
                        <br><code>R And</code>, <code>M31</code>, <code>NGC 7000</code>
                    </li>
                    <li class="mb-2">
                        <strong>Wildcard:</strong>
                        <span class="text-muted">Pattern with SQL LIKE</span>
                        <br><code>V* R %</code>, <code>NGC 70%</code>
                    </li>
                    <li class="mb-2">
                        <strong>Variable Stars:</strong>
                        <span class="text-muted">Search variable stars by pattern</span>
                        <br><code>R And</code>, <code>SS Cyg</code>
                    </li>
                </ul>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <i class="bi bi-stars me-2"></i>Quick Search Examples
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <button class="btn btn-outline-info btn-sm text-start" onclick="quickSearch('Betelgeuse', 'name')">
                        <i class="bi bi-star me-2"></i>Betelgeuse
                    </button>
                    <button class="btn btn-outline-info btn-sm text-start" onclick="quickSearch('M31', 'name')">
                        <i class="bi bi-stars me-2"></i>M31 (Andromeda Galaxy)
                    </button>
                    <button class="btn btn-outline-info btn-sm text-start" onclick="quickSearch('R And', 'name')">
                        <i class="bi bi-star me-2"></i>R And (Mira variable)
                    </button>
                    <button class="btn btn-outline-info btn-sm text-start" onclick="quickSearch('NGC 7000', 'name')">
                        <i class="bi bi-cloud me-2"></i>NGC 7000 (North America)
                    </button>
                    <button class="btn btn-outline-info btn-sm text-start" onclick="quickSearch('Algol', 'name')">
                        <i class="bi bi-star me-2"></i>Algol (Eclipsing binary)
                    </button>
                    <button class="btn btn-outline-info btn-sm text-start" onclick="quickSearch('V* R %', 'wildcard')">
                        <i class="bi bi-search me-2"></i>All R-named variables
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function importObject(name) {
    document.getElementById('importName').value = name;
    document.getElementById('formAction').value = 'import_one';
    document.getElementById('searchForm').submit();
}

function quickSearch(query, type) {
    document.getElementById('query').value = query;
    document.getElementById('search_type').value = type;
    document.getElementById('formAction').value = 'search';
    document.getElementById('searchForm').submit();
}

document.getElementById('search_type').addEventListener('change', function() {
    var help = document.getElementById('searchTypeHelp');
    switch(this.value) {
        case 'name':
            help.textContent = 'Search by exact name/identifier (e.g. M31, Algol, NGC 7000)';
            break;
        case 'wildcard':
            help.textContent = 'Use SQL LIKE patterns with % as wildcard (e.g. NGC 70%, V* R %)';
            break;
        case 'type_variable':
            help.textContent = 'Search for variable stars, optionally filter by name pattern';
            break;
    }
});
</script>
{% endblock %}''')

    print("✓ SIMBAD search template created")


def create_backup_template():
    """Create backup/restore template"""
    os.makedirs('templates/backup', exist_ok=True)

    with open('templates/backup/index.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Backup & Restore - Astronomy Observations{% endblock %}

{% block content %}
<h2><i class="bi bi-cloud-arrow-down me-2"></i>Backup & Restore</h2>
<p class="text-muted mb-4">Export your data, import from a backup file, or fully restore from a previous backup.</p>

<!-- Current Data Summary -->
<div class="card mb-4">
    <div class="card-header">
        <i class="bi bi-database me-1"></i> Current Data Summary
    </div>
    <div class="card-body">
        <div class="row text-center">
            <div class="col"><span class="d-block fs-4 fw-bold">{{ counts.get('types', 0) }}</span><small class="text-muted">Types</small></div>
            <div class="col"><span class="d-block fs-4 fw-bold">{{ counts.get('properties', 0) }}</span><small class="text-muted">Properties</small></div>
            <div class="col"><span class="d-block fs-4 fw-bold">{{ counts.get('places', 0) }}</span><small class="text-muted">Places</small></div>
            <div class="col"><span class="d-block fs-4 fw-bold">{{ counts.get('instruments', 0) }}</span><small class="text-muted">Instruments</small></div>
            <div class="col"><span class="d-block fs-4 fw-bold">{{ counts.get('objects', 0) }}</span><small class="text-muted">Objects</small></div>
            <div class="col"><span class="d-block fs-4 fw-bold">{{ counts.get('sessions', 0) }}</span><small class="text-muted">Sessions</small></div>
            <div class="col"><span class="d-block fs-4 fw-bold">{{ counts.get('observations', 0) }}</span><small class="text-muted">Observations</small></div>
        </div>
    </div>
</div>

<div class="row">
    <!-- Export -->
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-header">
                <i class="bi bi-download me-1"></i> Export Data
            </div>
            <div class="card-body d-flex flex-column">
                <p>Download all your data as a JSON file. This includes types, properties, places, instruments, objects, sessions, and observations.</p>
                <div class="mt-auto">
                    <a href="{{ url_for('web.backup_export') }}" class="btn btn-primary w-100">
                        <i class="bi bi-download me-1"></i> Download Backup
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Import (Merge) -->
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-header">
                <i class="bi bi-upload me-1"></i> Import Data
            </div>
            <div class="card-body d-flex flex-column">
                <p>Merge data from a backup file into your current database. Existing records are kept; only new records are added.</p>
                <form method="POST" action="{{ url_for('web.backup_import') }}" enctype="multipart/form-data" class="mt-auto">
                    <div class="mb-3">
                        <input type="file" class="form-control" name="backup_file" accept=".json" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="bi bi-upload me-1"></i> Import & Merge
                    </button>
                </form>
            </div>
        </div>
    </div>

    <!-- Restore -->
    <div class="col-md-4 mb-4">
        <div class="card h-100 border-danger">
            <div class="card-header bg-danger bg-opacity-25">
                <i class="bi bi-arrow-counterclockwise me-1"></i> Restore Data
            </div>
            <div class="card-body d-flex flex-column">
                <p><strong class="text-danger">Warning:</strong> This will delete all current data and replace it with the contents of the backup file.</p>
                <form method="POST" action="{{ url_for('web.backup_restore') }}" enctype="multipart/form-data" class="mt-auto" id="restoreForm">
                    <div class="mb-3">
                        <input type="file" class="form-control" name="backup_file" accept=".json" required>
                    </div>
                    <button type="button" class="btn btn-danger w-100" data-bs-toggle="modal" data-bs-target="#confirmRestoreModal">
                        <i class="bi bi-arrow-counterclockwise me-1"></i> Restore from Backup
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

<!-- Confirm Restore Modal -->
<div class="modal fade" id="confirmRestoreModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title text-danger"><i class="bi bi-exclamation-triangle me-2"></i>Confirm Restore</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>This will <strong>permanently delete all current data</strong> and replace it with the backup file contents.</p>
                <p>Are you sure you want to continue?</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-danger" id="confirmRestoreBtn">Yes, Restore</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.getElementById('confirmRestoreBtn').addEventListener('click', function() {
    document.getElementById('restoreForm').submit();
});
</script>
{% endblock %}''')

    print("✓ Backup template created")


def create_icq_export_template():
    """Create ICQ export template"""
    os.makedirs('templates/export', exist_ok=True)

    with open('templates/export/icq.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Export ICQ - Astronomy Observations{% endblock %}

{% block extra_css %}
<style>
    .icq-line {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        background-color: #0d1117;
        color: #58a6ff;
        padding: 2px 6px;
        white-space: pre;
        letter-spacing: 0.5px;
    }
    .icq-preview {
        background-color: #0d1117;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 6px;
        padding: 1rem;
        overflow-x: auto;
        max-height: 500px;
        overflow-y: auto;
    }
    .icq-header-row {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.75rem;
        color: rgba(255,255,255,0.35);
        white-space: pre;
        letter-spacing: 0.5px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 4px;
        margin-bottom: 8px;
    }
    .column-guide {
        font-size: 0.78rem;
        color: rgba(255,255,255,0.5);
    }
</style>
{% endblock %}

{% block content %}
<h2><i class="bi bi-file-earmark-text me-2"></i>Export Comet Observations (ICQ Format)</h2>
<p class="text-muted mb-4">Export your comet observations in the <a href="https://www.cobs.si/help/icq_format/" target="_blank" class="text-info">International Comet Quarterly (ICQ)</a> standard 80-column format.</p>

<div class="row">
    <!-- Filter Form -->
    <div class="col-md-4 mb-4">
        <div class="card">
            <div class="card-header">
                <i class="bi bi-funnel me-1"></i> Filter Observations
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('web.export_icq') }}">
                    <div class="mb-3">
                        <label class="form-label">Comet</label>
                        <select name="comet_id" class="form-select">
                            <option value="all">All Comets</option>
                            {% for comet in comet_objects %}
                            <option value="{{ comet.id }}">{{ comet.name }} ({{ comet.desination }})</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Date From</label>
                        <input type="date" name="date_from" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Date To</label>
                        <input type="date" name="date_to" class="form-control">
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="bi bi-search me-1"></i> Preview ICQ Output
                    </button>
                </form>
            </div>
        </div>

        <!-- ICQ Column Reference -->
        <div class="card mt-3">
            <div class="card-header">
                <i class="bi bi-info-circle me-1"></i> ICQ Column Reference
            </div>
            <div class="card-body column-guide">
                <table class="table table-sm mb-0" style="font-size: 0.78rem;">
                    <thead><tr><th>Cols</th><th>Field</th></tr></thead>
                    <tbody>
                        <tr><td>1-3</td><td>Periodic comet number</td></tr>
                        <tr><td>4-11</td><td>Comet designation</td></tr>
                        <tr><td>12-17</td><td>Year + Month</td></tr>
                        <tr><td>18-23</td><td>Day.fraction</td></tr>
                        <tr><td>27</td><td>Magnitude method</td></tr>
                        <tr><td>28-33</td><td>Magnitude</td></tr>
                        <tr><td>34-35</td><td>Reference catalog</td></tr>
                        <tr><td>36-40</td><td>Aperture (cm)</td></tr>
                        <tr><td>41</td><td>Instrument type</td></tr>
                        <tr><td>44-47</td><td>Power/magnification</td></tr>
                        <tr><td>49-54</td><td>Coma diameter</td></tr>
                        <tr><td>56-57</td><td>DC (0-9)</td></tr>
                        <tr><td>59-64</td><td>Tail length</td></tr>
                        <tr><td>65-67</td><td>Position angle</td></tr>
                        <tr><td>76-80</td><td>Observer code</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Results -->
    <div class="col-md-8">
        {% if exported %}
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span><i class="bi bi-file-code me-1"></i> ICQ Output — {{ icq_lines|length }} observation{{ 's' if icq_lines|length != 1 }} exported</span>
                {% if icq_lines %}
                <form method="POST" action="{{ url_for('web.export_icq_download') }}" class="d-inline">
                    <input type="hidden" name="comet_id" value="{{ request.form.get('comet_id', 'all') }}">
                    <input type="hidden" name="date_from" value="{{ request.form.get('date_from', '') }}">
                    <input type="hidden" name="date_to" value="{{ request.form.get('date_to', '') }}">
                    <button type="submit" class="btn btn-sm btn-success">
                        <i class="bi bi-download me-1"></i> Download .txt
                    </button>
                </form>
                {% endif %}
            </div>
            <div class="card-body">
                {% if icq_lines %}
                <div class="icq-preview">
                    <div class="icq-header-row">Col: 1  4   8 12  16 18    27 28    3436   41  44  49    5556 59    6567  76</div>
                    {% for entry in icq_lines %}
                    <div class="mb-1" title="{{ entry.comet_name }} — {{ entry.date }}">
                        <code class="icq-line">{{ entry.line }}</code>
                        <small class="text-muted ms-2">{{ entry.comet_name }}</small>
                    </div>
                    {% endfor %}
                </div>

                <div class="mt-3">
                    <h6>Raw Text (for copy/paste):</h6>
                    <textarea class="form-control" rows="6" readonly onclick="this.select()">{% for entry in icq_lines %}{{ entry.line }}
{% endfor %}</textarea>
                </div>
                {% else %}
                <div class="text-center text-muted py-4">
                    <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                    <p class="mt-2">No comet observations with COBS data found for the selected filters.</p>
                    <p class="small">Make sure your comet observations include COBS fields (magnitude, coma, etc.).</p>
                </div>
                {% endif %}
            </div>
        </div>
        {% else %}
        <div class="card">
            <div class="card-body text-center text-muted py-5">
                <i class="bi bi-file-earmark-text" style="font-size: 4rem;"></i>
                <h5 class="mt-3">Select filters and click Preview</h5>
                <p>Choose a comet and/or date range, then preview the ICQ formatted output before downloading.</p>
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}''')

    print("✓ ICQ export template created")


def create_aavso_export_template():
    """Create AAVSO Visual format export template"""
    os.makedirs('templates/export', exist_ok=True)

    with open('templates/export/aavso.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Export AAVSO - Astronomy Observations{% endblock %}

{% block extra_css %}
<style>
    .aavso-line {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        background-color: #0d1117;
        color: #7ee787;
        padding: 2px 6px;
        white-space: pre;
    }
    .aavso-header {
        color: #d2a8ff;
    }
    .aavso-preview {
        background-color: #0d1117;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 6px;
        padding: 1rem;
        overflow-x: auto;
        max-height: 500px;
        overflow-y: auto;
    }
</style>
{% endblock %}

{% block content %}
<h2><i class="bi bi-file-earmark-ruled me-2"></i>Export Variable Star Observations (AAVSO Format)</h2>
<p class="text-muted mb-4">Export your variable star observations in the <a href="https://www.aavso.org/aavso-visual-file-format" target="_blank" class="text-info">AAVSO Visual File Format</a> for submission to the AAVSO International Database.</p>

{% if observer_code %}
<div class="alert alert-info py-2">
    <i class="bi bi-person-badge me-1"></i> AAVSO Observer Code: <strong>{{ observer_code }}</strong>
</div>
{% else %}
<div class="alert alert-warning py-2">
    <i class="bi bi-exclamation-triangle me-1"></i> No AAVSO observer code set. <a href="{{ url_for('web.user_settings') }}">Set it in your profile settings</a> to include it in exports.
</div>
{% endif %}

<div class="row">
    <!-- Filter Form -->
    <div class="col-md-4 mb-4">
        <div class="card">
            <div class="card-header">
                <i class="bi bi-funnel me-1"></i> Filter Observations
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('web.export_aavso') }}">
                    <div class="mb-3">
                        <label class="form-label">Variable Star</label>
                        <select name="star_id" class="form-select">
                            <option value="all">All Variable Stars</option>
                            {% for star in vs_objects %}
                            <option value="{{ star.id }}">{{ star.name }}{% if star.desination %} ({{ star.desination }}){% endif %}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Date From</label>
                        <input type="date" name="date_from" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Date To</label>
                        <input type="date" name="date_to" class="form-control">
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="bi bi-search me-1"></i> Preview AAVSO Output
                    </button>
                </form>
            </div>
        </div>

        <!-- AAVSO Format Reference -->
        <div class="card mt-3">
            <div class="card-header">
                <i class="bi bi-info-circle me-1"></i> AAVSO Visual Format Fields
            </div>
            <div class="card-body" style="font-size: 0.85rem;">
                <table class="table table-sm mb-0">
                    <thead><tr><th>Field</th><th>Description</th></tr></thead>
                    <tbody>
                        <tr><td><code>NAME</code></td><td>Star designation</td></tr>
                        <tr><td><code>DATE</code></td><td>Julian Date</td></tr>
                        <tr><td><code>MAG</code></td><td>Magnitude estimate</td></tr>
                        <tr><td><code>COMMENTCODE</code></td><td>Comment code</td></tr>
                        <tr><td><code>COMP1</code></td><td>Comparison star 1</td></tr>
                        <tr><td><code>COMP2</code></td><td>Comparison star 2</td></tr>
                        <tr><td><code>CHART</code></td><td>Chart identification</td></tr>
                        <tr><td><code>NOTES</code></td><td>Additional comments</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Results -->
    <div class="col-md-8">
        {% if exported %}
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span><i class="bi bi-file-code me-1"></i> AAVSO Output &mdash; {{ aavso_lines|length }} observation{{ 's' if aavso_lines|length != 1 }} exported</span>
                {% if aavso_lines %}
                <form method="POST" action="{{ url_for('web.export_aavso_download') }}" class="d-inline">
                    <input type="hidden" name="star_id" value="{{ request.form.get('star_id', 'all') }}">
                    <input type="hidden" name="date_from" value="{{ request.form.get('date_from', '') }}">
                    <input type="hidden" name="date_to" value="{{ request.form.get('date_to', '') }}">
                    <button type="submit" class="btn btn-sm btn-success">
                        <i class="bi bi-download me-1"></i> Download .txt
                    </button>
                </form>
                {% endif %}
            </div>
            <div class="card-body">
                {% if aavso_lines %}
                <!-- Preview Table -->
                <div class="table-responsive mb-3">
                    <table class="table table-sm table-striped table-hover">
                        <thead>
                            <tr>
                                <th>Star</th>
                                <th>Date</th>
                                <th>JD</th>
                                <th>Mag</th>
                                <th>Comp1</th>
                                <th>Comp2</th>
                                <th>Chart</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for entry in aavso_lines %}
                            <tr>
                                <td>{{ entry.star_name }}</td>
                                <td>{{ entry.date }}</td>
                                <td><code>{{ entry.jd }}</code></td>
                                <td><strong>{{ entry.magnitude }}</strong></td>
                                <td>{{ entry.comp1 or 'na' }}</td>
                                <td>{{ entry.comp2 or 'na' }}</td>
                                <td>{{ entry.chart or 'na' }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                <!-- Raw AAVSO File Preview -->
                <h6>File Preview:</h6>
                <div class="aavso-preview">
                    <div><code class="aavso-line aavso-header">#TYPE=Visual</code></div>
                    <div><code class="aavso-line aavso-header">#OBSCODE={{ observer_code or 'na' }}</code></div>
                    <div><code class="aavso-line aavso-header">#SOFTWARE=Astronomy Observations App</code></div>
                    <div><code class="aavso-line aavso-header">#DELIM=,</code></div>
                    <div><code class="aavso-line aavso-header">#DATE=JD</code></div>
                    <div><code class="aavso-line aavso-header">#OBSTYPE=Visual</code></div>
                    {% for entry in aavso_lines %}
                    <div><code class="aavso-line">{{ entry.designation or entry.star_name }},{{ entry.jd }},{{ entry.magnitude or 'na' }},na,{{ entry.comp1 or 'na' }},{{ entry.comp2 or 'na' }},{{ entry.chart or 'na' }},na</code></div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="text-center text-muted py-4">
                    <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                    <p class="mt-2">No variable star observations with AAVSO data found for the selected filters.</p>
                    <p class="small">Make sure your variable star observations include AAVSO fields (magnitude, comparison stars, etc.).</p>
                </div>
                {% endif %}
            </div>
        </div>
        {% else %}
        <div class="card">
            <div class="card-body text-center text-muted py-5">
                <i class="bi bi-file-earmark-ruled" style="font-size: 4rem;"></i>
                <h5 class="mt-3">Select filters and click Preview</h5>
                <p>Choose a variable star and/or date range, then preview the AAVSO formatted output before downloading.</p>
                <p class="small">The exported file follows the <strong>AAVSO Visual File Format</strong> and can be submitted directly to the <a href="https://www.aavso.org" target="_blank" class="text-info">AAVSO</a> database.</p>
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}''')

    print("✓ AAVSO export template created")


def create_cobs_submit_template():
    """Create COBS submission template"""
    os.makedirs('templates/cobs', exist_ok=True)

    with open('templates/cobs/submit.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Submit to COBS - Astronomy Observations{% endblock %}

{% block content %}
<h2><i class="bi bi-cloud-upload me-2"></i>Submit Observations to COBS</h2>
<p class="text-muted mb-4">Submit your comet observations directly to the <a href="https://www.cobs.si" target="_blank" class="text-info">Comet OBServation database (COBS)</a>.</p>

{% if step == 'filter' %}
<!-- Step 1: Filter observations -->
<div class="row">
    <div class="col-md-6 mx-auto">
        <div class="card">
            <div class="card-header">
                <i class="bi bi-funnel me-1"></i> Step 1: Select Observations
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('web.cobs_submit') }}">
                    <input type="hidden" name="step" value="preview">
                    <div class="mb-3">
                        <label class="form-label">Comet</label>
                        <select name="comet_id" class="form-select">
                            <option value="all">All Comets</option>
                            {% for comet in comet_objects %}
                            <option value="{{ comet.id }}">{{ comet.name }} ({{ comet.desination }})</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Date From</label>
                        <input type="date" name="date_from" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Date To</label>
                        <input type="date" name="date_to" class="form-control">
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="bi bi-arrow-right me-1"></i> Preview & Match Comets
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

{% elif step == 'preview' %}
<!-- Step 2: Preview and match COBS comets -->
<form method="POST" action="{{ url_for('web.cobs_submit') }}">
    <input type="hidden" name="step" value="submit">

    {% if preview_data %}
    <div class="alert alert-info">
        <i class="bi bi-info-circle me-1"></i>
        Found <strong>{{ preview_data|length }}</strong> comet observations with COBS data.
        Match each observation to the correct COBS comet, then click Submit.
    </div>

    <div class="table-responsive">
        <table class="table table-sm table-hover">
            <thead>
                <tr>
                    <th><input type="checkbox" id="selectAll" checked></th>
                    <th>Comet</th>
                    <th>Date</th>
                    <th>Mag</th>
                    <th>Coma</th>
                    <th>DC</th>
                    <th>Tail</th>
                    <th>PA</th>
                    <th>COBS Comet Match</th>
                </tr>
            </thead>
            <tbody>
                {% for obs in preview_data %}
                <tr>
                    <td><input type="checkbox" name="obs_ids" value="{{ obs.obs_id }}" checked></td>
                    <td>
                        <strong>{{ obs.comet_name }}</strong>
                        <br><small class="text-muted">{{ obs.designation }}</small>
                    </td>
                    <td>{{ obs.date }}</td>
                    <td><strong>{{ obs.magnitude }}</strong></td>
                    <td>{{ obs.coma }}</td>
                    <td>{{ obs.dc }}</td>
                    <td>{{ obs.tail }}</td>
                    <td>{{ obs.pa }}</td>
                    <td>
                        <select name="cobs_comet_{{ obs.obs_id }}" class="form-select form-select-sm" required>
                            <option value="">-- Select COBS comet --</option>
                            {% for cc in cobs_comets %}
                            <option value="{{ cc.id }}" {{ 'selected' if cc.id == obs.matched_cobs_id else '' }}>{{ cc.name }}</option>
                            {% endfor %}
                        </select>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="d-flex justify-content-between mt-3">
        <a href="{{ url_for('web.cobs_submit') }}" class="btn btn-secondary">
            <i class="bi bi-arrow-left me-1"></i> Back
        </a>
        <button type="submit" class="btn btn-success" onclick="return confirm('Submit selected observations to COBS?')">
            <i class="bi bi-cloud-upload me-1"></i> Submit to COBS
        </button>
    </div>
    {% else %}
    <div class="text-center text-muted py-5">
        <i class="bi bi-inbox" style="font-size: 3rem;"></i>
        <p class="mt-2">No comet observations with COBS data found for the selected filters.</p>
        <a href="{{ url_for('web.cobs_submit') }}" class="btn btn-secondary mt-2">
            <i class="bi bi-arrow-left me-1"></i> Back
        </a>
    </div>
    {% endif %}
</form>

{% elif step == 'results' %}
<!-- Step 3: Submission results -->
<div class="card">
    <div class="card-header">
        <i class="bi bi-check-circle me-1"></i> Submission Results
    </div>
    <div class="card-body">
        <table class="table table-sm">
            <thead>
                <tr><th>Comet</th><th>Date</th><th>Status</th><th>Message</th></tr>
            </thead>
            <tbody>
                {% for r in submitted_results %}
                <tr class="{{ 'table-success' if r.success else 'table-danger' }}">
                    <td>{{ r.comet_name }}</td>
                    <td>{{ r.date }}</td>
                    <td>
                        {% if r.success %}
                        <span class="badge bg-success"><i class="bi bi-check"></i> OK</span>
                        {% else %}
                        <span class="badge bg-danger"><i class="bi bi-x"></i> Failed</span>
                        {% endif %}
                    </td>
                    <td>{{ r.msg }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <a href="{{ url_for('web.cobs_submit') }}" class="btn btn-primary mt-2">
            <i class="bi bi-arrow-left me-1"></i> Submit More
        </a>
    </div>
</div>
{% endif %}
{% endblock %}

{% block extra_js %}
<script>
// Select all checkbox
var selectAll = document.getElementById('selectAll');
if (selectAll) {
    selectAll.addEventListener('change', function() {
        document.querySelectorAll('input[name="obs_ids"]').forEach(function(cb) {
            cb.checked = selectAll.checked;
        });
    });
}
</script>
{% endblock %}''')

    print("✓ COBS submit template created")


def create_aavso_submit_template():
    """Create AAVSO observation submission template."""
    import os
    os.makedirs('templates/aavso', exist_ok=True)

    with open('templates/aavso/submit.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Submit to AAVSO - Astronomy Observations{% endblock %}

{% block content %}
<h2><i class="bi bi-star me-2 text-warning"></i>Submit Observations to AAVSO</h2>
<p class="text-muted mb-4">Submit your variable star observations directly to the <a href="https://www.aavso.org" target="_blank" class="text-info">AAVSO WebObs</a>.</p>

{% if step == 'filter' %}
<!-- Step 1: Filter observations -->
<div class="row">
    <div class="col-md-6 mx-auto">
        <div class="card">
            <div class="card-header">
                <i class="bi bi-funnel me-1"></i> Step 1: Select Observations
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('web.aavso_submit') }}">
                    <input type="hidden" name="step" value="preview">
                    <div class="mb-3">
                        <label class="form-label">Variable Star</label>
                        <select name="star_id" class="form-select">
                            <option value="all">All Variable Stars</option>
                            {% for star in varstar_objects %}
                            <option value="{{ star.id }}">{{ star.name }}{% if star.desination %} ({{ star.desination }}){% endif %}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Date From</label>
                        <input type="date" name="date_from" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Date To</label>
                        <input type="date" name="date_to" class="form-control">
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="bi bi-arrow-right me-1"></i> Preview Observations
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

{% elif step == 'preview' %}
<!-- Step 2: Preview and submit -->
<form method="POST" action="{{ url_for('web.aavso_submit') }}">
    <input type="hidden" name="step" value="submit">

    {% if preview_data %}
    <div class="alert alert-info">
        <i class="bi bi-info-circle me-1"></i>
        Found <strong>{{ preview_data|length }}</strong> variable star observations with AAVSO data.
        Review and click Submit.
    </div>

    <div class="table-responsive">
        <table class="table table-sm table-hover">
            <thead>
                <tr>
                    <th><input type="checkbox" id="selectAll" checked></th>
                    <th>Star</th>
                    <th>Date (UTC)</th>
                    <th>JD</th>
                    <th>Mag</th>
                    <th>Comp1</th>
                    <th>Comp2</th>
                    <th>Chart</th>
                    <th>Band</th>
                    <th>Method</th>
                </tr>
            </thead>
            <tbody>
                {% for obs in preview_data %}
                <tr>
                    <td><input type="checkbox" name="obs_ids" value="{{ obs.obs_id }}" checked></td>
                    <td>
                        <strong>{{ obs.star_name }}</strong>
                        {% if obs.auid %}<br><small class="text-muted">{{ obs.auid }}</small>{% endif %}
                    </td>
                    <td>{{ obs.date }}</td>
                    <td><small>{{ obs.jd }}</small></td>
                    <td><strong>{{ obs.magnitude }}</strong></td>
                    <td>{{ obs.comp1 }}</td>
                    <td>{{ obs.comp2 }}</td>
                    <td>{{ obs.chart }}</td>
                    <td>{{ obs.band }}</td>
                    <td>{{ obs.method }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="d-flex justify-content-between mt-3">
        <a href="{{ url_for('web.aavso_submit') }}" class="btn btn-secondary">
            <i class="bi bi-arrow-left me-1"></i> Back
        </a>
        <button type="submit" class="btn btn-success" onclick="return confirm('Submit selected observations to AAVSO?')">
            <i class="bi bi-cloud-upload me-1"></i> Submit to AAVSO
        </button>
    </div>
    {% else %}
    <div class="text-center text-muted py-5">
        <i class="bi bi-inbox" style="font-size: 3rem;"></i>
        <p class="mt-2">No variable star observations with AAVSO data found for the selected filters.</p>
        <a href="{{ url_for('web.aavso_submit') }}" class="btn btn-secondary mt-2">
            <i class="bi bi-arrow-left me-1"></i> Back
        </a>
    </div>
    {% endif %}
</form>

{% elif step == 'results' %}
<!-- Step 3: Submission results -->
<div class="card">
    <div class="card-header">
        <i class="bi bi-check-circle me-1"></i> Submission Results
    </div>
    <div class="card-body">
        <table class="table table-sm">
            <thead>
                <tr><th>Star</th><th>Date</th><th>Status</th><th>Message</th></tr>
            </thead>
            <tbody>
                {% for r in submitted_results %}
                <tr class="{{ 'table-success' if r.success else 'table-danger' }}">
                    <td>{{ r.star_name }}</td>
                    <td>{{ r.date }}</td>
                    <td>
                        {% if r.success %}
                        <span class="badge bg-success"><i class="bi bi-check"></i> OK</span>
                        {% else %}
                        <span class="badge bg-danger"><i class="bi bi-x"></i> Failed</span>
                        {% endif %}
                    </td>
                    <td>{{ r.msg }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <a href="{{ url_for('web.aavso_submit') }}" class="btn btn-primary mt-2">
            <i class="bi bi-arrow-left me-1"></i> Submit More
        </a>
    </div>
</div>
{% endif %}
{% endblock %}

{% block extra_js %}
<script>
var selectAll = document.getElementById('selectAll');
if (selectAll) {
    selectAll.addEventListener('change', function() {
        document.querySelectorAll('input[name="obs_ids"]').forEach(function(cb) {
            cb.checked = selectAll.checked;
        });
    });
}
</script>
{% endblock %}''')

    print("✓ AAVSO submit template created")


if __name__ == '__main__':
    create_complete_templates()
    create_comet_import_template()
    create_vsx_import_template()
    create_vsx_charts_template()
    create_simbad_search_template()
    create_backup_template()
    create_icq_export_template()
    create_aavso_export_template()
    create_cobs_submit_template()
    create_aavso_submit_template()