from flask import Flask
from extensions import db, login_manager
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.watchlist import watchlist_bp

def create_app():
    app = Flask(__name__)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///crypto_users.db"
    app.config["SECRET_KEY"] = "supersecretkey"

    db.init_app(app)
    login_manager.init_app(app)

    # Register the blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(watchlist_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
