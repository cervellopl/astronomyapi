"""
Simple test to check for syntax errors in server.py
"""

import os
import sys

print("Checking server.py for syntax errors...")

try:
    # Open and read the file
    with open('server.py', 'r') as f:
        content = f.readlines()
    
    # Print line numbers and content around line 22
    print("Content around line 22:")
    for i in range(max(0, 22-5), min(len(content), 22+5)):
        print(f"{i+1:3d}: {content[i].rstrip()}")
    
    # Try to compile the file to check for syntax errors
    compile(''.join(content), 'server.py', 'exec')
    
    print("No syntax errors detected in compilation.")
except Exception as e:
    print(f"Error: {str(e)}")
