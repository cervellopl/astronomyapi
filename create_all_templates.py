"""
Create all template files for the web interface
"""

import os

def create_all_templates():
    """Create all template files"""
    print("Creating all template files...")
    
    # Ensure directories exist
    os.makedirs('templates/objects', exist_ok=True)
    os.makedirs('templates/observations', exist_ok=True)
    os.makedirs('templates/instruments', exist_ok=True)
    os.makedirs('templates/places', exist_ok=True)
    os.makedirs('templates/types', exist_ok=True)
    os.makedirs('templates/properties', exist_ok=True)
    
    # Simple list template
    list_template = '''{% extends "layout.html" %}
{% block title %}{TITLE}{% endblock %}
{% block content %}
<div class="container-fluid">
    <h1>{TITLE}</h1>
    <p>Count: {{ {ITEMS}|length }}</p>
    <ul>
    {% for item in {ITEMS} %}
        <li>{{ item.name if item.name else item.id }}</li>
    {% endfor %}
    </ul>
</div>
{% endblock %}'''
    
    # Simple add template
    add_template = '''{% extends "layout.html" %}
{% block title %}Add {TITLE}{% endblock %}
{% block content %}
<div class="container-fluid">
    <h1>Add {TITLE}</h1>
    <p>Form coming soon...</p>
</div>
{% endblock %}'''
    
    # Create templates for each entity
    entities = {
        'objects': 'Objects',
        'observations': 'Observations',
        'instruments': 'Instruments',
        'places': 'Places',
        'types': 'Types',
        'properties': 'Properties'
    }
    
    for entity, title in entities.items():
        # List template
        with open(f'templates/{entity}/list.html', 'w') as f:
            content = list_template.replace('{TITLE}', title).replace('{ITEMS}', entity)
            f.write(content)
        
        # Add template
        with open(f'templates/{entity}/add.html', 'w') as f:
            content = add_template.replace('{TITLE}', title)
            f.write(content)
    
    # Search template
    with open('templates/search.html', 'w') as f:
        f.write('''{% extends "layout.html" %}
{% block title %}Search{% endblock %}
{% block content %}
<div class="container-fluid">
    <h1>Search Observations</h1>
    <p>Search functionality coming soon...</p>
</div>
{% endblock %}''')
    
    print("All template files created successfully!")

if __name__ == '__main__':
    create_all_templates()