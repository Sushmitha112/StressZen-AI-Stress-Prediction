#from reportlab.lib import styles

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pandas as pd
import sqlite3
import joblib
#import email
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # For session management

# Load trained model
model = joblib.load('wearable_stress_model.pkl')

# 👉 Home Page
@app.route('/')
def home():
    return render_template(
        "index.html",
        logged_in=session.get("logged_in", False),
        user_name=session.get("user_name")
    )
# 👉 About Page
@app.route('/about')
def about():
    return render_template('about.html')

# 👉 Login Page (GET + POST)
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email,password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session['logged_in'] = True
            session['user_email'] = email
            session['user_name'] = user[1]   # name column
            return redirect('/')

        else:
            return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')

# 👉 Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
 #registration
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (name,email,password)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            return render_template('register.html', error="Email already registered")

        finally:
            conn.close()

        # 🔹 Auto login after signup
        session['logged_in'] = True
        session['user_email'] = email
        session['user_name'] = name

        return redirect('/')

    return render_template('register.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')


# 👉 Prediction Form Page (requires login)
@app.route('/form')
def form():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('form.html')

# 👉 Predict API (POST request from JS)
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print("Received data:", data)

        age = float(data.get('age', 0))
        gender = int(data.get('gender', 0))
        social_media = float(data.get('social_media', 0))
        exercise = float(data.get('exercise', 0))
        sleep = float(data.get('sleep', 0))
        screen_time = float(data.get('screen_time', 0))
        survey_stress = int(data.get('survey_stress', 0))
        support_system = int(data.get('support_system', 0))
        academic_performance = int(data.get('academic_performance', 0))

        if age < 10 or age > 20:
            return jsonify({'error': 'Invalid age provided.'}), 400

        stress_gap = survey_stress - 0.4

        # Build dataframe with ALL features expected by model
        input_data = pd.DataFrame([{
            'Age': age,
            'Gender': gender,

            # NOTICE THE SPACE BEFORE Social_Media_Hours
            ' Social_Media_Hours': social_media,

            'Exercise_Hours': exercise,
            'Sleep_Hours': sleep,
            'Screen_Time_Hours': screen_time,
            'Survey_Stress_Score': survey_stress,
            'Support_System': support_system,
            'Academic_Performance': academic_performance,
            'Stress_Gap': stress_gap,

            'Anxiety_Symptoms': 0,
            'Diet_Quality': 0,
            'Financial_Stress': 0,
            'Home_Environment': 0,

            'Parental_Pressure': 0,
            'Peer_Pressure': 0,
            'Mood_Rating': 0,
            'Self_Esteem_Score': 0,
            'Relationship_Issues': 0,
            'Time_Management': 0,
            'Sleep_Quality': 0
        }])

        # Ensure correct feature order for the model
        input_data = input_data.reindex(columns=model.feature_names_in_, fill_value=0)

        prediction = model.predict(input_data)[0]

        if prediction < 0.33:
            level = "low"
        elif prediction < 0.66:
            level = "moderate"
        else:
            level = "high"

        if 'user_email' not in session:
            return jsonify({'error': 'User not logged in'}), 401

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO predictions (user_email, stress_score, stress_level)
        VALUES (?, ?, ?)
        """, (session['user_email'], float(prediction), level))

        conn.commit()
        conn.close()

        return jsonify({
            'prediction': round(float(prediction), 4),
            'level': level
        })

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400

@app.route('/history')
def history():

    if not session.get('logged_in'):
        return redirect('/login')

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT stress_score, stress_level, created_at
    FROM predictions
    WHERE user_email=?
    ORDER BY created_at DESC
    """,(session['user_email'],))

    data = cursor.fetchall()

    conn.close()

    return render_template("history.html", data=data)

@app.route('/download_report', methods=['POST'])
def download_report():

    data = request.get_json()
    prediction = data["prediction"]
    level = data["level"]
    answers = data["answers"]

    buffer = io.BytesIO()

    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()

    elements = []

    # StressZen Logo Text
    elements.append(Paragraph(
    "<font size=28 color='#5e72e4'><b>🧠 StressZen</b></font>",
    styles['Title']
    ))

    elements.append(Spacer(1,5))

    elements.append(Paragraph(
    "AI Powered Stress Assessment Report",
    styles['Normal']
    ))
    elements.append(Paragraph(
    f"<font size=10 color='grey'>Generated on {datetime.now().strftime('%d %B %Y')}</font>",
    styles['Normal']
    ))

    elements.append(Spacer(1,20))

    # Prediction result
    elements.append(Paragraph("<b>Stress Prediction Result</b>", styles['Heading2']))
    elements.append(Spacer(1,10))

    result_table = Table([
        ["Stress Score", prediction],
        ["Stress Level", level]
    ])

    result_table.setStyle([
        ("BACKGROUND",(0,0),(1,0),colors.lightblue),
        ("GRID",(0,0),(-1,-1),1,colors.black)
    ])

    elements.append(result_table)
    elements.append(Spacer(1,20))

    # User answers
    elements.append(Paragraph("<b>User Responses</b>", styles['Heading2']))
    elements.append(Spacer(1,10))

    table_data = [["Question","Answer"]]

    for q,a in answers.items():
        table_data.append([q,a])

    table = Table(table_data)

    table.setStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("GRID",(0,0),(-1,-1),1,colors.grey)
    ])

    elements.append(table)
    elements.append(Spacer(1,20))

    # Recommendations
    elements.append(Paragraph("<b>Recommendations</b>", styles['Heading2']))

    if "high" in level:
        recs = [
            "Practice meditation daily",
            "Reduce screen time",
            "Maintain consistent sleep schedule",
            "Seek support from friends or counselor",
            "Engage in physical activity"
        ]
    elif "moderate" in level:
        recs = [
            "Take regular breaks",
            "Exercise regularly",
            "Improve sleep routine",
            "Limit social media",
            "Practice relaxation techniques"
        ]
    else:
        recs = [
            "Maintain healthy lifestyle",
            "Continue regular exercise",
            "Stay socially connected",
            "Practice mindfulness",
            "Maintain balanced digital habits"
        ]

    for r in recs:
        elements.append(Paragraph(f"• {r}", styles['Normal']))
    elements.append(Spacer(1,25))

    elements.append(Paragraph(
    "<b>Disclaimer</b>",
    styles['Heading2']
    ))

    elements.append(Spacer(1,10))

    elements.append(Paragraph(
    "This tool provides AI-based stress estimation and is not a medical diagnosis. "
    "For mental health concerns please consult a qualified healthcare professional.",
    styles['Normal']
    ))
    pdf.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="StressZen_Report.pdf",
        mimetype="application/pdf"
    )
    
# 👉 Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
