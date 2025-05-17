"""
SQLAlchemy 2.0 Compatibility Fixer
=================================
Script to fix SQLAlchemy 2.0 compatibility issues in Python files.

This script imports necessary modules and wraps raw SQL queries with text().
"""

import os
import re
import sys

def fix_file(filename):
    """Fix SQLAlchemy compatibility issues in a file."""
    if not os.path.isfile(filename):
        print(f"File not found: {filename}")
        return False
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Add import if needed
    if 'from sqlalchemy import text' not in content and 'db.session.execute(' in content:
        # Find a good place to add the import
        if 'import sqlalchemy' in content:
            content = re.sub(r'import sqlalchemy', 'import sqlalchemy\nfrom sqlalchemy import text', content)
        elif 'from sqlalchemy import' in content:
            content = re.sub(r'from sqlalchemy import ([^\\n]*)', r'from sqlalchemy import \1, text', content)
        elif 'from flask_sqlalchemy import SQLAlchemy' in content:
            content = re.sub(
                r'from flask_sqlalchemy import SQLAlchemy',
                'from flask_sqlalchemy import SQLAlchemy\nfrom sqlalchemy import text',
                content
            )
        else:
            # Add at the top with other imports
            import_section = re.search(r'^(import [^\n]+\n|from [^\n]+\n)+', content)
            if import_section:
                end_of_imports = import_section.end()
                content = content[:end_of_imports] + 'from sqlalchemy import text\n' + content[end_of_imports:]
            else:
                # Just add at the top
                content = 'from sqlalchemy import text\n' + content
    
    # Fix db.session.execute
    original_content = content
    content = re.sub(r"db\.session\.execute\(\s*'([^']+)'\s*\)", r"db.session.execute(text('\1'))", content)
    content = re.sub(r'db\.session\.execute\(\s*"([^"]+)"\s*\)', r'db.session.execute(text("\1"))', content)
    
    # Check if any changes were made
    if content == original_content:
        print(f"No changes needed in {filename}")
        return False
    
    # Write the modified content
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"Fixed SQLAlchemy compatibility issues in {filename}")
    return True

def main():
    """Main function."""
    # List of files to check
    files = [
        'config.py',
        'database.py',
        'server.py',
        'web_routes.py',
        'resources.py',
        'models.py'
    ]
    
    print("Fixing SQLAlchemy 2.0 compatibility issues...")
    fixed = 0
    
    for filename in files:
        if fix_file(filename):
            fixed += 1
    
    print(f"Fixed {fixed} files")

if __name__ == '__main__':
    main()
