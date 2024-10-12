Auto-Analyst is an AI-driven data analytics system designed to generate insightful stories and visualizations based on user inputs. It leverages multiple agents for data processing and visualization, integrates with AWS S3 for image storage, and is deployed on Heroku for accessibility.

Key Features:
User Interface:

Web-based interface built with Flask.
Allows users to input data, specify themes, and generate stories.
Agents:

Doer Agents: Generate visualizations using Plotly based on user queries.
Helper Agents: Fix errors in generated code.
Planner Agent: Routes queries to appropriate agents.
Storage:

AWS S3 integration for persistent image storage.
Deployment:

Hosted on Heroku for easy access and scalability.
