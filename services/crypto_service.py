from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googlesearch import search  # Alternative to Twitter API
from newspaper import Article  # Extracts text from news articles

# --- API Endpoints ---
COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"
FEAR_GREED_INDEX_URL = "https://api.alternative.me/fng/"

import requests
import time

_crypto_data_cache = None
_crypto_data_cache_timestamp = 0
_CRYPTO_DATA_TTL = 60  # cache TTL in seconds

# Cache for historical price data: coin_id -> (timestamp, data)
_historical_cache = {}
_HIST_TTL = 86400  # 24 hours in seconds

def fetch_crypto_data():
    global _crypto_data_cache, _crypto_data_cache_timestamp
    if _crypto_data_cache is not None and (time.time() - _crypto_data_cache_timestamp) < _CRYPTO_DATA_TTL:
        print("🔄 Using cached crypto data.")
        return _crypto_data_cache

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "30d"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Define risk levels based on market capitalization
        high_risk = []
        medium_risk = []
        low_risk = []

        # Define keyword-based sector mappings
        sector_keywords = {
            "DeFi": ["uni", "aave", "comp", "curve", "balancer", "sushi", "1inch"],
            "Gaming": ["axs", "mana", "sand", "gala", "enj"],
            "Layer 1": ["eth", "sol", "ada", "dot", "avax", "near", "atom"],
            "Stablecoin": ["tether", "usdt", "usdc", "usd coin", "dai", "busd", "tusd", "usd-coin"],
            "Exchange": ["bnb", "okb", "cro", "ht", "leo"],
            "AI": ["agix", "fet", "ocean", "ali", "nmr"],
            "Privacy": ["monero", "xmr", "zec", "beam", "grin"],
            "Infrastructure": ["link", "graph", "fil", "ar", "icp", "bat"],
            "Meme": ["doge", "shib", "pepe", "floki"],
            "Lending": ["maker", "compound", "aave", "cream"]
        }
        sector_dict = {}

        def assign_sector(coin):
            normalized_id = coin["id"].lower()
            normalized_name = coin["name"].lower()

            # Prioritize specific Stablecoin matches for Tether (USDT) and USDC
            if normalized_id in ["tether", "usdt"] or normalized_name in ["tether", "usdt"]:
                return "Stablecoin"
            if normalized_id in ["usd-coin", "usdc"] or normalized_name in ["usd coin", "usdc"]:
                return "Stablecoin"

            for sector, keywords in sector_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in normalized_id.lower() or keyword.lower() in normalized_name.lower():
                        return sector
            return "Other"

        for coin in data:
            coin["sector"] = assign_sector(coin)
            coin["potential_roi"] = round(coin.get("price_change_percentage_30d_in_currency", 0), 2)
            sector = coin["sector"]
            if sector not in sector_dict:
                sector_dict[sector] = []
            sector_dict[sector].append(coin)
            market_cap = coin.get("market_cap", 0)

            if market_cap >= 10_000_000_000:  # Large-cap coins (safe)
                low_risk.append(coin)
            elif 1_000_000_000 <= market_cap < 10_000_000_000:  # Mid-cap coins
                medium_risk.append(coin)
            else:  # Small-cap coins (high risk)
                high_risk.append(coin)

        result = {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk,
            "sectors": sector_dict
        }
        # cache and return
        _crypto_data_cache = result
        _crypto_data_cache_timestamp = time.time()
        return result
    
    result = {"high": [], "medium": [], "low": [], "sectors": {}}
    _crypto_data_cache = result
    _crypto_data_cache_timestamp = time.time()
    return result  # Fallback now includes 'sectors'


def fetch_fear_greed_index():
    """ Fetches Fear-Greed Index for market sentiment analysis """
    try:
        response = requests.get(FEAR_GREED_INDEX_URL)
        response.raise_for_status()
        data = response.json()
        if "data" in data:
            latest_index = data["data"][0]["value"]
            latest_sentiment = data["data"][0]["value_classification"]
            return int(latest_index), latest_sentiment
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Fear-Greed Index: {e}")
    return None, None

import requests
import time

# Cache storage
cached_news_sentiment = None
cache_timestamp = 0
CACHE_EXPIRATION = 300  # Cache valid for 300 seconds (5 minutes)

def fetch_bitcoin_news_sentiment():
    global cached_news_sentiment, cache_timestamp
    
    #  Return cached data if it's still valid
    if cached_news_sentiment and (time.time() - cache_timestamp < CACHE_EXPIRATION):
        print("🔄 Using cached news sentiment data.")
        return cached_news_sentiment

    url = "https://api.coingecko.com/api/v3/news?page=1"
    
    try:
        response = requests.get(url)
        news_data = response.json()

        #  Check for API rate limit error
        if "status" in news_data and news_data["status"].get("error_code") == 429:
            print(" API Rate Limit Exceeded! Returning cached data.")
            return cached_news_sentiment if cached_news_sentiment else (0, 0, 0)

        if "data" not in news_data or not isinstance(news_data["data"], list):
            print(" API response is missing 'data'. Returning default values.")
            return 0, 0, 0

        positive, neutral, negative = 0, 0, 0
        total_articles = len(news_data["data"])

        if total_articles == 0:
            return 0, 0, 0  # Avoid division errors if API fails

        for article in news_data["data"]:
            title = article["title"].lower()
            description = article.get("description", "").lower()

            combined_text = title + " " + description

            #  Stronger Negative Filtering
            negative_words = ["crash", "scam", "fraud", "sell", "decline", "collapse", "dump", "fear", "manipulation", "bear"]
            positive_words = ["rise", "bullish", "gain", "soar", "adopt", "positive", "growth", "rally"]

            if any(word in combined_text for word in negative_words):
                negative += 1
            elif any(word in combined_text for word in positive_words):
                positive += 1
            else:
                neutral += 1

        # Normalize to percentages
        pos_percent = round((positive / total_articles) * 100, 2)
        neu_percent = round((neutral / total_articles) * 100, 2)
        neg_percent = round((negative / total_articles) * 100, 2)

        #  Cache the result to avoid frequent API calls
        cached_news_sentiment = (pos_percent, neu_percent, neg_percent)
        cache_timestamp = time.time()

        print("\n📊 UPDATED SENTIMENT ANALYSIS:")
        print(f" Positive: {pos_percent}%")
        print(f" Neutral: {neu_percent}%")
        print(f"Negative: {neg_percent}%")

        return pos_percent, neu_percent, neg_percent

    except Exception as e:
        print(f" ERROR FETCHING NEWS SENTIMENT: {e}")
        return cached_news_sentiment if cached_news_sentiment else (0, 0, 0)


# --- New function to fetch historical prices from CoinGecko ---
def fetch_historical_prices(coin_id, days=30):
    """
    Returns a list of [timestamp, price] pairs for the last `days` days from CoinGecko.
    Caches results for _HIST_TTL seconds to avoid rate limits.
    """
    now = time.time()
    # Return cached data if still valid
    cached = _historical_cache.get(coin_id)
    if cached and (now - cached[0] < _HIST_TTL):
        return cached[1]

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    try:
        resp = requests.get(url, params=params)
        # If rate limited, return cached or empty
        if resp.status_code == 429:
            print(f"⚠️ Rate limited fetching historical for {coin_id}, returning cached or empty.")
            return cached[1] if cached else []
        resp.raise_for_status()
        data = resp.json().get("prices", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical for {coin_id}: {e}")
        return cached[1] if cached else []

    # Cache and return
    _historical_cache[coin_id] = (now, data)
    return data
