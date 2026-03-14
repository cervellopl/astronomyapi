"""
Fix web_routes.py to handle POST requests for adding data
"""

def fix_web_routes_add():
    """Fix web_routes add functions"""
    print("Fixing web_routes.py add functions...")
    
    try:
        with open('web_routes.py', 'r') as f:
            content = f.read()
        
        # Find and replace the add_object function
        if 'def add_object():' in content:
            # Replace the entire add_object function
            old_add_object = '''def add_object():
    """Add a new object"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            desination = request.form.get('desination')
            object_type = request.form.get('type')
            props = request.form.get('props')
            
            # Create object data
            data = {
                'name': name,
                'desination': desination,
                'type': int(object_type),
                'props': props
            }
            
            # Call API to create object
            response = api_request('POST', '/api/objects', data=data)
            
            if response.status_code == 201:
                flash('Object added successfully!', 'success')
                return redirect(url_for('web.list_objects'))
            else:
                flash(f'Error adding object: {response.json().get("message", "Unknown error")}', 'danger')
        except Exception as e:
            flash(f'Error adding object: {str(e)}', 'danger')
    
    # Get types for the form
    types_response = api_request('GET', '/api/types')
    types = types_response.json() if types_response.status_code == 200 else []
    
    return render_template('objects/add.html', types=types)'''
            
            new_add_object = '''def add_object():
    """Add a new object"""
    if request.method == 'POST':
        try:
            from models import Object
            from database import db
            
            # Get form data
            name = request.form.get('name')
            desination = request.form.get('desination')
            object_type = request.form.get('type')
            props = request.form.get('props')
            
            # Create new object
            new_object = Object(
                name=name,
                desination=desination,
                type=int(object_type),
                props=props
            )
            
            db.session.add(new_object)
            db.session.commit()
            
            flash('Object added successfully!', 'success')
            return redirect(url_for('web.list_objects'))
        except Exception as e:
            flash(f'Error adding object: {str(e)}', 'danger')
            db.session.rollback()
    
    # Get types for the form - use direct API
    try:
        from direct_api import get_types
        types = get_types()
    except:
        types = []
    
    return render_template('objects/add.html', types=types)'''
            
            content = content.replace(old_add_object, new_add_object)
        
        # Write the fixed content
        with open('web_routes.py', 'w') as f:
            f.write(content)
        
        print("Fixed web_routes.py add functions!")
        return True
    except Exception as e:
        print(f"Error fixing web_routes.py: {str(e)}")
        return False

if __name__ == '__main__':
    fix_web_routes_add()