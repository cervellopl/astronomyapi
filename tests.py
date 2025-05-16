"""
Astronomy API Tests
=================
Unit and integration tests for the Astronomy Observations API.

This module contains tests for all API endpoints and database models.
"""

import unittest
import json
import os
from datetime import datetime, timedelta
from flask_testing import TestCase

from config import app, db, configure_app
from models import Type, Property, Place, Instrument, Object, Observation
from server import api  # Import to register API resources


class BaseTestCase(TestCase):
    """Base test case class."""
    
    def create_app(self):
        """Configure the Flask application for testing."""
        app = configure_app(app, 'testing')
        return app
    
    def setUp(self):
        """Set up test environment before each test."""
        db.create_all()
        self._seed_test_data()
    
    def tearDown(self):
        """Clean up test environment after each test."""
        db.session.remove()
        db.drop_all()
    
    def _seed_test_data(self):
        """Seed the database with test data."""
        # Create test types
        galaxy_type = Type(id=1, name="Galaxy")
        planet_type = Type(id=2, name="Planet")
        
        db.session.add_all([galaxy_type, planet_type])
        db.session.commit()
        
        # Create test properties
        magnitude_prop = Property(id=1, name="Magnitude", valueType="float")
        distance_prop = Property(id=2, name="Distance", valueType="string")
        
        db.session.add_all([magnitude_prop, distance_prop])
        db.session.commit()
        
        # Create test places
        greenwich = Place(
            id=1,
            name="Royal Observatory Greenwich",
            lat="51.4778",
            lon="0.0015",
            alt="45m",
            timezone="Europe/London"
        )
        
        mauna_kea = Place(
            id=2,
            name="Mauna Kea Observatory",
            lat="19.8208",
            lon="-155.4681",
            alt="4205m",
            timezone="Pacific/Honolulu"
        )
        
        db.session.add_all([greenwich, mauna_kea])
        db.session.commit()
        
        # Create test instruments
        telescope1 = Instrument(
            id=1,
            name="Celestron NexStar 8SE",
            aperture="203.2mm",
            power="2032mm"
        )
        
        telescope2 = Instrument(
            id=2,
            name="Subaru Telescope",
            aperture="8.2m",
            power="Primary f/1.83, Final f/12.2"
        )
        
        db.session.add_all([telescope1, telescope2])
        db.session.commit()
        
        # Create test objects
        andromeda = Object(
            id=1,
            name="Andromeda Galaxy",
            desination="M31",
            type=1,  # Galaxy
            props=json.dumps({
                "distance": "2.537 million light years",
                "diameter": "220,000 light years",
                "constellation": "Andromeda"
            })
        )
        
        mars = Object(
            id=2,
            name="Mars",
            desination="Sol d",
            type=2,  # Planet
            props=json.dumps({
                "distance": "227.9 million km from Sun",
                "diameter": "6,779 km",
                "moons": 2
            })
        )
        
        db.session.add_all([andromeda, mars])
        db.session.commit()
        
        # Create test observations
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)
        
        observations = [
            Observation(
                object=1,  # Andromeda
                place=1,   # Greenwich
                instrument=1,  # Celestron
                datetime=now,
                observation="Clear spiral structure visible. Excellent seeing conditions.",
                prop1=1,  # Magnitude property
                prop1value="3.4"
            ),
            Observation(
                object=2,  # Mars
                place=2,   # Mauna Kea
                instrument=2,  # Subaru
                datetime=yesterday,
                observation="Detailed surface features and polar ice caps visible.",
                prop1=2,  # Distance property
                prop1value="78.34 million km"
            ),
            Observation(
                object=1,  # Andromeda
                place=2,   # Mauna Kea
                instrument=2,  # Subaru
                datetime=last_week,
                observation="High-resolution imaging of dust lanes and central core.",
                prop1=1,  # Magnitude property
                prop1value="3.2"
            )
        ]
        
        db.session.add_all(observations)
        db.session.commit()


# =============================================================================
# Type Tests
# =============================================================================

