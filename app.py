# import re
# from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


# import os
# from flask import Flask, render_template, request, redirect, url_for
# import pickle
# import requests
# import csv
# from datetime import datetime

# # -------------------------
# # Load ML model
# # -------------------------
# model = pickle.load(open("model.pkl", "rb"))

# NEWSAPI_KEY = "036cf1fb384a4f7abd309081805851f8"

# app = Flask(__name__)

# # -------------------------
# # Function: Step 1 → Check News API
# # Step 2 → If no match, use ML model
# # -------------------------

# def analyze_news_headline(headline):
#     cleaned = re.sub(r'[^a-zA-Z ]', '', headline).lower()
#     keywords = [word for word in cleaned.split() if word not in ENGLISH_STOP_WORDS]

#     if not keywords:
#         prediction = model.predict([headline])[0]
#         return f"API: Not enough keywords to query → ML Prediction: {'Real' if prediction == 1 else 'Fake'} 🤖"

#     query = "+".join(keywords[:5])
#     api_url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={NEWSAPI_KEY}"

#     try:
#         response = requests.get(api_url, timeout=5).json()
        
#         if response.get("status") != "ok":
#             prediction = model.predict([headline])[0]
#             return f"API Error: {response.get('message', 'Unknown')} → ML Prediction: {'Real' if prediction == 1 else 'Fake'} 🤖"

#         articles = response.get("articles", [])

#         if len(articles) > 0:
#             return f"API: Found {len(articles)} article(s) → Real News ✅"

#         # API returned 0 articles → fallback to ML
#         prediction = model.predict([headline])[0]
#         return f"API: No articles found → ML Prediction: {'Real' if prediction == 1 else 'Fake'} 🤖"

#     except Exception as e:
#         prediction = model.predict([headline])[0]
#         return f"API Request Failed: {e} → ML Prediction: {'Real' if prediction == 1 else 'Fake'} 🤖"

# # -------------------------
# # Routes
# # -------------------------
# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/predict", methods=["POST"])
# def predict():
#     text = request.form["news"]
#     result_info = analyze_news_headline(text)
#     return render_template("index.html", result=result_info)


# @app.route("/about")
# def about():
#     return render_template("about.html")

# @app.route("/contact", methods=["GET", "POST"])
# def contact():
#     if request.method == "POST":
#         name = request.form.get("name")
#         email = request.form.get("email")
#         message = request.form.get("message")
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         with open("messages.csv", "a", newline="", encoding="utf-8") as f:
#             writer = csv.writer(f)
#             writer.writerow([timestamp, name, email, message])

#         return redirect(url_for("home"))

#     return render_template("contact.html")


# if __name__ == "__main__":
#     app.run(
#         host="0.0.0.0",
#         port=int(os.environ.get("PORT", 5000)),
#         debug=True
#     )











import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import os
from flask import Flask, render_template, request, redirect, url_for
import pickle
import requests
import sqlite3
from datetime import datetime

# -------------------------
# Load ML model
# -------------------------
model = pickle.load(open("model.pkl", "rb"))

NEWSAPI_KEY = "036cf1fb384a4f7abd309081805851f8"

app = Flask(__name__)

# -------------------------
# Initialize SQLite DB
# -------------------------
def init_db():
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            name TEXT,
            email TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Call this once at app startup
init_db()

# -------------------------
# Save message to DB
# -------------------------
def save_message(name, email, message):
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (timestamp, name, email, message) VALUES (?,?,?,?)
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, email, message))
    conn.commit()
    conn.close()

# -------------------------
# Analyze News Headline
# -------------------------
def analyze_news_headline(headline):
    cleaned = re.sub(r'[^a-zA-Z ]', '', headline).lower()
    keywords = [word for word in cleaned.split() if word not in ENGLISH_STOP_WORDS]

    if not keywords:
        prediction = model.predict([headline])[0]
        return f"API: Not enough keywords to query → ML Prediction: {'Real' if prediction == 1 else 'Fake'} 🤖"

    query = "+".join(keywords[:5])
    api_url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={NEWSAPI_KEY}"

    try:
        response = requests.get(api_url, timeout=5).json()
        
        if response.get("status") != "ok":
            prediction = model.predict([headline])[0]
            return f"API Error: {response.get('message', 'Unknown')} → ML Prediction: {'Real' if prediction == 1 else 'Fake'} 🤖"

        articles = response.get("articles", [])

        if len(articles) > 0:
            return f"API: Found {len(articles)} article(s) → Real News ✅"

        # API returned 0 articles → fallback to ML
        prediction = model.predict([headline])[0]
        return f"API: No articles found → ML Prediction: {'Real' if prediction == 1 else 'Fake'} 🤖"

    except Exception as e:
        prediction = model.predict([headline])[0]
        return f"API Request Failed: {e} → ML Prediction: {'Real' if prediction == 1 else 'Fake'} 🤖"

# -------------------------
# Routes
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    text = request.form["news"]
    result_info = analyze_news_headline(text)
    return render_template("index.html", result=result_info)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        save_message(name, email, message)
        return redirect(url_for("home"))

    return render_template("contact.html")

# -------------------------
# Run the app
# -------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
