import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from agents import DataProcessingAgent, PreprocessingAgent, AnalysisAgent, VisualizationAgent
import openai
import json

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_default_secret_key')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Custom Jinja2 filter to check if a value is numeric
@app.template_filter('is_number')
def is_number(value):
    return isinstance(value, (int, float))

# Initialize agents
data_processing_agent = DataProcessingAgent()
preprocessing_agent = PreprocessingAgent()
analysis_agent = AnalysisAgent()
visualization_agent = VisualizationAgent()

# Load your OpenAI API key from an environment variable
openai.api_key = os.environ.get('OPENAI_API_KEY')

def interpret_query(user_query):
    # Use OpenAI API to interpret the query using ChatCompletion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that determines which analyses to perform based on a user's query. Options are: descriptive_statistics, correlation_matrix, missing_values, value_counts. Provide the options as a JSON object with keys as options and values as true or false. For example: {'descriptive_statistics': true, 'correlation_matrix': false, ...}"},
            {"role": "user", "content": user_query}
        ],
        max_tokens=150,
        temperature=0
    )

    # Default analysis parameters
    analysis_params = {
        "descriptive_statistics": False,
        "correlation_matrix": False,
        "missing_values": False,
        "value_counts": False
    }

    try:
        ai_response = response['choices'][0]['message']['content'].strip()
        logger.info(f"AI Response: {ai_response}")
        # Parse the AI response
        parsed_response = json.loads(ai_response.lower())
        # Update analysis parameters
        analysis_params.update(parsed_response)
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error interpreting AI response: {e}")
        flash('There was an issue interpreting your query. Default analysis will be performed.', 'warning')
        analysis_params["descriptive_statistics"] = True
        ai_response = "There was an issue interpreting your query. Default analysis will be performed."
    except Exception as e:
        logger.error(f"Error interpreting AI response: {e}")
        flash('Error processing your query. Please try again.', 'danger')
        analysis_params["descriptive_statistics"] = True
        ai_response = "Error processing your query. Default analysis will be performed."

    return analysis_params, ai_response

def perform_analysis(data):
    """
    Perform the entire analysis workflow:
    1. Data Processing
    2. Preprocessing
    3. Data Analysis
    4. Data Visualization
    """
    df = data.get("dataframe")
    analysis_params = data.get("analysis_params", {})
    styling_params = data.get("styling_params", "Default styling.")
    openai_response_text = data.get("openai_response_text", "No OpenAI query provided.")

    if df is None:
        return {"error": "No dataset provided."}, 400

    # Step 1: Data Processing
    try:
        processed_data = data_processing_agent.process(df)
        processed_data = preprocessing_agent.preprocess(processed_data)
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
        "graphJSON": graphJSON,
        "openai_response_text": openai_response_text
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
            # Validate file size
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            if file_length > MAX_FILE_SIZE:
                flash('File size exceeds the limit of 10 MB.', 'danger')
                return redirect(request.url)
            file.seek(0)  # Reset file pointer after checking size

            # Read the uploaded file directly into a DataFrame
            try:
                df = pd.read_csv(file)
            except Exception as e:
                logger.error(f"Failed to read CSV file: {e}")
                flash('Failed to read CSV file. Please ensure it is a valid CSV.', 'danger')
                return redirect(request.url)

            logger.info("Dataset uploaded and read successfully.")

            user_query = request.form.get('user_query', '').strip()

            if user_query:
                # Interpret the user's natural language query
                analysis_params, openai_response_text = interpret_query(user_query)
            else:
                # Get analysis parameters from the form
                analysis_params = {
                    "descriptive_statistics": 'descriptive_statistics' in request.form,
                    "correlation_matrix": 'correlation_matrix' in request.form,
                    "missing_values": 'missing_values' in request.form,
                    "value_counts": 'value_counts' in request.form
                }
                openai_response_text = "No query was provided."

            # Get styling parameters
            styling_params = request.form.get('styling_params', 'Default styling.')

            # Prepare data to send to analysis function
            data = {
                "dataframe": df,
                "analysis_params": analysis_params,
                "styling_params": styling_params,
                "openai_response_text": openai_response_text
            }

            # Call the analysis function directly
            result, status_code = perform_analysis(data)
            if status_code == 200:
                analysis = result.get("analysis", {})
                commentary = result.get("commentary", "")
                graphJSON = result.get("graphJSON", None)
                openai_response_text = result.get("openai_response_text", "No response from OpenAI.")
                return render_template('analysis.html',
                                       analysis=analysis,
                                       commentary=commentary,
                                       graphJSON=graphJSON,
                                       openai_response_text=openai_response_text)
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
