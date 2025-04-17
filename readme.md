# AI-Powered Finance Dashboard

This project is an AI-powered finance dashboard that allows users to upload an Excel file, visualize financial data, and get insights through an AI assistant. The dashboard provides a dynamic and interactive interface to analyze financial performance, track expenses, and generate reports.

The AI-Powered Finance Dashboard is a comprehensive tool designed to help users visualize and analyze their financial data with ease. This project leverages AI to provide insights, generate reports, and offer a dynamic and interactive interface for financial management.

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
    python3 src/main.py
    ```

6.  **Access the Dashboard:**
    Open your browser and navigate to `http://127.0.0.1:5000` to access the file upload page. Upload a file or use sample data to generate the dashboard.

## Required Excel Format
**To ensure proper processing and visualization, the application requires your financial data to follow this strict format**

| Column Name | Description                                                                 |
| ----------- | --------------------------------------------------------------------------- |
| Date        | Transaction date and time in format YYYY-MM-DD HH:MM:SS                     |
| Category    | Category of the transaction (e.g., Marketing, Salaries)                     |
| Description | Brief description of the transaction                                        |
| Amount      | Numeric value of the transaction (use . as decimal separator)               |
| Type        | Either Income or Expense                                                    |

### **Required excel format sample**

| Date             | Category          | Description                     | Amount    | Type    |
| ---------------- | ----------------- | ------------------------------- | --------- | ------- |
| 2024-04-10 17:53:49 | Investment Returns | Investment Returns - Transaction 1 | 15374.36  | Income  |
| 2024-04-10 17:53:49 | Marketing         | Marketing - Transaction 2       | 1315.32   | Expense |

📌 Important: Even though this can be adapted to any excel just by modifying the code, uploading a file with incorrect column names or formats will result in a validation error.


## Project Structure
![image](https://github.com/user-attachments/assets/5204d93d-66ac-40c7-ab8a-6c098706544f)


## Demo
![Screenshot from 2025-04-11 15-59-17](https://github.com/user-attachments/assets/c74c21eb-05a8-43e1-9d22-8c54142a2df2)


https://github.com/user-attachments/assets/6b901807-eb36-453c-a8ad-cfbe7d54a197





