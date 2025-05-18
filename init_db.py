"""
Initialize database schema directly from SQL file
"""

import os
import pymysql
import time

def wait_for_database():
    """Wait for the database to be ready."""
    host = os.environ.get('DATABASE_URL', 'mysql+pymysql://astronomy:astronomy@astronomy-db:3306/astronomy_db')
    
    # Extract host, port, user, password, and database from the DATABASE_URL
    if 'mysql+pymysql://' in host:
        parts = host.replace('mysql+pymysql://', '').split('@')
        user_pass = parts[0].split(':')
        host_port_db = parts[1].split('/')
        
        user = user_pass[0]
        password = user_pass[1]
        host_port = host_port_db[0].split(':')
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 3306
        database = host_port_db[1]
    else:
        # Default values
        host = 'astronomy-db'
        port = 3306
        user = 'astronomy'
        password = 'astronomy'
        database = 'astronomy_db'
    
    print(f"Waiting for database at {host}:{port}...")
    
    retries = 30
    while retries > 0:
        try:
            # Try to connect to the database
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            conn.close()
            print("Database is ready!")
            return True
        except Exception as e:
            retries -= 1
            if retries == 0:
                print(f"Could not connect to database: {str(e)}")
                return False
            print(f"Database not ready (retries left: {retries}). Waiting...")
            time.sleep(2)
    
    return False

def initialize_database():
    """Initialize the database schema."""
    print("Initializing database schema...")
    
    host = os.environ.get('DATABASE_URL', 'mysql+pymysql://astronomy:astronomy@astronomy-db:3306/astronomy_db')
    
    # Extract host, port, user, password, and database from the DATABASE_URL
    if 'mysql+pymysql://' in host:
        parts = host.replace('mysql+pymysql://', '').split('@')
        user_pass = parts[0].split(':')
        host_port_db = parts[1].split('/')
        
        user = user_pass[0]
        password = user_pass[1]
        host_port = host_port_db[0].split(':')
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 3306
        database = host_port_db[1]
    else:
        # Default values
        host = 'astronomy-db'
        port = 3306
        user = 'astronomy'
        password = 'astronomy'
        database = 'astronomy_db'
    
    try:
        # Try to execute the SQL file directly
        if os.path.exists('mc3jpyObs.sql'):
            print("Using mc3jpyObs.sql file to initialize database...")
            
            # Load SQL file contents
            with open('mc3jpyObs.sql', 'r') as f:
                sql_content = f.read()
            
            # Connect to the database
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            
            # Execute SQL statements
            with conn.cursor() as cursor:
                # Split and execute each statement
                for statement in sql_content.split(';'):
                    if statement.strip():
                        print(f"Executing: {statement[:50]}...")
                        cursor.execute(statement)
            
            conn.commit()
            conn.close()
            
            print("Database schema initialized successfully!")
            return True
        else:
            print("SQL file not found. Creating tables from scratch...")
            
            # Connect to the database
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            
            # Create tables
            with conn.cursor() as cursor:
                # Create instruments table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS `instruments` (
                  `id` int NOT NULL,
                  `name` varchar(255) DEFAULT NULL,
                  `aperture` varchar(255) DEFAULT NULL,
                  `power` varchar(255) DEFAULT NULL,
                  PRIMARY KEY (`id`)
                )
                ''')
                
                # Create types table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS `types` (
                  `id` int NOT NULL,
                  `name` varchar(255) DEFAULT NULL,
                  PRIMARY KEY (`id`)
                )
                ''')
                
                # Create properities table (note the spelling from original SQL)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS `properities` (
                  `id` int NOT NULL,
                  `name` varchar(255) DEFAULT NULL,
                  `valueType` varchar(255) DEFAULT NULL,
                  PRIMARY KEY (`id`)
                )
                ''')
                
                # Create places table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS `places` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `name` varchar(255) DEFAULT NULL,
                  `lat` varchar(255) DEFAULT NULL,
                  `lon` varchar(255) DEFAULT NULL,
                  `alt` varchar(255) DEFAULT NULL,
                  `timezone` varchar(255) DEFAULT NULL,
                  PRIMARY KEY (`id`)
                )
                ''')
                
                # Create objects table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS `objects` (
                  `id` int NOT NULL,
                  `name` varchar(255) DEFAULT NULL,
                  `desination` varchar(255) DEFAULT NULL,
                  `type` int DEFAULT NULL,
                  `props` longtext,
                  PRIMARY KEY (`id`),
                  KEY `type` (`type`),
                  CONSTRAINT `type` FOREIGN KEY (`type`) REFERENCES `types` (`id`)
                )
                ''')
                
                # Create observations table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS `observations` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `object` int DEFAULT NULL,
                  `place` int DEFAULT NULL,
                  `instrument` int DEFAULT NULL,
                  `datetime` datetime DEFAULT NULL,
                  `observation` varchar(255) DEFAULT NULL,
                  `prop1` int DEFAULT NULL,
                  `prop1value` varchar(255) DEFAULT NULL,
                  PRIMARY KEY (`id`),
                  KEY `instr` (`instrument`),
                  KEY `place` (`place`),
                  KEY `obj` (`object`),
                  KEY `prop1` (`prop1`),
                  CONSTRAINT `instr` FOREIGN KEY (`instrument`) REFERENCES `instruments` (`id`),
                  CONSTRAINT `obj` FOREIGN KEY (`object`) REFERENCES `objects` (`id`),
                  CONSTRAINT `place` FOREIGN KEY (`place`) REFERENCES `places` (`id`),
                  CONSTRAINT `prop1` FOREIGN KEY (`prop1`) REFERENCES `properities` (`id`)
                )
                ''')
            
            conn.commit()
            conn.close()
            
            print("Database tables created successfully!")
            return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False

