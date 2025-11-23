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
├── views/                     # View modules (NOT pages/ to avoid Streamlit auto-detection)
│   ├── __init__.py
│   ├── dashboard.py           # Dashboard view
│   ├── predict_sepsis.py      # Sepsis prediction view
│   ├── predict_mortality.py   # Mortality prediction view
│   ├── model_performance.py   # Model performance view
│   └── settings.py            # Settings view
├── components/                # Reusable UI components (future)
├── services/                  # API client services (future)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

**Important:** The directory is named `views/` instead of `pages/` to prevent Streamlit from automatically creating default sidebar navigation. This ensures only our custom navigation menu is shown.

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

### Adding a New View/Page

1. Create a new file in `views/` (e.g., `new_view.py`)
2. Implement a `show()` function
3. Add the view to the navigation menu in `streamlit_app.py`
4. Import and call the view's `show()` function in the main app

Example:

```python
# views/new_view.py
import streamlit as st

def show():
    st.title("🆕 New View")
    st.write("Content goes here...")
```

```python
# streamlit_app.py
nav_options = [
    "🏠 Dashboard",
    "🔬 Predict Sepsis",
    "💔 Predict Mortality",
    "📊 Model Performance",
    "🆕 New View",  # Add here
    "⚙️ Settings"
]

# ...

elif st.session_state.current_page == "🆕 New View":
    from views import new_view
    new_view.show()
```

## Troubleshooting

### Sidebar Navigation Still Showing

If you still see the default Streamlit navigation:

1. **Verify directory structure:** Ensure views are in `views/` NOT `pages/`
   - Streamlit auto-detects `pages/` directory and creates navigation
   - Using `views/` prevents auto-detection
2. **Clear browser cache:** Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. **Restart Streamlit:** Stop and restart the application completely
4. **Check CSS:** Verify the custom CSS in `streamlit_app.py` is loaded
5. **Inspect browser:** Use browser DevTools to check if `[data-testid="stSidebarNav"]` exists

**IMPORTANT:** Never create a `pages/` directory with Python files, as Streamlit will automatically create sidebar navigation from it!

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
