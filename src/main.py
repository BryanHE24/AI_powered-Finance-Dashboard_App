# main.py
import os
import sys
import webbrowser

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.generate_sample_data import generate_sample_data

def main():
    """
    Main function to set up directories, check for sample data, and run the Flask app.
    """
    # Setup directories
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("app/static/css", exist_ok=True)

    # Check if sample data exists, generate if not
    sample_data_path = "data/sample_data.xlsx"
    if not os.path.exists(sample_data_path):
        print("Generating sample financial data...")
        generate_sample_data()

    # Open the Flask app in the browser
    webbrowser.open("http://127.0.0.1:5000")

    # Run Flask app
    os.system("python app/routes.py")

if __name__ == "__main__":
    main()
