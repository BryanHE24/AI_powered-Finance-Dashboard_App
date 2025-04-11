# routes.py
from flask import Flask, render_template, request, redirect, url_for, flash
import os
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

            # Redirect to the Streamlit dashboard with the file path as a query parameter
            return redirect(url_for('dashboard', filepath=filepath))

    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Redirect to Streamlit dashboard with file path as a query parameter"""
    filepath = request.args.get('filepath')
    if filepath:
        # Set the current file path for Streamlit
        set_current_file(filepath)
        # Redirect to the Streamlit dashboard
        return redirect('http://localhost:8501')
    else:
        flash('No file selected. Please upload a file.')
        return redirect(url_for('index'))

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

    # Redirect to the Streamlit dashboard with the file path as a query parameter
    return redirect(url_for('dashboard', filepath=sample_path))

if __name__ == "__main__":
    app.run(debug=True)
