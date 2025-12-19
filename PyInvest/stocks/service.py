from flask import Blueprint, render_template
from flask_login import login_required

from stocks.data.csv_loader import list_available_tickers, load_stock_csv
from stocks.data.yahoo import get_raw_data
from stocks.fundamentals import calcular_fundamentos_csv
from stocks.decision import score_barsi, status_final

stocks_bp = Blueprint("stocks", __name__)


@stocks_bp.route("/")
@login_required
def dashboard():
    resultados = []

    tickers = list_available_tickers()

    for ticker in tickers:
        # CSV (fundamentos)
        df = load_stock_csv(ticker)
        fund = calcular_fundamentos_csv(df)

        # Yahoo (preço)
        price = None
        try:
            yahoo = get_raw_data(ticker)
            price = yahoo.get("price")
        except Exception:
            price = None

        score = score_barsi(fund, ticker)
        status = status_final(score)

        resultados.append({
            "ticker": ticker,
            "price": round(price, 2) if price else None,
            **fund,
            "score": score,
            "status": status
        })

    return render_template("dashboard.html", stocks=resultados)
