"""
Astronomy API Client Module
===========================
A Python client library for interacting with the Astronomy Observations API.

This module provides easy-to-use functions for:
- Managing astronomical objects, instruments, and observation places
- Recording and retrieving observations
- Working with observation properties and types
"""

import requests
import json
from datetime import datetime


class AstronomyClient:
    """Client for interacting with the Astronomy Observations API."""
    
    def __init__(self, base_url='http://localhost:5000'):
        """
        Initialize the client with the API base URL.
        
        Args:
            base_url (str): The base URL of the API
        """
        self.base_url = base_url.rstrip('/')
        
    def _handle_response(self, response):
        """
        Handle API response and check for errors.
        
        Args:
            response: The requests Response object
            
        Returns:
            dict: The JSON response if successful
            
        Raises:
            Exception: If API request fails
        """
        if response.status_code >= 400:
            try:
                error_msg = response.json().get('message', 'Unknown error')
            except ValueError:
                error_msg = response.text
            
            raise Exception(f"API error ({response.status_code}): {error_msg}")
        
        return response.json()
    
    # =========================================================================
    # Types API
    # =========================================================================
    
    def get_types(self):
        """
        Get all object types.
        
        Returns:
            list: List of type objects
        """
        response = requests.get(f"{self.base_url}/api/types")
        return self._handle_response(response)
    
    def get_type(self, type_id):
        """
        Get a specific object type.
        
        Args:
            type_id (int): ID of the type
            
        Returns:
            dict: Type object
        """
        response = requests.get(f"{self.base_url}/api/types/{type_id}")
        return self._handle_response(response)
    
    def create_type(self, name):
        """
        Create a new object type.
        
        Args:
            name (str): Name of the type
            
        Returns:
            dict: Created type object
        """
        data = {"name": name}
        response = requests.post(
            f"{self.base_url}/api/types",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def update_type(self, type_id, name):
        """
        Update an object type.
        
        Args:
            type_id (int): ID of the type
            name (str): New name for the type
            
        Returns:
            dict: Updated type object
        """
        data = {"name": name}
        response = requests.put(
            f"{self.base_url}/api/types/{type_id}",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def delete_type(self, type_id):
        """
        Delete an object type.
        
        Args:
            type_id (int): ID of the type to delete
            
        Returns:
            bool: True if successful
        """
        response = requests.delete(f"{self.base_url}/api/types/{type_id}")
        if response.status_code == 204:
            return True
        return self._handle_response(response)
    
    # =========================================================================
    # Properties API
    # =========================================================================
    
    def get_properties(self):
        """
        Get all properties.
        
        Returns:
            list: List of property objects
        """
        response = requests.get(f"{self.base_url}/api/properties")
        return self._handle_response(response)
    
    def get_property(self, property_id):
        """
        Get a specific property.
        
        Args:
            property_id (int): ID of the property
            
        Returns:
            dict: Property object
        """
        response = requests.get(f"{self.base_url}/api/properties/{property_id}")
        return self._handle_response(response)
    
    def create_property(self, name, value_type, property_id=None):
        """
        Create a new property.
        
        Args:
            name (str): Name of the property
            value_type (str): Type of the property value
            property_id (int, optional): ID for the property
            
        Returns:
            dict: Created property object
        """
        data = {
            "name": name,
            "valueType": value_type
        }
        
        if property_id is not None:
            data["id"] = property_id
            
        response = requests.post(
            f"{self.base_url}/api/properties",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def update_property(self, property_id, name, value_type):
        """
        Update a property.
        
        Args:
            property_id (int): ID of the property
            name (str): New name for the property
            value_type (str): New type for the property value
            
        Returns:
            dict: Updated property object
        """
        data = {
            "name": name,
            "valueType": value_type
        }
        
        response = requests.put(
            f"{self.base_url}/api/properties/{property_id}",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def delete_property(self, property_id):
        """
        Delete a property.
        
        Args:
            property_id (int): ID of the property to delete
            
        Returns:
            bool: True if successful
        """
        response = requests.delete(f"{self.base_url}/api/properties/{property_id}")
        if response.status_code == 204:
            return True
        return self._handle_response(response)
    
    # =========================================================================
    # Places API
    # =========================================================================
    
    def get_places(self):
        """
        Get all observation places.
        
        Returns:
            list: List of place objects
        """
        response = requests.get(f"{self.base_url}/api/places")
        return self._handle_response(response)
    
    def get_place(self, place_id):
        """
        Get a specific observation place.
        
        Args:
            place_id (int): ID of the place
            
        Returns:
            dict: Place object
        """
        response = requests.get(f"{self.base_url}/api/places/{place_id}")
        return self._handle_response(response)
    
    def create_place(self, name, latitude, longitude, altitude=None, timezone=None):
        """
        Create a new observation place.
        
        Args:
            name (str): Name of the place
            latitude (str): Latitude of the place
            longitude (str): Longitude of the place
            altitude (str, optional): Altitude of the place
            timezone (str, optional): Timezone of the place
            
        Returns:
            dict: Created place object
        """
        data = {
            "name": name,
            "lat": latitude,
            "lon": longitude
        }
        
        if altitude is not None:
            data["alt"] = altitude
            
        if timezone is not None:
            data["timezone"] = timezone
            
        response = requests.post(
            f"{self.base_url}/api/places",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def update_place(self, place_id, name=None, latitude=None, longitude=None, altitude=None, timezone=None):
        """
        Update an observation place.
        
        Args:
            place_id (int): ID of the place
            name (str, optional): New name for the place
            latitude (str, optional): New latitude for the place
            longitude (str, optional): New longitude for the place
            altitude (str, optional): New altitude for the place
            timezone (str, optional): New timezone for the place
            
        Returns:
            dict: Updated place object
        """
        data = {}
        
        if name is not None:
            data["name"] = name
            
        if latitude is not None:
            data["lat"] = latitude
            
        if longitude is not None:
            data["lon"] = longitude
            
        if altitude is not None:
            data["alt"] = altitude
            
        if timezone is not None:
            data["timezone"] = timezone
            
        response = requests.put(
            f"{self.base_url}/api/places/{place_id}",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def delete_place(self, place_id):
        """
        Delete an observation place.
        
        Args:
            place_id (int): ID of the place to delete
            
        Returns:
            bool: True if successful
        """
        response = requests.delete(f"{self.base_url}/api/places/{place_id}")
        if response.status_code == 204:
            return True
        return self._handle_response(response)
    
    def get_place_observations(self, place_id):
        """
        Get all observations made at a specific place.
        
        Args:
            place_id (int): ID of the place
            
        Returns:
            list: List of observation objects
        """
        response = requests.get(f"{self.base_url}/api/places/{place_id}/observations")
        return self._handle_response(response)
    
    # =========================================================================
    # Instruments API
    # =========================================================================
    
    def get_instruments(self):
        """
        Get all instruments.
        
        Returns:
            list: List of instrument objects
        """
        response = requests.get(f"{self.base_url}/api/instruments")
        return self._handle_response(response)
    
    def get_instrument(self, instrument_id):
        """
        Get a specific instrument.
        
        Args:
            instrument_id (int): ID of the instrument
            
        Returns:
            dict: Instrument object
        """
        response = requests.get(f"{self.base_url}/api/instruments/{instrument_id}")
        return self._handle_response(response)
    
    def create_instrument(self, name, aperture=None, power=None, instrument_id=None):
        """
        Create a new instrument.
        
        Args:
            name (str): Name of the instrument
            aperture (str, optional): Aperture of the instrument
            power (str, optional): Power of the instrument
            instrument_id (int, optional): ID for the instrument
            
        Returns:
            dict: Created instrument object
        """
        data = {"name": name}
        
        if aperture is not None:
            data["aperture"] = aperture
            
        if power is not None:
            data["power"] = power
            
        if instrument_id is not None:
            data["id"] = instrument_id
            
        response = requests.post(
            f"{self.base_url}/api/instruments",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def update_instrument(self, instrument_id, name=None, aperture=None, power=None):
        """
        Update an instrument.
        
        Args:
            instrument_id (int): ID of the instrument
            name (str, optional): New name for the instrument
            aperture (str, optional): New aperture for the instrument
            power (str, optional): New power for the instrument
            
        Returns:
            dict: Updated instrument object
        """
        data = {}
        
        if name is not None:
            data["name"] = name
            
        if aperture is not None:
            data["aperture"] = aperture
            
        if power is not None:
            data["power"] = power
            
        response = requests.put(
            f"{self.base_url}/api/instruments/{instrument_id}",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def delete_instrument(self, instrument_id):
        """
        Delete an instrument.
        
        Args:
            instrument_id (int): ID of the instrument to delete
            
        Returns:
            bool: True if successful
        """
        response = requests.delete(f"{self.base_url}/api/instruments/{instrument_id}")
        if response.status_code == 204:
            return True
        return self._handle_response(response)
    
    def get_instrument_observations(self, instrument_id):
        """
        Get all observations made with a specific instrument.
        
        Args:
            instrument_id (int): ID of the instrument
            
        Returns:
            list: List of observation objects
        """
        response = requests.get(f"{self.base_url}/api/instruments/{instrument_id}/observations")
        return self._handle_response(response)
    
    # =========================================================================
    # Objects API
    # =========================================================================
    
    def get_objects(self):
        """
        Get all celestial objects.
        
        Returns:
            list: List of object objects
        """
        response = requests.get(f"{self.base_url}/api/objects")
        return self._handle_response(response)
    
    def get_object(self, object_id):
        """
        Get a specific celestial object.
        
        Args:
            object_id (int): ID of the object
            
        Returns:
            dict: Object object
        """
        response = requests.get(f"{self.base_url}/api/objects/{object_id}")
        return self._handle_response(response)
    
    def create_object(self, name, type_id, designation=None, props=None, object_id=None):
        """
        Create a new celestial object.
        
        Args:
            name (str): Name of the object
            type_id (int): ID of the object type
            designation (str, optional): Designation of the object
            props (str, optional): Properties of the object
            object_id (int, optional): ID for the object
            
        Returns:
            dict: Created object object
        """
        data = {
            "name": name,
            "type": type_id
        }
        
        if designation is not None:
            data["desination"] = designation  # Maintaining original spelling from SQL
            
        if props is not None:
            data["props"] = props
            
        if object_id is not None:
            data["id"] = object_id
            
        response = requests.post(
            f"{self.base_url}/api/objects",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def update_object(self, object_id, name=None, type_id=None, designation=None, props=None):
        """
        Update a celestial object.
        
        Args:
            object_id (int): ID of the object
            name (str, optional): New name for the object
            type_id (int, optional): New type ID for the object
            designation (str, optional): New designation for the object
            props (str, optional): New properties for the object
            
        Returns:
            dict: Updated object object
        """
        data = {}
        
        if name is not None:
            data["name"] = name
            
        if type_id is not None:
            data["type"] = type_id
            
        if designation is not None:
            data["desination"] = designation  # Maintaining original spelling from SQL
            
        if props is not None:
            data["props"] = props
            
        response = requests.put(
            f"{self.base_url}/api/objects/{object_id}",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def delete_object(self, object_id):
        """
        Delete a celestial object.
        
        Args:
            object_id (int): ID of the object to delete
            
        Returns:
            bool: True if successful
        """
        response = requests.delete(f"{self.base_url}/api/objects/{object_id}")
        if response.status_code == 204:
            return True
        return self._handle_response(response)
    
    def get_object_observations(self, object_id):
        """
        Get all observations of a specific object.
        
        Args:
            object_id (int): ID of the object
            
        Returns:
            list: List of observation objects
        """
        response = requests.get(f"{self.base_url}/api/objects/{object_id}/observations")
        return self._handle_response(response)
    
    # =========================================================================
    # Observations API
    # =========================================================================
    
    def get_observations(self):
        """
        Get all observations.
        
        Returns:
            list: List of observation objects
        """
        response = requests.get(f"{self.base_url}/api/observations")
        return self._handle_response(response)
    
    def get_observation(self, observation_id):
        """
        Get a specific observation.
        
        Args:
            observation_id (int): ID of the observation
            
        Returns:
            dict: Observation object
        """
        response = requests.get(f"{self.base_url}/api/observations/{observation_id}")
        return self._handle_response(response)
    
    def create_observation(self, object_id, place_id, instrument_id, observation_datetime, 
                           observation_text, property_id=None, property_value=None):
        """
        Create a new observation.
        
        Args:
            object_id (int): ID of the observed object
            place_id (int): ID of the observation place
            instrument_id (int): ID of the instrument used
            observation_datetime (datetime or str): Date and time of the observation
            observation_text (str): Description of the observation
            property_id (int, optional): ID of the property
            property_value (str, optional): Value of the property
            
        Returns:
            dict: Created observation object
        """
        # Convert datetime to ISO format if needed
        if isinstance(observation_datetime, datetime):
            observation_datetime = observation_datetime.isoformat()
            
        data = {
            "object": object_id,
            "place": place_id,
            "instrument": instrument_id,
            "datetime": observation_datetime,
            "observation": observation_text
        }
        
        if property_id is not None:
            data["prop1"] = property_id
            
        if property_value is not None:
            data["prop1value"] = property_value
            
        response = requests.post(
            f"{self.base_url}/api/observations",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def update_observation(self, observation_id, object_id=None, place_id=None, instrument_id=None,
                           observation_datetime=None, observation_text=None, property_id=None, 
                           property_value=None):
        """
        Update an observation.
        
        Args:
            observation_id (int): ID of the observation
            object_id (int, optional): New observed object ID
            place_id (int, optional): New observation place ID
            instrument_id (int, optional): New instrument ID
            observation_datetime (datetime or str, optional): New date and time
            observation_text (str, optional): New description
            property_id (int, optional): New property ID
            property_value (str, optional): New property value
            
        Returns:
            dict: Updated observation object
        """
        data = {}
        
        if object_id is not None:
            data["object"] = object_id
            
        if place_id is not None:
            data["place"] = place_id
            
        if instrument_id is not None:
            data["instrument"] = instrument_id
            
        if observation_datetime is not None:
            # Convert datetime to ISO format if needed
            if isinstance(observation_datetime, datetime):
                observation_datetime = observation_datetime.isoformat()
            data["datetime"] = observation_datetime
            
        if observation_text is not None:
            data["observation"] = observation_text
            
        if property_id is not None:
            data["prop1"] = property_id
            
        if property_value is not None:
            data["prop1value"] = property_value
            
        response = requests.put(
            f"{self.base_url}/api/observations/{observation_id}",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        return self._handle_response(response)
    
    def delete_observation(self, observation_id):
        """
        Delete an observation.
        
        Args:
            observation_id (int): ID of the observation to delete
            
        Returns:
            bool: True if successful
        """
        response = requests.delete(f"{self.base_url}/api/observations/{observation_id}")
        if response.status_code == 204:
            return True
        return self._handle_response(response)
    
    def search_observations(self, start_date=None, end_date=None, object_id=None, place_id=None, instrument_id=None):
        """
        Search observations with filters.
        
        Args:
            start_date (datetime or str, optional): Start date for filtering
            end_date (datetime or str, optional): End date for filtering
            object_id (int, optional): Object ID for filtering
            place_id (int, optional): Place ID for filtering
            instrument_id (int, optional): Instrument ID for filtering
            
        Returns:
            list: List of observation objects matching the filters
        """
        params = {}
        
        if start_date is not None:
            # Convert datetime to ISO format if needed
            if isinstance(start_date, datetime):
                start_date = start_date.isoformat()
            params["start_date"] = start_date
            
        if end_date is not None:
            # Convert datetime to ISO format if needed
            if isinstance(end_date, datetime):
                end_date = end_date.isoformat()
            params["end_date"] = end_date
            
        if object_id is not None:
            params["object_id"] = object_id
            
        if place_id is not None:
            params["place_id"] = place_id
            
        if instrument_id is not None:
            params["instrument_id"] = instrument_id
            
        response = requests.get(
            f"{self.base_url}/api/observations/search",
            params=params
        )
        return self._handle_response(response)
        
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def get_api_info(self):
        """
        Get information about the API endpoints.
        
        Returns:
            dict: API information
        """
        response = requests.get(self.base_url)
        return self._handle_response(response)
    
    def validate_connection(self):
        """
        Validate the connection to the API server.
        
        Returns:
            bool: True if connected
            
        Raises:
            Exception: If connection fails
        """
        try:
            self.get_api_info()
            return True
        except Exception as e:
            raise Exception(f"Failed to connect to API server at {self.base_url}: {str(e)}")

