import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from agents import DataProcessingAgent, PreprocessingAgent, AnalysisAgent, VisualizationAgent
import openai
import json
import re
import time
from typing import Tuple, Dict, Any  # Added 'Any' here

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_default_secret_key')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename: str) -> bool:
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

# Define valid analysis keys
VALID_ANALYSIS_KEYS = {
    "descriptive_statistics",
    "correlation_matrix",
    "missing_values",
    "value_counts",
    "time_series_analysis",
    "clustering_analysis"
}

def interpret_query(user_query: str) -> Tuple[Dict[str, bool], str]:
    """
    Uses OpenAI's ChatCompletion API to interpret the user's natural language query
    and determine which data analyses to perform.
    
    Args:
        user_query (str): The natural language query from the user.
    
    Returns:
        Tuple[Dict[str, bool], str]: A dictionary of analysis parameters and the AI's explanation.
    """
    # Define the system prompt with JSON specification
    system_content = (
        "You are an assistant that helps determine which analyses to perform based on a user's query and provides insights. "
        "First, provide the analyses as a JSON object labeled with 'json' and enclosed in triple backticks, like ```json\n{...}\n```. "
        "Ensure the JSON only includes the following keys with boolean values: descriptive_statistics, correlation_matrix, missing_values, value_counts, "
        "time_series_analysis, clustering_analysis. "
        "After the JSON, provide a brief natural language explanation of the insights you can offer based on the user's query."
    )
    
    # Default analysis parameters
    analysis_params = {key: False for key in VALID_ANALYSIS_KEYS}
    openai_response_text = ""
    
    retries = 3
    backoff_factor = 2

    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Updated model
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=750,
                temperature=0.3,  # Lowered temperature for deterministic responses
            )
            break  # Exit the retry loop if successful
        except openai.error.RateLimitError:
            logger.warning(f"Rate limit exceeded. Retrying in {backoff_factor ** attempt} seconds...")
            time.sleep(backoff_factor ** attempt)
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            flash('An error occurred while processing your request. Please try again later.', 'danger')
            return analysis_params, "Error processing your query. Default analysis will be performed."
    else:
        # All retries failed
        flash('The service is currently unavailable. Please try again later.', 'danger')
        return analysis_params, "Service is currently unavailable."

    try:
        ai_response = response['choices'][0]['message']['content'].strip()
        logger.info(f"AI Response: {ai_response}")

        # Extract JSON object labeled with 'json' enclosed in triple backticks
        match = re.search(r'```json\s*\n?(\{.*?\})\n?```', ai_response, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
            parsed_response = json.loads(json_str)
            logger.info(f"Parsed JSON from AI: {parsed_response}")

            # Update analysis parameters with validated keys and boolean values
            for key in VALID_ANALYSIS_KEYS:
                if key in parsed_response and isinstance(parsed_response[key], bool):
                    analysis_params[key] = parsed_response[key]
                else:
                    logger.warning(f"Missing or invalid key '{key}' in AI response.")

            # Remove JSON part to get the explanation
            explanation = ai_response.replace(match.group(0), '').strip()
            openai_response_text = explanation
        else:
            # If no valid JSON found, default to descriptive statistics
            logger.warning("No valid JSON found in AI response.")
            analysis_params["descriptive_statistics"] = True
            openai_response_text = ai_response  # Treat entire response as explanation

    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error interpreting AI response: {e}")
        flash('There was an issue interpreting your query. Default analysis will be performed.', 'warning')
        analysis_params["descriptive_statistics"] = True
        openai_response_text = "There was an issue interpreting your query. Default analysis will be performed."
    except Exception as e:
        logger.error(f"Error interpreting AI response: {e}")
        flash('Error processing your query. Please try again.', 'danger')
        analysis_params["descriptive_statistics"] = True
        openai_response_text = "Error processing your query. Default analysis will be performed."

    return analysis_params, openai_response_text

def perform_analysis(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Perform the entire analysis workflow:
    1. Data Processing
    2. Preprocessing
    3. Data Analysis
    4. Data Visualization
    
    Args:
        data (Dict[str, Any]): A dictionary containing dataframe, analysis parameters, styling parameters, and OpenAI response text.
    
    Returns:
        Tuple[Dict[str, Any], int]: A dictionary with analysis results and an HTTP status code.
    """
    df = data.get("dataframe")
    analysis_params = data.get("analysis_params", {})
    styling_params = data.get("styling_params", "Default styling.")
    openai_response_text = data.get("openai_response_text", "No OpenAI query provided.")

    if df is None:
        logger.error("No dataset provided.")
        return {"error": "No dataset provided."}, 400

    # Step 1: Data Processing
    try:
        logger.info("Starting data processing.")
        processed_data = data_processing_agent.process(df)
        processed_data = preprocessing_agent.preprocess(processed_data)
        logger.info("Data processing completed successfully.")
    except Exception as e:
        logger.error(f"DataProcessingAgent failed: {e}")
        return {"error": "Data processing failed."}, 500

    # Step 2: Data Analysis
    try:
        logger.info("Starting data analysis.")
        analysis_results = analysis_agent.analyze(processed_data, analysis_params)
        logger.info("Data analysis completed successfully.")
    except Exception as e:
        logger.error(f"AnalysisAgent failed: {e}")
        return {"error": "Data analysis failed."}, 500

    # Step 3: Data Visualization
    try:
        logger.info("Starting data visualization.")
        graphJSON, commentary = visualization_agent.visualize(processed_data, analysis_results, styling_params)
        logger.info("Data visualization completed successfully.")
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
                logger.info("Dataset uploaded and read successfully.")
            except Exception as e:
                logger.error(f"Failed to read CSV file: {e}")
                flash('Failed to read CSV file. Please ensure it is a valid CSV.', 'danger')
                return redirect(request.url)

            user_query = request.form.get('user_query', '').strip()

            if user_query:
                # Interpret the user's natural language query
                analysis_params, openai_response_text = interpret_query(user_query)
            else:
                # Get analysis parameters from the form
                analysis_params = {
                    key: key in request.form
                    for key in VALID_ANALYSIS_KEYS
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
