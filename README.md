# Invoice Processing System

An intelligent invoice processing system using Google's ADK and Generative AI for automated invoice data extraction and validation.

## Project Structure
```
📦 Root
 ┣ 📂 Agents
 ┃ ┗ 📂 invoices
 ┃   ┣ 📜 __init__.py
 ┃   ┣ 📜 agent.py
 ┃   ┣ 📜 prompt.py
 ┃   ┗ 📜 .env
 ┣ 📂 Latest
 ┃ ┣ 📜 invoice_validator.py
 ┃ ┣ 📜 styles.py
 ┃ ┗ 📜 Ui.py
 ┣ 📂 Older versions
 ┃ ┣ 📜 Early_ui.py
 ┃ ┣ 📜 first_validator.py
 ┃ ┗ 📜 Semi-validated_Ui.py
 ┣ 📂 Sample invoices
 ┃ ┣ 📜 invoice1.pdf
 ┃ ┗ 📜 wordpress-pdf-invoice-plugin-sample.pdf
 ┣ 📜 .gitignore
 ┗ 📜 Google-ADK.postman_collection.json
```

## Components

### Agent Module (`/Agents/invoices/`)
- `agent.py` - Configures the Google ADK agent using Gemini 1.5 Flash model
- `prompt.py` - Contains extraction prompts and instructions
- `.env` - Environment configuration for Google API
- `__init__.py` - Package initialization

### Latest Version (`/Latest/`)
- `invoice_validator.py` - Current invoice validation logic
- `styles.py` - UI styling components
- `Ui.py` - Current user interface implementation

### Legacy Code (`/Older versions/`)
- `Early_ui.py` - Initial UI implementation
- `first_validator.py` - Original validation logic
- `Semi-validated_Ui.py` - Intermediate UI version

### Sample Data (`/Sample invoices/`)
- Sample PDF invoices for testing
- Includes WordPress plugin sample invoice

### Development Tools
- `Google-ADK.postman_collection.json` - API testing collection
- `.gitignore` - Git ignore configurations

## Setup

1. Clone the repository
```bash
git clone <repository-url>
```

2. Configure environment variables
```bash
# In Agents/invoices/.env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY="YOUR_API_KEY"
```

3. Install dependencies
```bash
pip install

# Core Dependencies
google-adk
streamlit
python-dotenv
PyPDF2
pillow

# Data Processing
pandas
numpy

# API & Networking
requests
aiohttp

# Validation & Type Checking
pydantic

```

## Usage

### 1. Start the ADK API Server
```bash
# Navigate to Agents folder
cd Agents

# Start the API server
adk api_server
```

### 2. Launch the UI
```bash
# Open a new terminal
# Navigate to Latest folder
cd Latest

# Start the Streamlit app
streamlit run Ui.py
```

> **Important**: Both servers (ADK API Server and Streamlit) must be running simultaneously for the application to work properly.

### Troubleshooting
- Make sure your `.env` file in the Agents/invoices folder contains valid API keys
- Verify both terminals show successful startup messages
- Check ports 8000 (ADK) and 8501 (Streamlit) are available

### Testing
Use the sample invoices in `/Sample invoices/` for testing the extraction and validation features.

