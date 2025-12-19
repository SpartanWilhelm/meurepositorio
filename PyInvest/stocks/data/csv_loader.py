import pandas as pd
from pathlib import Path

BASE_PATH = Path("stocks/data/stocks")


def list_available_tickers():
    """
    Retorna lista de tickers com CSV disponível
    Ex: ["PETR4", "VALE3"]
    """
    return [p.stem for p in BASE_PATH.glob("*.csv")]


def load_stock_csv(ticker):
    path = BASE_PATH / f"{ticker}.csv"

    df = pd.read_csv(path, sep=";")
    df.set_index("Indicador", inplace=True)

    return df
