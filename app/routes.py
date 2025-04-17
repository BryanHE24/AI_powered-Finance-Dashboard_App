from flask import render_template, request, redirect, url_for, flash
import os
import subprocess
from werkzeug.utils import secure_filename
from create_app import create_app

app = create_app()

# Create a file to communicate with Streamlit
SHARED_FILE_PATH = 'data/current_file.txt'

def allowed_file(filename):
    """
    Check if file has allowed extension.

    Args:
        filename (str): The filename.

    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def set_current_file(filepath):
    """
    Store filepath in a shared file for Streamlit to read.

    Args:
        filepath (str): The filepath.
    """
    with open(SHARED_FILE_PATH, 'w') as f:
        f.write(filepath)

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handle file upload and redirect to dashboard.

    Returns:
        render_template: The rendered template.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            set_current_file(filepath)

            streamlit_cmd = ["streamlit", "run", "src/dashboard.py"]
            subprocess.Popen(streamlit_cmd)

            return redirect('http://localhost:8501')

    return render_template('index.html')

@app.route('/sample')
def use_sample_data():
    """
    Use sample data instead of uploading.

    Returns:
        redirect: Redirect to the Streamlit dashboard.
    """
    sample_path = "data/sample_data.xlsx"
    if not os.path.exists(sample_path):
        from src.generate_sample_data import generate_sample_data
        sample_path = generate_sample_data()

    set_current_file(sample_path)

    streamlit_cmd = ["streamlit", "run", "src/dashboard.py"]
    subprocess.Popen(streamlit_cmd)

    return redirect('http://localhost:8501')

if __name__ == "__main__":
    app.run(debug=True)
