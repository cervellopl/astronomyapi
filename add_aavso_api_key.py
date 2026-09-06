# add_aavso_api_key.py
"""
Add the users.aavso_api_key column to existing databases.

AAVSO retired the old open VSX endpoints behind Cloudflare; the replacement
apps.aavso.org v2 API needs a per-user token. SQLAlchemy's create_all() adds
missing tables but never missing columns, so an existing database needs this
one-off ALTER. Safe to re-run.
"""

import pymysql


def add_aavso_api_key_column():
    """Add users.aavso_api_key if it isn't there yet."""
    print("Checking users.aavso_api_key column...")

    try:
        conn = pymysql.connect(
            host='astronomy-db',
            port=3306,
            user='astronomy',
            password='astronomy',
            database='astronomy_db'
        )

        with conn.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM users LIKE 'aavso_api_key'")
            if cursor.fetchone():
                print("users.aavso_api_key already present - nothing to do.")
            else:
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN aavso_api_key VARCHAR(128)")
                conn.commit()
                print("users.aavso_api_key column added.")

        conn.close()
        return True

    except Exception as e:
        print(f"Error adding users.aavso_api_key: {str(e)}")
        return False


if __name__ == '__main__':
    add_aavso_api_key_column()
