# routes.py (move to root directory, rename from app/routes.py)
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import subprocess
from werkzeug.utils import secure_filename

# Create Flask app
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
app.secret_key = 'finance_dashboard_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls', 'csv'}

# Create a file to communicate with Streamlit
SHARED_FILE_PATH = 'current_file.txt'

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def set_current_file(filepath):
    """Store filepath in a shared file for Streamlit to read"""
    with open(SHARED_FILE_PATH, 'w') as f:
        f.write(filepath)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle file upload and redirect to dashboard"""
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # If user does not select file
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Store filepath for Streamlit
            set_current_file(filepath)

            # Start Streamlit in a separate process
            streamlit_cmd = ["streamlit", "run", "dashboard.py"]
            subprocess.Popen(streamlit_cmd)

            # Redirect to the Streamlit dashboard in a new window
            return redirect('http://localhost:8501')

    return render_template('index.html')

@app.route('/sample')
def use_sample_data():
    """Use sample data instead of uploading"""
    # Check if sample data exists
    sample_path = "sample_data.xlsx"
    if not os.path.exists(sample_path):
        from generate_sample_data import generate_sample_data
        sample_path = generate_sample_data()

    # Store filepath for Streamlit
    set_current_file(sample_path)

    # Start Streamlit in a separate process
    streamlit_cmd = ["streamlit", "run", "dashboard.py"]
    subprocess.Popen(streamlit_cmd)

    # Redirect to the Streamlit dashboard in a new window
    return redirect('http://localhost:8501')
