## Web Interface Directory Structure

```
astronomy-api/
│
├── server.py                # Main entry point
├── models.py                # Database models
├── resources.py             # API resources
├── config.py                # Configuration
├── database.py              # Database connection
├── web_routes.py            # Web interface routes
│
├── templates/               # HTML templates for web interface
│   ├── layout.html          # Base template (shared layout)
│   ├── dashboard.html       # Dashboard template
│   │
│   ├── objects/             # Templates for objects
│   │   ├── list.html        # List all objects
│   │   └── add.html         # Add new object form
│   │
│   ├── observations/        # Templates for observations
│   │   ├── list.html        # List all observations
│   │   └── add.html         # Add new observation form
│   │
│   ├── instruments/         # Templates for instruments
│   │   ├── list.html        # List all instruments
│   │   └── add.html         # Add new instrument form
│   │
│   ├── places/              # Templates for places
│   │   ├── list.html        # List all places
│   │   └── add.html         # Add new place form
│   │
│   ├── types/               # Templates for types
│   │   ├── list.html        # List all types
│   │   └── add.html         # Add new type form
│   │
│   ├── properties/          # Templates for properties
│   │   ├── list.html        # List all properties
│   │   └── add.html         # Add new property form
│   │
│   └── search.html          # Search observations template
│
├── static/                  # Static files (CSS, JS, etc.)
│   └── styles.css           # Custom styles (if needed)
│
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── README.md                # Main documentation
└── WEB_INTERFACE.md         # Web interface documentation
```

### Template Structure

Each template extends the base `layout.html` template, which provides:
- Common styling and structure
- Navigation sidebar
- Header
- Flash message display

Template directories are organized by entity type, with each directory containing:
- `list.html`: Table view of all entities
- `add.html`: Form for adding new entities

The `dashboard.html` template serves as the main entry point, with:
- Statistics cards
- Recent observations
- Quick action buttons
