

# 🚀 AI-Powered Data Analysis Platform with AnalytIQ 🚀

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT%204-blue.svg)

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Demo](#demo)
4. [Architecture](#architecture)
5. [Technology Stack](#technology-stack)
6. [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Setup](#setup)
    - [Environment Variables](#environment-variables)
    - [Dependencies](#dependencies)
7. [Usage](#usage)
    - [Running the Data Analysis Platform](#running-the-data-analysis-platform)
    - [Using AnalytIQ – The Conversational Agent](#using-analytiq---the-conversational-agent)
8. [Project Structure](#project-structure)
9. [Agents Explained](#agents-explained)
10. [API Documentation](#api-documentation)
11. [Deployment](#deployment)
    - [Local Deployment](#local-deployment)
    - [Production Deployment](#production-deployment)
12. [Contributing](#contributing)
13. [License](#license)
14. [Contact](#contact)
15. [Acknowledgements](#acknowledgements)
16. [FAQ](#faq)

---

## Introduction

Welcome to the **AI-Powered Data Analysis Platform with AnalytIQ** repository! This platform is a Flask-based web application designed to streamline data workflows using automation and **Large Language Models (LLMs)**. It enables users to upload datasets, automate data cleaning, perform statistical analysis, and generate interactive visualizations. Additionally, our integrated conversational agent, **AnalytIQ**, serves as an AI-powered Data Analytics Tutor, providing real-time educational support and guidance.

---

## Features

### Data Analysis Platform

- **Data Upload:** Users can upload CSV files up to 10 MB.
- **Automation:** Automate data cleaning, duplicate removal, and dataset preparation.
- **Statistical Analysis:** Generates descriptive statistics, correlation matrices, missing values analysis, and value counts.
- **Data Visualization:** Creates interactive Plotly graphs based on analysis results.
- **Natural Language Queries:** Ask questions in plain English and receive actionable insights.
- **Results Presentation:** Displays analysis results, visualizations, and AI interpretations in a user-friendly interface.
- **Future Integrations:** Upcoming machine learning models and predictive analytics for trend forecasting.

### AnalytIQ – AI-Powered Data Analytics Tutor

- **Real-Time Support:** Get explanations and guidance on complex data concepts.
- **Step-by-Step Tutorials:** Learn best practices and data analytics techniques.
- **Interactive Assistance:** Engage with the tutor to enhance your data-driven decision-making skills.
- **Contextual Understanding:** AnalytIQ uses the platform's data to provide tailored advice and insights.

---


1. **Frontend:** User Interface built with modern web technologies (e.g., HTML, CSS, JavaScript, React.js).
2. **Backend:** Flask-based API server handling data processing and conversational agent interactions.
3. **Database:** Stores user data, datasets, and analysis results.
4. **Vector Search Engine:** FAISS for efficient similarity search and retrieval.
5. **Conversational Agent:** AnalytIQ, powered by OpenAI's GPT-4 Turbo for natural language understanding and response generation.
6. **Deployment:** Containerized using Docker for scalable and consistent deployments.

---

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** PostgreSQL / SQLite
- **Vector Search:** FAISS
- **Conversational AI:** OpenAI GPT-4 Turbo
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly, Matplotlib, Seaborn
- **Deployment:**  Heroku
- **Version Control:** Git, GitHub

---

## Installation

### Prerequisites

- **Python 3.7+**
- **pip** 
- **Git**
- **OpenAI API Key:** Required for AnalytIQ functionality.

### Setup

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/data-analysis-platform.git
    cd data-analysis-platform
    ```

2. **Create a Virtual Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

### Environment Variables

Create a `.env` file in the root directory and add the following variables:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development

# Database Configuration
DATABASE_URL=sqlite:///data_analysis.db

# FAISS Index Path
FAISS_INDEX_PATH=faiss_index.index

# Context Chunks Path
CONTEXT_CHUNKS_PATH=context_chunks.npy
```

**Note:** Replace `your_openai_api_key_here` with your actual OpenAI API key.

### Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

**`requirements.txt` Example:**

```plaintext
requests==2.31.0
Pillow==10.0.1
Werkzeug==2.3.4
numpy>=1.23,<1.25
plotly==5.15.0
kaleido==0.2.1
gunicorn==21.2.0
Flask==2.2.5
Flask-Cors==3.0.10
python-dotenv==1.0.0
tabulate==0.9.0
matplotlib==3.8.0
pandas==2.2.2
statsmodels==0.14.2
scikit-learn==1.2.2
openai==0.28.0
```

---

## Usage

### Running the Data Analysis Platform

1. **Start the Flask Server**

    ```bash
    flask run
    ```

    The application will be accessible at `http://localhost:5000/`.

2. **Access the Web Interface**

    Open your web browser and navigate to `http://localhost:5000/` to interact with the platform.

3. **Upload Datasets**

    Use the upload feature to add your datasets (CSV). The platform will automatically process and prepare the data for analysis.

4. **Perform Analysis**

    Utilize the platform's features to clean data, perform statistical analysis, and generate visualizations.

### Using AnalytIQ – The Conversational Agent

1. **Interact via the Web Interface**

    - Locate the chat interface integrated into the platform.
    - Ask natural language queries like, "What is the correlation between sales and marketing spend?".
    - Receive instant, actionable insights and explanations from AnalytIQ.

2. **Understanding Responses**

    - AnalytIQ provides step-by-step explanations, best practices, and tailored advice based on the uploaded datasets.

---

## Project Structure

```
├── app.py
├── agents.py
├── analytiq.py
├── templates
│   ├── index.html
│   └── analysis.html
├── static
│   ├── css
│       └── styles.css    
├── requirements.txt
├── README.md
└── .env 
```

static: Contains static assets such as CSS files and images.
templates: Contains HTML templates for rendering web pages.
.env: Environment variables file, which includes sensitive information (excluded from version control).
.gitignore: Specifies files and directories to ignore in version control.
LICENSE: License file for the project.
Procfile: Configuration file used for deploying the application on platforms like Heroku.
README.md: Documentation file providing detailed project information.
agents.py: Contains agent classes for data processing, preprocessing, analysis, and visualization.
app.py: The main application file that runs the Flask server.
requirements.txt: Lists the dependencies required to run the project.
runtime.txt: Specifies the runtime environment (Python version).

---

## Agents Explained

### DataProcessingAgent

- **Role:** Cleans the dataset by removing duplicates and performing initial data cleaning steps.
- **Functionality:**
  - **Duplicate Removal:** Identifies and removes duplicate records.
  - **Data Cleaning:** Handles inconsistencies and standardizes data formats.
- **Technologies:** Utilizes Pandas for data manipulation.

### PreprocessingAgent

- **Role:** Preprocesses the data by handling missing values, converting data types, and preparing the data for analysis.
- **Functionality:**
  - **Missing Data Detection:** Identifies null or NaN values.
  - **Imputation Methods:** Applies mean, median, mode, or advanced techniques for missing data.
  - **Data Formatting:** Ensures consistent data types and structures for numeric and categorical variables.
- **Technologies:** Uses Pandas and NumPy for preprocessing tasks.

### AnalysisAgent

- **Role:** Performs statistical analyses based on specified parameters.
- **Functionality:**
  - **Descriptive Statistics:** Calculates mean, median, mode, standard deviation, etc.
  - **Correlation Matrices:** Computes correlation coefficients between variables.
  - **Missing Values Analysis:** Assesses the extent and impact of missing data.
  - **Value Counts:** Provides frequency distribution of categorical variables.
- **Technologies:** Employs Pandas, NumPy, and SciPy for statistical computations.

### VisualizationAgent

- **Role:** Generates visualizations from the analysis results.
- **Functionality:**
  - **Interactive Visualizations:** Creates heatmaps, bar charts, scatter plots, and more using Plotly.
  - **Customization:** Allows users to specify styling preferences for visualizations.
- **Technologies:** Utilizes Plotly, Matplotlib, and Seaborn for creating interactive and static visualizations.

### AnalytIQ Integration

- **Role:** Provides real-time educational support and guidance, interpreting natural language queries to generate actionable insights.
- **Functionality:**
  - **Context Retrieval:** Uses FAISS for retrieving relevant data chunks from uploaded datasets.
  - **Prompt Engineering:** Constructs prompts to guide GPT-4 Turbo responses based on retrieved context.
  - **Response Handling:** Cleans and formats responses for clarity and usability.
  - **Educational Support:** Offers explanations, best practices, and step-by-step tutorials to help users understand data analytics concepts.
- **Technologies:** Powered by OpenAI's GPT-4 Turbo, integrated via the OpenAI API.

---

## API Documentation

### Endpoint: `/question`

- **Method:** `POST`
- **Description:** Handles user questions, retrieves relevant data chunks, and generates responses using AnalytIQ.
- **Request Body:**

    ```json
    {
        "question": "What is the correlation between sales and marketing spend?"
    }
    ```

- **Response:**

    ```json
    {
        "answer": "The correlation between sales and marketing spend is 0.85, indicating a strong positive relationship. This suggests that as marketing spend increases, sales tend to increase as well."
    }
    ```

- **Error Responses:**

    - **400 Bad Request:**

        ```json
        {
            "error": "No document uploaded."
        }
        ```

    - **500 Internal Server Error:**

        ```json
        {
            "error": "A descriptive error message."
        }
        ```

### Additional Endpoints

*(Add additional API endpoints as your platform expands.)*

---

## Deployment

### Local Deployment

For local development and testing:

1. **Ensure Environment Variables are Set**

    As outlined in the [Environment Variables](#environment-variables) section.

2. **Run the Application**

    ```bash
    flask run
    ```

3. **Access Locally**

    Visit `http://localhost:5000/` in your web browser.

### Production Deployment

For deploying the application to a production environment (e.g., AWS, Heroku):

1. **Containerization with Docker**

    **Dockerfile Example:**

    ```dockerfile
    # Use an official Python runtime as a parent image
    FROM python:3.8-slim

    # Set environment variables
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1

    # Set work directory
    WORKDIR /app

    # Install dependencies
    COPY requirements.txt .
    RUN pip install --upgrade pip
    RUN pip install -r requirements.txt

    # Copy project
    COPY . .

    # Expose the port
    EXPOSE 5000

    # Run the application
    CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "3"]
    ```

2. **Build the Docker Image**

    ```bash
    docker build -t data-analysis-platform .
    ```

3. **Run the Docker Container**

    ```bash
    docker run -d -p 5000:5000 --env-file .env data-analysis-platform
    ```

4. **Deploy to Cloud Platforms**

    - **Heroku:** Follow Heroku's deployment guides for Docker-based applications.
    - **AWS Elastic Beanstalk:** Use AWS's documentation to deploy Docker containers.
    - **Other Platforms:** Adjust based on the chosen platform's requirements.

**Note:** Ensure that your `.env` file or environment variables are securely managed in production environments.

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

    Click the **Fork** button at the top right of the repository to create your own forked version.

2. **Clone the Forked Repository**

    ```bash
    git clone https://github.com/yourusername/data-analysis-platform.git
    cd data-analysis-platform
    ```

3. **Create a New Branch**

    ```bash
    git checkout -b feature/YourFeatureName
    ```

4. **Make Changes**

    Implement your feature or fix bugs. Ensure that your code follows the project's coding standards.

5. **Commit Your Changes**

    ```bash
    git commit -m "Add Your Feature Description"
    ```

6. **Push to the Branch**

    ```bash
    git push origin feature/YourFeatureName
    ```

7. **Create a Pull Request**

    Navigate to the original repository and click the **New Pull Request** button. Provide a clear description of your changes and submit.

### Code of Conduct

Please adhere to the [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and respectful environment for all contributors.

---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## Contact

**Your Name** – Mohamed Habib Agrebi , habibagrebi7@gmail.com

Project Link: [https://github.com/Engmhabib/AI-Powered-Data-Analysis-Platform-with-AnalytIQ]

---

## Acknowledgements

- [OpenAI](https://openai.com/) for providing powerful language models.
- [FAISS](https://github.com/facebookresearch/faiss) for efficient similarity search.
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Plotly](https://plotly.com/) for interactive visualizations.
- [Python](https://www.python.org/) community for the extensive libraries and support.
- [React.js](https://reactjs.org/) for building the frontend.
- [Docker](https://www.docker.com/) for containerization.
- [GitHub](https://github.com/) for version control and collaboration.

---

## FAQ

### 1. **How do I obtain an OpenAI API key?**

- Visit [OpenAI's API page](https://openai.com/api/) and sign up for access. Once registered, you can generate your API key from the dashboard.

### 2. **Can I use this platform with large datasets?**

- Yes, the platform is designed to handle large datasets efficiently. However, performance may vary based on your hardware and the complexity of operations. For extremely large datasets, consider deploying the application on scalable cloud infrastructure.

### 3. **How can I contribute new features to AnalytIQ?**

- Fork the repository, create a new branch, implement your feature, and submit a pull request. Ensure that your changes align with the project's coding standards and include relevant tests.

### 4. **Is the platform compatible with other conversational AI models?**

- Currently, AnalytIQ is integrated with OpenAI's GPT-4 Turbo. Integration with other models can be implemented by modifying the `analytiq.py` module to interface with different APIs or models.

### 5. **How secure is the platform regarding data privacy?**

- We prioritize data security and privacy. Ensure that sensitive information is handled appropriately, especially when deploying the application. Follow best practices for securing API keys, using HTTPS, and managing user data.

### 6. **How do I delete a group of pages in a Word document?**

- Refer to the [How to Delete a Group of Pages in Word](https://github.com/yourusername/data-analysis-platform#how-to-delete-a-group-of-pages-in-word) section in the documentation for detailed instructions.

### 7. **How do I delete spaces in a document?**

- For instructions on deleting spaces, see the [How to Delete Spaces](https://github.com/yourusername/data-analysis-platform#how-to-deletespaces) section in the documentation.

---

# Getting Started

To get started with developing or deploying the **AI-Powered Data Analysis Platform with AnalytIQ**, follow the installation and usage instructions provided above. If you encounter any issues or have suggestions, feel free to open an issue or contribute to the project!

---

**Happy Analyzing! 🚀📊🤖**
