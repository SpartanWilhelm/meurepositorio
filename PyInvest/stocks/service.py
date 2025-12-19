from flask import Blueprint, render_template
from flask_login import login_required, current_user

from stocks.data.csv_loader import list_available_tickers, load_stock_csv
from stocks.data.yahoo import get_raw_data
from stocks.fundamentals import calcular_fundamentos_csv
from stocks.decision import score_barsi, status_final, SETORES
from stocks.indicators import (
    color_pl, color_dy, color_payout,
    color_roe, color_roic, color_divida, color_dividendos
)
from stocks.price_analysis import analisar_preco


stocks_bp = Blueprint("stocks", __name__)


@stocks_bp.route("/")
@login_required
def dashboard():
    resultados = []

    tickers = list_available_tickers()

    for ticker in tickers:
        # -----------------------------
        # Fundamentais (CSV)
        # -----------------------------
        df = load_stock_csv(ticker)
        fund = calcular_fundamentos_csv(df)

        # -----------------------------
        # Preço atual (Yahoo)
        # -----------------------------
        yahoo = get_raw_data(ticker)
        price = yahoo.get("price")

        # -----------------------------
        # Camada 1 — Preço (timing)
        # -----------------------------
        price_info = analisar_preco(ticker)

        # -----------------------------
        # Setor
        # -----------------------------
        setor = SETORES.get(ticker, "outros")
        is_commodity = setor == "commodity"

        # -----------------------------
        # Score Barsi
        # -----------------------------
        score = score_barsi(fund, ticker)
        status = status_final(score)

        # -----------------------------
        # Cores dos indicadores
        # -----------------------------
        colors = {
            "price": price_info["price_color"],
            "pl": color_pl(fund["pl"], fund["pl_medio"]),
            "dy": color_dy(fund["dy"], fund["dy_medio"], is_commodity),
            "payout": color_payout(fund["payout"], setor),
            "roe": color_roe(fund["roe"]),
            "roic": color_roic(fund["roic"]),
            "divida": color_divida(fund["divida_ebitda"], setor),
            "dividendos": color_dividendos(fund["anos_dividendos"]),
        }

        resultados.append({
            "ticker": ticker,
            "price": round(price, 2) if price else None,
            **fund,
            "colors": colors,
            "score": score,
            "status": status
        })

    return render_template(
        "dashboard.html",
        stocks=resultados,
        current_user=current_user
    )
