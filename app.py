import os

from flask import Flask, render_template, request, redirect, url_for
import pickle
import requests
import csv
from datetime import datetime 

# -------------------------
# Load your trained pipeline model
# -------------------------
model = pickle.load(open("model.pkl", "rb"))

# Your NewsAPI key as string
NEWSAPI_KEY = "pub_f0a3a4f603f4482f82c5f71d5473cbd5"

app = Flask(__name__)

# -------------------------
# Function to check headline with NewsAPI
# -------------------------
def check_news_api(headline):
    url = f"https://newsapi.org/v2/everything?q={headline}&apiKey={NEWSAPI_KEY}"
    try:
        response = requests.get(url).json()
        articles = response.get("articles")
        if articles and len(articles) > 0:
            return "Real News (Verified via API) ✅"
        else:
            # fallback to ML prediction
            prediction = model.predict([headline])[0]
            return "Fake News ❌" if prediction == 0 else "Real News ✅"
    except:
        # fallback to ML if API fails
        prediction = model.predict([headline])[0]
        return "Fake News ❌" if prediction == 0 else "Real News ✅"

# -------------------------
# Home route
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------
# Prediction route
# -------------------------
@app.route("/predict", methods=["POST"])
def predict():
    text = request.form["news"]
    result = check_news_api(text)
    return render_template("index.html", result=result)

# -------------------------
# About page route
# -------------------------
@app.route("/about")
def about():
    return render_template("about.html")

# -------------------------
# Contact page route
# -------------------------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to CSV
        with open("messages.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, name, email, message])

        return redirect(url_for("home"))

    return render_template("contact.html")

# -------------------------
# Run the app
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

