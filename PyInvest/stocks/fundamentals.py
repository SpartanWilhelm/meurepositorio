import pandas as pd


def media_5a(df, indicador):
    """
    Calcula média dos últimos 5 anos ignorando valores inválidos
    """
    try:
        valores = df.loc[indicador, ["2024", "2023", "2022", "2021", "2020"]]
        valores = pd.to_numeric(valores, errors="coerce")
        return round(valores.mean(), 2)
    except Exception:
        return None


def calcular_fundamentos_csv(df):
    def val(ind):
        try:
            v = df.loc[ind, "Atual"]
            return float(v) if pd.notna(v) else None
        except Exception:
            return None

    fundamentos = {
        "pl": val("PL"),
        "pl_medio": media_5a(df, "PL"),
        "dy": val("DY"),
        "dy_medio": media_5a(df, "DY"),
        "payout": val("PAYOUT"),
        "roe": val("ROE"),
        "roic": val("ROIC"),
        "divida_ebitda": val("DIV_LIQ_EBITDA"),
        "anos_dividendos": int(
            pd.to_numeric(
                df.loc["DY", ["2024", "2023", "2022", "2021", "2020"]],
                errors="coerce"
            ).count()
        )
    }

    return fundamentos
