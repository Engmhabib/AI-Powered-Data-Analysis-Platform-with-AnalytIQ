# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import logging
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management and flash messages

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Home Route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        child_name = request.form.get('child_name')
        age = request.form.get('age')
        themes = request.form.get('themes')
        additional_details = request.form.get('additional_details')

        # Input validation
        if not child_name or not age or not themes:
            flash('Please fill out all required fields.', 'warning')
            return render_template('index.html')

        # Prepare data to send to backend
        data = {
            "query": f"Generate a story for {child_name}, age {age}, themes: {themes}. {additional_details}",
            "data": {},  # Add dataset info if necessary
            "styling_index": "Default styling."  # Add styling instructions if necessary
        }

        try:
            # Send request to backend server
            backend_url = os.environ.get('BACKEND_URL', 'http://localhost:5001/api/analyze')
            response = requests.post(backend_url, json=data)
            if response.status_code == 200:
                result = response.json()
                story = result.get("story", "No story generated.")
                image_url = result.get("image_url", url_for('static', filename='images/placeholder.png'))
                return render_template('story.html', story=story, image_url=image_url)
            else:
                flash('An error occurred while processing your request.', 'danger')
                logger.error(f"Backend Error: {response.text}")
                return render_template('index.html')
        except Exception as e:
            flash('Failed to connect to the backend server.', 'danger')
            logger.error(f"Connection Error: {e}")
            return render_template('index.html')

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
