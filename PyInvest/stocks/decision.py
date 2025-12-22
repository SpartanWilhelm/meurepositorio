from stocks.data.sectors import SETORES


def score_barsi(fund, ticker):
    score = 0
    setor = SETORES.get(ticker, "outros")

    # =========================
    # 1️⃣ Dividend Yield
    # =========================
    if fund.get("dy") and fund.get("dy_medio"):
        if fund["dy"] >= fund["dy_medio"]:
            score += 2
        elif fund["dy"] >= fund["dy_medio"] * 0.8:
            score += 1

    # =========================
    # 2️⃣ P/L vs histórico
    # =========================
    if fund.get("pl") and fund.get("pl_medio"):
        if fund["pl"] <= fund["pl_medio"] * 0.9:
            score += 2
        elif fund["pl"] <= fund["pl_medio"] * 1.1:
            score += 1

    # =========================
    # 3️⃣ Qualidade do negócio
    # =========================
    roe = fund.get("roe")
    roic = fund.get("roic")

    if roe and roe >= 0.15:
        score += 1
    if roic and roic >= 0.12:
        score += 1

    # ROIC negativo é grave
    if roic is not None and roic < 0:
        score -= 2

    # =========================
    # 4️⃣ Dívida
    # =========================
    divida = fund.get("divida_ebitda")
    if divida is not None:
        if divida <= 2.5:
            score += 2
        elif divida <= 3.5:
            score += 1
        else:
            score -= 1

    # =========================
    # 5️⃣ Histórico de dividendos
    # =========================
    anos = fund.get("anos_dividendos", 0)
    if anos >= 10:
        score += 2
    elif anos >= 5:
        score += 1

    # =========================
    # 🔧 AJUSTES CONCEITUAIS
    # =========================

    # Penalidade para commodities
    if setor == "commodity":
        score -= 2

    # Bônus previsibilidade
    if setor in ["energia", "banco", "seguro"]:
        score += 1

    # =========================
    # ❗ Payout (CRÍTICO)
    # =========================
    payout = fund.get("payout")

    if payout is not None:
        # payout acima de 100% → grave
        if payout > 1:
            score -= 3

        # payout muito alto (exceto seguradoras)
        elif payout > 0.9 and setor != "seguro":
            score -= 1

        # payout saudável
        elif 0.3 <= payout <= 0.7:
            score += 1

    # Limite final
    return max(0, min(score, 10))


def status_final(score, fund=None):
    """
    Status final com trava conceitual.
    """

    # 🚨 Trava: payout acima de 100% nunca pode ser 🟢
    if fund and fund.get("payout") is not None and fund["payout"] > 1:
        return "🔴 Aguardar"

    if score >= 8:
        return "🟢 Comprar"
    elif score >= 6:
        return "🟡 Comprar aos poucos"
    else:
        return "🔴 Aguardar"
