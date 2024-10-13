# agents.py

import pandas as pd
import plotly.express as px
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessingAgent:
    """
    Agent responsible for cleaning and preprocessing the dataset.
    """
    def process(self, dataset_path):
        try:
            # Load dataset
            df = pd.read_csv(dataset_path)
            logger.info("Dataset loaded successfully.")

            # Data Cleaning Steps (Example)
            df.dropna(inplace=True)  # Remove missing values
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
                # Select only numeric columns to avoid FutureWarning
                correlation = df.select_dtypes(include='number').corr()
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
            # Example Visualization: Bar Chart of Mean Values
            if "descriptive_statistics" in analysis_results:
                desc_stats = analysis_results["descriptive_statistics"]
                categories = list(desc_stats.keys())
                means = [desc_stats[cat]["mean"] for cat in categories]

                fig_bar = px.bar(
                    x=categories,
                    y=means,
                    title='Mean Values of Categories',
                    labels={'x': 'Category', 'y': 'Mean Value'}
                )
                fig_bar.update_layout(title_font_size=24)

                commentary = "Generated a bar chart showcasing the mean values of each category."

                return fig_bar, commentary  # Return the figure object and commentary

            # Example Visualization: Heatmap of Correlation Matrix
            elif "correlation_matrix" in analysis_results:
                correlation = analysis_results["correlation_matrix"]
                df_corr = pd.DataFrame(correlation)

                fig_heatmap = px.imshow(
                    df_corr,
                    text_auto=True,
                    title='Correlation Matrix',
                    labels=dict(x="Variables", y="Variables", color="Correlation Coefficient")
                )
                fig_heatmap.update_layout(title_font_size=24)

                commentary = "Generated a heatmap displaying the correlation matrix of the dataset."

                return fig_heatmap, commentary  # Return the figure object and commentary

            else:
                commentary = "No visualizations generated based on the analysis results."
                return None, commentary
        except Exception as e:
            logger.error(f"Error in VisualizationAgent: {e}")
            raise e
