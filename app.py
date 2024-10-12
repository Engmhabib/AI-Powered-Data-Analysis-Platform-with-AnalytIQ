# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
import os
import logging
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management and flash messages

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home Route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'dataset' not in request.files:
            flash('No file part in the form.', 'danger')
            return redirect(request.url)
        
        file = request.files['dataset']
        
        # If user does not select file, browser may submit an empty part
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            dataset_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(dataset_path)
            logger.info(f"Dataset uploaded: {dataset_path}")
            
            # Get analysis parameters from the form
            analysis_params = {
                "descriptive_statistics": 'descriptive_statistics' in request.form,
                "correlation_matrix": 'correlation_matrix' in request.form
                # Add more parameters as needed
            }
            
            # Get styling parameters
            styling_params = request.form.get('styling_params', 'Default styling.')
            
            # Prepare data to send to backend
            data = {
                "dataset": dataset_path,
                "analysis_params": analysis_params,
                "styling_params": styling_params
            }
            
            try:
                # Send request to backend server
                backend_url = os.environ.get('BACKEND_URL', 'http://localhost:5001/api/analyze')
                response = requests.post(backend_url, json=data)
                if response.status_code == 200:
                    result = response.json()
                    analysis = result.get("analysis", {})
                    commentary = result.get("commentary", "")
                    image_url = result.get("image_url", url_for('static', filename='images/placeholder.png'))
                    return render_template('analysis.html', analysis=analysis, commentary=commentary, image_url=image_url)
                else:
                    flash('An error occurred while processing your request.', 'danger')
                    logger.error(f"Backend Error: {response.text}")
                    return redirect(request.url)
            except Exception as e:
                flash('Failed to connect to the backend server.', 'danger')
                logger.error(f"Connection Error: {e}")
                return redirect(request.url)
        
        else:
            flash('Allowed file types are CSV.', 'warning')
            return redirect(request.url)
    
    return render_template('index.html')

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"Page not found: {e}")
    flash('Page not found.', 'warning')
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    flash('An internal error occurred. Please try again later.', 'danger')
    return render_template('index.html'), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
