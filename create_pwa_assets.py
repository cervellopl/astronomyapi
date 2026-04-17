"""
Create Progressive Web App (PWA) assets for Android mobile support.
Generates: manifest.json, service worker, real PNG app icons, mobile CSS.
"""

import os
import json
import math


def create_pwa_assets():
    """Create all PWA assets in static/ directory."""
    print("Creating PWA assets for mobile Android support...")

    os.makedirs('static', exist_ok=True)
    os.makedirs('static/icons', exist_ok=True)

    # =========================================================================
    # 1. Generate real PNG icons with Pillow
    # =========================================================================
    _create_icons()

    # =========================================================================
    # 2. Web App Manifest
    # =========================================================================
    manifest = {
        "name": "Astronomy Observations",
        "short_name": "AstroObs",
        "description": "Track and manage astronomical observations - stars, comets, sessions and more.",
        "start_url": "/web",
        "scope": "/",
        "display": "standalone",
        "orientation": "any",
        "background_color": "#0a0e27",
        "theme_color": "#1a1f3a",
        "icons": [
            {"src": "/static/icons/icon-72.png", "sizes": "72x72", "type": "image/png"},
            {"src": "/static/icons/icon-96.png", "sizes": "96x96", "type": "image/png"},
            {"src": "/static/icons/icon-128.png", "sizes": "128x128", "type": "image/png"},
            {"src": "/static/icons/icon-144.png", "sizes": "144x144", "type": "image/png"},
            {"src": "/static/icons/icon-152.png", "sizes": "152x152", "type": "image/png"},
            {"src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/static/icons/icon-384.png", "sizes": "384x384", "type": "image/png"},
            {"src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
        "categories": ["education", "utilities"],
        "lang": "en",
        "dir": "ltr",
    }

    with open('static/manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    print("  manifest.json created")

    # =========================================================================
    # 3. Service Worker
    # =========================================================================
    sw_content = r"""// Astronomy Observations - Service Worker
const CACHE_NAME = 'astro-obs-v2';
const STATIC_ASSETS = [
    '/web',
    '/static/mobile.css',
    '/static/icons/icon-192.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js',
];

// Install: cache static assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Fetch: network-first for API/pages, cache-first for static
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // Skip non-GET requests
    if (event.request.method !== 'GET') return;

    // Cache-first for CDN assets and static files
    if (url.pathname.startsWith('/static/') ||
        url.hostname === 'cdn.jsdelivr.net') {
        event.respondWith(
            caches.match(event.request).then(cached => {
                return cached || fetch(event.request).then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    }
                    return response;
                });
            })
        );
        return;
    }

    // Network-first for everything else (pages, API)
    event.respondWith(
        fetch(event.request)
            .then(response => {
                if (response.ok && url.pathname.startsWith('/web')) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                }
                return response;
            })
            .catch(() => caches.match(event.request))
    );
});
"""

    with open('static/sw.js', 'w') as f:
        f.write(sw_content)
    print("  sw.js (service worker) created")

    # =========================================================================
    # 4. Mobile CSS
    # =========================================================================
    mobile_css = """/* =============================================
   Astronomy Observations - Mobile / PWA Styles
   ============================================= */

/* --- Mobile Navigation --- */
@media (max-width: 767.98px) {
    /* Hide desktop sidebar on mobile */
    .sidebar {
        position: fixed;
        top: 56px;
        left: -280px;
        width: 260px;
        height: calc(100% - 56px);
        z-index: 1050;
        transition: left 0.3s ease;
        padding-top: 0 !important;
    }
    .sidebar.show {
        left: 0;
        box-shadow: 4px 0 20px rgba(0,0,0,0.5);
    }

    /* Main content full width on mobile */
    .main-content {
        margin-left: 0 !important;
        padding: 1rem !important;
    }

    body {
        padding-top: 56px;
    }

    /* Mobile hamburger button */
    .mobile-menu-btn {
        display: inline-flex !important;
    }

    /* Backdrop overlay */
    .sidebar-backdrop {
        display: none;
        position: fixed;
        top: 56px;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 1040;
    }
    .sidebar-backdrop.show {
        display: block;
    }

    /* Responsive tables */
    .table-responsive-wrapper {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }

    /* Cards: reduce padding on mobile */
    .card-body {
        padding: 0.75rem;
    }

    /* Dashboard stats: 2 columns on mobile */
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
    }
    .stats-grid .card {
        margin-bottom: 0 !important;
    }

    /* Forms: full width inputs */
    .form-control, .form-select {
        font-size: 16px !important; /* Prevent iOS zoom */
    }

    /* Navbar adjustments */
    .navbar {
        padding: 0.25rem 0.5rem;
    }
    .navbar-brand {
        font-size: 1.1rem !important;
    }

    /* Hide long text on mobile nav */
    .nav-link {
        font-size: 0.9rem;
        padding: 0.6rem 1rem;
    }

    /* Action buttons stack on mobile */
    .btn-group-mobile {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .btn-group-mobile .btn {
        width: 100%;
    }

    /* ICQ/AAVSO preview scroll */
    .icq-preview, .aavso-preview {
        font-size: 0.7rem;
    }

    /* Backup page: stack columns */
    .backup-cards .col-md-4 {
        margin-bottom: 1rem;
    }
}

/* --- Tablet adjustments --- */
@media (min-width: 768px) and (max-width: 991.98px) {
    .sidebar {
        width: 200px;
    }
    .main-content {
        margin-left: 200px !important;
    }
}

/* --- Desktop: hide mobile elements --- */
@media (min-width: 768px) {
    .mobile-menu-btn {
        display: none !important;
    }
    .sidebar-backdrop {
        display: none !important;
    }
}

/* --- PWA standalone mode tweaks --- */
@media (display-mode: standalone) {
    /* Extra top padding for Android status bar */
    body {
        padding-top: env(safe-area-inset-top, 0px);
    }
    .navbar {
        padding-top: env(safe-area-inset-top, 0px);
    }
}

/* --- Touch-friendly improvements --- */
@media (pointer: coarse) {
    /* Larger tap targets */
    .nav-link {
        min-height: 44px;
        display: flex;
        align-items: center;
    }
    .btn {
        min-height: 44px;
    }
    .table td, .table th {
        padding: 0.6rem 0.5rem;
    }

    /* Easier to tap close buttons */
    .btn-close {
        padding: 0.75rem;
    }
}

/* --- Pull-to-refresh indicator --- */
.refresh-indicator {
    display: none;
    text-align: center;
    padding: 0.5rem;
    color: #4dabf7;
    font-size: 0.85rem;
}
.refresh-indicator.visible {
    display: block;
}

/* --- Install banner --- */
.pwa-install-banner {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #1a1f3a, #2d3561);
    color: #fff;
    padding: 1rem;
    z-index: 2000;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.4);
    border-top: 1px solid rgba(77,171,247,0.3);
}
.pwa-install-banner.show {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.pwa-install-banner .btn-install {
    background: #4dabf7;
    border: none;
    color: #fff;
    padding: 0.5rem 1.5rem;
    border-radius: 6px;
    font-weight: 600;
    white-space: nowrap;
}
.pwa-install-banner .btn-dismiss {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.3);
    color: rgba(255,255,255,0.7);
    padding: 0.5rem 1rem;
    border-radius: 6px;
    margin-left: 0.5rem;
}
"""

    with open('static/mobile.css', 'w') as f:
        f.write(mobile_css)
    print("  mobile.css created")

    print("PWA assets created successfully!")


def _create_icons():
    """Generate real PNG app icons using Pillow."""
    from PIL import Image, ImageDraw

    def _draw_icon(size):
        """Draw the astronomy app icon at the given size."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        s = size  # shorthand

        # Background with rounded corners
        corner_r = int(s * 0.156)  # ~80/512
        draw.rounded_rectangle(
            [0, 0, s - 1, s - 1],
            radius=corner_r,
            fill=(26, 31, 58),    # #1a1f3a
        )
        # Gradient effect: lighter bottom-right overlay
        for i in range(s):
            alpha = int(30 * (i / s))
            draw.line([(i, 0), (s, s - i)], fill=(45, 53, 97, alpha))

        # Stars (small dots)
        stars = [
            (0.234, 0.195, 0.012), (0.742, 0.156, 0.008),
            (0.820, 0.390, 0.010), (0.176, 0.586, 0.006),
            (0.390, 0.117, 0.006), (0.879, 0.684, 0.008),
            (0.140, 0.430, 0.005), (0.600, 0.070, 0.005),
            (0.930, 0.500, 0.004), (0.300, 0.850, 0.005),
        ]
        for sx, sy, sr in stars:
            r = max(1, int(sr * s))
            cx, cy = int(sx * s), int(sy * s)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 180))

        # Telescope tube (rotated -30 degrees from center)
        cx, cy = int(0.50 * s), int(0.52 * s)
        angle = math.radians(-30)
        tube_len = int(0.31 * s)
        tube_w = int(0.047 * s)

        # Tube direction
        dx = math.cos(angle)
        dy = math.sin(angle)

        # Draw tube as thick line
        for offset in range(-tube_w // 2, tube_w // 2 + 1):
            px = -dy * offset
            py = dx * offset
            x1 = int(cx + px - dx * tube_len * 0.6)
            y1 = int(cy + py - dy * tube_len * 0.6)
            x2 = int(cx + px + dx * tube_len * 0.4)
            y2 = int(cy + py + dy * tube_len * 0.4)
            draw.line([(x1, y1), (x2, y2)], fill=(77, 171, 247), width=1)

        # Lens (ellipse at top of tube)
        lens_cx = int(cx - dx * tube_len * 0.65)
        lens_cy = int(cy - dy * tube_len * 0.65)
        lens_r = int(0.044 * s)
        draw.ellipse(
            [lens_cx - lens_r, lens_cy - int(lens_r * 0.7),
             lens_cx + lens_r, lens_cy + int(lens_r * 0.7)],
            fill=(51, 154, 240), outline=(77, 171, 247), width=max(1, int(0.005 * s))
        )

        # Tripod legs
        base_x = int(cx + dx * tube_len * 0.25)
        base_y = int(cy + dy * tube_len * 0.25)
        leg_len = int(0.22 * s)
        leg_w = max(2, int(0.012 * s))
        # Left leg
        draw.line([(base_x, base_y), (base_x - int(0.15 * s), base_y + leg_len)],
                  fill=(142, 200, 240), width=leg_w)
        # Center leg
        draw.line([(base_x, base_y), (base_x, base_y + int(leg_len * 1.1))],
                  fill=(142, 200, 240), width=leg_w)
        # Right leg
        draw.line([(base_x, base_y), (base_x + int(0.15 * s), base_y + leg_len)],
                  fill=(142, 200, 240), width=leg_w)

        # Main sparkle/star
        sparkle_cx = int(0.68 * s)
        sparkle_cy = int(0.27 * s)
        sparkle_r = int(0.058 * s)
        # Four-point star
        points = []
        for i in range(8):
            a = math.radians(i * 45 - 90)
            r = sparkle_r if i % 2 == 0 else int(sparkle_r * 0.35)
            points.append((sparkle_cx + int(r * math.cos(a)),
                           sparkle_cy + int(r * math.sin(a))))
        draw.polygon(points, fill=(255, 212, 59))
        # White center
        cr = max(1, int(0.016 * s))
        draw.ellipse([sparkle_cx - cr, sparkle_cy - cr, sparkle_cx + cr, sparkle_cy + cr],
                     fill=(255, 255, 255))

        return img

    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    for size in sizes:
        icon = _draw_icon(size)
        icon.save(f'static/icons/icon-{size}.png', 'PNG')

    # Also save SVG version for browsers that prefer it
    svg_icon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1f3a"/>
      <stop offset="100%" style="stop-color:#2d3561"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="80" fill="url(#bg)"/>
  <circle cx="120" cy="100" r="6" fill="#fff" opacity="0.8"/>
  <circle cx="380" cy="80" r="4" fill="#fff" opacity="0.6"/>
  <circle cx="420" cy="200" r="5" fill="#fff" opacity="0.7"/>
  <circle cx="90" cy="300" r="3" fill="#fff" opacity="0.5"/>
  <circle cx="200" cy="60" r="3" fill="#fff" opacity="0.4"/>
  <circle cx="450" cy="350" r="4" fill="#fff" opacity="0.5"/>
  <g transform="translate(256,280) rotate(-30)">
    <rect x="-12" y="-120" width="24" height="160" rx="4" fill="#4dabf7"/>
    <ellipse cx="0" cy="-130" rx="22" ry="14" fill="#339af0" stroke="#4dabf7" stroke-width="3"/>
    <rect x="-4" y="40" width="8" height="60" fill="#8ec8f0"/>
  </g>
  <line x1="232" y1="340" x2="180" y2="440" stroke="#8ec8f0" stroke-width="6" stroke-linecap="round"/>
  <line x1="256" y1="340" x2="256" y2="450" stroke="#8ec8f0" stroke-width="6" stroke-linecap="round"/>
  <line x1="280" y1="340" x2="332" y2="440" stroke="#8ec8f0" stroke-width="6" stroke-linecap="round"/>
  <g transform="translate(350,140)">
    <polygon points="0,-30 8,-8 30,0 8,8 0,30 -8,8 -30,0 -8,-8" fill="#ffd43b"/>
    <circle cx="0" cy="0" r="8" fill="#fff"/>
  </g>
</svg>'''
    with open('static/icons/icon.svg', 'w') as f:
        f.write(svg_icon)

    print("  App icons created (real PNG at 8 sizes + SVG)")


if __name__ == '__main__':
    create_pwa_assets()
