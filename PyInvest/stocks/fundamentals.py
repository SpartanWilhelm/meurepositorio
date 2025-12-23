import pandas as pd
import numpy as np


def _get_value(df, indicador, coluna="Atual"):
    """
    Retorna valor float do indicador na coluna desejada.
    """
    try:
        value = df.loc[indicador, coluna]
        if pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def _get_media(df, indicador, anos=("2024", "2023", "2022", "2021", "2020")):
    """
    Calcula média histórica ignorando NaN.
    """
    try:
        serie = df.loc[indicador, list(anos)]
        serie = pd.to_numeric(serie, errors="coerce")
        if serie.dropna().empty:
            return None
        return float(serie.mean())
    except Exception:
        return None


def calcular_fundamentos_csv(df):
    """
    Lê o CSV exatamente no formato do Investidor10 exportado.
    """

    # Garantia mínima
    df = df.copy()
    df.index = df.index.astype(str).str.strip().str.upper()

    fundamentos = {
        # P/L
        "pl": _get_value(df, "PL"),
        "pl_medio": _get_media(df, "PL"),

        # Dividend Yield
        "dy": _get_value(df, "DY"),
        "dy_medio": _get_media(df, "DY"),

        # Payout
        "payout": _get_value(df, "PAYOUT"),

        # Rentabilidade
        "roe": _get_value(df, "ROE"),
        "roic": _get_value(df, "ROIC"),

        # Dívida / EBITDA
        "divida_ebitda": (
            _get_value(df, "DIVIDA_LIQUIDA_EBITDA")
            or _get_value(df, "DIVIDA_LIQ_EBITDA")
            or _get_value(df, "DÍVIDA LÍQUIDA / EBITDA")
            or _get_value(df, "EV_EBITDA")

        ),

        # Histórico (placeholder simples por enquanto)
        "anos_dividendos": 5,
    }

    # Normalização: tudo que é percentual → decimal
    for key in ["dy", "dy_medio", "payout", "roe", "roic"]:
        if fundamentos[key] is not None:
            fundamentos[key] = fundamentos[key] / 100

    return fundamentos
