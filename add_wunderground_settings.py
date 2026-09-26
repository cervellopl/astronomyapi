# add_wunderground_settings.py
"""
Add the Weather Underground columns to existing databases.

The dashboard shows live readings from a personal weather station, which needs
a station id and an API key per user. SQLAlchemy's create_all() adds missing
tables but never missing columns, so an existing database needs this one-off
ALTER. Safe to re-run.
"""

import pymysql

COLUMNS = (
    ('wu_station_id', 'VARCHAR(32)'),
    ('wu_api_key', 'VARCHAR(64)'),
)
# The station this install was set up for; a user can change it in Settings.
DEFAULT_STATION = 'IGSAWY6'


def add_wunderground_columns():
    """Add users.wu_station_id and users.wu_api_key if they are missing."""
    print("Checking Weather Underground columns...")

    try:
        conn = pymysql.connect(
            host='astronomy-db',
            port=3306,
            user='astronomy',
            password='astronomy',
            database='astronomy_db'
        )

        with conn.cursor() as cursor:
            for name, coltype in COLUMNS:
                cursor.execute(f"SHOW COLUMNS FROM users LIKE '{name}'")
                if cursor.fetchone():
                    print(f"users.{name} already present - nothing to do.")
                    continue
                cursor.execute(f"ALTER TABLE users ADD COLUMN {name} {coltype}")
                conn.commit()
                print(f"users.{name} column added.")

            # Seed the default station for anyone who has none yet
            cursor.execute(
                "UPDATE users SET wu_station_id = %s "
                "WHERE wu_station_id IS NULL OR wu_station_id = ''",
                (DEFAULT_STATION,))
            conn.commit()

        conn.close()
        return True

    except Exception as e:
        print(f"Error adding Weather Underground columns: {str(e)}")
        return False


if __name__ == '__main__':
    add_wunderground_columns()
