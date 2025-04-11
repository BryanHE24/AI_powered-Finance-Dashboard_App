# AI-Powered Finance Dashboard

This project is an AI-powered finance dashboard that allows users to upload an Excel file, visualize financial data, and get insights through an AI assistant. The dashboard provides a dynamic and interactive interface to analyze financial performance, track expenses, and generate reports.

## Features

* **File Upload:** Upload an Excel file to visualize financial data.
* **AI-Powered Insights:** Get insights and answers about your financial data using an AI assistant.
* **Dynamic Visualization:** Automatically generate interactive charts from your Excel data.
* **Responsive Design:** Access your dashboard from any device.
* **Downloadable Reports:** Generate and download PDF reports of your financial insights.
* **Seasonal Analysis:** Identify and visualize seasonal trends in your financial data.
* **Expense Breakdown:** Analyze expenses by category to identify areas for cost reduction.

## How to Use

1.  **Upload a File:** Upload an Excel file containing your financial data to generate visualizations and insights.
2.  **AI Assistant:** Ask questions about your financial data and get AI-powered insights and answers.
3.  **Interactive Dashboard:** Explore dynamic charts and visualizations to understand your financial performance.
4.  **Download Reports:** Generate and download PDF reports of your financial insights for further analysis.

## How to Set Up

### Prerequisites

* Python 3.x
* pip (Python package installer)

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/BryanHE24/AI_PoweredFinanceDashboardApp.git](https://github.com/BryanHE24/AI_PoweredFinanceDashboardApp.git)
    cd AI_PoweredFinanceDashboardApp
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    Create a `.env` file in the root directory with your OpenAI API key:
    ```
    OPENAI_API_KEY=your_openai_api_key
    ```

5.  **Run the Application:**
    ```bash
    python3 main.py
    ```

6.  **Access the Dashboard:**
    Open your browser and navigate to `http://127.0.0.1:5001` to access the file upload page. Upload a file or use sample data to generate the dashboard.

## Project Structure
AI_PoweredFinanceDashboardApp/
├── main.py                     # The main entry point of the application.
├── routes.py                   # Flask routes for handling file uploads and redirection.
├── generate_sample_data.py     # Script to generate sample financial data.
├── processor.py                # Data processing functions.
├── assistant.py                # AI assistant functions.
├── dashboard.py                # Streamlit dashboard for visualizing financial data.
├── templates/                  # HTML templates for the Flask app.
│   └── ...
├── static/                     # CSS styles for the app.
│   └── css/
│       └── ...
├── requirements.txt            # List of project dependencies.
├── .env                        # Environment variables for configuration.
└── README.md                   # Project overview and setup instructions (this file).

