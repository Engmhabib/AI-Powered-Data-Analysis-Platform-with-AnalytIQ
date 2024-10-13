# agents.py

import pandas as pd
import plotly.express as px
import logging
import json
from plotly.utils import PlotlyJSONEncoder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessingAgent:
    """
    Agent responsible for cleaning and preprocessing the dataset.
    """
    def process(self, df):
        try:
            # Data Cleaning Steps (Example)
            df = df.dropna()  # Remove missing values
            logger.info("Missing values removed.")

            # Additional preprocessing can be added here
            return df
        except Exception as e:
            logger.error(f"Error in DataProcessingAgent: {e}")
            raise e

class AnalysisAgent:
    """
    Agent responsible for performing statistical analysis on the dataset.
    """
    def analyze(self, df, analysis_params):
        try:
            analysis_results = {}

            # Example Analysis: Descriptive Statistics
            if analysis_params.get("descriptive_statistics", False):
                analysis_results["descriptive_statistics"] = df.describe().to_dict()
                logger.info("Descriptive statistics generated.")

            # Example Analysis: Correlation Matrix
            if analysis_params.get("correlation_matrix", False):
                # Select only numeric columns to avoid issues
                numeric_df = df.select_dtypes(include='number')
                correlation = numeric_df.corr()
                analysis_results["correlation_matrix"] = correlation.to_dict()
                logger.info("Correlation matrix generated.")

            # Additional analyses can be added based on analysis_params
            return analysis_results
        except Exception as e:
            logger.error(f"Error in AnalysisAgent: {e}")
            raise e

class VisualizationAgent:
    """
    Agent responsible for creating visualizations based on analysis results.
    """
    def visualize(self, df, analysis_results, styling_params):
        try:
            # Initialize empty figure
            fig = None
            commentary = ""

            # Example Visualization: Bar Chart of Mean Values
            if "descriptive_statistics" in analysis_results:
                desc_stats = analysis_results["descriptive_statistics"]
                # Get the mean values from descriptive statistics
                means = {col: stats['mean'] for col, stats in desc_stats.items()}
                categories = list(means.keys())
                mean_values = list(means.values())

                fig = px.bar(
                    x=categories,
                    y=mean_values,
                    title='Mean Values of Numerical Columns',
                    labels={'x': 'Columns', 'y': 'Mean Value'}
                )
                fig.update_layout(title_font_size=24)

                commentary = "Generated a bar chart showcasing the mean values of each numerical column."

            # Example Visualization: Heatmap of Correlation Matrix
            elif "correlation_matrix" in analysis_results:
                correlation = analysis_results["correlation_matrix"]
                df_corr = pd.DataFrame(correlation)

                fig = px.imshow(
                    df_corr,
                    text_auto=True,
                    title='Correlation Matrix',
                    labels=dict(x="Variables", y="Variables", color="Correlation Coefficient")
                )
                fig.update_layout(title_font_size=24)

                commentary = "Generated a heatmap displaying the correlation matrix of the dataset."

            else:
                commentary = "No visualizations generated based on the analysis results."

            if fig is not None:
                # Serialize figure to JSON
                graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
            else:
                graphJSON = None

            return graphJSON, commentary
        except Exception as e:
            logger.error(f"Error in VisualizationAgent: {e}")
            raise e
