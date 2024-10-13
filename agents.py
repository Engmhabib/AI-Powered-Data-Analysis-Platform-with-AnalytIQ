import pandas as pd
import numpy as np
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
            df = df.drop_duplicates()
            logger.info(f"Duplicates removed. Data now has {df.shape[0]} rows and {df.shape[1]} columns.")
            # Additional preprocessing can be added here
            return df
        except Exception as e:
            logger.error(f"Error in DataProcessingAgent: {e}")
            raise e

class PreprocessingAgent:
    """
    Agent responsible for further cleaning and preprocessing the dataset.
    """
    def preprocess(self, df):
        try:
            # Identify numeric and categorical columns
            categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

            # Handle missing values
            df[categorical_columns] = df[categorical_columns].fillna('Unknown')
            df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())

            # Convert date columns to datetime
            for col in df.columns:
                if 'date' in col.lower():
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            # Handle mixed data types (e.g., object columns that should be numeric)
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        df[col] = pd.to_numeric(df[col], errors='ignore')
                    except Exception as e:
                        logger.warning(f"Failed to convert column {col} to numeric. Skipping conversion.")

            logger.info("Data preprocessing completed.")
            return df
        except Exception as e:
            logger.error(f"Error in PreprocessingAgent: {e}")
            raise e

class AnalysisAgent:
    """
    Agent responsible for performing statistical analysis on the dataset.
    """
    def analyze(self, df, analysis_params):
        try:
            analysis_results = {}

            # Descriptive Statistics
            if analysis_params.get("descriptive_statistics", False):
                descriptive_stats = df.describe(include='all').to_dict()
                # Convert NumPy data types to native Python types
                descriptive_stats = self.convert_to_native_types(descriptive_stats)
                analysis_results["descriptive_statistics"] = descriptive_stats
                logger.info("Descriptive statistics generated.")

            # Correlation Matrix
            if analysis_params.get("correlation_matrix", False):
                numeric_df = df.select_dtypes(include='number')
                correlation = numeric_df.corr().to_dict()
                # Convert NumPy data types to native Python types
                correlation = self.convert_to_native_types(correlation)
                analysis_results["correlation_matrix"] = correlation
                logger.info("Correlation matrix generated.")

            # Missing Values Analysis
            if analysis_params.get("missing_values", False):
                missing_values = df.isnull().sum().to_dict()
                # Convert NumPy data types to native Python types
                missing_values = self.convert_to_native_types(missing_values)
                analysis_results["missing_values"] = missing_values
                logger.info("Missing values analysis completed.")

            # Value Counts for Categorical Variables
            if analysis_params.get("value_counts", False):
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns
                value_counts = {col: df[col].value_counts().to_dict() for col in categorical_cols}
                # Convert NumPy data types to native Python types
                value_counts = self.convert_to_native_types(value_counts)
                analysis_results["value_counts"] = value_counts
                logger.info("Value counts for categorical variables generated.")

            return analysis_results
        except Exception as e:
            logger.error(f"Error in AnalysisAgent: {e}")
            raise e

    def convert_to_native_types(self, data):
        """
        Recursively convert NumPy data types to native Python types.
        """
        if isinstance(data, dict):
            return {k: self.convert_to_native_types(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.convert_to_native_types(v) for v in data]
        elif isinstance(data, np.generic):
            return data.item()  # Handle NumPy scalars
        elif pd.isnull(data):
            return None  # Handle NaNs
        else:
            return data

class VisualizationAgent:
    """
    Agent responsible for creating visualizations based on analysis results.
    """
    def visualize(self, df, analysis_results, styling_params):
        try:
            # Initialize empty figure
            fig = None
            commentary = ""

            # Visualization based on Descriptive Statistics
            if "descriptive_statistics" in analysis_results:
                desc_stats = analysis_results["descriptive_statistics"]
                # Get the mean values from descriptive statistics
                means = {col: stats['mean'] for col, stats in desc_stats.items() if 'mean' in stats and isinstance(stats['mean'], (int, float))}
                categories = list(means.keys())
                mean_values = list(means.values())

                if mean_values:
                    fig = px.bar(
                        x=categories,
                        y=mean_values,
                        title='Mean Values of Numerical Columns',
                        labels={'x': 'Columns', 'y': 'Mean Value'},
                        color_discrete_sequence=px.colors.qualitative.Pastel  # Custom color scheme example
                    )
                    fig.update_layout(title_font_size=24)

                    commentary = "Generated a bar chart showcasing the mean values of each numerical column."
                else:
                    commentary = "No numerical columns with mean values found for visualization."
                    fig = None

            # Visualization based on Correlation Matrix
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

            # Scatter plot example based on Correlation Matrix
            elif "correlation_matrix" in analysis_results and df.shape[1] >= 2:
                columns = df.select_dtypes(include='number').columns[:2]
                fig = px.scatter(df, x=columns[0], y=columns[1], title=f'Scatter Plot of {columns[0]} vs {columns[1]}')
                commentary = f"Generated a scatter plot for the correlation between {columns[0]} and {columns[1]}."

            else:
                commentary = "No visualizations generated based on the analysis results."
                fig = None

            if fig is not None:
                # Serialize figure to JSON string using PlotlyJSONEncoder
                graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
            else:
                graphJSON = None

            return graphJSON, commentary
        except Exception as e:
            logger.error(f"Error in VisualizationAgent: {e}")
            raise e
