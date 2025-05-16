"""
Astronomy API Usage Examples
===========================
Examples demonstrating how to use the Astronomy API client library.

This script provides examples for:
- Database setup and initialization
- Working with astronomical objects, types, and properties
- Recording and querying observations
- Advanced searching and filtering
"""

import json
from datetime import datetime, timedelta
from astronomy_client import AstronomyClient

# Initialize the client
client = AstronomyClient('http://localhost:5000')  # Update with your server URL

# ===============================================================================
# Example 1: Setting up the database with initial data
# ===============================================================================

def setup_database():
    """Set up the database with initial astronomical data."""
    print("Setting up database with initial data...")
    
    # Create object types
    galaxy_type = client.create_type(name="Galaxy")
    star_type = client.create_type(name="Star")
    planet_type = client.create_type(name="Planet")
    nebula_type = client.create_type(name="Nebula")
    asteroid_type = client.create_type(name="Asteroid")
    
    print(f"Created object types: Galaxy (ID: {galaxy_type['id']}), Star (ID: {star_type['id']}), etc.")
    
    # Create properties
    magnitude_prop = client.create_property(name="Magnitude", value_type="float", property_id=1)
    distance_prop = client.create_property(name="Distance", value_type="float", property_id=2)
    
    print(f"Created properties: Magnitude (ID: {magnitude_prop['id']}), Distance (ID: {distance_prop['id']})")
    
    # Create observation places
    greenwich = client.create_place(
        name="Royal Observatory Greenwich", 
        latitude="51.4778", 
        longitude="0.0015",
        altitude="45m",
        timezone="Europe/London"
    )
    
    mauna_kea = client.create_place(
        name="Mauna Kea Observatory", 
        latitude="19.8208", 
        longitude="-155.4681",
        altitude="4205m",
        timezone="Pacific/Honolulu"
    )
    
    print(f"Created observation places: Greenwich (ID: {greenwich['id']}), Mauna Kea (ID: {mauna_kea['id']})")
    
    # Create instruments
    telescope1 = client.create_instrument(
        name="Celestron NexStar 8SE", 
        aperture="203.2mm", 
        power="2032mm",
        instrument_id=1
    )
    
    telescope2 = client.create_instrument(
        name="Subaru Telescope", 
        aperture="8.2m", 
        power="Primary f/1.83, Final f/12.2",
        instrument_id=2
    )
    
    print(f"Created instruments: NexStar (ID: {telescope1['id']}), Subaru (ID: {telescope2['id']})")
    
    # Create celestial objects
    andromeda = client.create_object(
        name="Andromeda Galaxy",
        type_id=galaxy_type['id'],
        designation="M31",
        props=json.dumps({
            "distance": "2.537 million light years",
            "diameter": "220,000 light years",
            "constellation": "Andromeda"
        }),
        object_id=1
    )
    
    mars = client.create_object(
        name="Mars",
        type_id=planet_type['id'],
        designation="Sol d",
        props=json.dumps({
            "distance": "227.9 million km from Sun",
            "diameter": "6,779 km",
            "moons": 2
        }),
        object_id=2
    )
    
    print(f"Created celestial objects: Andromeda (ID: {andromeda['id']}), Mars (ID: {mars['id']})")
    
    print("Database setup complete!")


# ===============================================================================
# Example 2: Recording observations
# ===============================================================================

def record_observations():
    """Record some astronomical observations."""
    print("Recording new observations...")
    
    # Record an observation of Andromeda Galaxy from Greenwich with Celestron telescope
    observation1 = client.create_observation(
        object_id=1,  # Andromeda
        place_id=1,   # Greenwich
        instrument_id=1,  # Celestron
        observation_datetime=datetime.now(),
        observation_text="Clear spiral structure visible. Excellent seeing conditions.",
        property_id=1,  # Magnitude property
        property_value="3.4"
    )
    
    print(f"Created observation of Andromeda (ID: {observation1['id']})")
    
    # Record an observation of Mars from Mauna Kea with Subaru telescope
    observation2 = client.create_observation(
        object_id=2,  # Mars
        place_id=2,   # Mauna Kea
        instrument_id=2,  # Subaru
        observation_datetime=datetime.now(),
        observation_text="Detailed surface features and polar ice caps visible.",
        property_id=2,  # Distance property
        property_value="78.34 million km"
    )
    
    print(f"Created observation of Mars (ID: {observation2['id']})")
    
    # Record an observation from a week ago
    past_date = datetime.now() - timedelta(days=7)
    observation3 = client.create_observation(
        object_id=1,  # Andromeda
        place_id=2,   # Mauna Kea
        instrument_id=2,  # Subaru
        observation_datetime=past_date,
        observation_text="High-resolution imaging of dust lanes and central core.",
        property_id=1,  # Magnitude property
        property_value="3.2"
    )
    
    print(f"Created past observation of Andromeda (ID: {observation3['id']})")
    
    print("Observations recorded successfully!")


# ===============================================================================
# Example 3: Querying observations
# ===============================================================================

