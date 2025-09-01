# app.py
# --------------------------
# A simple Flask app that fetches today's news from NewsAPI
# and uses Gemini API to simplify article summaries.
# --------------------------

from flask import Flask, render_template, request, jsonify
import requests
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

# Load API keys from environment variables
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")   # Get this from https://newsapi.org/
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Function to get top headlines from NewsAPI
def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    # Return only first 5 articles to keep UI clean
    return data.get("articles", [])[:5]

# Function to simplify text using Gemini
def simplify_text(article_text):
    model = "gemini-2.5-flash"

    # Gemini content structure
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"Simplify this news article in 2-3 easy to understand sentences:\n\n{article_text}")
            ],
        ),
    ]

    # No need for extra tools in this case
    generate_content_config = types.GenerateContentConfig()

    # Stream the response from Gemini
    simplified_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        simplified_text += chunk.text or ""

    return simplified_text.strip()

# Route: Homepage
@app.route("/")
def home():
    articles = fetch_news()
    return render_template("index.html", articles=articles)

# Route: Simplify endpoint (AJAX call)
@app.route("/simplify", methods=["POST"])
def simplify():
    data = request.json
    article_text = data.get("content", "")
    simplified = simplify_text(article_text)
    return jsonify({"summary": simplified})

if __name__ == "__main__":
    app.run(debug=True)
