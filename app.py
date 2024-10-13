# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import logging
import uuid
from io import BytesIO
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from werkzeug.utils import secure_filename
from agents import DataProcessingAgent, AnalysisAgent, VisualizationAgent

# Initialize Flask app
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

# Initialize agents
data_processing_agent = DataProcessingAgent()
analysis_agent = AnalysisAgent()
visualization_agent = VisualizationAgent()

# Initialize AWS S3 client
s3_bucket = os.environ.get('AWS_S3_BUCKET_NAME')
s3_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
s3_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

s3_client = boto3.client(
    's3',
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key
)

def upload_image_to_s3(image, filename):
    try:
        # Convert Plotly figure to image bytes
        img_byte_arr = BytesIO()
        image.write_image(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Upload to S3
        s3_client.upload_fileobj(
            img_byte_arr,
            s3_bucket,
            filename,
            ExtraArgs={'ContentType': 'image/png'}
        )

        # Generate the S3 URL
        s3_url = f"https://{s3_bucket}.s3.amazonaws.com/{filename}"
        return s3_url
    except NoCredentialsError:
        logger.error("AWS credentials not available.")
        return ""
    except ClientError as e:
        logger.error(f"Failed to upload image to S3: {e}")
        return ""

def perform_analysis(data):
    """
    Perform the entire analysis workflow:
    1. Data Processing
    2. Data Analysis
    3. Data Visualization
    4. Uploading the visualization to S3
    """
    dataset = data.get("dataset", "")
    analysis_params = data.get("analysis_params", {})
    styling_params = data.get("styling_params", "Default styling.")

    if not dataset:
        return {"error": "No dataset provided."}, 400

    # Step 1: Data Processing
    try:
        processed_data = data_processing_agent.process(dataset)
    except Exception as e:
        logger.error(f"DataProcessingAgent failed: {e}")
        return {"error": "Data processing failed."}, 500

    # Step 2: Data Analysis
    try:
        analysis_results = analysis_agent.analyze(processed_data, analysis_params)
    except Exception as e:
        logger.error(f"AnalysisAgent failed: {e}")
        return {"error": "Data analysis failed."}, 500

    # Step 3: Data Visualization
    try:
        visualization_code, commentary = visualization_agent.visualize(processed_data, analysis_results, styling_params)
    except Exception as e:
        logger.error(f"VisualizationAgent failed: {e}")
        return {"error": "Data visualization failed."}, 500

    # Step 4: Execute Visualization Code and Upload Image
    try:
        exec_globals = {}
        exec(visualization_code, exec_globals)
        plotly_fig = exec_globals.get("fig", None)
        if plotly_fig:
            unique_filename = f"{uuid.uuid4()}.png"
            image_url = upload_image_to_s3(plotly_fig, unique_filename)
        else:
            image_url = ""
    except Exception as e:
        logger.error(f"Failed to execute visualization code: {e}")
        image_url = ""

    # Prepare response
    response = {
        "analysis": analysis_results,
        "commentary": commentary,
        "image_url": image_url if image_url else f"https://{s3_bucket}.s3.amazonaws.com/placeholder.png"
    }

    return response, 200

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
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
            
            # Prepare data to send to analysis function
            data = {
                "dataset": dataset_path,
                "analysis_params": analysis_params,
                "styling_params": styling_params
            }
            
            # Call the analysis function directly
            result, status_code = perform_analysis(data)
            if status_code == 200:
                analysis = result.get("analysis", {})
                commentary = result.get("commentary", "")
                image_url = result.get("image_url", url_for('static', filename='images/placeholder.png'))
                return render_template('analysis.html', analysis=analysis, commentary=commentary, image_url=image_url)
            else:
                flash(result.get("error", "An error occurred while processing your request."), 'danger')
                logger.error(f"Analysis Error: {result.get('error')}")
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
