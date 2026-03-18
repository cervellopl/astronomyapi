"""
Direct database table creation
"""

import os
import time
import pymysql

def create_tables_directly():
    """Create database tables directly using SQL"""
    print("Creating database tables directly using SQL...")
    
    # Connection parameters
    try:
        host = 'astronomy-db'
        port = 3306
        user = 'astronomy'
        password = 'astronomy'
        database = 'astronomy_db'
        
        print(f"Connecting to {host}:{port} as {user}...")
        
        # Wait for database to be ready
        retries = 30
        while retries > 0:
            try:
                conn = pymysql.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    connect_timeout=30
                )
                print("Connected to database successfully!")
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    print(f"Failed to connect to database: {str(e)}")
                    return False
                print(f"Database not ready yet. Retrying in 2 seconds... ({retries} retries left)")
                print(f"Error: {str(e)}")
                time.sleep(2)
        
        # Create tables
        with conn.cursor() as cursor:
            # Drop tables if they exist
            cursor.execute("DROP TABLE IF EXISTS observations")
            cursor.execute("DROP TABLE IF EXISTS sessions")
            cursor.execute("DROP TABLE IF EXISTS objects")
            cursor.execute("DROP TABLE IF EXISTS places")
            cursor.execute("DROP TABLE IF EXISTS instruments")
            cursor.execute("DROP TABLE IF EXISTS properities")
            cursor.execute("DROP TABLE IF EXISTS types")
            cursor.execute("DROP TABLE IF EXISTS users")
            
            # Create types table
            print("Creating types table...")
            cursor.execute("""
            CREATE TABLE types (
                id INT NOT NULL,
                name VARCHAR(255),
                PRIMARY KEY (id)
            )
            """)
            
            # Create properities table
            print("Creating properities table...")
            cursor.execute("""
            CREATE TABLE properities (
                id INT NOT NULL,
                name VARCHAR(255),
                valueType VARCHAR(255),
                PRIMARY KEY (id)
            )
            """)
            
            # Create places table
            print("Creating places table...")
            cursor.execute("""
            CREATE TABLE places (
                id INT NOT NULL AUTO_INCREMENT,
                name VARCHAR(255),
                lat VARCHAR(255),
                lon VARCHAR(255),
                alt VARCHAR(255),
                timezone VARCHAR(255),
                PRIMARY KEY (id)
            )
            """)
            
            # Create instruments table
            print("Creating instruments table...")
            cursor.execute("""
            CREATE TABLE instruments (
                id INT NOT NULL,
                name VARCHAR(255),
                instrument_type VARCHAR(255),
                aperture VARCHAR(255),
                power VARCHAR(255),
                eyepiece VARCHAR(255),
                PRIMARY KEY (id)
            )
            """)
            
            # Create objects table
            print("Creating objects table...")
            cursor.execute("""
            CREATE TABLE objects (
                id INT NOT NULL,
                name VARCHAR(255),
                desination VARCHAR(255),
                type INT,
                props LONGTEXT,
                PRIMARY KEY (id),
                FOREIGN KEY (type) REFERENCES types(id)
            )
            """)
            
            # Create users table
            print("Creating users table...")
            cursor.execute("""
            CREATE TABLE users (
                id INT NOT NULL AUTO_INCREMENT,
                username VARCHAR(80) NOT NULL UNIQUE,
                email VARCHAR(255),
                password_hash VARCHAR(255) NOT NULL,
                postal_address TEXT,
                aavso_code VARCHAR(20),
                icq_code VARCHAR(20),
                default_timezone VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id)
            )
            """)

            # Create sessions table
            print("Creating sessions table...")
            cursor.execute("""
            CREATE TABLE sessions (
                id INT NOT NULL AUTO_INCREMENT,
                number VARCHAR(20),
                start_datetime DATETIME,
                end_datetime DATETIME,
                cloud_percentage INT,
                cloud_type VARCHAR(255),
                light_pollution INT,
                limiting_magnitude FLOAT,
                moon_phase VARCHAR(50),
                moon_altitude FLOAT,
                instrument INT,
                PRIMARY KEY (id),
                FOREIGN KEY (instrument) REFERENCES instruments(id)
            )
            """)

            # Create observations table
            print("Creating observations table...")
            cursor.execute("""
            CREATE TABLE observations (
                id INT NOT NULL AUTO_INCREMENT,
                object INT,
                place INT,
                instrument INT,
                session_id INT,
                datetime DATETIME,
                observation VARCHAR(255),
                prop1 INT,
                prop1value VARCHAR(255),
                PRIMARY KEY (id),
                FOREIGN KEY (object) REFERENCES objects(id),
                FOREIGN KEY (place) REFERENCES places(id),
                FOREIGN KEY (instrument) REFERENCES instruments(id),
                FOREIGN KEY (session_id) REFERENCES sessions(id),
                FOREIGN KEY (prop1) REFERENCES properities(id)
            )
            """)
            
            # Insert sample data
            print("Inserting sample data...")
            
            # Insert types
            cursor.execute("INSERT INTO types (id, name) VALUES (1, 'Galaxy')")
            cursor.execute("INSERT INTO types (id, name) VALUES (2, 'Star')")
            cursor.execute("INSERT INTO types (id, name) VALUES (3, 'Planet')")
            cursor.execute("INSERT INTO types (id, name) VALUES (4, 'Nebula')")
            cursor.execute("INSERT INTO types (id, name) VALUES (5, 'Asteroid')")
            
            # Insert default admin user (password: admin)
            from werkzeug.security import generate_password_hash
            admin_hash = generate_password_hash('admin')
            cursor.execute(f"INSERT INTO users (username, email, password_hash, default_timezone) VALUES ('admin', 'admin@observatory.local', '{admin_hash}', 'Europe/London')")

            # Insert properties
            cursor.execute("INSERT INTO properities (id, name, valueType) VALUES (1, 'Magnitude', 'float')")
            cursor.execute("INSERT INTO properities (id, name, valueType) VALUES (2, 'Distance', 'string')")
            cursor.execute("INSERT INTO properities (id, name, valueType) VALUES (3, 'Temperature', 'float')")
            
            # Insert instruments
            cursor.execute("INSERT INTO instruments (id, name, instrument_type, aperture, power, eyepiece) VALUES (1, 'Celestron NexStar 8SE', 'SCT', '203.2mm', '2032mm', '25mm Plossl')")
            cursor.execute("INSERT INTO instruments (id, name, instrument_type, aperture, power, eyepiece) VALUES (2, 'Subaru Telescope', 'Reflector', '8.2m', 'Primary f/1.83, Final f/12.2', NULL)")
            cursor.execute("INSERT INTO instruments (id, name, instrument_type, aperture, power, eyepiece) VALUES (3, 'Nikon 10x50 Aculon', 'Binoculars', '50mm', '10x', NULL)")
            cursor.execute("INSERT INTO instruments (id, name, instrument_type, aperture, power, eyepiece) VALUES (4, 'Sky-Watcher 200P', 'Reflector', '200mm', '1000mm f/5', '10mm BST Explorer')")
            
            # Insert places
            cursor.execute("""
            INSERT INTO places (id, name, lat, lon, alt, timezone) 
            VALUES (1, 'Royal Observatory Greenwich', '51.4778', '0.0015', '45m', 'Europe/London')
            """)
            cursor.execute("""
            INSERT INTO places (id, name, lat, lon, alt, timezone) 
            VALUES (2, 'Mauna Kea Observatory', '19.8208', '-155.4681', '4205m', 'Pacific/Honolulu')
            """)
            
            # Insert objects
            cursor.execute("""
            INSERT INTO objects (id, name, desination, type, props) 
            VALUES (1, 'Andromeda Galaxy', 'M31', 1, '{"distance": "2.537 million light years", "diameter": "220,000 light years"}')
            """)
            cursor.execute("""
            INSERT INTO objects (id, name, desination, type, props) 
            VALUES (2, 'Mars', 'Sol d', 3, '{"distance": "227.9 million km from Sun", "diameter": "6,779 km"}')
            """)
            
            # Insert observations
            cursor.execute("""
            INSERT INTO observations (object, place, instrument, datetime, observation, prop1, prop1value)
            VALUES (1, 1, 1, NOW(), 'Clear spiral structure visible. Excellent seeing conditions.', 1, '3.4')
            """)
            cursor.execute("""
            INSERT INTO observations (object, place, instrument, datetime, observation, prop1, prop1value)
            VALUES (2, 2, 2, NOW(), 'Detailed surface features and polar ice caps visible.', 2, '78.34 million km')
            """)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("Database tables created and sample data inserted successfully!")
        return True
    
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        return False

if __name__ == "__main__":
    create_tables_directly()