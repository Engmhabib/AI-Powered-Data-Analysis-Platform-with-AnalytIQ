# app.py

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from agents import DataProcessingAgent, AnalysisAgent, VisualizationAgent

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_default_secret_key')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize agents
data_processing_agent = DataProcessingAgent()
analysis_agent = AnalysisAgent()
visualization_agent = VisualizationAgent()

def perform_analysis(data):
    """
    Perform the entire analysis workflow:
    1. Data Processing
    2. Data Analysis
    3. Data Visualization
    """
    df = data.get("dataframe")
    analysis_params = data.get("analysis_params", {})
    styling_params = data.get("styling_params", "Default styling.")

    if df is None:
        return {"error": "No dataset provided."}, 400

    # Step 1: Data Processing
    try:
        processed_data = data_processing_agent.process(df)
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
        graphJSON, commentary = visualization_agent.visualize(processed_data, analysis_results, styling_params)
    except Exception as e:
        logger.error(f"VisualizationAgent failed: {e}")
        return {"error": "Data visualization failed."}, 500

    # Prepare response
    response = {
        "analysis": analysis_results,
        "commentary": commentary,
        "graphJSON": graphJSON
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
            # Read the uploaded file directly into a DataFrame
            try:
                df = pd.read_csv(file)
            except Exception as e:
                logger.error(f"Failed to read CSV file: {e}")
                flash('Failed to read CSV file. Please ensure it is a valid CSV.', 'danger')
                return redirect(request.url)

            logger.info("Dataset uploaded and read successfully.")

            # Get analysis parameters from the form
            analysis_params = {
                "descriptive_statistics": 'descriptive_statistics' in request.form,
                "correlation_matrix": 'correlation_matrix' in request.form,
                "missing_values": 'missing_values' in request.form,
                "value_counts": 'value_counts' in request.form
                # Add more parameters as needed
            }

            # Get styling parameters
            styling_params = request.form.get('styling_params', 'Default styling.')

            # Prepare data to send to analysis function
            data = {
                "dataframe": df,
                "analysis_params": analysis_params,
                "styling_params": styling_params
            }

            # Call the analysis function directly
            result, status_code = perform_analysis(data)
            if status_code == 200:
                analysis = result.get("analysis", {})
                commentary = result.get("commentary", "")
                graphJSON = result.get("graphJSON", None)
                return render_template('analysis.html', analysis=analysis, commentary=commentary, graphJSON=graphJSON)
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
    app.run(port=5000, debug=False)
