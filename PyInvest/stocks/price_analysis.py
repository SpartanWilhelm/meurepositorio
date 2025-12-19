import yfinance as yf
import pandas as pd


def analisar_preco(ticker: str) -> dict:
    try:
        df = yf.download(
            f"{ticker}.SA",
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty or len(df) < 50:
            return {
                "price_color": "neutral",
                "price_status": "indefinido"
            }

        # 🔑 GARANTE SERIES ESCALAR
        close = df["Close"].squeeze()

        preco_atual = float(close.iloc[-1])

        mm50 = float(close.rolling(50).mean().iloc[-1])
        mm200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None

        media_ref = mm200 if mm200 and not pd.isna(mm200) else mm50

        if media_ref is None or pd.isna(media_ref):
            return {
                "price_color": "neutral",
                "price_status": "indefinido"
            }

        # 🎯 Avaliação do momento do preço
        if preco_atual <= media_ref * 0.95:
            return {
                "price_color": "green",
                "price_status": "abaixo da média"
            }

        elif preco_atual <= media_ref * 1.05:
            return {
                "price_color": "yellow",
                "price_status": "na média"
            }

        else:
            return {
                "price_color": "red",
                "price_status": "acima da média"
            }

    except Exception as e:
        print(f"[ERRO PREÇO] {ticker}: {e}")
        return {
            "price_color": "neutral",
            "price_status": "erro"
        }

