from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import requests
from openai import OpenAI

app = Flask(__name__)

# Use Sessions
# This is used to store information specific to users, in this case the selected interests
app.secret_key = 'si568'
app.config['SESSION_COOKIE_NAME'] = 'si568-session'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# News Topics of Interests
interests = ["Technology", "Sports", "Politics", "Entertainment", "Finance", "Business", "Health"]

@app.route('/', methods=['GET', 'POST'])
def hello():
    # Handle form submission
    if request.method == 'POST':
        selected_interest = request.form.getlist('interest')
        print("Selected interests: ", selected_interest)
        session["user_interests"] = selected_interest # stores the selected interests in the session
        return redirect(url_for('show_news', interest=selected_interest))

    # Display the form with interests checkboxes
    return render_template('index.html', interests=interests)

# Calling a news API and filtering the results
# https://newsapi.org/v2/everything?q=Apple&from=2024-04-05&sortBy=popularity&apiKey=API_KEY
def fetch_news(interests):
    print("Function started")
    API_KEY = "30adde1a2d9443d88d27dcb76e5fe6db"
    BASE_URL= "https://newsapi.org/v2/everything"
    news_items = []

    for interest in interests:
        params = {
            "q": interest,
            "apiKey": API_KEY,
            "sortBy": "popularity",
            "language": "en",
            "pageSize": 5
        }
        response = requests.get(BASE_URL, params=params)
        print("Response: ", response.json())
        if response.status_code == 200:
            articles = response.json().get("articles", [])[:5]
            for article in articles:
                news_items.append({
                    "title": article["title"],
                    "summary": article["description"],
                    "url": article["url"],
                })
    return news_items

# Summarize News Articles Using OpenAI API
client = OpenAI(base_url="https://openai.vocareum.com/v1", api_key="voc-1599995263104020273543565f0c5c9db1643.85936589")

def summarize_text(text):
    response = (client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful news journalist AI that gives news summaries."},
            {"role": "user", "content": f"Summarize the following news article: {text}. "
                                        f"Do not mention that you are an AI on the news summary. "
                                        f"If there are errors, find some work around with the summary. "
                                        f"Only present newspaper like news summaries."
                                        f"If there is a lack of information or you are unable to create a news summary,"
                                        f"direct the user to click the link for more information."},
        ]
    ))
    return response.choices[0].message.content

@app.route('/news')
def show_news():
    news_items = []
    user_interests = session.get("user_interests", [])
    print("User interests: ", user_interests)
    if not user_interests:
        # When no interests are selected
        print("No user interests")
        # Redirect to the home page
    else:
        print("Fetching news for user interests: ", user_interests)
        raw_news = fetch_news(user_interests)
        news_items = [
            {
                "title": item['title'],
                "summary": summarize_text(item['summary']),
                "url": item['url']
            }
            for item in raw_news[:5]  # limit to top 5 articles just for extra precaution
        ]
        if not raw_news:
            print("No news fetched")
        else:
            summarized_news = []
            for item in raw_news:
                summary = summarize_text(item["summary"])
                summarized_news.append({
                    "title": item["title"],
                    "summary": summary,
                    "url": item["url"]
                })
            news_items = summarized_news
    return render_template('news.html', interests=user_interests, news_items=news_items)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
