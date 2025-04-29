from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.watchlist import Watchlist
from services.crypto_service import fetch_crypto_data
import json
import requests

watchlist_bp = Blueprint("watchlist_bp", __name__)

@watchlist_bp.route("/watchlist")
@login_required
def watchlist():
    entries = Watchlist.query.filter_by(user_id=current_user.id).all()
    watchlist_coins = []

    if entries:
        # Fetch all market coins from CoinGecko
        response = requests.get(
            'https://api.coingecko.com/api/v3/coins/markets',
            params={
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 250,
                'page': 1,
                'price_change_percentage': '24h,30d'
            }
        )
        coins = response.json() if response.ok else []
        coin_map = {coin.get('name', '').lower(): coin for coin in coins if isinstance(coin, dict) and 'name' in coin}

        from services.crypto_service import ID_TO_SYMBOL, predict_30_day_roi

        for entry in entries:
            entry_name = entry.coin_name.lower()
            api_coin = coin_map.get(entry_name)
            if api_coin:
                symbol = ID_TO_SYMBOL.get(api_coin.get('id'))
                if symbol:
                    potential_roi = predict_30_day_roi(symbol)
                    potential_roi = round(potential_roi, 2) if potential_roi is not None else 'N/A'
                else:
                    potential_roi = 'N/A'

                coin_data = {
                    'entry_id': entry.id,
                    'id': api_coin.get('id'),
                    'name': api_coin.get('name'),
                    'current_price': api_coin.get('current_price'),
                    'market_cap': api_coin.get('market_cap'),
                    'price_change_percentage_24h': api_coin.get('price_change_percentage_24h'),
                    'potential_roi': potential_roi
                }
            else:
                coin_data = {
                    'entry_id': entry.id,
                    'id': None,
                    'name': entry.coin_name,
                    'current_price': None,
                    'market_cap': None,
                    'price_change_percentage_24h': None,
                    'potential_roi': None
                }
            watchlist_coins.append(coin_data)

    return render_template("watchlist.html", watchlist_coins=watchlist_coins)

@watchlist_bp.route("/add_to_watchlist", methods=["POST"])
@login_required
def add_to_watchlist():
    coin_name = request.form.get("coin_name")
    if not coin_name:
        flash("No coin name provided.", "error")
        return redirect(request.referrer or url_for("main_routes.index"))

    existing_entry = Watchlist.query.filter_by(user_id=current_user.id, coin_name=coin_name).first()
    if existing_entry:
        flash(f"{coin_name} is already in your watchlist.", "info")
        return redirect(request.referrer or url_for("main_routes.index"))

    new_entry = Watchlist(user_id=current_user.id, coin_name=coin_name)
    db.session.add(new_entry)
    db.session.commit()
    flash(f"{coin_name} added to your watchlist.", "success")
    return redirect(request.referrer or url_for("main_routes.index"))

@watchlist_bp.route("/remove_from_watchlist/<int:coin_id>", methods=["POST"])
@login_required
def remove_from_watchlist(coin_id):
    entry = Watchlist.query.get_or_404(coin_id)
    if entry.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("watchlist_bp.watchlist"))

    db.session.delete(entry)
    db.session.commit()
    flash("Coin removed from your watchlist.", "success")
    return redirect(url_for("watchlist_bp.watchlist"))

@watchlist_bp.route("/remove_from_watchlist_by_name", methods=["POST"])
@login_required
def remove_from_watchlist_by_name():
    coin_name = request.form.get("coin_name")
    if not coin_name:
        return '', 400
    entry = Watchlist.query.filter_by(user_id=current_user.id, coin_name=coin_name).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
    return '', 204