def query_observations():
    """Query and display observations."""
    print("\nQuerying observations...")
    
    # Get all observations
    observations = client.get_observations()
    print(f"Total observations: {len(observations)}")
    
    # Get observations for a specific object (Andromeda)
    andromeda_observations = client.get_object_observations(1)
    print(f"Andromeda observations: {len(andromeda_observations)}")
    
    # Get observations from a specific place (Mauna Kea)
    mauna_kea_observations = client.get_place_observations(2)
    print(f"Mauna Kea observations: {len(mauna_kea_observations)}")
    
    # Get observations with a specific instrument (Subaru)
    subaru_observations = client.get_instrument_observations(2)
    print(f"Subaru Telescope observations: {len(subaru_observations)}")
    
    # Display details of Andromeda observations
    if andromeda_observations:
        print("\nDetails of Andromeda observations:")
        for obs in andromeda_observations:
            obj = client.get_object(obs['object'])
            place = client.get_place(obs['place'])
            instrument = client.get_instrument(obs['instrument'])
            
            print(f"Date: {obs['datetime']}")
            print(f"Object: {obj['name']} ({obj.get('desination', 'No designation')})")
            print(f"Location: {place['name']} ({place['lat']}, {place['lon']})")
            print(f"Instrument: {instrument['name']} (Aperture: {instrument.get('aperture', 'Unknown')})")
            print(f"Observation: {obs['observation']}")
            
            if obs.get('prop1') and obs.get('prop1value'):
                property_obj = client.get_property(obs['prop1'])
                print(f"{property_obj['name']}: {obs['prop1value']}")
            
            print("-" * 50)


# ===============================================================================
# Example 4: Advanced searching
# ===============================================================================

def advanced_search():
    """Demonstrate advanced search capabilities."""
    print("\nPerforming advanced searches...")
    
    # Search for observations within a date range
    start_date = datetime(2025, 1, 1)
    end_date = datetime.now()
    
    date_filtered = client.search_observations(
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"Observations between {start_date.isoformat()} and {end_date.isoformat()}: {len(date_filtered)}")
    
    # Search for observations of a specific object (Mars) using a specific instrument (Subaru)
    mars_subaru = client.search_observations(
        object_id=2,  # Mars
        instrument_id=2  # Subaru
    )
    
    print(f"Mars observations with Subaru telescope: {len(mars_subaru)}")
    
    # Search for all observations from a specific location (Greenwich)
    greenwich_obs = client.search_observations(place_id=1)
    print(f"Observations from Greenwich: {len(greenwich_obs)}")
    
    # Search for recent observations (last 3 days)
    three_days_ago = datetime.now() - timedelta(days=3)
    recent_obs = client.search_observations(start_date=three_days_ago)
    print(f"Observations in the last 3 days: {len(recent_obs)}")


# ===============================================================================
# Example 5: Working with types and properties
# ===============================================================================

def manage_types_and_properties():
    """Demonstrate management of types and properties."""
    print("\nManaging types and properties...")
    
    # List all object types
    types = client.get_types()
    print("Available object types:")
    for t in types:
        print(f"- {t['name']} (ID: {t['id']})")
    
    # Create a new type
    comet_type = client.create_type(name="Comet")
    print(f"Created new 'Comet' type with ID: {comet_type['id']}")
    
    # Update a type
    updated_type = client.update_type(comet_type['id'], "Comet/Asteroid")
    print(f"Updated type name to: {updated_type['name']}")
    
    # List all properties
    properties = client.get_properties()
    print("\nAvailable properties:")
    for p in properties:
        print(f"- {p['name']} (Type: {p['valueType']}, ID: {p['id']})")
    
    # Create a new property
    orbit_prop = client.create_property(
        name="Orbital Period", 
        value_type="string",
        property_id=3
    )
    print(f"Created new 'Orbital Period' property with ID: {orbit_prop['id']}")


# ===============================================================================
# Example 6: Working with objects
# ===============================================================================

def manage_celestial_objects():
    """Demonstrate management of celestial objects."""
    print("\nManaging celestial objects...")
    
    # Get all object types for reference
    types = client.get_types()
    type_map = {t['name']: t['id'] for t in types}
    
    # List all objects
    objects = client.get_objects()
    print("Available celestial objects:")
    for obj in objects:
        print(f"- {obj['name']} (ID: {obj['id']})")
    
    # Create a new object
    vega = client.create_object(
        name="Vega",
        type_id=type_map.get("Star"),
        designation="Alpha Lyrae",
        props=json.dumps({
            "distance": "25 light years",
            "constellation": "Lyra",
            "spectral_type": "A0V"
        }),
        object_id=3
    )
    print(f"Created new 'Vega' object with ID: {vega['id']}")
    
    # Get detailed information about an object
    obj_detail = client.get_object(vega['id'])
    print("\nVega details:")
    print(f"- Name: {obj_detail['name']}")
    print(f"- Designation: {obj_detail.get('desination', 'None')}")
    print(f"- Type ID: {obj_detail['type']}")
    if obj_detail.get('props'):
        props = json.loads(obj_detail['props'])
        for key, value in props.items():
            print(f"- {key.capitalize()}: {value}")


