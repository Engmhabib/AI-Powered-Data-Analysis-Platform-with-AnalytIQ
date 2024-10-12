# server.py
from flask import Flask, request, jsonify
from agents import DataVizAgent, CodeFixAgent, PlannerAgent
import dspy
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
data_viz_agent = dspy.ChainOfThought(DataVizAgent)
code_fix_agent = dspy.ChainOfThought(CodeFixAgent)
planner_agent = dspy.ChainOfThought(PlannerAgent)

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
    query = data.get("query", "")
    dataset = data.get("data", {})
    styling_index = data.get("styling_index", "Default styling.")

    if not query:
        return jsonify({"error": "No query provided."}), 400

    # Step 1: Planner Agent routes the query
    try:
        planner_result = planner_agent(query=query)
        routed_agents = planner_result.get("routed_agents", ["DataVizAgent"])
    except Exception as e:
        logger.error(f"Planner Agent failed: {e}")
        return jsonify({"error": "Failed to route the query."}), 500

    # Step 2: Data Visualization Agent generates code
    try:
        viz_result = data_viz_agent(goal=query, dataset=dataset, styling_index=styling_index)
        code = viz_result.get("code", "")
        commentary = viz_result.get("commentary", "")
    except Exception as e:
        logger.error(f"DataViz Agent failed: {e}")
        # Attempt to fix code using CodeFixAgent
        try:
            fix_result = code_fix_agent(faulty_code=code, error="Code generation error.")
            fixed_code = fix_result.get("fixed_code", "")
            # Retry DataVizAgent with fixed code
            viz_result = data_viz_agent(goal=query, dataset=dataset, styling_index=styling_index)
            code = viz_result.get("code", "")
            commentary = viz_result.get("commentary", "")
        except Exception as ex:
            logger.error(f"CodeFix Agent failed: {ex}")
            return jsonify({"error": "Failed to generate visualization."}), 500

    # Step 3: Execute the generated code and capture output (Plotly image)
    try:
        # Execute the code safely
        exec_globals = {}
        exec(code, exec_globals)
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
        "story": commentary,
        "image_url": image_url if image_url else f"https://{s3_bucket}.s3.amazonaws.com/placeholder.png"
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)
