from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
import configparser

from database import db
from auth.models import User

login_manager = LoginManager()
migrate = Migrate()   # 👈 SEM app aqui

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def create_app():
    app = Flask(__name__)

    # Config
    config = configparser.ConfigParser()
    config.read("config.ini")

    app.config["SECRET_KEY"] = config["APP"]["secret_key"]
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # 👈 AQUI é o lugar certo

    login_manager.login_view = "auth.login"

    # Blueprints
    from auth.routes import auth_bp
    from stocks.service import stocks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(stocks_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
