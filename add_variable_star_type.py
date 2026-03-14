# add_variable_star_type.py
"""
Add Variable Star type and example variable stars to the database
"""

import pymysql
import time

def add_variable_star_type():
    """Add Variable Star as a new type"""
    print("Adding Variable Star type to database...")
    
    try:
        conn = pymysql.connect(
            host='astronomy-db',
            port=3306,
            user='astronomy',
            password='astronomy',
            database='astronomy_db'
        )
        
        with conn.cursor() as cursor:
            # Check if Variable Star type already exists
            cursor.execute("SELECT COUNT(*) FROM types WHERE name = 'Variable Star'")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Add Variable Star type
                cursor.execute("INSERT INTO types (id, name) VALUES (7, 'Variable Star')")
                print("Variable Star type added successfully!")
                
                # Add some example variable stars
                cursor.execute("""
                INSERT INTO objects (id, name, desination, type, props) 
                VALUES (20, 'Delta Cephei', 'δ Cep', 7, '{"type": "Classical Cepheid", "period": "5.366341 days", "magnitude_range": "3.48-4.37"}')
                """)
                
                cursor.execute("""
                INSERT INTO objects (id, name, desination, type, props) 
                VALUES (21, 'Mira', 'ο Cet', 7, '{"type": "Mira variable", "period": "332 days", "magnitude_range": "2.0-10.1"}')
                """)
                
                cursor.execute("""
                INSERT INTO objects (id, name, desination, type, props) 
                VALUES (22, 'Algol', 'β Per', 7, '{"type": "Eclipsing binary (EA)", "period": "2.867328 days", "magnitude_range": "2.1-3.4"}')
                """)
                
                cursor.execute("""
                INSERT INTO objects (id, name, desination, type, props) 
                VALUES (23, 'R Leonis', 'R Leo', 7, '{"type": "Mira variable", "period": "310 days", "magnitude_range": "4.4-11.3"}')
                """)
                
                cursor.execute("""
                INSERT INTO objects (id, name, desination, type, props) 
                VALUES (24, 'SS Cygni', 'SS Cyg', 7, '{"type": "Dwarf nova", "period": "variable", "magnitude_range": "8.2-12.4"}')
                """)
                
                print("Example variable stars added!")
            else:
                print("Variable Star type already exists")
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error adding variable star type: {str(e)}")
        return False

if __name__ == '__main__':
    time.sleep(5)  # Wait for database
    add_variable_star_type()