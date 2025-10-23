# Stack Overflow Question Quality Analysis

## Project Overview
This project analyzes Stack Overflow questions to predict their quality using machine learning techniques. The analysis includes feature engineering, data visualization, and predictive modeling to understand what makes a good quality Stack Overflow question.

## Project Structure
- `stackoverflow_question_quality_analysis.ipynb`: Main Jupyter notebook containing the analysis
- `requirements.txt`: List of Python dependencies
- `train.csv`: Training dataset (not included in repository)
- `valid.csv`: Validation dataset (not included in repository)

## Getting Started

### Prerequisites
- Python 3.x
- Jupyter Notebook

### Installation
1. Clone this repository:
```bash
git clone [repository-url]
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Usage
1. Open the Jupyter notebook:
```bash
jupyter notebook stackoverflow_question_quality_analysis.ipynb
```

2. Make sure to place the required datasets (`train.csv` and `valid.csv`) in the project root directory.

## Features
- Text analysis of question titles and bodies
- Time-based feature engineering
- Tag analysis
- Data visualization using seaborn and matplotlib
- Quality prediction modeling

## Note
The datasets are not included in the repository due to size constraints. Please ensure you have the required CSV files before running the notebook.