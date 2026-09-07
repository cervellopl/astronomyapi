# Web app guide

The interface lives under `/web` and needs a login. The first start seeds an
`admin` / `admin` account — change the password in Settings.

The sidebar has three groups: **Main** (Dashboard, Search, Observing Plan),
**Data** (Objects, Sessions, Observations, Instruments, Places, Weather, Sky
Map, Visibility Chart, Path Chart, Types, Properties) and **Tools** (Import
Comets, Import VSX Stars, Batch Finder Charts, Magnitude Check, Light Curve,
SIMBAD Search, Export ICQ, Export AAVSO, Submit to COBS, Submit to AAVSO),
followed by Backup and Settings.

## Recording observations

### Sessions

A session is one night's observing: number, start and end, and the conditions
that matter later — cloud cover and type, light pollution, limiting magnitude,
moon phase and altitude, and the instrument.

Opening a session lists the observations recorded in it, each with Edit and
Delete, and an **Add Observation** button. That button carries the session's
context into the form: date and time, instrument, place (taken from the
session's most recent observation) and limiting magnitude. Saving returns you
to the session rather than the global list, so a night's entries can be logged
one after another.

### Observations

`Observations → Add Observation` records object, date/time (UTC), place,
instrument, optional session, notes, and any number of property/value pairs.

The form adapts to what you selected:

- **Variable stars** reveal the AAVSO block — magnitude, uncertainty,
  comparison stars, check star, chart, band, observer code, method.
- **Comets** reveal the COBS/ICQ block — m1, coma diameter, degree of
  condensation, tail length and position angle, method, reference catalogue.

Editing an observation shows the same AAVSO fields, filled in from the stored
record; the notes box holds just your text. Saving rebuilds the tagged block,
so repeated edits never stack duplicates. Clearing the magnitude removes the
AAVSO block entirely.

#### Checking a star before you log it

The magnifier beside the Magnitude field asks AAVSO what the star is doing now
and answers inline:

> AAVSO **6.0** (Visual) · on 2026-09-05 · by JDAA · brightening · range 3.3-14.2 (M) · **use**

It pairs the newest observation with the star's VSX range, so an estimate can
be judged both against what others just reported and against where the star
sits between maximum and minimum. **use** copies the value into the field.
Requires an [AAVSO API key](configuration.md#aavso-api-key).

#### Comparison stars from the chart

Pick a finder chart (or type a chart ID and press the download button) and its
comparison stars load as clickable chips showing label and magnitude — first
click sets Comp 1, second sets Comp 2. The fields stay free-text with
type-ahead, so a label can still be typed by hand.

Only the AAVSO label goes into the field, which is what the COMP1/COMP2 columns
expect on export. Comparison stars are cached next to the chart image when it is
downloaded, so a chart you already have works without network access.

The Chart ID field offers the charts already downloaded on this system,
filtered to the star you are observing.

## Variable star tools

### Magnitude check

**Magnitude Check** lists your variable stars. Tick some and it queries
AAVSO for each one's latest magnitude, date and tendency, one at a time with a
progress bar so a long list never times out.

From the results you can:

- **Save the selection** as a named star list and load it again later. Lists
  store object ids, so a renamed star stays in its list; loading tells you if
  any are no longer in the catalogue.
- **Export a PDF observing list** — an A4 two-column form, each star showing
  its latest AAVSO reading with an empty box to write your estimate in, and
  ruled Date / Place / Instrument / Lim. mag fields at the top. 32 stars per
  page.
- **Make an observing plan** from the ticked stars.

### Observing plans

A plan is an ordered list of stars with shared defaults (place, instrument,
session). Running one steps through it a star at a time, showing the finder
chart and recording your observation before moving on. Plans are saved and
re-runnable.

### Light curves

Available from the observation form and as a standalone page
(**Light Curve**). Plot your own observations of a star, or AAVSO's over
a chosen window, grouped by band with the magnitude axis inverted. Both save as
**PNG** or **JPG**.

### Finder charts

A variable star's object page links to its finder charts, which download from
the AAVSO Variable Star Plotter at scales A–F (3° down to 2′) and are stored
locally so they are available offline during a session. **Batch Finder Charts**
does the same for many stars at once, pacing itself and retrying the transient
failures AAVSO returns under load.

## Planning tools

### Sky map

A live all-sky chart for your default site: 2839 stars to magnitude 5.5 from
SIMBAD, plus the Sun, Moon and planets from PyEphem. Zenith at the centre,
horizon at the rim, north up and east left, so it matches the sky held
overhead.

It redraws every second, and a conditions line gives the two facts that decide
whether tonight works: the Sun's altitude with its twilight class, and the
Moon's illumination and phase. Hovering a star shows its designation,
magnitude, altitude and azimuth.

### Visibility chart

An almanac-style diagram: dates across the bottom, time of night up the side,
the background shaded through daylight, civil, nautical and astronomical
twilight into full night. Over it, a curve per body — solid for rise and set,
dashed for culmination.

Choose the period, any of your places, local time or UTC, and which planets and
catalogue objects to include. Comets are computed from their orbital elements,
so their curves are real rather than a fixed position. Objects that never rise
or never set are labelled as such rather than leaving an unexplained gap.

A second panel below plots **predicted magnitude** over the same dates — the
Moon through its phases, planets, and comets from their brightness parameters.
Catalogue objects with a recorded range show it as a band.

Both panels export as PNG or JPG.

### Path chart

A finder chart of an object's track across the star field, in the style of a
printed magazine chart: the path in yellow with dated ticks, an RA/Dec grid,
and named stars. Works for comets, planets and catalogue objects.

**Field of view** switches between the whole path and a *lens view* — a 5° down
to 15′ circle centred on one night, which can show stars to **magnitude 16**
from Gaia. A wide field at a deep limit is refused rather than drawn as an
unreadable smear, as is a path too long to fit one projection (a fast comet can
cross 100° in two months).

### Weather

Tabbed forecasts for your default site, all ten viewpoints loading at once:
WXCHARTS ECMWF, meteo.pl UM and COAMPS meteorograms, Weather Underground
station and map views, IMGW radar and satellite, and LightningMaps. Services
that accept coordinates are centred on your site. Two providers block
embedding, so those tabs offer a direct link instead.

## Catalogue imports

| Page | Source | Notes |
|---|---|---|
| **SIMBAD Search** | SIMBAD | By identifier, wildcard, variable type, or every variable of a type in a constellation |
| **Import VSX Stars** | AAVSO VSX | Variable stars by name, constellation or type |
| **Import Comets** | Minor Planet Center | Comets with full orbital elements |

SIMBAD results show each star's magnitude range with the photometric band it
was measured in, and mark objects already in your database.

## Reporting

### Exports

- **AAVSO Visual** (**Export AAVSO**) — pick a star and date range,
  preview the report lines, download the file. Any observation carrying an
  `[AAVSO: ...]` block is included, whatever the object's type.
- **ICQ** (**Export ICQ**) — the same for comet observations.

### Direct submission

**Submit to AAVSO** and **Submit to COBS** upload observations
using the credentials in Settings.

### Backup

**Backup & Restore** exports the whole database as a file, optionally AES
encrypted, and restores or merges from one. Backups can also be written to
internal storage on a schedule.

## Places and the default site

Places hold name, alias, latitude, longitude, altitude and timezone, and are
shown on a map. One place is marked **default** with the star button — the sky
map, weather page, visibility chart and path chart all use it, so set it before
using those.
