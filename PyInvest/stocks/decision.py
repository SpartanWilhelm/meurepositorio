from stocks.data.sectors import SETORES


def score_barsi(fund, ticker):
    score = 0
    setor = SETORES.get(ticker, "outros")

    # 1️⃣ DY atual > DY médio
    if fund["dy"] and fund["dy_medio"] and fund["dy"] > fund["dy_medio"]:
        score += 2

    # 2️⃣ P/L atual < P/L médio
    if fund["pl"] and fund["pl_medio"] and fund["pl"] < fund["pl_medio"]:
        score += 2

    # 3️⃣ Qualidade
    if (fund["roe"] and fund["roe"] > 0.15) or (fund["roic"] and fund["roic"] > 0.15):
        score += 2

    # 4️⃣ Dívida controlada
    if fund["divida_ebitda"] is not None and fund["divida_ebitda"] < 3:
        score += 2

    # 5️⃣ Histórico de dividendos
    if fund["anos_dividendos"] >= 5:
        score += 2

    # 🔧 AJUSTES CONCEITUAIS

    # Penalidade commodities
    if setor == "commodity":
        score -= 2

    # Bônus previsibilidade
    if setor in ["energia", "banco", "seguro"]:
        score += 1

    # Payout excessivo (exceto seguradoras)
    if fund["payout"] and fund["payout"] > 0.9 and setor != "seguro":
        score -= 1

    # ROIC negativo
    if fund["roic"] is not None and fund["roic"] < 0:
        score -= 1

    return max(0, min(score, 10))


def status_final(score):
    if score >= 8:
        return "🟢 Comprar"
    elif score >= 6:
        return "🟡 Comprar aos poucos"
    else:
        return "🔴 Aguardar"
