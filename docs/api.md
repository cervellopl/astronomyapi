# REST API

Base URL: `http://<host>:5000/api`

`GET /` returns a machine-readable index of the API with its version. A
human-readable version of this reference is served by the running app at
`/web/api-docs`.

## Authentication

The `/api` endpoints are **not** behind the session login that protects `/web`.
Anything that can reach the port can read and write the database, so do not
expose the port to an untrusted network — put it behind a reverse proxy with
its own authentication, or keep it on a private network.

Two endpoints behave differently because they call AAVSO on your behalf:
`/api/aavso/recent` needs an AAVSO API key, which is read from the signed-in
user's profile. Called without a session there is no key to use, and the
response is `401` telling you to set one. See
[Configuration](configuration.md#aavso-api-key).

## Conventions

- Request and response bodies are JSON; `POST`/`PUT` expect `Content-Type: application/json`.
- Dates are ISO 8601 (`2026-09-07T21:30:00`).
- Errors return `{"message": "..."}` with a 4xx/5xx status.
- `id` is assigned by the database; do not send it when creating.

## Core resources

Every resource below supports the same five operations.

| Method | Path | Description |
|---|---|---|
| GET | `/api/<resource>` | List all |
| POST | `/api/<resource>` | Create |
| GET | `/api/<resource>/<id>` | Fetch one |
| PUT | `/api/<resource>/<id>` | Update |
| DELETE | `/api/<resource>/<id>` | Delete |

Resources: **`types`**, **`properties`**, **`places`**, **`instruments`**,
**`objects`**, **`observations`**, **`sessions`**, **`plans`**.

### Relationship endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/objects/<id>/observations` | Observations of an object |
| GET | `/api/places/<id>/observations` | Observations made at a place |
| GET | `/api/instruments/<id>/observations` | Observations made with an instrument |
| GET | `/api/sessions/<id>/observations` | Observations recorded in a session |

### Searching observations

```
GET /api/observations/search
```

| Parameter | Meaning |
|---|---|
| `start_date` | Earliest observation datetime (ISO 8601) |
| `end_date` | Latest observation datetime |
| `object_id` | Restrict to one object |
| `place_id` | Restrict to one place |
| `instrument_id` | Restrict to one instrument |

All parameters are optional and combine with AND.

```bash
curl "http://localhost:5000/api/observations/search?start_date=2026-08-01&object_id=974"
```

### Creating an observation

```bash
curl -X POST http://localhost:5000/api/observations \
  -H "Content-Type: application/json" \
  -d '{
        "object": 974,
        "place": 4,
        "instrument": 9,
        "session_id": 12,
        "datetime": "2026-09-07T21:30:00",
        "observation": "Lim.mag: 5.2 [AAVSO: Magnitude: 7.4, Comp1: 7.2, Chart: X42135BWY, Band: Vis.]"
      }'
```

Variable star and comet data live inside the `observation` text as tagged
blocks — `[AAVSO: ...]` and `[COBS: ...]` — which is what the exporters and the
edit form parse. The web form builds these for you; if you write them by hand,
keep the key names it uses (`Magnitude`, `Uncertainty`, `Comp1`, `Comp2`,
`Check`, `Chart`, `Band`, `Observer`, `Method`).

### Observing plans

```bash
curl -X POST http://localhost:5000/api/plans \
  -H "Content-Type: application/json" \
  -d '{"name": "Autumn Miras", "stars": [20, 21, 22]}'
```

`stars` accepts an array of object ids; `star_ids` accepts the same as a
comma-separated string. `name` is required.

## Tool endpoints

These wrap external services rather than the local database.

### AAVSO

| Method | Path | Description |
|---|---|---|
| GET | `/api/aavso/recent/<star_name>` | Latest magnitude, date and brightness tendency |
| GET | `/api/aavso/recent?stars=R+Leo,Mira,AC+Her` | Batch form, max 50 stars per request |

The batch form returns one entry per star with a `star` key added, reporting
per-star errors inline rather than failing the whole request. Both require an
AAVSO API key (see above).

```json
{
  "obs_count": 60,
  "total_available": 556,
  "truncated": true,
  "last_date": "2026-09-05",
  "last_mag": "6.0",
  "last_observer": "JDAA",
  "band": "Visual",
  "tendency": "brightening",
  "first_date": "2025-09-08",
  "days_span": 362
}
```

`truncated` is not a failure: the AAVSO v2 API pages at a fixed ten rows, so
long windows are capped and the response says how many observations exist
(`total_available`) versus how many were fetched.

### SIMBAD

```
GET /api/simbad/search
```

| Parameter | Meaning |
|---|---|
| `q` | Search term (**required**, see note) |
| `type` | `name` \| `wildcard` \| `type_variable` \| `variable_constellation` (default `name`) |
| `max` | Max records, 1–2000 (default 50; constellation sweeps allow up to 5000) |
| `var_type` | Variable-star type, for `variable_constellation` |
| `constellation` | Constellation name or abbreviation, for `variable_constellation` |

```bash
# by identifier
curl "http://localhost:5000/api/simbad/search?q=SS+Cyg"

# every Mira variable in Cygnus
curl "http://localhost:5000/api/simbad/search?type=variable_constellation&var_type=Mira&constellation=Cyg&max=1000&q=Mira"
```

`q` is validated before the search type is considered, so it must be non-empty
even for `variable_constellation`, where the search is driven by `var_type` and
`constellation` and `q` is ignored. Pass any placeholder.

### AAVSO VSP finder charts

| Method | Path | Description |
|---|---|---|
| GET | `/api/charts/vsp` | Resolve a chart: id, image URL and comparison-star photometry |
| GET | `/api/charts/vsp/scales` | The available scales A–F and their fields of view |

| Parameter | Meaning |
|---|---|
| `star` | Star name or designation (**required**) |
| `scale` | `A`, `AB`, `B`, `C`, `D`, `E`, `F` — maps to a field of view |
| `fov` | Explicit field of view in degrees, overrides `scale` |
| `maglimit` | Faintest magnitude to plot (default 14.5) |

This resolves a chart without downloading it. The web interface caches chart
images and their comparison stars locally — see
[Web app](web-app.md#finder-charts).

## Web AJAX endpoints

The browser interface calls a number of JSON endpoints under `/web`. They
require a logged-in session, but are useful to know about when scripting
against your own instance.

| Path | Returns |
|---|---|
| `/web/aavso/recent/<star>` | Same summary as `/api/aavso/recent/<star>` |
| `/web/aavso/current/<star>` | Latest observation paired with the star's VSX range |
| `/web/aavso/lightcurve/<star>?days=N` | AAVSO time series as light-curve points |
| `/web/observations/lightcurve/<star>` | Your own observations of a star |
| `/web/sky/stars` | The bundled naked-eye star catalogue (mag ≤ 5.5) |
| `/web/sky/solar-system` | Sun, Moon and planet positions for the default site |
| `/web/almanac/data` | Twilight bands and rise/set/culmination curves |
| `/web/comet-path/data` | An object's sky track plus its star field |
| `/web/vsp/comparisons/<chartid>` | Comparison stars for a VSP chart |
| `/web/vsp/charts-available` | Chart ids already downloaded on this system |
| `/web/star-lists` | Saved star lists |

## Python client

`astronomy_client.py` in the repository root wraps the API:

```python
from astronomy_client import AstronomyClient

client = AstronomyClient('http://localhost:5000')
observations = client.get_observations()
```

See `astronomy_examples.py` for worked examples.
