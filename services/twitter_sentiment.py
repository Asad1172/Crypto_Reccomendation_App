import os
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

load_dotenv()

def fetch_twitter_sentiment(keyword="Bitcoin", max_results=25):
    analyzer = SentimentIntensityAnalyzer()
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        print("❌ Twitter API bearer token not found.")
        return 0, 0, 0

    client = tweepy.Client(bearer_token=bearer_token)

    cache_file = "cached_twitter_sentiment.json"
    today = datetime.utcnow().date()

    # Try to load cached sentiment
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            cached = json.load(f)
            cache_date = datetime.strptime(cached.get("date", ""), "%Y-%m-%d").date()
            if (today - cache_date).days < 7:
                print("✅ Using cached Twitter sentiment.")
                return (
                    cached.get("positive", 0),
                    cached.get("neutral", 0),
                    cached.get("negative", 0),
                )

    # Fetch tweets from the past 7 days
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)

    try:
        response = client.search_recent_tweets(
            query=f"{keyword} lang:en",
            max_results=max_results,
            start_time=start_time.isoformat("T") + "Z",
            tweet_fields=["text", "created_at", "lang"]
        )
        tweets = [tweet.text for tweet in response.data if tweet.lang == "en"] if response.data else []

        sentiment_scores = {"positive": 0, "neutral": 0, "negative": 0}

        for text in tweets:
            score = analyzer.polarity_scores(text)
            compound = score['compound']
            if compound >= 0.1:
                sentiment_scores['positive'] += 1
            elif compound <= -0.05:
                sentiment_scores['negative'] += 1
            else:
                sentiment_scores['neutral'] += 1

        total = sum(sentiment_scores.values())
        if total == 0:
            return 0, 0, 0

        pos = round(sentiment_scores['positive'] / total * 100, 2)
        neu = round(sentiment_scores['neutral'] / total * 100, 2)
        neg = round(sentiment_scores['negative'] / total * 100, 2)

        # Cache the result
        with open(cache_file, "w") as f:
            json.dump({
                "date": today.strftime("%Y-%m-%d"),
                "positive": pos,
                "neutral": neu,
                "negative": neg
            }, f)

        return pos, neu, neg

    except Exception as e:
        print(f"❌ Twitter sentiment fetch failed: {e}")
        return 0, 0, 0