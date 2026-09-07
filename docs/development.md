# Development

## The one thing to know first

**`web_routes.py`, `server.py` and everything under `templates/` and `static/`
are generated, not hand-written.** They are produced at container startup by
generator scripts, so editing them directly is wiped on the next deploy. The
copies committed to the repository are usually stale.

| Generated artifact | Produced by |
|---|---|
| `web_routes.py` | `create_new_web_routes.py` |
| `server.py` | `create_new_server.py` |
| `templates/**` | `create_complete_templates.py` |
| `static/comp-stars.js`, `static/chart-export.js` | `create_complete_templates.py` |
| `static/stars.json` | `create_star_catalog.py` |
| `static/icons/**`, `manifest.json` | `create_pwa_assets.py` |

Each generator holds its output inside a large triple-quoted string. To change
a route, edit the `content` string in `create_new_web_routes.py`; to change a
page, edit the corresponding `with open('templates/...') as f: f.write('''...''')`
block in `create_complete_templates.py`.

Hand-written modules that are *not* generated: `models.py`, `resources.py`,
`config.py`, `database.py`, `aavso_recent.py`, `import_simbad.py`,
`import_vsx.py`, `import_comets_mpc.py`, and the `add_*.py` migrations.

## Working on it

```bash
# regenerate and check the artifacts compile / parse
python3 create_new_web_routes.py && python3 -m py_compile web_routes.py
python3 create_complete_templates.py

python3 - <<'EOF'
from jinja2 import Environment
import glob
for t in glob.glob('templates/**/*.html', recursive=True):
    Environment().parse(open(t).read())
print('all templates parse')
EOF

# then discard the regenerated artifacts so the diff stays generators-only
git checkout -- web_routes.py server.py templates
git clean -fd templates static
```

Inline JavaScript is worth syntax-checking too, since a broken script silently
disables a whole page. Strip the Jinja expressions first:

```bash
python3 - <<'EOF'
import re
h = open('templates/observations/add.html').read()
b = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', h, re.S)[0]
b = re.sub(r'\{\{.*?\}\}', 'null', b, flags=re.S)
b = re.sub(r'\{%.*?%\}', '', b, flags=re.S)
open('/tmp/check.js', 'w').write(b)
EOF
node --check /tmp/check.js
```

## Deploying

The container has **no source volume mount** — code is baked into the image at
build time, so a restart re-runs the generators already inside the image and
will *not* pick up host edits:

```bash
sudo docker compose up -d --build api
```

Startup then runs, in order: schema creation, reference-data seeds, the column
migrations, template generation, the star catalogue, PWA assets, `server.py`,
`web_routes.py`, and finally the server. Watch it with:

```bash
sudo docker logs -f astronomy-api
```

## Adding things

**A route.** Add it to the `content` string in `create_new_web_routes.py`.
Blueprint routes are `@web.route(...)` and mount under `/web`. Anything the
browser calls as JSON should return `jsonify(...)` and report failures as a
message rather than a stack trace.

**A page.** Add a `with open('templates/<dir>/<name>.html', 'w')` block in
`create_complete_templates.py`, and add `<dir>` to the `dir_name` list near the
top of `create_complete_templates()` if it is new. Add the sidebar entry in the
`layout.html` block.

**A REST resource.** Add the class to `resources.py` and register it in the
`api.add_resource(...)` list inside `create_new_server.py`.

**A model column.** Add it to `models.py` *and* write an idempotent
`add_<thing>.py` migration wired into the compose command —
`db.create_all()` adds tables but never columns. Follow `add_default_place.py`.

**A dependency.** Add it to `requirements.txt`; the image must be rebuilt.

## Shared front-end helpers

Rather than duplicating JavaScript across generated templates:

- `static/comp-stars.js` — AAVSO comparison-star pickers, used by the add form,
  the edit form and the plan runner.
- `static/chart-export.js` — `saveChartImage(canvasId, format, name)`, used by
  the light curves, visibility chart and path chart. It paints the page
  background before exporting, because a Chart.js canvas is transparent and
  JPEG cannot hold transparency.

## Conventions worth keeping

- **Do not swallow errors into empty results.** An early bug rendered the
  observations list inside a `try`, so a template error became "No observations
  found" instead of an error. Keep rendering outside the `try`.
- **Say why something is missing.** A star with no rise time is either
  circumpolar or never up; a truncated AAVSO fetch should report how many
  observations exist. Blank cells and silent caps cost more time than they save.
- **Cap and report, rather than hanging.** External catalogues can return
  enormous results; every query that can explode has a limit and tells the user
  when it hit one.
- **Verify against a second source.** Positional code is checked against
  PyEphem, and derived values against the stored data they came from — a
  comet's derived semi-major axis should reproduce its catalogued period.

## Repository layout

```
astronomy_api.py        Flask app factory and API bootstrap
config.py               Configuration classes and CLI helpers
database.py             SQLAlchemy setup
models.py               ORM models (hand-written)
resources.py            REST API resources (hand-written)
aavso_recent.py         AAVSO v2 API client
import_simbad.py        SIMBAD search and import
import_vsx.py           AAVSO VSX import
import_comets_mpc.py    Minor Planet Center comet import
create_*.py             Generators for routes, server, templates, assets
add_*.py                Idempotent schema migrations
astronomy_client.py     Python client for the REST API
astronomy_examples.py   Worked examples against the client
docker-compose.yml      Services, environment and the startup sequence
docs/                   This documentation
```
