import pandas as pd
import numpy as np
import plotly.express as px
import logging
from sklearn.cluster import KMeans

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessingAgent:
    """
    Agent responsible for cleaning and preprocessing the dataset.
    """
    def process(self, df):
        try:
            # Data Cleaning Steps
            df = df.drop_duplicates()
            logger.info(f"Duplicates removed. Data now has {df.shape[0]} rows and {df.shape[1]} columns.")
            # Additional preprocessing can be added here
            return df
        except Exception as e:
            logger.error(f"Error in DataProcessingAgent.process: {e}")
            raise Exception(f"DataProcessingAgent.process failed: {e}")

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

            # Handle mixed data types
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
    """
    Agent responsible for performing statistical analysis on the dataset.
    """
    def analyze(self, df, analysis_params):
        try:
            analysis_results = {}

            # Descriptive Statistics
            if analysis_params.get("descriptive_statistics", False):
                descriptive_stats = df.describe(include='all').to_dict()
                descriptive_stats = self.convert_to_native_types(descriptive_stats)
                analysis_results["descriptive_statistics"] = descriptive_stats
                logger.info("Descriptive statistics generated.")

            # Correlation Matrix
            if analysis_params.get("correlation_matrix", False):
                numeric_df = df.select_dtypes(include='number')
                correlation = numeric_df.corr().to_dict()
                correlation = self.convert_to_native_types(correlation)
                analysis_results["correlation_matrix"] = correlation
                logger.info("Correlation matrix generated.")

            # Missing Values Analysis
            if analysis_params.get("missing_values", False):
                missing_values = df.isnull().sum().to_dict()
                missing_values = self.convert_to_native_types(missing_values)
                analysis_results["missing_values"] = missing_values
                logger.info("Missing values analysis completed.")

            # Value Counts for Categorical Variables
            if analysis_params.get("value_counts", False):
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns
                value_counts = {col: df[col].value_counts().to_dict() for col in categorical_cols}
                value_counts = self.convert_to_native_types(value_counts)
                analysis_results["value_counts"] = value_counts
                logger.info("Value counts for categorical variables generated.")

            # Time Series Analysis
            if analysis_params.get("time_series_analysis", False):
                time_series_results = self.time_series_analysis(df)
                analysis_results["time_series_analysis"] = time_series_results
                logger.info("Time series analysis completed.")

            # Clustering Analysis
            if analysis_params.get("clustering_analysis", False):
                clustering_results = self.clustering_analysis(df)
                analysis_results["clustering_analysis"] = clustering_results
                logger.info("Clustering analysis completed.")

            return analysis_results
        except Exception as e:
            logger.error(f"Error in AnalysisAgent.analyze: {e}")
            raise Exception(f"AnalysisAgent.analyze failed: {e}")

    def time_series_analysis(self, df):
        # Identify date columns
        date_cols = df.select_dtypes(include=['datetime', 'datetime64']).columns
        if len(date_cols) > 0:
            date_col = date_cols[0]  # Use the first date column
            df_sorted = df.sort_values(by=date_col)
            df_sorted.set_index(date_col, inplace=True)
            numeric_cols = df_sorted.select_dtypes(include='number').columns
            if len(numeric_cols) > 0:
                time_series_summary = df_sorted[numeric_cols].resample('M').mean().to_dict()
                return self.convert_to_native_types(time_series_summary)
            else:
                logger.warning("No numeric columns for time series analysis.")
                return {}
        else:
            logger.warning("No date columns found for time series analysis.")
            return {}

    def clustering_analysis(self, df):
        numeric_df = df.select_dtypes(include='number').dropna()
        if numeric_df.shape[0] > 0 and numeric_df.shape[1] >= 2:
            kmeans = KMeans(n_clusters=3)
            kmeans.fit(numeric_df)
            clusters = kmeans.labels_
            df['Cluster'] = clusters
            cluster_counts = df['Cluster'].value_counts().to_dict()
            return self.convert_to_native_types(cluster_counts)
        else:
            logger.warning("Insufficient numeric data available for clustering.")
            return {}

    def convert_to_native_types(self, data):
        """
        Recursively convert NumPy and pandas data types to native Python types.
        """
        if isinstance(data, dict):
            return {k: self.convert_to_native_types(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.convert_to_native_types(v) for v in data]
        elif isinstance(data, (np.integer, np.floating, np.bool_)):
            return data.item()
        elif pd.isnull(data):
            return None
        else:
            return data

class VisualizationAgent:
    """
    Agent responsible for creating visualizations based on analysis results.
    """
    def visualize(self, df, analysis_results, styling_params):
        try:
            fig = None
            commentary = ""

            if "descriptive_statistics" in analysis_results:
                desc_stats = analysis_results["descriptive_statistics"]
                means = {col: stats['mean'] for col, stats in desc_stats.items() if 'mean' in stats and isinstance(stats['mean'], (int, float))}
                categories = list(means.keys())
                mean_values = list(means.values())

                if mean_values:
                    fig = px.bar(
                        x=categories,
                        y=mean_values,
                        title='Mean Values of Numerical Columns',
                        labels={'x': 'Columns', 'y': 'Mean Value'},
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_layout(title_font_size=24)

                    commentary = "Generated a bar chart showcasing the mean values of each numerical column."
                else:
                    commentary = "No numerical columns with mean values found for visualization."
                    fig = None

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

            elif "time_series_analysis" in analysis_results:
                # For simplicity, let's plot the time series of the first numeric column
                time_series_data = analysis_results["time_series_analysis"]
                if time_series_data:
                    first_metric = next(iter(time_series_data))
                    dates = list(time_series_data[first_metric].keys())
                    values = list(time_series_data[first_metric].values())
                    fig = px.line(x=dates, y=values, title=f'Time Series of {first_metric}')
                    commentary = f"Generated a time series plot for {first_metric}."
                else:
                    commentary = "No time series data available for visualization."
                    fig = None

            elif "clustering_analysis" in analysis_results:
                # Scatter plot with clusters
                if 'Cluster' in df.columns:
                    numeric_cols = df.select_dtypes(include='number').columns.tolist()
                    if len(numeric_cols) >= 2:
                        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], color='Cluster',
                                         title='Clustering Analysis',
                                         labels={'color': 'Cluster'})
                        commentary = f"Generated a scatter plot with clusters based on {numeric_cols[0]} and {numeric_cols[1]}."
                    else:
                        commentary = "Not enough numeric columns for clustering visualization."
                        fig = None
                else:
                    commentary = "No clustering data available for visualization."
                    fig = None

            else:
                # Fallback visualization
                numeric_cols = df.select_dtypes(include='number').columns
                if len(numeric_cols) >= 2:
                    fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                                     title=f'Scatter Plot of {numeric_cols[0]} vs {numeric_cols[1]}')
                    commentary = f"Generated a scatter plot for {numeric_cols[0]} vs {numeric_cols[1]}."
                else:
                    commentary = "No suitable data for visualization."
                    fig = None

            if fig:
                graphJSON = fig.to_json()
            else:
                graphJSON = None

            return graphJSON, commentary
        except Exception as e:
            logger.error(f"Error in VisualizationAgent.visualize: {e}")
            raise Exception(f"VisualizationAgent.visualize failed: {e}")
