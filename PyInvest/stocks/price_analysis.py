import yfinance as yf
import pandas as pd


def analisar_preco(ticker: str) -> dict:
    try:
        df = yf.download(
            f"{ticker}.SA",
            period="1y",
            interval="1d",
            progress=False
        )

        if df.empty or len(df) < 50:
            return {
                "price_status": "indefinido",
                "price_color": "neutral"
            }

        preco_atual = float(df["Close"].iloc[-1])

        # Médias móveis (ESCALARES)
        mm50 = float(df["Close"].rolling(50).mean().iloc[-1])
        mm200 = float(df["Close"].rolling(200).mean().iloc[-1]) if len(df) >= 200 else None

        # Referência principal
        media_ref = mm200 if mm200 is not None else mm50

        if media_ref is None or pd.isna(media_ref):
            return {
                "price_status": "indefinido",
                "price_color": "neutral"
            }

        # Avaliação do momento
        if preco_atual < media_ref * 0.95:
            status = "barato"
            color = "green"
        elif preco_atual <= media_ref * 1.05:
            status = "neutro"
            color = "yellow"
        else:
            status = "caro"
            color = "red"

        return {
            "price_status": status,
            "price_color": color
        }

    except Exception as e:
        print(f"[ERRO PREÇO] {ticker}: {e}")
        return {
            "price_status": "erro",
            "price_color": "neutral"
        }

