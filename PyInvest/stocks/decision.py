from stocks.data.sectors import SETORES


def score_barsi(fund: dict, ticker: str) -> int:
    score = 0
    setor = SETORES.get(ticker, "outros")

    # DY relativo
    if fund["dy"] and fund["dy_medio"] and fund["dy"] >= fund["dy_medio"]:
        score += 2

    # P/L relativo
    if fund["pl"] and fund["pl_medio"] and fund["pl"] <= fund["pl_medio"]:
        score += 2

    # Qualidade
    if fund["roe"] and fund["roe"] >= 0.15:
        score += 2

    if fund["roic"] and fund["roic"] >= 0.12:
        score += 2

    # Dívida
    if fund["divida_ebitda"] is not None and fund["divida_ebitda"] <= 3:
        score += 1

    # Histórico
    if fund["anos_dividendos"] >= 5:
        score += 1

    # Penalidades
    if setor == "commodity":
        score -= 2

    if fund["payout"] and fund["payout"] > 0.9 and setor != "seguro":
        score -= 2

    if fund["roic"] is not None and fund["roic"] < 0:
        score -= 2

    return max(0, min(score, 10))


def status_final(score: int) -> str:
    if score >= 8:
        return "🟢 Comprar"
    elif score >= 6:
        return "🟡 Comprar aos poucos"
    else:
        return "🔴 Aguardar"
