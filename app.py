import openai
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import requests
from openai import OpenAI

app = Flask(__name__)

# Use Sessions
# This is used to store information specific to users, in this case the selected interests
app.secret_key = 'si568'

# News Topics of Interests
interests = ["Technology", "Sports", "Politics", "Entertainment"]

@app.route('/', methods=['GET', 'POST'])
def hello():
    # Handle form submission
    if request.method == 'POST':
        selected_interest = request.form.getlist('interest')
        session["user_interests"] = selected_interest # stores the selected interests in the session
        return redirect(url_for('show_news', interest=selected_interest))

    # Display the form with interests checkboxes
    return render_template('index.html', interests=interests)

'''
# To use the stored interests in the session
@app.route('/news')
def show_news():
    # Getting user interests from the session
    user_interests = session.get("user_interests", [])
    # Get and display news based on the selected interests
    return render_template('news.html', interests=user_interests, news_items=news_items)
'''

# Calling a news API and filtering the results
# https://newsapi.org/v2/everything?q=Apple&from=2024-04-05&sortBy=popularity&apiKey=API_KEY
def fetch_news(interests):
    API_KEY = "30adde1a2d9443d88d27dcb76e5fe6db"
    BASE_URL= "https://newsapi.org/v2/everything"
    news_items = []

    for interest in interests:
        params = {
            "q": interest,
            "apiKey": API_KEY,
            "sortBy": "popularity",
            "language": "en"
        }
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            articles = response.json().get("articles")
            for article in articles:
                news_items.append({
                    "title": article["title"],
                    "summary": article["description"],
                    "url": article["url"],
                })
    return news_items

# Summarize News Articles Using OpenAI API

openai.api_key = "voc-1599995263104020273543565f0c5c9db1643.85936589"

def summarize_text(text):
    response = openai.Completion.create(
        enging="text-davinci-003",
        prompt="Summarize this article:" + text,
        max_tokens=150
    )
    return response.choices[0].text.strip()

@app.route('/news')
def show_news():
    user_interests = session.get("user_interests", [])
    raw_news = fetch_news(user_interests)
    summarized_news = []

    for item in raw_news:
        summary = summarize_text(item["summary"])
        summarized_news.append({
            "title": item["title"],
            "summary": summary,
            "url": item["url"]
        })

    return render_template('news.html', interests=user_interests, news_items=summarized_news)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)