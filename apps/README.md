# MediAI Streamlit Application

This is the web-based user interface for the MediAI Healthcare ML Platform.

## Features

- **🏠 Dashboard** - Overview of predictions and system status
- **🔬 Predict Sepsis** - Sepsis risk prediction (6-hour early warning)
- **💔 Predict Mortality** - Hospital mortality risk prediction
- **📊 Model Performance** - Model metrics and performance analytics
- **⚙️ Settings** - Application configuration and preferences

## Navigation

The application uses a **custom navigation menu** with icons in the sidebar. This replaces the default Streamlit page navigation for a cleaner, more intuitive user experience.

### Why Custom Navigation?

- ✅ Clean, icon-based menu
- ✅ No confusing default page names
- ✅ Better user experience
- ✅ Professional appearance
- ✅ Easy to understand at a glance

## Running the Application

### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Start the Application

```bash
# From the apps directory
cd /home/user/MediAI/apps
streamlit run streamlit_app.py --server.port 8501
```

Or use the Docker Compose setup (recommended):

```bash
# From the project root
docker-compose up streamlit
```

### Access the Application

Open your web browser and navigate to:
```
http://localhost:8501
```

## Configuration

The application configuration is stored in `.streamlit/config.toml`. You can customize:

- Theme colors
- Server settings
- Browser behavior
- Client options

## Project Structure

```
apps/
├── streamlit_app.py          # Main application entry point
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── pages/                     # Page modules
│   ├── __init__.py
│   ├── dashboard.py           # Dashboard page
│   ├── predict_sepsis.py      # Sepsis prediction page
│   ├── predict_mortality.py   # Mortality prediction page
│   ├── model_performance.py   # Model performance page
│   └── settings.py            # Settings page
├── components/                # Reusable UI components (future)
├── services/                  # API client services (future)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Important Notes

### Custom Navigation Implementation

The application hides Streamlit's default sidebar navigation using custom CSS:

```python
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)
```

This ensures users only see the clean, icon-based navigation menu.

### Session State Management

The application uses Streamlit's session state to track the current page:

```python
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"
```

When a user selects a different page from the navigation menu, the app uses `st.rerun()` to reload with the new page content.

## Development

### Adding a New Page

1. Create a new file in `pages/` (e.g., `new_page.py`)
2. Implement a `show()` function
3. Add the page to the navigation menu in `streamlit_app.py`
4. Import and call the page's `show()` function in the main app

Example:

```python
# pages/new_page.py
import streamlit as st

def show():
    st.title("🆕 New Page")
    st.write("Content goes here...")
```

```python
# streamlit_app.py
nav_options = [
    "🏠 Dashboard",
    "🔬 Predict Sepsis",
    "💔 Predict Mortality",
    "📊 Model Performance",
    "🆕 New Page",  # Add here
    "⚙️ Settings"
]

# ...

elif st.session_state.current_page == "🆕 New Page":
    from pages import new_page
    new_page.show()
```

## Troubleshooting

### Sidebar Navigation Still Showing

If you still see the default Streamlit navigation:

1. Clear your browser cache
2. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. Restart the Streamlit application
4. Check that custom CSS is properly loaded

### Pages Not Loading

If pages aren't loading correctly:

1. Check the console for import errors
2. Ensure all page modules have a `show()` function
3. Verify the session state is properly initialized
4. Check for Python syntax errors in page files

## API Integration

Currently, the application displays mock data. To connect to the actual backend API:

1. Update the API client configuration in settings
2. Implement API service calls in `services/`
3. Replace mock data with real API calls
4. Add error handling for API failures

## License

See the main project LICENSE file.
