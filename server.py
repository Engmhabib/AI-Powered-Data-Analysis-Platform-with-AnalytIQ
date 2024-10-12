# server.py

from flask import Flask, request, jsonify
from agents import DataProcessingAgent, AnalysisAgent, VisualizationAgent
import logging
import os
import uuid
from io import BytesIO
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    dataset = data.get("dataset", "")
    analysis_params = data.get("analysis_params", {})
    styling_params = data.get("styling_params", "Default styling.")

    if not dataset:
        return jsonify({"error": "No dataset provided."}), 400

    # Step 1: Data Processing
    try:
        processed_data = data_processing_agent.process(dataset)
    except Exception as e:
        logger.error(f"DataProcessingAgent failed: {e}")
        return jsonify({"error": "Data processing failed."}), 500

    # Step 2: Data Analysis
    try:
        analysis_results = analysis_agent.analyze(processed_data, analysis_params)
    except Exception as e:
        logger.error(f"AnalysisAgent failed: {e}")
        return jsonify({"error": "Data analysis failed."}), 500

    # Step 3: Data Visualization
    try:
        visualization_code, commentary = visualization_agent.visualize(processed_data, analysis_results, styling_params)
    except Exception as e:
        logger.error(f"VisualizationAgent failed: {e}")
        return jsonify({"error": "Data visualization failed."}), 500

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

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)
