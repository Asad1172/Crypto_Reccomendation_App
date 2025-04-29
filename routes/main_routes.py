from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services.crypto_service import fetch_crypto_data, fetch_fear_greed_index, fetch_bitcoin_news_sentiment, fetch_historical_prices_from_coingecko, predict_30_day_roi
from services.crypto_service import ID_TO_SYMBOL
from flask_login import login_required
from services.twitter_sentiment import fetch_twitter_sentiment
from models import Watchlist
from flask_login import current_user

#  Define the Blueprint with the correct name
main_bp = Blueprint("main_routes", __name__)

@main_bp.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")

@main_bp.route("/learning", methods=["GET"])
@login_required
def learning():
    return render_template("learning.html")

@main_bp.route("/results", methods=["GET"])
@login_required
def results():
    risk_level = request.args.get("risk_level")
    selected_sector = request.args.get("sector", "all")

    # Validate risk level before proceeding
    if risk_level not in ["high", "medium", "low"]:
        flash("Invalid risk level. Redirecting to the homepage.")
        return redirect(url_for("main_routes.index"))

    # Fetch only the required risk level
    all_data = fetch_crypto_data().get(risk_level, [])

    # Normalize sector names to prevent mismatches
    def normalize_sector(sector_name):
        if not isinstance(sector_name, str) or not sector_name.strip():
            return "other"
        sector = sector_name.strip().lower()
        if "stable" in sector:
            return "stablecoin"
        return sector

    selected_sector_normalized = normalize_sector(selected_sector)
    selected_sector = selected_sector_normalized

    # Filter coins by selected sector
    filtered_data = []
    for coin in all_data:
        raw_sector = coin.get("sector", "")
        coin_sector = normalize_sector(raw_sector)
        if selected_sector_normalized == "all" or coin_sector == selected_sector_normalized:
            filtered_data.append(coin)

    crypto_data = filtered_data

    # For each coin, predict the 30-day ROI and add it to the coin dictionary
    for coin in crypto_data:
        try:
            symbol = ID_TO_SYMBOL.get(coin['id'])  # Correct symbol lookup
            if symbol:
                predicted_roi = predict_30_day_roi(symbol)
            else:
                predicted_roi = None
            coin['potential_roi'] = round(predicted_roi, 2) if predicted_roi is not None else 'N/A'
        except Exception as e:
            print(f"Error predicting ROI for {coin['id']}: {e}")
            coin['potential_roi'] = 'N/A'

    # Rebuild sector dictionary for rendering
    sector_dict = {}
    for coin in crypto_data:
        coin_sector = normalize_sector(coin.get("sector", "Other")).title()
        if coin_sector not in sector_dict:
            sector_dict[coin_sector] = []
        sector_dict[coin_sector].append(coin)

    # Build full sectors list from all_data (before filtering)
    unique_sectors = set()
    for coin in all_data:
        sec = normalize_sector(coin.get("sector", "Other")).title()
        unique_sectors.add(sec)
    sectors = ['all'] + sorted(unique_sectors)

    # If a specific sector was selected, narrow down sector_dict for display
    if selected_sector_normalized != 'all':
        sector_title = selected_sector_normalized.title()
        sector_dict = { sector_title: sector_dict.get(sector_title, []) }

    fear_greed_value, fear_greed_label = fetch_fear_greed_index()
    pos_sent, neu_sent, neg_sent = fetch_bitcoin_news_sentiment()
    twitter_pos, twitter_neu, twitter_neg = fetch_twitter_sentiment("Bitcoin")

    # Fetch the user's current watchlist (coin names only)
    user_watchlist = [entry.coin_name for entry in Watchlist.query.filter_by(user_id=current_user.id).all()]

    return render_template(
        "results.html",
        risk_level=risk_level.capitalize(),
        crypto_data=crypto_data,
        sector_dict=sector_dict,
        fear_greed_value=fear_greed_value,
        fear_greed_label=fear_greed_label,
        pos_sent=pos_sent,
        neu_sent=neu_sent,
        neg_sent=neg_sent,
        twitter_pos=twitter_pos,
        twitter_neu=twitter_neu,
        twitter_neg=twitter_neg,
        selected_sector=selected_sector,
        sectors=sectors,
        user_watchlist=user_watchlist,
    )

@main_bp.route("/chart/<string:coin_id>", methods=["GET"])
@login_required
def chart(coin_id):
    """
    Return JSON time-series price history for the given coin.
    Query param 'days' (int) controls how many past days to fetch (default 30).
    """
    days = request.args.get("days", default=30, type=int)
    data = fetch_historical_prices_from_coingecko(coin_id, days)
    return jsonify(data)
