"""
Simple test to check for import errors
"""

print("Starting import test...")

try:
    print("Importing Flask...")
    from flask import Flask, jsonify, redirect, url_for, render_template, request, flash
    print("Flask imported successfully")
    
    print("Importing Flask extensions...")
    from flask_restful import Api, Resource
    from flask_sqlalchemy import SQLAlchemy
    print("Flask extensions imported successfully")
    
    print("Importing other modules...")
    import os
    import json
    from datetime import datetime
    print("Other modules imported successfully")
    
    print("All imports successful!")
except ImportError as e:
    print(f"Import error: {str(e)}")