def seed_database_with_sample_data():
    """Seed the database with sample data."""
    print("Seeding database with sample data...")
    
    host = os.environ.get('DATABASE_URL', 'mysql+pymysql://astronomy:astronomy@astronomy-db:3306/astronomy_db')
    
    # Extract host, port, user, password, and database from the DATABASE_URL
    if 'mysql+pymysql://' in host:
        parts = host.replace('mysql+pymysql://', '').split('@')
        user_pass = parts[0].split(':')
        host_port_db = parts[1].split('/')
        
        user = user_pass[0]
        password = user_pass[1]
        host_port = host_port_db[0].split(':')
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 3306
        database = host_port_db[1]
    else:
        # Default values
        host = 'astronomy-db'
        port = 3306
        user = 'astronomy'
        password = 'astronomy'
        database = 'astronomy_db'
    
    try:
        # Connect to the database
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        # Seed tables
        with conn.cursor() as cursor:
            # Check if there's data already
            cursor.execute("SELECT COUNT(*) FROM types")
            count = cursor.fetchone()[0]
            
            if count > 0:
                print("Database already has data, skipping seed...")
                conn.close()
                return True
            
            # Insert types
            cursor.execute("INSERT INTO types (id, name) VALUES (1, 'Galaxy')")
            cursor.execute("INSERT INTO types (id, name) VALUES (2, 'Star')")
            cursor.execute("INSERT INTO types (id, name) VALUES (3, 'Planet')")
            cursor.execute("INSERT INTO types (id, name) VALUES (4, 'Nebula')")
            cursor.execute("INSERT INTO types (id, name) VALUES (5, 'Asteroid')")
            
            # Insert properties
            cursor.execute("INSERT INTO properities (id, name, valueType) VALUES (1, 'Magnitude', 'float')")
            cursor.execute("INSERT INTO properities (id, name, valueType) VALUES (2, 'Distance', 'string')")
            cursor.execute("INSERT INTO properities (id, name, valueType) VALUES (3, 'Temperature', 'float')")
            
            # Insert instruments
            cursor.execute("INSERT INTO instruments (id, name, aperture, power) VALUES (1, 'Celestron NexStar 8SE', '203.2mm', '2032mm')")
            cursor.execute("INSERT INTO instruments (id, name, aperture, power) VALUES (2, 'Subaru Telescope', '8.2m', 'Primary f/1.83, Final f/12.2')")
            
            # Insert places
            cursor.execute('''
            INSERT INTO places (name, lat, lon, alt, timezone) 
            VALUES ('Royal Observatory Greenwich', '51.4778', '0.0015', '45m', 'Europe/London')
            ''')
            cursor.execute('''
            INSERT INTO places (name, lat, lon, alt, timezone) 
            VALUES ('Mauna Kea Observatory', '19.8208', '-155.4681', '4205m', 'Pacific/Honolulu')
            ''')
            
            # Insert objects
            cursor.execute('''
            INSERT INTO objects (id, name, desination, type, props) 
            VALUES (1, 'Andromeda Galaxy', 'M31', 1, '{"distance": "2.537 million light years", "diameter": "220,000 light years"}')
            ''')
            cursor.execute('''
            INSERT INTO objects (id, name, desination, type, props) 
            VALUES (2, 'Mars', 'Sol d', 3, '{"distance": "227.9 million km from Sun", "diameter": "6,779 km"}')
            ''')
            
            # Insert observations
            cursor.execute('''
            INSERT INTO observations (object, place, instrument, datetime, observation, prop1, prop1value)
            VALUES (1, 1, 1, NOW(), 'Clear spiral structure visible. Excellent seeing conditions.', 1, '3.4')
            ''')
            cursor.execute('''
            INSERT INTO observations (object, place, instrument, datetime, observation, prop1, prop1value)
            VALUES (2, 2, 2, NOW(), 'Detailed surface features and polar ice caps visible.', 2, '78.34 million km')
            ''')
        
        conn.commit()
        conn.close()
        
        print("Database seeded with sample data successfully!")
        return True
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        return False

if __name__ == '__main__':
    # Make sure the database is ready
    if wait_for_database():
        # Initialize the database schema
        if initialize_database():
            # Seed the database with sample data
            seed_database_with_sample_data()
