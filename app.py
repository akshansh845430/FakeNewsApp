import os
from flask import Flask, render_template, request, redirect, url_for
import pickle
import requests
import csv
from datetime import datetime

# -------------------------
# Load ML model
# -------------------------
model = pickle.load(open("model.pkl", "rb"))

NEWSAPI_KEY = "pub_f0a3a4f603f4482f82c5f71d5473cbd5"

app = Flask(__name__)

# -------------------------
# Function: Step 1 → Check News API
# Step 2 → If no match, use ML model
# -------------------------
def analyze_news_headline(headline):
    api_url = f"https://newsapi.org/v2/everything?q={headline}&language=en&apiKey={NEWSAPI_KEY}"

    try:
        response = requests.get(api_url, timeout=5).json()
        articles = response.get("articles", [])

        # --- If NewsAPI found related published news ---
        if len(articles) > 0:
            return {
                "status": "real",
                "source": "API",
                "message": "This headline was found in verified online news sources.",
                "final_label": "Real News (Verified via NewsAPI) ✅"
            }

        # --- Else: Use Machine Learning Model ---
        prediction = model.predict([headline])[0]
        return {
            "status": "real" if prediction == 1 else "fake",
            "source": "ML",
            "message": "Not found in NewsAPI — using trained AI model:",
            "final_label": "Real News (ML Model) 🤖" if prediction == 1 else "Fake News (ML Model) ❌"
        }

    except Exception:
        # If API fails, fallback to ML prediction only
        prediction = model.predict([headline])[0]
        return {
            "status": "real" if prediction == 1 else "fake",
            "source": "ML-Fallback",
            "message": "Couldn't connect to NewsAPI — using ML fallback:",
            "final_label": "Real News (ML Model Fallback) 🤖" if prediction == 1 else "Fake News (ML Model Fallback) ❌"
        }



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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("messages.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, name, email, message])

        return redirect(url_for("home"))

    return render_template("contact.html")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
