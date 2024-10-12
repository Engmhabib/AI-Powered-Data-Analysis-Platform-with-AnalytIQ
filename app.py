# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import logging
from rq import Queue
from redis import Redis
from tasks import generate_story_and_image

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management and flash messages

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis connection
redis_url = os.environ.get('REDIS_URL')
if not redis_url:
    logger.error("REDIS_URL is not set. Please check your environment variables.")
    exit(1)

try:
    redis_conn = Redis.from_url(redis_url)
    q = Queue(connection=redis_conn)  # Default queue
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    exit(1)

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
        
        try:
            # Enqueue the background job
            job = q.enqueue(generate_story_and_image, child_name, age, themes, additional_details)
            logger.info(f"Enqueued job {job.id}")
        except Exception as e:
            logger.error(f"Error enqueuing job: {e}")
            flash('An error occurred while processing your request.', 'danger')
            return render_template('index.html')
        
        # Redirect to the status page with 'job_id'
        return redirect(url_for('task_status', job_id=job.id))
    
    return render_template('index.html')

@app.route('/status/<job_id>')
def task_status(job_id):
    try:
        job = q.fetch_job(job_id)
        if job is None:
            flash('Job not found.', 'warning')
            return redirect(url_for('index'))
        
        if job.is_finished:
            result = job.result
            story = result.get('story', 'No story generated.')
            image_filename = result.get('image_filename', 'placeholder.png')
            image_url = url_for('static', filename=f'images/{image_filename}')
            return render_template('story.html', story=story, image_url=image_url)
        elif job.is_failed:
            flash('An error occurred while processing your request.', 'danger')
            return redirect(url_for('index'))
        else:
            flash('Your story is being generated. Please wait...', 'info')
            return render_template('status.html', job_id=job_id)
    except Exception as e:
        logger.error(f"Error fetching job status: {e}")
        flash('An error occurred while fetching job status.', 'danger')
        return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Server Error: {error}")
    flash('An internal error occurred. Please try again later.', 'danger')
    return render_template('index.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"Page Not Found: {error}")
    flash('Page not found.', 'warning')
    return render_template('index.html'), 404

if __name__ == '__main__':
    app.run(debug=False)