# ===============================================================================
# Example 7: Error handling
# ===============================================================================

def error_handling_example():
    """Demonstrate error handling."""
    print("\nError handling examples...")
    
    # Try to get a non-existent object
    try:
        non_existent = client.get_object(999)
        print("This should not execute!")
    except Exception as e:
        print(f"Handled error: {str(e)}")
    
    # Try to create an object with an invalid type
    try:
        invalid_obj = client.create_object(
            name="Invalid Object",
            type_id=999,  # Non-existent type ID
            designation="Invalid"
        )
        print("This should not execute!")
    except Exception as e:
        print(f"Handled error: {str(e)}")
    
    # Validate connection to API
    try:
        client.validate_connection()
        print("API connection validated successfully!")
    except Exception as e:
        print(f"Connection error: {str(e)}")


# ===============================================================================
# Example 8: Complete workflow
# ===============================================================================

def complete_workflow():
    """Run a complete workflow demonstration."""
    print("\nRunning complete workflow demonstration...")
    
    # 1. First, validate connection to API
    try:
        client.validate_connection()
        print("Connected to API server successfully.")
    except Exception as e:
        print(f"Failed to connect to API: {str(e)}")
        return
    
    # 2. Create a new object type for the demonstration
    pulsar_type = client.create_type(name="Pulsar")
    print(f"Created 'Pulsar' type with ID: {pulsar_type['id']}")
    
    # 3. Create a new property for the demonstration
    rotation_prop = client.create_property(
        name="Rotation Period", 
        value_type="string",
        property_id=4
    )
    print(f"Created 'Rotation Period' property with ID: {rotation_prop['id']}")
    
    # 4. Create a new observation place
    arecibo = client.create_place(
        name="Arecibo Observatory",
        latitude="18.3442",
        longitude="-66.7528",
        altitude="498m",
        timezone="America/Puerto_Rico"
    )
    print(f"Created 'Arecibo Observatory' place with ID: {arecibo['id']}")
    
    # 5. Create a new instrument
    radio_telescope = client.create_instrument(
        name="Arecibo Radio Telescope",
        aperture="305m",
        power="430MHz receiver",
        instrument_id=3
    )
    print(f"Created 'Arecibo Radio Telescope' instrument with ID: {radio_telescope['id']}")
    
    # 6. Create a new celestial object
    crab_pulsar = client.create_object(
        name="Crab Pulsar",
        type_id=pulsar_type['id'],
        designation="PSR B0531+21",
        props=json.dumps({
            "distance": "6,500 light years",
            "constellation": "Taurus",
            "age": "967 years"
        }),
        object_id=4
    )
    print(f"Created 'Crab Pulsar' object with ID: {crab_pulsar['id']}")
    
    # 7. Record an observation
    observation = client.create_observation(
        object_id=crab_pulsar['id'],
        place_id=arecibo['id'],
        instrument_id=radio_telescope['id'],
        observation_datetime=datetime.now(),
        observation_text="Strong periodic radio emissions detected. Clear spin-down rate observed.",
        property_id=rotation_prop['id'],
        property_value="33 milliseconds"
    )
    print(f"Created observation with ID: {observation['id']}")
    
    # 8. Retrieve the observation
    retrieved_obs = client.get_observation(observation['id'])
    
    # 9. Display full details of the observation
    print("\nObservation details:")
    obj = client.get_object(retrieved_obs['object'])
    place = client.get_place(retrieved_obs['place'])
    instrument = client.get_instrument(retrieved_obs['instrument'])
    property_obj = client.get_property(retrieved_obs['prop1'])
    
    print(f"Date: {retrieved_obs['datetime']}")
    print(f"Object: {obj['name']} ({obj.get('desination', 'No designation')})")
    print(f"Type: {client.get_type(obj['type'])['name']}")
    print(f"Location: {place['name']} ({place['lat']}, {place['lon']})")
    print(f"Instrument: {instrument['name']} (Aperture: {instrument.get('aperture', 'Unknown')})")
    print(f"Observation: {retrieved_obs['observation']}")
    print(f"{property_obj['name']}: {retrieved_obs['prop1value']}")
    
    print("\nComplete workflow demonstration finished successfully!")


# ===============================================================================
# Main function to run the examples
# ===============================================================================

def main():
    """Run all examples."""
    print("=" * 80)
    print("ASTRONOMY DATABASE API CLIENT EXAMPLES")
    print("=" * 80)
    
    # Uncomment the examples you want to run
    
    # Basic setup and data management
    setup_database()
    record_observations()
    query_observations()
    
    # Advanced functionality
    advanced_search()
    manage_types_and_properties()
    manage_celestial_objects()
    
    # Error handling and workflow
    error_handling_example()
    complete_workflow()
    
    print("\nAll examples completed.")


if __name__ == "__main__":
    main()
