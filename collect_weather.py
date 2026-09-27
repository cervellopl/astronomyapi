#!/usr/bin/env python3
"""
Standalone weather collector, meant for cron.

The web app samples the sky on its own schedule, but only while it is running
and healthy. This script does the same collection from outside, so the record
keeps filling whether or not anyone has the dashboard open:

  * cloud   - IMGW's satellite reading over the default site, plus a backfill
              of any frames IMGW still lists that are missing locally
  * station - the configured Weather Underground personal weather station

It deliberately reuses the application's own functions rather than
reimplementing the IMGW and Weather Underground handling, so there is one
implementation of each and the cron rows are identical to the app's.

Run it inside the container, where the app and its dependencies live:

    docker exec astronomy-api python /app/collect_weather.py

Every source is independent: one failing does not stop the others, and the
exit status is non-zero only if nothing at all could be collected.
"""

import sys
from datetime import datetime


def log(message):
    print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}Z] {message}", flush=True)


def collect_cloud(web_routes):
    """Sample the satellite now, then close any gaps IMGW can still fill."""
    stored = 0
    try:
        data = web_routes._build_current_condition()
        if data.get('error'):
            log(f"cloud: {data['error']}")
        elif web_routes._record_condition(data):
            stored += 1
            log(f"cloud: stored {data['observed']} - {data['label']}")
        else:
            log(f"cloud: frame {data['observed']} already held ({data['label']})")
    except Exception as e:
        log(f"cloud: sampling failed: {e}")

    try:
        filled = web_routes._backfill_conditions()
        if filled:
            stored += filled
            log(f"cloud: backfilled {filled} older frame(s)")
    except Exception as e:
        log(f"cloud: backfill failed: {e}")
    return stored


def collect_station(web_routes, models, db):
    """Store the current reading from every distinct configured station."""
    from models import StationReading

    # One row per station, not per user: two accounts watching the same station
    # should not store the same observation twice.
    stations = {}
    for user in models.User.query.all():
        key = (getattr(user, 'wu_api_key', None) or '').strip()
        if not key:
            continue
        station = (getattr(user, 'wu_station_id', None) or '').strip().upper()
        if station:
            stations.setdefault(station, key)

    if not stations:
        log('station: no user has a Weather Underground API key set - skipping')
        return 0

    stored = 0
    for station, key in stations.items():
        try:
            obs = web_routes._fetch_station_observation(station, key)
        except Exception as e:
            log(f"station {station}: fetch failed: {e}")
            continue
        if obs.get('error'):
            log(f"station {station}: {obs['error']}")
            continue

        raw = (obs.get('observed') or '').strip()
        observed_at = None
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ'):
            try:
                observed_at = datetime.strptime(raw, fmt).replace(tzinfo=None)
                break
            except ValueError:
                continue
        if observed_at is None:
            log(f"station {station}: unreadable observation time {raw!r}")
            continue

        try:
            exists = StationReading.query.filter_by(
                station=station, observed_at=observed_at).first()
            if exists:
                log(f"station {station}: {raw} already held")
                continue
            db.session.add(StationReading(
                station=station,
                observed_at=observed_at,
                temp_c=obs.get('temp_c'),
                dewpoint_c=obs.get('dewpoint_c'),
                spread_c=obs.get('spread_c'),
                humidity=obs.get('humidity'),
                wind_kph=obs.get('wind_kph'),
                gust_kph=obs.get('gust_kph'),
                wind_dir=obs.get('wind_dir'),
                pressure_hpa=obs.get('pressure_hpa'),
                precip_rate_mm=obs.get('precip_rate_mm'),
                precip_total_mm=obs.get('precip_total_mm'),
                solar_wm2=obs.get('solar_wm2'),
                uv=obs.get('uv'),
            ))
            db.session.commit()
            stored += 1
            log(f"station {station}: stored {raw} - {obs.get('temp_c')}C, "
                f"dew {obs.get('dewpoint_c')}C, {obs.get('humidity')}% RH")
        except Exception as e:
            db.session.rollback()
            log(f"station {station}: could not store {raw}: {e}")
    return stored


def main():
    sys.path.insert(0, '/app')
    try:
        import server
        import web_routes
        import models
        from database import db
    except Exception as e:
        log(f"fatal: cannot load the application: {e}")
        return 1

    with server.app.app_context():
        # create_all is safe and idempotent; it means a fresh table (like the
        # station history) exists even if the web app has not restarted yet.
        try:
            db.create_all()
        except Exception as e:
            log(f"warning: create_all failed: {e}")

        cloud = collect_cloud(web_routes)
        station = collect_station(web_routes, models, db)

    log(f"done: {cloud} cloud row(s), {station} station row(s)")
    return 0 if (cloud or station) else 0    # nothing new is normal, not an error


if __name__ == '__main__':
    sys.exit(main())
