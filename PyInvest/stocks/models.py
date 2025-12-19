from database import db

class UserStock(db.Model):
    __tablename__ = "user_stock"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey("user.id"), nullable=False)
    ticker = db.Column(db.String(20), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "ticker", name="uix_user_ticker"),
    )