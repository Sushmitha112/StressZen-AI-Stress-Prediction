# StressZen – AI Stress Prediction System

StressZen is a full-stack machine learning web application that predicts student stress levels based on lifestyle and behavioral factors. The system collects user inputs through an interactive questionnaire and uses a trained ML model to estimate stress levels.

## Features

* Interactive stress assessment questionnaire
* Machine learning based stress prediction
* Visualization of stress score using Chart.js
* Stress level classification (Low / Moderate / High)
* User authentication system (Login & Register)
* Prediction history storage using SQLite
* Downloadable stress assessment PDF report

## Technologies Used

* Python
* Flask
* Scikit-learn
* HTML, CSS, JavaScript
* Bootstrap
* Chart.js
* SQLite

## Project Structure

```
StressZen
│
├── app.py
├── wearable_stress_model.pkl
├── create_db.py
├── templates/
├── static/
├── updated_dataset.csv
├── mental1.ipynb
└── .gitignore
```

## How to Run the Project

1. Clone the repository

```
git clone https://github.com/Sushmitha112/StressZen-AI-Stress-Prediction.git
```

2. Navigate to the project folder

```
cd StressZen-AI-Stress-Prediction
```

3. Install required libraries

```
pip install flask pandas scikit-learn reportlab
```

4. Run the Flask application

```
python app.py
```

5. Open in browser

```
http://127.0.0.1:5000
```

## Disclaimer

This system provides an AI-based stress estimation and is not a medical diagnosis. For mental health concerns please consult a qualified healthcare professional.

## Author

Sushmitha
