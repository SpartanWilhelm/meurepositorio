from flask import Blueprint, render_template
from flask_login import login_required
import yfinance as yf
import configparser
from stocks.score import calcular_score

stocks_bp = Blueprint("stocks", __name__)

@stocks_bp.route("/")
@login_required
def dashboard():
    config = configparser.ConfigParser()
    config.read("config.ini")

    resultados = []

    for t in config["STOCKS"]["tickers"].split(","):
        info = yf.Ticker(t.strip()).info
        score = calcular_score(info)

        resultados.append({
            "ticker": t,
            "price": info.get("currentPrice"),
            "score": score,
            "status": (
                "Excelente" if score >= 75 else
                "Boa" if score >= 50 else
                "Fraca"
            )
        })

    resultados.sort(key=lambda x: x["score"], reverse=True)

    return render_template("dashboard.html", stocks=resultados)
