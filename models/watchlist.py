

from extensions import db  # Adjust this import if your db setup is different

class Watchlist(db.Model):
    __tablename__ = 'watchlist'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    coin_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Watchlist {self.coin_name}>'