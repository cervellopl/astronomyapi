# Web Interface for Astronomy Observations API

The Astronomy Observations API now includes a web interface for easier data management!

## Features

- Dashboard with summary statistics
- Forms for adding new data (objects, observations, places, etc.)
- Filterable listings of all data entities
- Advanced search functionality
- Clean, responsive Bootstrap-based interface

## How to Access

The web interface is available at the `/web` endpoint when the API is running. For example:

- API documentation: `http://localhost:5000/`
- Web interface: `http://localhost:5000/web`

## Web Interface Structure

The web interface follows a consistent pattern:
- **Dashboard**: Quick overview and direct access to all functions
- **List pages**: View all items of a particular type (e.g., objects, observations)
- **Add pages**: Forms for adding new items
- **Search page**: Advanced search functionality for observations

## Directory Structure

- `web_routes.py`: Contains all routes for the web interface
- `templates/`: Contains HTML templates for all web pages
  - `layout.html`: Base template with common structure
  - `dashboard.html`: Main dashboard template
  - Various subdirectories for entity-specific templates

## Technologies Used

- Flask for the backend
- Bootstrap 5 for the frontend styling
- Font Awesome icons
- Flatpickr for date pickers

## User Interface Overview

### Dashboard
The dashboard provides a quick overview of your astronomical data, including:
- Count cards for all entity types
- Recent observations list
- Quick access buttons to add new data

### Object Management
- View all celestial objects
- Add new objects with type, designation and JSON properties

### Observation Management
- Record new observations with datetime, object, place, and instrument
- View all observations in a sortable table

### Search
- Search observations by date range, object, place, and instrument
- Results displayed in a clean, tabular format

## Development

To modify the web interface:
1. Edit templates in the `templates/` directory
2. Edit route handlers in `web_routes.py`
3. Restart the application to see changes

## Dependencies

All necessary dependencies are included in `requirements.txt`.
