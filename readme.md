# 📄 Invoice Processing and Validation System

This project presents an automated system for extracting, editing, and validating data from PDF invoices. It leverages Artificial Intelligence (LLMs) for data extraction and Pydantic for robust field validation. The user interface is developed with Streamlit, providing an interactive experience for reviewing and correcting the extracted data.

## ✨ Key Features

* **LLM-powered Data Extraction:** Utilizes a Large Language Model (LLM) (presumably `gemini-1.5-flash` via `google-adk`) to extract key information from PDF invoice documents (document type, ID, date, financial values, vendor, and customer details).
* **Interactive Interface (Streamlit):** A user-friendly web application allows for PDF uploads, visualization of extracted data, and manual editing.
* **Robust Data Validation:** Implements strict validations (based on `invoice_validator.py` and Pydantic) to ensure the integrity and correct format of extracted data (dates, currencies, tax IDs, financial values, etc.).
* **Clear Visual Feedback:** Provides visual indicators (green, yellow, red) for the validation status of each field, along with detailed messages about errors or warnings.
* **Validation Summary:** Presents a summary panel with the overall validation status of the invoice.
* **Dynamic Form Configuration:** Allows selecting which fields should be displayed and editable in the interface, via presets or custom selection.
* **Data Export:** Enables exporting the (edited and validated) invoice data to JSON format.

## 🚀 How to Run the Project

### Prerequisites

* Python 3.8+
* `pip` (Python package manager)
* **LLM Server:** This project interacts with an LLM server for data extraction. `agent.py` demonstrates the configuration of a Google ADK `Agent`. For the UI to function, an accessible endpoint (e.g., `http://localhost:8000/run`) that processes PDFs and returns invoice data is required.

### Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/invoice-processor-project.git](https://github.com/YOUR_USERNAME/invoice-processor-project.git)
    cd invoice-processor-project
    ```
    *(Replace `YOUR_USERNAME` with your GitHub username)*

2.  **Create a Virtual Environment (Highly Recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables Configuration (Optional, but Recommended):**
    If your agent or API requires keys, create a `.env` file at the root of the project:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    # Other variables, if necessary
    ```
    Remember that the `.env` file is configured to be ignored by Git (`.gitignore`).

### Running the Application

1.  **Ensure Your LLM Server is Active:**
    Before starting the UI, the endpoint for data extraction (as configured in `ui5.py`, e.g., `http://localhost:8000/run`) must be accessible and functional. The implementation in `agent.py` demonstrates the use of Google ADK, but how to expose this agent as an HTTP service must be done separately.

2.  **Start the LLM Agent Server (if using `adk api_server`):**
    Open your terminal and navigate to the `src/Agents` directory:
    ```bash
    cd src/Agents
    adk api_server
    ```
    Keep this terminal window open as it runs the server.

3.  **Execute the Streamlit Interface:**
    Open a **new terminal window** and navigate back to the `src` folder:
    ```bash
    cd src
    streamlit run ui5.py
    ```
    This will open the application in your default web browser (usually `http://localhost:8501`).

## 🛠️ Technologies Used

* **Python 3.8+**
* **Streamlit:** For creating the interactive user interface.
* **Pydantic:** For declarative data modeling and validation.
* **Requests:** For HTTP communication with external services (like the LLM server).
* **Google ADK (Agent Development Kit):** For building AI agents for document processing.

