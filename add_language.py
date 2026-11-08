#!/usr/bin/env python3
"""Add users.language, the interface language for each account.

create_all() makes missing tables but never missing columns, so each new
column needs a one-off step like this one. Running it twice is harmless.
"""

import sys
from sqlalchemy import text

from server import app
from database import db


def main():
    with app.app_context():
        existing = {row[0] for row in db.session.execute(
            text("SHOW COLUMNS FROM users")).fetchall()}
        if 'language' in existing:
            print('users.language already present')
            return 0
        db.session.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR(5)"))
        db.session.commit()
        print('users.language added')
    return 0


if __name__ == '__main__':
    sys.exit(main())
