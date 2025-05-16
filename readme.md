# Astronomy Observations API

A comprehensive Python API for managing astronomical observations, including celestial objects, observation locations, instruments, and more.

## Overview

This API provides a complete interface for astronomers to:

- Track and catalog celestial objects with detailed properties
- Record observation data from different locations
- Manage astronomical instruments
- Search and filter observations based on various criteria

## Features

- **RESTful API**: Full CRUD operations for all database entities
- **Comprehensive Schema**: Based on a well-designed relational database schema
- **Flexible Search**: Advanced filtering and relationship querying
- **Validation**: Data validation and error handling
- **Documentation**: Detailed API documentation with endpoint descriptions
- **Docker Support**: Easy deployment using Docker and docker-compose

## Installation

### Option 1: Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/astronomy-api.git
   cd astronomy-api
   ```

2. Create a `.env` file with your configuration:
   ```
   MYSQL_ROOT_PASSWORD=securepassword
   MYSQL_DATABASE=astronomy_db
   MYSQL_USER=astronomy
   MYSQL_PASSWORD=astronomy_password
   FLASK_CONFIG=production
   SECRET_KEY=your-secret-key
   API_PORT=5000
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the API at http://localhost:5000

### Option 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/astronomy-api.git
   cd astronomy-api
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your MySQL database and create the database schema:
   ```bash
   mysql -u root -p
   CREATE DATABASE astronomy_db;
   exit
   ```

5. Set up environment variables:
   ```bash
   export DATABASE_URL=mysql+pymysql://username:password@localhost/astronomy_db
   export FLASK_CONFIG=development
   export FLASK_APP=server.py
   ```

6. Initialize and seed the database:
   ```bash
   flask init-db
   flask seed-db
   ```

7. Start the development server:
   ```bash
   flask run
   ```

## API Usage

### Python Client Library

The repository includes a Python client library (`astronomy_client.py`) that makes it easy to interact with the API:

```python
from astronomy_client import AstronomyClient

# Initialize the client
client = AstronomyClient('http://localhost:5000')

# Get all observations
observations = client.get_observations()

# Create a new celestial object
new_object = client.create_object(
    name="Europa",
    type_id=3,  # Planet/Moon type
    designation="Jupiter II",
    props='{"distance": "628.3 million km", "diameter": "3,122 km"}'
)

# Record an observation
observation = client.create_observation(
    object_id=new_object['id'],
    place_id=1,  # Greenwich Observatory
    instrument_id=1,  # Celestron telescope
    observation_datetime=datetime.now(),
    observation_text="Subsurface ocean detected through spectral analysis.",
    property_id=2,  # Distance property
    property_value="628.3 million km"
)
```

### REST API Endpoints

The API provides the following endpoints:

#### Types
- `GET /api/types` - Get all types
- `POST /api/types` - Create a new type
- `GET /api/types/<id>` - Get a specific type
- `PUT /api/types/<id>` - Update a specific type
- `DELETE /api/types/<id>` - Delete a specific type

#### Properties
- `GET /api/properties` - Get all properties
- `POST /api/properties` - Create a new property
- `GET /api/properties/<id>` - Get a specific property
- `PUT /api/properties/<id>` - Update a specific property
- `DELETE /api/properties/<id>` - Delete a specific property

#### Places
- `GET /api/places` - Get all places
- `POST /api/places` - Create a new place
- `GET /api/places/<id>` - Get a specific place
- `PUT /api/places/<id>` - Update a specific place
- `DELETE /api/places/<id>` - Delete a specific place
- `GET /api/places/<id>/observations` - Get all observations made at a specific place

#### Instruments
- `GET /api/instruments` - Get all instruments
- `POST /api/instruments` - Create a new instrument
- `GET /api/instruments/<id>` - Get a specific instrument
- `PUT /api/instruments/<id>` - Update a specific instrument
- `DELETE /api/instruments/<id>` - Delete a specific instrument
- `GET /api/instruments/<id>/observations` - Get all observations made with a specific instrument

#### Objects
- `GET /api/objects` - Get all objects
- `POST /api/objects` - Create a new object
- `GET /api/objects/<id>` - Get a specific object
- `PUT /api/objects/<id>` - Update a specific object
- `DELETE /api/objects/<id>` - Delete a specific object
- `GET /api/objects/<id>/observations` - Get all observations of a specific object

#### Observations
- `GET /api/observations` - Get all observations
- `POST /api/observations` - Create a new observation
- `GET /api/observations/<id>` - Get a specific observation
- `PUT /api/observations/<id>` - Update a specific observation
- `DELETE /api/observations/<id>` - Delete a specific observation
- `GET /api/observations/search` - Search observations with filters (params: start_date, end_date, object_id, place_id, instrument_id)

## Examples

The repository includes example scripts in the `examples` directory that demonstrate common use cases:

- `setup_database.py` - Set up the database with initial data
- `record_observations.py` - Record astronomical observations
- `query_observations.py` - Query and filter observations
- `advanced_search.py` - Perform advanced searches
- `complete_workflow.py` - Run a complete workflow demonstration

## Database Schema

The API is built around the following database schema:

- **types**: Celestial object types (Galaxy, Star, Planet, etc.)
- **properties**: Observation properties (Magnitude, Distance, Temperature, etc.)
- **places**: Observation locations (Observatories, research stations, etc.)
- **instruments**: Astronomical instruments (Telescopes, spectrometers, etc.)
- **objects**: Celestial objects (Andromeda Galaxy, Mars, etc.)
- **observations**: Astronomical observations with details and property values

## Development

### Running Tests

```bash
# Set the environment to testing
export FLASK_CONFIG=testing

# Run the tests
python -m pytest tests/
```

### Migrations

```bash
# Create a migration
flask db migrate -m "Migration message"

# Apply migrations
flask db upgrade
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the SQL schema from `mc3jpyObs.sql`
- Built with Flask, SQLAlchemy, and other open-source tools
