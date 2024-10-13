import pandas as pd
import numpy as np
import plotly.express as px
import logging
from sklearn.cluster import KMeans

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessingAgent:
    # Existing code remains unchanged
    def process(self, df):
        try:
            df = df.drop_duplicates()
            logger.info(f"Duplicates removed. Data now has {df.shape[0]} rows and {df.shape[1]} columns.")
            return df
        except Exception as e:
            logger.error(f"Error in DataProcessingAgent.process: {e}")
            raise Exception(f"DataProcessingAgent.process failed: {e}")

class PreprocessingAgent:
    def preprocess(self, df):
        try:
            # Identify columns
            categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

            # Handle missing values
            df[categorical_columns] = df[categorical_columns].fillna('Unknown')
            df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())

            # Convert date columns to datetime
            for col in df.columns:
                if 'date' in col.lower():
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            # Convert numeric-like strings to numbers
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        df[col] = pd.to_numeric(df[col])
                    except ValueError:
                        logger.warning(f"Column {col} contains non-numeric values. Skipping conversion.")

            logger.info("Data preprocessing completed.")
            return df
        except Exception as e:
            logger.error(f"Error in PreprocessingAgent.preprocess: {e}")
            raise Exception(f"PreprocessingAgent.preprocess failed: {e}")

class AnalysisAgent:
    # Existing code remains unchanged
    def analyze(self, df, analysis_params):
        # Analysis methods as before
        # Ensure all analysis methods are correctly implemented
        pass  # Replace with the full implementation as provided earlier

class VisualizationAgent:
    # Existing code remains unchanged
    def visualize(self, df, analysis_results, styling_params):
        # Visualization methods as before
        pass  # Replace with the full implementation as provided earlier