class TypeTestCase(BaseTestCase):
    """Test cases for Type API endpoints."""
    
    def test_get_types(self):
        """Test getting all types."""
        response = self.client.get('/api/types')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Galaxy')
        self.assertEqual(data[1]['name'], 'Planet')
    
    def test_get_type(self):
        """Test getting a specific type."""
        response = self.client.get('/api/types/1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Galaxy')
    
    def test_get_nonexistent_type(self):
        """Test getting a nonexistent type."""
        response = self.client.get('/api/types/999')
        self.assertEqual(response.status_code, 404)
    
    def test_create_type(self):
        """Test creating a new type."""
        new_type = {'name': 'Star'}
        response = self.client.post(
            '/api/types',
            data=json.dumps(new_type),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Star')
        
        # Verify the type was created in the database
        created_type = Type.query.filter_by(name='Star').first()
        self.assertIsNotNone(created_type)
    
    def test_update_type(self):
        """Test updating a type."""
        updated_type = {'name': 'Spiral Galaxy'}
        response = self.client.put(
            '/api/types/1',
            data=json.dumps(updated_type),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Spiral Galaxy')
        
        # Verify the type was updated in the database
        type_obj = Type.query.get(1)
        self.assertEqual(type_obj.name, 'Spiral Galaxy')
    
    def test_delete_type(self):
        """Test deleting a type that is not in use."""
        # Create a new type that won't be in use
        new_type = Type(name='Test Type')
        db.session.add(new_type)
        db.session.commit()
        
        type_id = new_type.id
        
        response = self.client.delete(f'/api/types/{type_id}')
        self.assertEqual(response.status_code, 204)
        
        # Verify the type was deleted from the database
        deleted_type = Type.query.get(type_id)
        self.assertIsNone(deleted_type)
    
    def test_delete_type_in_use(self):
        """Test deleting a type that is in use."""
        response = self.client.delete('/api/types/1')  # Galaxy type is in use by Andromeda
        self.assertEqual(response.status_code, 400)


# =============================================================================
# Property Tests
# =============================================================================

class PropertyTestCase(BaseTestCase):
    """Test cases for Property API endpoints."""
    
    def test_get_properties(self):
        """Test getting all properties."""
        response = self.client.get('/api/properties')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Magnitude')
        self.assertEqual(data[1]['name'], 'Distance')
    
    def test_get_property(self):
        """Test getting a specific property."""
        response = self.client.get('/api/properties/1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Magnitude')
        self.assertEqual(data['valueType'], 'float')
    
    def test_create_property(self):
        """Test creating a new property."""
        new_property = {
            'name': 'Temperature',
            'valueType': 'float'
        }
        response = self.client.post(
            '/api/properties',
            data=json.dumps(new_property),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Temperature')
        self.assertEqual(data['valueType'], 'float')
    
    def test_update_property(self):
        """Test updating a property."""
        updated_property = {
            'name': 'Brightness',
            'valueType': 'float'
        }
        response = self.client.put(
            '/api/properties/1',
            data=json.dumps(updated_property),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Brightness')
        
        # Verify the property was updated in the database
        prop = Property.query.get(1)
        self.assertEqual(prop.name, 'Brightness')


# =============================================================================
# Observation Tests
# =============================================================================

class ObservationTestCase(BaseTestCase):
    """Test cases for Observation API endpoints."""
    
    def test_get_observations(self):
        """Test getting all observations."""
        response = self.client.get('/api/observations')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
    
    def test_get_observation(self):
        """Test getting a specific observation."""
        response = self.client.get('/api/observations/1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['object'], 1)  # Andromeda
        self.assertEqual(data['place'], 1)   # Greenwich
    
    def test_create_observation(self):
        """Test creating a new observation."""
        new_observation = {
            'object': 2,  # Mars
            'place': 1,   # Greenwich
            'instrument': 1,  # Celestron
            'datetime': datetime.utcnow().isoformat(),
            'observation': 'New test observation',
            'prop1': 1,  # Magnitude property
            'prop1value': '4.2'
        }
        response = self.client.post(
            '/api/observations',
            data=json.dumps(new_observation),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['object'], 2)
        self.assertEqual(data['observation'], 'New test observation')
    
    def test_update_observation(self):
        """Test updating an observation."""
        updated_observation = {
            'observation': 'Updated observation text',
            'prop1value': '3.8'
        }
        response = self.client.put(
            '/api/observations/1',
            data=json.dumps(updated_observation),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['observation'], 'Updated observation text')
        self.assertEqual(data['prop1value'], '3.8')
    
    def test_delete_observation(self):
        """Test deleting an observation."""
        response = self.client.delete('/api/observations/1')
        self.assertEqual(response.status_code, 204)
        
        # Verify the observation was deleted from the database
        deleted_observation = Observation.query.get(1)
        self.assertIsNone(deleted_observation)


# =============================================================================
# Search Tests
# =============================================================================

class SearchTestCase(BaseTestCase):
    """Test cases for search functionality."""
    
    def test_search_by_object(self):
        """Test searching observations by object."""
        response = self.client.get('/api/observations/search?object_id=1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)  # Should find 2 observations of Andromeda
        
        for obs in data:
            self.assertEqual(obs['object'], 1)  # All observations should be of Andromeda
    
    def test_search_by_place(self):
        """Test searching observations by place."""
        response = self.client.get('/api/observations/search?place_id=2')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)  # Should find 2 observations from Mauna Kea
        
        for obs in data:
            self.assertEqual(obs['place'], 2)  # All observations should be from Mauna Kea
    
    def test_search_by_instrument(self):
        """Test searching observations by instrument."""
        response = self.client.get('/api/observations/search?instrument_id=1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)  # Should find 1 observation with Celestron
        
        for obs in data:
            self.assertEqual(obs['instrument'], 1)  # All observations should be with Celestron
    
    def test_search_by_date_range(self):
        """Test searching observations by date range."""
        now = datetime.utcnow()
        yesterday = (now - timedelta(days=1)).isoformat()
        tomorrow = (now + timedelta(days=1)).isoformat()
        
        response = self.client.get(f'/api/observations/search?start_date={yesterday}&end_date={tomorrow}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)  # Should find observations from yesterday and today
    
    def test_search_with_multiple_filters(self):
        """Test searching observations with multiple filters."""
        now = datetime.utcnow()
        last_month = (now - timedelta(days=30)).isoformat()
        tomorrow = (now + timedelta(days=1)).isoformat()
        
        response = self.client.get(
            f'/api/observations/search?start_date={last_month}&end_date={tomorrow}&object_id=1&instrument_id=2'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)  # Should find 1 observation of Andromeda with Subaru
        
        obs = data[0]
        self.assertEqual(obs['object'], 1)        # Andromeda
        self.assertEqual(obs['instrument'], 2)    # Subaru


# =============================================================================
# Relationship Tests
# =============================================================================

class RelationshipTestCase(BaseTestCase):
    """Test cases for relationship endpoints."""
    
    def test_object_observations(self):
        """Test getting observations for a specific object."""
        response = self.client.get('/api/objects/1/observations')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)  # Should find 2 observations of Andromeda
        
        for obs in data:
            self.assertEqual(obs['object'], 1)  # All observations should be of Andromeda
    
    def test_place_observations(self):
        """Test getting observations for a specific place."""
        response = self.client.get('/api/places/1/observations')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)  # Should find 1 observation from Greenwich
        
        for obs in data:
            self.assertEqual(obs['place'], 1)  # All observations should be from Greenwich
    
    def test_instrument_observations(self):
        """Test getting observations for a specific instrument."""
        response = self.client.get('/api/instruments/2/observations')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)  # Should find 2 observations with Subaru
        
        for obs in data:
            self.assertEqual(obs['instrument'], 2)  # All observations should be with Subaru


# =============================================================================
# Main Test Runner
# =============================================================================

if __name__ == '__main__':
    unittest.main()
