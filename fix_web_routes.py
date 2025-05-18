"""
Fix web_routes.py to use direct API access
"""

import os

def fix_web_routes():
    """Fix web_routes.py to use direct API access"""
    print("Fixing web_routes.py to use direct API access...")
    
    try:
        # Read the file
        with open('web_routes.py', 'r') as f:
            content = f.read()
        
        # Replace the api_request import/function with direct API access
        if "import requests" in content:
            content = content.replace(
                "import requests",
                "# Using direct API access instead of HTTP requests\nfrom direct_api import api_request"
            )
        
        # Remove or comment out the api_request function if present
        if "def api_request(" in content:
            import re
            # Match the full function definition
            pattern = r"def api_request\([^)]*\):.*?return response"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                function_text = match.group(0)
                commented_function = "'''\n" + function_text + "\n'''"
                content = content.replace(function_text, commented_function)
        
        # Write the fixed content
        with open('web_routes.py', 'w') as f:
            f.write(content)
        
        print("Fixed web_routes.py to use direct API access")
        return True
    except Exception as e:
        print(f"Error fixing web_routes.py: {str(e)}")
        return False

# Main function
if __name__ == '__main__':
    fix_web_routes()
