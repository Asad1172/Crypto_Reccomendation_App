from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googlesearch import search  # Alternative to Twitter API
from newspaper import Article  # Extracts text from news articles
import numpy as np
from sklearn.linear_model import LinearRegression

# --- Mapping CoinGecko IDs to CoinMarketCap Symbols ---
ID_TO_SYMBOL = {
    # 🔵 Low Risk Coins (Large Cap)
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "tether": "USDT",
    "binancecoin": "BNB",
    "solana": "SOL",
    "ripple": "XRP",
    "usd-coin": "USDC",
    "staked-ether": "STETH",
    "dogecoin": "DOGE",
    "cardano": "ADA",
    "avalanche-2": "AVAX",
    "tron": "TRX",
    "wrapped-bitcoin": "WBTC",
    "polkadot": "DOT",
    "chainlink": "LINK",
    "toncoin": "TON",
    "matic-network": "MATIC",
    "litecoin": "LTC",
    "internet-computer": "ICP",
    "dai": "DAI",
    
    # 🟠 Medium Risk Coins (Mid Cap)
    "stellar": "XLM",
    "aptos": "APT",
    "vechain": "VET",
    "filecoin": "FIL",
    "lido-dao": "LDO",
    "arbitrum": "ARB",
    "cosmos": "ATOM",
    "immutable-x": "IMX",
    "okb": "OKB",
    "hedera-hashgraph": "HBAR",
    "render-token": "RNDR",
    "the-graph": "GRT",
    "quant-network": "QNT",
    "maker": "MKR",
    "kaspa": "KAS",
    "injective-protocol": "INJ",
    "aave": "AAVE",
    "algorand": "ALGO",
    "rocket-pool": "RPL",
    "bitget-token": "BGB",
    
    # 🔴 High Risk Coins (Small Cap)
    "pepe": "PEPE",
    "floki": "FLOKI",
    "gala": "GALA",
    "fantom": "FTM",
    "theta-token": "THETA",
    "optimism": "OP",
    "pancakeswap-token": "CAKE",
    "mina-protocol": "MINA",
    "iota": "MIOTA",
    "sui": "SUI",
    "kava": "KAVA",
    "zilliqa": "ZIL",
    "oasis-network": "ROSE",
    "chiliz": "CHZ",
    "curve-dao-token": "CRV",
    "convex-finance": "CVX",
    "frax-share": "FXS",
    "radix": "XRD",
    "threshold": "T",
    "celo": "CELO",
    # --- Manual Mappings for Missing Coins ---
    "paypal-usd": "PYUSD",
    "raydium": "RAY",
    "binance-bridged-usdc-bnb-smart-chain": "USDC",
    "wrapped-bnb": "WBNB",
    "rocket-pool-eth": "RETH",
    "kucoin": "KCS",
    "flare": "FLR",
    "toncoin": "TON",
    "usds": "USDS",
    "bitcoin-cash": "BCH",
    "pi-network": "PI",
    "whitebit-coin": "WBT",
    "coinbase-wrapped-btc": "CBETH",
    "bittensor": "TAO",
    "ondo-finance": "ONDO",
    "official-trump": "TRUMP",
    "gate": "GT",
    "tokenize-xchange": "TKX",
    "fasttoken": "FTN",
    "celestia": "TIA",
    "sonic": "SONIC",
    "bonk": "BONK",
    "worldcoin": "WLD",
    "first-digital-usd": "FDUSD",
    "nexo": "NEXO",
    "sei": "SEI",
    # --- Additional mappings ---
    "leo-token": "LEO",
    "cronos": "CRO",
    "xdc-network": "XDC",
    "shiba-inu": "SHIB",
    "wrapped-steth": "WSTETH",
    "weth": "WETH",
    "ethena-usde": "USDE",
    "wrapped-eeth": "WEETH",
    "near": "NEAR",
    "ethereum-classic": "ETC",
    "ethena-staked-usde": "SUSDE",
    "ethena": "ETHENA",
    "solv-protocol-solvbtc": "SOLV",
    "jupiter-exchange-solana": "JUP",
    "binance-staked-sol": "BSOL",
    "binance-peg-ethereum-token": "WETH",
    "kelp-dao-restaked-eth": "RESTETH",
    "monero": "XMR",
    "uniswap": "UNI",
    "artificial-superintelligence-alliance": "ASI"
}
# --- Mapping CoinGecko IDs to CoinMarketCap IDs ---
ID_TO_CMC_ID = {
    # 🔵 Low Risk Coins (Large Cap)
    "bitcoin": 1,
    "ethereum": 1027,
    "tether": 825,
    "binancecoin": 1839,
    "solana": 5426,
    "ripple": 52,
    "usd-coin": 3408,
    "staked-ether": 8085,
    "dogecoin": 74,
    "cardano": 2010,
    "avalanche-2": 5805,
    "tron": 1958,
    "wrapped-bitcoin": 3717,
    "polkadot": 6636,
    "chainlink": 1975,
    "toncoin": 11419,
    "matic-network": 3890,
    "litecoin": 2,
    "internet-computer": 8916,
    "dai": 4943,

    # 🟠 Medium Risk Coins (Mid Cap)
    "stellar": 512,
    "aptos": 21794,
    "vechain": 3077,
    "filecoin": 2280,
    "lido-dao": 8000,
    "arbitrum": 11841,
    "cosmos": 3794,
    "immutable-x": 10603,
    "okb": 3897,
    "hedera-hashgraph": 4642,
    "render-token": 5690,
    "the-graph": 6719,
    "quant-network": 3155,
    "maker": 1518,
    "kaspa": 20396,
    "injective-protocol": 7226,
    "aave": 7278,
    "algorand": 4030,
    "rocket-pool": 11474,
    "bitget-token": 8335,

    # 🔴 High Risk Coins (Small Cap)
    "pepe": 24478,
    "floki": 9025,
    "gala": 7080,
    "fantom": 3513,
    "theta-token": 2416,
    "optimism": 11840,
    "pancakeswap-token": 7186,
    "mina-protocol": 8646,
    "iota": 1720,
    "sui": 23095,
    "kava": 4846,
    "zilliqa": 2469,
    "oasis-network": 7224,
    "chiliz": 4066,
    "curve-dao-token": 6538,
    "convex-finance": 9903,
    "frax-share": 6952,
    "radix": 7692,
    "threshold": 11156,
    "celo": 5567
}
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

