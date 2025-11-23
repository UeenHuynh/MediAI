# MediAI Streamlit Application

This is the web-based user interface for the MediAI Healthcare ML Platform.

## Features

- **🏠 Dashboard** - Overview of predictions and system status
- **🔬 Predict Sepsis** - Sepsis risk prediction (6-hour early warning)
- **💔 Predict Mortality** - Hospital mortality risk prediction
- **📊 Model Performance** - Model metrics and performance analytics
- **⚙️ Settings** - Application configuration and preferences

## Architecture

The application uses **Streamlit's native multi-page app** feature for navigation.

### Why Streamlit Multi-Page?

- ✅ Built-in navigation with icons and proper routing
- ✅ Clean, professional appearance
- ✅ No custom CSS/JavaScript hacks needed
- ✅ Automatic page detection and routing
- ✅ Active page highlighting
- ✅ Better maintainability

## Project Structure

```
apps/
├── streamlit_app.py          # Main home/welcome page
├── pages/                     # Auto-detected by Streamlit
│   ├── 1_🏠_Dashboard.py     # Dashboard page
│   ├── 2_🔬_Predict_Sepsis.py        # Sepsis prediction page
│   ├── 3_💔_Predict_Mortality.py     # Mortality prediction page
│   ├── 4_📊_Model_Performance.py    # Model performance page
│   └── 5_⚙️_Settings.py              # Settings page
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── components/                # Reusable UI components
├── services/                  # API client services
├── requirements.txt           # Python dependencies
├── NAVIGATION_SOLUTION.md     # Technical documentation
└── README.md                  # This file
```

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

### Access the Application

Open your web browser and navigate to:
```
http://localhost:8501
```

## Navigation

Streamlit automatically generates sidebar navigation from files in the `pages/` directory:

- 🏥 **MediAI Healthcare ML Platform** (home page)
- 🏠 **Dashboard**
- 🔬 **Predict Sepsis**
- 💔 **Predict Mortality**
- 📊 **Model Performance**
- ⚙️ **Settings**

### Page Naming Convention

Pages follow the pattern: `{number}_{emoji}_{Name}.py`

- **Number**: Determines order in sidebar (1, 2, 3, etc.)
- **Emoji**: Icon shown in navigation
- **Name**: Page title (e.g., "Dashboard", "Predict_Sepsis")

## Configuration

The application configuration is in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[client]
showErrorDetails = true
toolbarMode = "minimal"
```

## Development

### Adding a New Page

1. Create a new file in `pages/` with proper naming: `{number}_{emoji}_{Name}.py`
2. Add `st.set_page_config()` at the top
3. Add page content directly (no wrapper function needed)

Example:

```python
# pages/6_📈_Analytics.py
import streamlit as st

st.set_page_config(page_title="Analytics", page_icon="📈")

st.title("📈 Analytics")
st.write("Content goes here...")
```

Streamlit will automatically detect the new page and add it to navigation!

### Page Structure

Each page file should follow this structure:

```python
import streamlit as st

# Page configuration (MUST be first)
st.set_page_config(
    page_title="Page Title",
    page_icon="🔬"
)

# Page content
st.title("🔬 Page Title")
# ... rest of content
```

## Troubleshooting

### Clear Streamlit Cache

If you see outdated navigation or pages:

```bash
# Option 1: Clear cache directory
rm -rf ~/.streamlit/cache

# Option 2: Clear cache via UI
# Click the hamburger menu (☰) → Clear cache
```

### Stop Running Streamlit Processes

```bash
# Find and kill Streamlit processes
ps aux | grep streamlit
kill <PID>

# Or use pkill
pkill -f streamlit
```

### Hard Refresh Browser

Press `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac) to clear browser cache

### Verify File Structure

```bash
cd /home/user/MediAI/apps
ls -la pages/
# Should show: 1_🏠_Dashboard.py, 2_🔬_Predict_Sepsis.py, etc.
```

## Technical Documentation

See [NAVIGATION_SOLUTION.md](NAVIGATION_SOLUTION.md) for detailed technical documentation on:
- Architecture and file structure
- How Streamlit's auto-detection works
- Benefits over custom navigation approach
- Migration from previous version

## API Integration

Currently, the application displays mock data. To connect to the actual backend API:

1. Configure API endpoint in settings
2. Implement API service calls in `services/`
3. Replace mock data with real API calls
4. Add error handling for API failures

## License

See the main project LICENSE file.
