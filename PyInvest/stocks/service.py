from flask import Blueprint, render_template
from flask_login import login_required
import yfinance as yf
import configparser

from stocks.score import calcular_score

stocks_bp = Blueprint("stocks", __name__)

def fmt_percent(valor):
    return f"{valor * 100:.2f}%" if isinstance(valor, (int, float)) else "N/A"

def fmt_number(valor):
    return f"{valor:.2f}" if isinstance(valor, (int, float)) else "N/A"

@stocks_bp.route("/")
@login_required
def dashboard():
    config = configparser.ConfigParser()
    config.read("config.ini")

    resultados = []

    for t in config["STOCKS"]["tickers"].split(","):
        ticker = t.strip()
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        pl = info.get("trailingPE")
        roe = info.get("returnOnEquity")

        score = calcular_score(info)

        resultados.append({
            "ticker": ticker,
            "price": fmt_number(info.get("currentPrice")),
            "pl": fmt_number(pl),
            "roe": fmt_percent(roe),
            "score": score,
            "status": (
                "Excelente" if score >= 75 else
                "Boa" if score >= 50 else
                "Fraca"
            )
        })

    resultados.sort(key=lambda x: x["score"], reverse=True)

    return render_template("dashboard.html", stocks=resultados)
