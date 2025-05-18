"""
Fix API URL in web_routes.py
"""

import os

def fix_api_url():
    """Fix API URL in web_routes.py"""
    print("Fixing API URL in web_routes.py...")
    
    try:
        # Read the file
        with open('web_routes.py', 'r') as f:
            content = f.read()
        
        # Update the API_BASE_URL
        if "API_BASE_URL = ''" in content:
            # Replace with a proper URL using the server's base URL
            content = content.replace(
                "API_BASE_URL = ''",
                "API_BASE_URL = 'http://localhost:5000'"
            )
        
        # Update the api_request function to use absolute URLs
        if "url = get_api_url(endpoint)" in content:
            # Modify function to ensure URLs are always absolute
            content = content.replace(
                "def get_api_url(endpoint):",
                """def get_api_url(endpoint):
    """Get the full URL for an API endpoint."""
    # If endpoint already starts with http, return as is
    if endpoint.startswith('http'):
        return endpoint
        
    # Ensure API_BASE_URL ends with slash if endpoint doesn't start with slash
    if not API_BASE_URL.endswith('/') and not endpoint.startswith('/'):
        return f"{API_BASE_URL}/{endpoint}"
    
    # Remove double slash if both base URL ends with slash and endpoint starts with slash
    if API_BASE_URL.endswith('/') and endpoint.startswith('/'):
        return f"{API_BASE_URL[:-1]}{endpoint}"
        """
            )
        
        # Write the fixed content
        with open('web_routes.py', 'w') as f:
            f.write(content)
        
        print("Fixed API URL in web_routes.py")
        return True
    except Exception as e:
        print(f"Error fixing web_routes.py: {str(e)}")
        return False

# Create a direct fix to the issue by modifying how API requests are made
def create_api_fix():
    """Create a direct fix for API requests"""
    print("Creating direct API fix...")
    
    api_fix_content = '''"""
Direct fix for API requests in web interface
"""

import requests

# Fix for the "No scheme supplied" error
def api_request(method, endpoint, data=None, params=None):
    """
    Make a request to the API with proper URL formatting.
    
    Args:
        method (str): HTTP method (GET, POST, PUT, DELETE)
        endpoint (str): API endpoint
        data (dict, optional): Data for POST/PUT requests
        params (dict, optional): Query parameters
        
    Returns:
        Response object
    """
    # Add scheme and host if endpoint is a relative URL
    if not endpoint.startswith(('http://', 'https://')):
        # Use the container name for direct access within Docker network
        url = f"http://localhost:5000{endpoint}"
    else:
        url = endpoint
    
    print(f"Making API request to: {url}")
    
    if method == 'GET':
        response = requests.get(url, params=params)
    elif method == 'POST':
        response = requests.post(url, json=data)
    elif method == 'PUT':
        response = requests.put(url, json=data)
    elif method == 'DELETE':
        response = requests.delete(url)
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    return response
'''
    
    try:
        with open('api_fix.py', 'w') as f:
            f.write(api_fix_content)
        print("Created api_fix.py")
        
        # Now update web_routes.py to import and use the fixed function
        with open('web_routes.py', 'r') as f:
            content = f.read()
        
        if "def api_request(" in content:
            # Replace the api_request function with an import
            content = content.replace(
                "def api_request(method, endpoint, data=None, params=None):",
                "# Import the fixed api_request function\nfrom api_fix import api_request\n\n# Original function replaced by import\n'''\ndef api_request(method, endpoint, data=None, params=None):"
            )
            
            # Find the end of the function to close the multiline comment
            import re
            function_body = re.search(r"def api_request\([^)]+\):.*?return response", content, re.DOTALL)
            if function_body:
                function_end = function_body.end()
                content = content[:function_end] + "\n'''" + content[function_end:]
        
        # Write the updated web_routes.py
        with open('web_routes.py', 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error creating API fix: {str(e)}")
        return False

# Update API base URL to use container networking
def update_api_base_url_container():
    """Update API base URL to use container networking"""
    print("Updating API base URL for container networking...")
    
    try:
        # Read the file
        with open('web_routes.py', 'r') as f:
            content = f.read()
        
        # Update the API_BASE_URL to use the API container name
        if "API_BASE_URL =" in content:
            # Replace with container name for Docker networking
            content = content.replace(
                "API_BASE_URL =",
                "# API_BASE_URL for internal Docker networking\nAPI_BASE_URL = 'http://astronomy-api:5000'"
            )
        
        # Write the fixed content
        with open('web_routes.py', 'w') as f:
            f.write(content)
        
        print("Updated API base URL for container networking")
        return True
    except Exception as e:
        print(f"Error updating API base URL: {str(e)}")
        return False

# Main function
if __name__ == '__main__':
    # First try to fix the API URL in web_routes.py
    fix_api_url()
    
    # Create a direct fix for API requests
    create_api_fix()
    
    # Update API base URL for container networking
    update_api_base_url_container()
