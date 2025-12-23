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
            return {"price_color": "neutral"}

        close = df["Close"]

        preco_atual = float(close.iloc[-1])
        mm50 = float(close.rolling(50).mean().iloc[-1])
        mm200 = (
            float(close.rolling(200).mean().iloc[-1])
            if len(close) >= 200
            else None
        )

        media_ref = mm200 if mm200 and not pd.isna(mm200) else mm50

        if preco_atual < media_ref * 0.95:
            return {"price_color": "green"}
        elif preco_atual <= media_ref * 1.05:
            return {"price_color": "yellow"}
        else:
            return {"price_color": "red"}

    except Exception:
        return {"price_color": "neutral"}
