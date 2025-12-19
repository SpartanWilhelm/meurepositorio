def calcular_score(info):
    score = 0
    score += 25 if info.get("returnOnEquity", 0) > 0.15 else 0
    score += 25 if info.get("debtToEquity", 200) < 100 else 0
    score += 25 if info.get("profitMargins", 0) > 0.10 else 0
    score += 25 if info.get("earningsGrowth", 0) > 0 else 0
    return score

