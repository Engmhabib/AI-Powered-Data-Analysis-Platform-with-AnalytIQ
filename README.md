

# Data Analysis Web Application

A Flask-based web application that allows users to upload CSV datasets, perform statistical analyses, and visualize results. The app integrates AI capabilities to interpret natural language queries using OpenAI's GPT-4 model.

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Agents Explained](#agents-explained)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Data Upload:** Users can upload CSV files up to 10 MB.
- **Analysis Parameters:** Choose from predefined analysis options or input a natural language query.
- **AI Query Interpretation:** Utilizes OpenAI's GPT-4 model to interpret user queries and determine analysis parameters.
- **Data Processing:** Automated data cleaning and preprocessing.
- **Statistical Analysis:** Generates descriptive statistics, correlation matrices, missing values analysis, and value counts.
- **Data Visualization:** Creates interactive Plotly graphs based on analysis results.
- **Results Presentation:** Displays analysis results, visualizations, and AI interpretations in a user-friendly interface.

## Demo

![Demo Screenshot](demo_screenshot.png)


## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- An OpenAI API key (for AI query interpretation)

### Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your_username/your_repository_name.git
   cd your_repository_name
   ```

2. **Create a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables:**

   Create a `.env` file in the root directory and add the following:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_secret_key
   ```

   Replace `your_openai_api_key` with your actual OpenAI API key and `your_secret_key` with a secret key for Flask sessions.

5. **Run the Application:**

   ```bash
   python app.py
   ```

6. **Access the App:**

   Open your web browser and navigate to `http://localhost:5000`.

## Usage

1. **Upload Dataset:**

   - Click on "Choose CSV File" to upload your dataset.
   - Ensure the file is a valid CSV and less than 10 MB.

2. **Select Analysis Parameters:**

   - Choose the analyses you want to perform by checking the appropriate boxes.
   - Alternatively, enter a natural language query in the "Or ask a question" field.

3. **Styling Parameters:**

   - Optionally, enter any styling preferences for the visualizations.

4. **Run Analysis:**

   - Click the "Analyze" button to perform the analysis.

5. **View Results:**

   - After processing, you will be presented with the analysis results, visualizations, and AI interpretation.

6. **Perform Another Analysis:**

   - Click on the "Perform Another Analysis" button to start over.

## Project Structure

```
├── app.py
├── agents.py
├── templates
│   ├── index.html
│   └── analysis.html
├── static
│   └── css
│       └── styles.css
├── requirements.txt
├── README.md
└── .env  # Should not be checked into version control
```

- **app.py:** Main Flask application file.
- **agents.py:** Contains the agent classes for data processing, preprocessing, analysis, and visualization.
- **templates:** HTML templates for rendering pages.
- **static:** Static files like CSS and images.
- **requirements.txt:** Python dependencies.
- **.env:** Environment variables (should be excluded from version control).

## Agents Explained

### DataProcessingAgent

- **Role:** Cleans the dataset by removing duplicates and performing initial data cleaning steps.
- **Automation:** Uses pandas functions to automate data cleaning.

### PreprocessingAgent

- **Role:** Preprocesses the data by handling missing values, converting data types, and preparing the data for analysis.
- **Automation:** Automates data preprocessing using standard techniques.

### AnalysisAgent

- **Role:** Performs statistical analyses based on specified parameters.
- **Automation:** Computes statistics like mean, median, correlation, etc., using pandas and numpy.

### VisualizationAgent

- **Role:** Generates visualizations from the analysis results.
- **Automation:** Creates charts and graphs using Plotly based on the data.

### AI Integration

- **Function:** The `interpret_query` function uses OpenAI's GPT-3.5-turbo model to interpret natural language queries.
- **AI Component:** Allows the application to understand and process user queries, mapping them to specific analysis actions.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes with clear messages.
4. Push your changes to your fork.
5. Submit a pull request.

## License

This project is licensed under the MIT License.

