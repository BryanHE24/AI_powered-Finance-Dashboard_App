# main.py
import os
import webbrowser
from generate_sample_data import generate_sample_data

if __name__ == "__main__":
    # Setup directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)

    # Check if sample data exists, generate if not
    sample_data_path = "sample_data.xlsx"
    if not os.path.exists(sample_data_path):
        print("Generating sample financial data...")
        generate_sample_data()

    # Open the Flask app in the browser
    webbrowser.open("http://127.0.0.1:5000")

    # Run Flask app
    os.system("flask --app routes run --debug")
