# Astronomy Observations

A self-hosted observation logbook for variable star and comet observers, with a
web interface, a REST API, and the observing tools that usually live in a pile
of separate bookmarks: finder charts, magnitude checks, twilight diagrams, a
live sky map and weather.

Built around a Flask + SQLAlchemy core on MariaDB, deployed with Docker.

- **Web interface:** `http://localhost:5000/web`
- **REST API:** `http://localhost:5000/api`
- **API docs in the app:** `http://localhost:5000/web/api-docs`

## What it does

### Logging observations

- Objects, places, instruments, sessions and observations, with any number of
  custom property/value pairs per observation.
- Sessions group a night's work and record conditions (cloud, light pollution,
  limiting magnitude, moon phase). Adding an observation from a session page
  pre-fills its date, instrument and place.
- Variable star observations carry the full AAVSO field set (magnitude,
  comparison stars, chart, band, observer code, method); comet observations
  carry the COBS/ICQ fields.

### Variable stars

- **Magnitude check** — batch-query AAVSO for the latest magnitude and
  brightness tendency of many stars at once. Selections can be saved as named
  star lists and exported as a printable two-column observing form (PDF).
- **Comparison stars** — pick an AAVSO VSP chart and its comparison stars fill
  the Comp 1 / Comp 2 fields, with magnitudes shown; cached alongside the chart
  so it works offline.
- **Light curves** — your own observations or AAVSO's, saveable as PNG/JPG.
- **Observing plans** — build a plan from a star list and step through it one
  star at a time, recording as you go.
- **Finder charts** — download AAVSO VSP charts (scales A–F) singly or in
  batches for offline use.

### Catalogue imports

- **SIMBAD** — search by identifier, wildcard, variable type, or every variable
  of a given type in a constellation.
- **AAVSO VSX** — import variable stars.
- **Minor Planet Center** — import comets with full orbital elements.

### Planning tools

- **Sky map** — live all-sky chart for your default site: 2839 stars to mag 5.5,
  plus the Sun, Moon and planets, redrawn every second.
- **Visibility chart** — an almanac-style diagram: dates across, time of night
  up, twilight shaded, with rise/set/culmination curves per body, and a second
  panel of predicted magnitudes.
- **Path chart** — a finder chart of a comet's or planet's track across the star
  field with dated ticks, including a deep "lens view" down to mag 16.
- **Weather** — tabbed forecasts and radar centred on your default site.

### Reporting

- Export to **AAVSO Visual** and **ICQ** format, or submit directly to
  **AAVSO** and **COBS**.
- Encrypted backup/restore, with scheduled automatic backups.

## Quick start

```bash
git clone https://github.com/cervellopl/astronomyapi.git
cd astronomyapi
sudo docker compose up -d --build
```

The first start creates the schema, seeds reference data, downloads the star
catalogue and generates the templates, which takes a minute or two. Then open
`http://localhost:5000/web` and sign in with **`admin` / `admin`** — change the
password under Settings straight away.

Then, to make the tools useful:

1. **Places** — add your observing site and mark it default (the star button).
   The sky map, weather and visibility charts all key off it.
2. **Settings** — add your AAVSO observer code and an
   [AAVSO API key](https://apps.aavso.org/v2/api/docs/). The key is required for
   magnitude checks and light curves; AAVSO's old open endpoints were retired.
3. **Instruments** — add what you observe with.

## Documentation

| Guide | Contents |
|---|---|
| [Web app](docs/web-app.md) | Page-by-page tour of the interface |
| [REST API](docs/api.md) | Endpoint reference with examples |
| [Configuration](docs/configuration.md) | Environment, settings, external services |
| [Development](docs/development.md) | Architecture, the code generators, deployment |

## Requirements

- Docker and Docker Compose (the supported path), or Python 3.9+ with MariaDB/MySQL
- Network access for the catalogue and forecast services listed in
  [Configuration](docs/configuration.md#external-services)

## Licence

See [LICENSE](LICENSE).
