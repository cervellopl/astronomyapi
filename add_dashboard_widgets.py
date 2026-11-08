# add_dashboard_widgets.py
"""
Add the users.dashboard_widgets column to existing databases.

The dashboard is configurable per user; the column holds the comma-separated
list of widget ids to show. SQLAlchemy's create_all() adds missing tables but
never missing columns, so an existing database needs this one-off ALTER. Safe
to re-run. A NULL column means "show everything", so nothing is seeded.
"""

import pymysql


def add_dashboard_widgets_column():
    """Add users.dashboard_widgets if it isn't there yet."""
    print("Checking users.dashboard_widgets column...")

    try:
        conn = pymysql.connect(
            host='astronomy-db',
            port=3306,
            user='astronomy',
            password='astronomy',
            database='astronomy_db'
        )

        with conn.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM users LIKE 'dashboard_widgets'")
            if cursor.fetchone():
                print("users.dashboard_widgets already present - nothing to do.")
            else:
                cursor.execute("ALTER TABLE users ADD COLUMN dashboard_widgets TEXT")
                conn.commit()
                print("users.dashboard_widgets column added.")

        conn.close()
        return True

    except Exception as e:
        print(f"Error adding users.dashboard_widgets: {str(e)}")
        return False


if __name__ == '__main__':
    add_dashboard_widgets_column()
