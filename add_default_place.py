# add_default_place.py
"""
Add the places.is_default column to existing databases.

SQLAlchemy's create_all() adds missing tables but never missing columns, so a
database created before the default-site feature needs this one-off ALTER.
Safe to re-run: it checks for the column first.
"""

import pymysql


def add_default_place_column():
    """Add places.is_default if it isn't there yet."""
    print("Checking places.is_default column...")

    try:
        conn = pymysql.connect(
            host='astronomy-db',
            port=3306,
            user='astronomy',
            password='astronomy',
            database='astronomy_db'
        )

        with conn.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM places LIKE 'is_default'")
            if cursor.fetchone():
                print("places.is_default already present - nothing to do.")
            else:
                cursor.execute(
                    "ALTER TABLE places ADD COLUMN is_default TINYINT(1) DEFAULT 0")
                conn.commit()
                print("places.is_default column added.")

            # Make sure at most one place is flagged, and that a single-place
            # database has a usable default.
            cursor.execute("SELECT COUNT(*) FROM places WHERE is_default = 1")
            flagged = cursor.fetchone()[0]
            if flagged == 0:
                cursor.execute("SELECT COUNT(*) FROM places")
                if cursor.fetchone()[0] == 1:
                    cursor.execute("UPDATE places SET is_default = 1")
                    conn.commit()
                    print("Single place found - marked it as the default site.")

        conn.close()
        return True

    except Exception as e:
        print(f"Error adding places.is_default: {str(e)}")
        return False


if __name__ == '__main__':
    add_default_place_column()
