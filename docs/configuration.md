# Configuration

## Environment variables

Set in `docker-compose.yml` for the `api` service, or in the environment for a
manual run.

| Variable | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | `mysql+pymysql://astronomy:astronomy@astronomy-db:3306/astronomy_db` | SQLAlchemy connection string |
| `FLASK_CONFIG` | `development` | `development`, `testing` or `production` — selects the config class in `config.py` |
| `FLASK_DEBUG` | `1` | Flask debug mode |
| `SECRET_KEY` | `astronomy-api-secret-key-change-in-production` | Session signing key — **change this** |
| `TEST_DATABASE_URL` | — | Used when `FLASK_CONFIG=testing` |

The shipped compose file runs in development mode with debug enabled and
default database credentials. Before exposing the app anywhere beyond a trusted
network, change `SECRET_KEY`, the MariaDB passwords, and set
`FLASK_CONFIG=production` with `FLASK_DEBUG=0`.

## Ports and volumes

| | |
|---|---|
| `5000` | Web interface and API |
| `3310` | MariaDB, mapped from the container's 3306 |
| `charts-data` volume | `/app/static/charts` — downloaded finder charts and their cached comparison stars |

Only the charts directory is on a volume. The database lives in the `db`
container's own storage, and everything else in the image is regenerated at
startup.

## Per-user settings

Settings (`/web/settings`) holds the identity and credentials the tools use.

| Setting | Used by |
|---|---|
| AAVSO observer code | AAVSO exports and submissions, the PDF observing list |
| ICQ observer code | ICQ comet exports |
| Default timezone | Display of local times |
| AAVSO email / password | Direct submission to AAVSO |
| **AAVSO API key** | Magnitude checks, light curves, the current-magnitude check |
| COBS username / password | Direct submission to COBS |
| Backup password | Encryption of exported backups |

### AAVSO API key

AAVSO retired its open VSX endpoints — the old
`aavso.org/vsx/index.php?view=api.delim` interface now sits behind Cloudflare
and answers `403`. Everything AAVSO-related therefore goes through the
[apps.aavso.org v2 API](https://apps.aavso.org/v2/api/docs/), which
authenticates with a per-user token.

Get a key from your AAVSO account and paste it into Settings → AAVSO
Integration → AAVSO API Key. Without it, magnitude checks and light curves
return `401` with a message pointing here.

The key is stored in the `users` table and rendered back into the settings form
so it can be edited, so treat that page as sensitive.

## The default observing site

Places (`/web/places`) each hold latitude, longitude, altitude and timezone.
One is marked **default** with the star button, and it drives the sky map,
weather page, visibility chart and path chart. Set one before using those
pages; they will tell you if none is set.

Coordinates are decimal degrees, east positive. The timezone is an IANA name
(`Europe/Warsaw`) and is used for local-time axes on the charts.

## Database schema

| Table | Holds |
|---|---|
| `users` | Accounts, observer codes and service credentials |
| `types` | Object classifications (Star, Variable Star, Comet, Galaxy…) |
| `objects` | Catalogue objects; `props` is JSON — coordinates, orbital elements, magnitudes |
| `places` | Observing sites, one flagged `is_default` |
| `instruments` | Telescopes, binoculars, eyes |
| `sessions` | A night's observing with its conditions |
| `observations` | Individual observations |
| `observation_properties` | Property/value pairs per observation |
| `properities` | Property definitions (spelling preserved from the original schema) |
| `plans` | Saved observing plans |
| `star_lists` | Saved star selections for the magnitude check |

### Schema migrations

`db.create_all()` at startup creates **missing tables**, but never missing
**columns**. A change that adds a column therefore needs a small idempotent
script, run from the compose command before the app starts:

| Script | Adds |
|---|---|
| `add_default_place.py` | `places.is_default` |
| `add_aavso_api_key.py` | `users.aavso_api_key` |

Both check for the column first and report "already present" on a database that
has it, so they are safe on every start. A new *table* needs no script.

## External services

The app talks to these at runtime. None require an account except AAVSO.

| Service | Used for |
|---|---|
| [SIMBAD](https://simbad.cds.unistra.fr/) (CDS Strasbourg) | Object search and import, star catalogue, star fields |
| [VizieR](https://vizier.cds.unistra.fr/) | Gaia DR3 stars for the path chart's deep lens view |
| [AAVSO v2 API](https://apps.aavso.org/v2/api/docs/) | Magnitudes, light curves, VSX star data — **needs a key** |
| [AAVSO VSP](https://app.aavso.org/vsp/) | Finder charts and comparison stars |
| [Minor Planet Center](https://minorplanetcenter.net/) | Comet orbital elements |
| [COBS](https://www.cobs.si/) | Comet observation submission |
| meteo.pl, IMGW, WXCHARTS, Weather Underground, LightningMaps | Weather page |

The star catalogue is downloaded once at first start by
`create_star_catalog.py` into `static/stars.json` (about 2839 stars to
magnitude 5.5, 100 KB) and skipped on later starts. If that download fails, the
sky map rebuilds it on demand instead of staying broken.
