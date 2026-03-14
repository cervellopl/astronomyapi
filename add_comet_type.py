# add_comet_type.py
"""
Add Comet type to the database
"""

import pymysql
import time

def add_comet_type():
    """Add Comet as a new type"""
    print("Adding Comet type to database...")
    
    try:
        conn = pymysql.connect(
            host='astronomy-db',
            port=3306,
            user='astronomy',
            password='astronomy',
            database='astronomy_db'
        )
        
        with conn.cursor() as cursor:
            # Check if Comet type already exists
            cursor.execute("SELECT COUNT(*) FROM types WHERE name = 'Comet'")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Add Comet type
                cursor.execute("INSERT INTO types (id, name) VALUES (6, 'Comet')")
                print("Comet type added successfully!")
                
                # Add some example comets
                cursor.execute("""
                INSERT INTO objects (id, name, desination, type, props) 
                VALUES (10, 'Comet Halley', '1P/Halley', 6, '{"period": "75-76 years", "last_perihelion": "1986"}')
                """)
                
                cursor.execute("""
                INSERT INTO objects (id, name, desination, type, props) 
                VALUES (11, 'Comet NEOWISE', 'C/2020 F3', 6, '{"discovery": "2020-03-27", "perihelion": "2020-07-03"}')
                """)
                
                print("Example comets added!")
            else:
                print("Comet type already exists")
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error adding comet type: {str(e)}")
        return False

if __name__ == '__main__':
    time.sleep(5)  # Wait for database
    add_comet_type()