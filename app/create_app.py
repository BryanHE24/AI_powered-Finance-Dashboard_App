# app/create_app
from flask import Flask

def create_app():
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')
    app.secret_key = 'finance_dashboard_secret_key'
    app.config['UPLOAD_FOLDER'] = 'data/uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls', 'csv'}
    return app
