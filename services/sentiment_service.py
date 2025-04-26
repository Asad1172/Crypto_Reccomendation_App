from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googlesearch import search
from newspaper import Article

def fetch_bitcoin_news_sentiment():
    analyzer = SentimentIntensityAnalyzer()
    query = "Bitcoin news"
    
    try:
        news_urls = list(search(query, num_results=10))
    except:
        return 0, 0, 0

    positive, neutral, negative = 0, 0, 0
    for url in news_urls:
        try:
            article = Article(url)
            article.download()
            article.parse()
            if len(article.text) < 100:
                continue
            sentiment = analyzer.polarity_scores(article.text)
            if sentiment["compound"] > 0.1:
                positive += 1
            elif sentiment["compound"] < -0.05:
                negative += 1
            else:
                neutral += 1
        except:
            pass

    total = positive + neutral + negative
    return (
        round((positive / total) * 100, 2),
        round((neutral / total) * 100, 2),
        round((negative / total) * 100, 2)
    ) if total else (0, 0, 0)
