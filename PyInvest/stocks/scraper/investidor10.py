import requests
from bs4 import BeautifulSoup


def _to_float(text):
    """
    Converte valores brasileiros:
    '14,69%' -> 0.1469
    '5,16'   -> 5.16
    '-%'     -> None
    """
    if not text:
        return None

    text = text.strip()

    if text in ["-%", "-"]:
        return None

    text = text.replace("%", "").replace(".", "").replace(",", ".")

    try:
        return float(text)
    except ValueError:
        return None


def scrape_investidor10(ticker: str) -> dict:
    url = f"https://investidor10.com.br/acoes/{ticker.lower()}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        return {"error": "Falha ao acessar Investidor10"}

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", id="table-indicators-history")
    if not table:
        return {"error": "Tabela não encontrada"}

    data = {}

    for row in table.find_all("tr"):
        indicator_td = row.find("td", class_="indicator")
        value_td = row.find("td", class_="value")

        if not indicator_td or not value_td:
            continue

        name = indicator_td.get_text(strip=True).upper()
        value_text = value_td.get_text(strip=True)

        # Mapeamento dos indicadores que você usa no app
        if "P/L" == name:
            data["pl"] = _to_float(value_text)

        elif "DIVIDEND YIELD" in name:
            data["dy"] = _to_float(value_text)

        elif "PAYOUT" in name:
            data["payout"] = _to_float(value_text) / 100 if value_text else None

        elif name == "ROE":
            data["roe"] = _to_float(value_text) / 100 if value_text else None

        elif name == "ROIC":
            data["roic"] = _to_float(value_text) / 100 if value_text else None

        elif "DÍVIDA LÍQUIDA / EBITDA" in name:
            data["divida_ebitda"] = _to_float(value_text)

    return data