#
# News sentiment cache (24 hours)
_news_sentiment_cache = None
_news_sentiment_cache_timestamp = 0
CACHE_EXPIRATION = 86400  # Cache valid for 86400 seconds (24 hours)

def fetch_bitcoin_news_sentiment():
    global _news_sentiment_cache, _news_sentiment_cache_timestamp
    #  Return cached data if it's still valid
    if _news_sentiment_cache and (time.time() - _news_sentiment_cache_timestamp < CACHE_EXPIRATION):
        print("🔄 Using cached news sentiment data.")
        return _news_sentiment_cache

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
        _news_sentiment_cache = (pos_percent, neu_percent, neg_percent)
        _news_sentiment_cache_timestamp = time.time()

        print("\n📊 UPDATED SENTIMENT ANALYSIS:")
        print(f" Positive: {pos_percent}%")
        print(f" Neutral: {neu_percent}%")
        print(f"Negative: {neg_percent}%")

        return pos_percent, neu_percent, neg_percent

    except Exception as e:
        print(f" ERROR FETCHING NEWS SENTIMENT: {e}")
        return _news_sentiment_cache if _news_sentiment_cache else (0, 0, 0)


import os
from dotenv import load_dotenv

load_dotenv()

# --- CryptoCompare API for historical prices ---
CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY")
CRYPTOCOMPARE_HISTORICAL_URL = "https://min-api.cryptocompare.com/data/v2/histoday"


def fetch_historical_prices_from_cryptocompare(coin_symbol, days=30):
    """
    Fetches historical daily closing prices for the last `days` days using CryptoCompare API.
    """
    now = time.time()
    cached = _historical_cache.get(coin_symbol)
    if cached:
        cached_time, cached_data = cached
        if now - cached_time < _HIST_TTL:
            print(f"🔄 Using cached historical data for {coin_symbol}")
            return cached_data

    headers = {
        "Authorization": f"Apikey {CRYPTOCOMPARE_API_KEY}",
    }

    params = {
        "fsym": coin_symbol.upper(),
        "tsym": "USD",
        "limit": days - 1  # 30 days = 29 intervals
    }

    try:
        response = requests.get(CRYPTOCOMPARE_HISTORICAL_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if "Data" in data and "Data" in data["Data"]:
            prices = [[entry["time"], entry["close"]] for entry in data["Data"]["Data"]]

            _historical_cache[coin_symbol] = (now, prices)
            return prices
        else:
            print(f"⚠️ Unexpected response from CryptoCompare for {coin_symbol}: {data}")
            return []
    except Exception as e:
        print(f"Error fetching historical prices for {coin_symbol} from CryptoCompare: {e}")
        return []


def fetch_historical_prices_from_coingecko(coin_id, days=30):
    """
    Fetches historical daily closing prices for the last `days` days using CoinGecko API.
    """
    now = time.time()
    cached = _historical_cache.get(coin_id)
    if cached:
        cached_time, cached_data = cached
        if now - cached_time < _HIST_TTL:
            print(f"🔄 Using cached historical data for {coin_id} from CoinGecko")
            return cached_data

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "prices" in data:
            prices = data["prices"]
            _historical_cache[coin_id] = (now, prices)
            return prices
        else:
            print(f"⚠️ Unexpected response from CoinGecko for {coin_id}: {data}")
            return []
    except Exception as e:
        print(f"Error fetching historical prices for {coin_id} from CoinGecko: {e}")
        return []


# --- Predict 30-day ROI using Linear Regression ---
def predict_30_day_roi(coin_symbol):
    """
    Fetches the last 30 days of historical prices, trains a Linear Regression model,
    predicts the price 30 days into the future, and calculates the predicted ROI.
    Attempts CryptoCompare first; if that fails, falls back to CoinGecko using ID_TO_SYMBOL mapping.
    """
    historical_data = fetch_historical_prices_from_cryptocompare(coin_symbol)
    if not historical_data or len(historical_data) < 2:
        # Try fallback: CoinGecko using Coin ID
        for coingecko_id, symbol in ID_TO_SYMBOL.items():
            if symbol.lower() == coin_symbol.lower():
                historical_data = fetch_historical_prices_from_coingecko(coingecko_id)
                break
        if not historical_data or len(historical_data) < 2:
            return None  # Still not enough data

    days = np.array([i for i in range(len(historical_data))]).reshape(-1, 1)
    prices = np.array([price[1] for price in historical_data]).reshape(-1, 1)

    model = LinearRegression()
    model.fit(days, prices)

    future_day = np.array([[len(historical_data) + 30]])
    predicted_price = model.predict(future_day)[0][0]
    current_price = prices[-1][0]

    predicted_roi = ((predicted_price - current_price) / current_price) * 100
    return predicted_roi
