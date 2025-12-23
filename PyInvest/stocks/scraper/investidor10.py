import re
import time
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

MAPA_INDICADORES = {
    "P/L": "PL",
    "DIVIDEND YIELD (DY)": "DY",
    "PAYOUT": "PAYOUT",
    "ROE": "ROE",
    "ROIC": "ROIC",
    "DÍVIDA LÍQUIDA / EBITDA": "DIVIDA_EBITDA",
}


def _normalizar(valor: str) -> str:
    return (
        valor.replace("%", "")
             .replace(".", "")
             .replace(",", ".")
             .strip()
    )


def scrape_investidor10(tickers: list[str], output_dir: str):
    """
    Faz scraping do Investidor10 e salva CSVs por ticker.
    """
    driver = webdriver.Chrome()

    for ticker in tickers:
        print(f"🔎 Scraping {ticker}")
        url = f"https://investidor10.com.br/acoes/{ticker.lower()}"
        driver.get(url)
        time.sleep(6)

        body = driver.find_element("tag name", "body")
        body.send_keys(Keys.CONTROL, "a")
        body.send_keys(Keys.CONTROL, "c")
        time.sleep(1)

        linhas = [
            l.strip()
            for l in pyperclip.paste().splitlines()
            if l.strip()
        ]

        try:
            ini = next(i for i, l in enumerate(linhas)
                       if "HISTÓRICO DE INDICADORES FUNDAMENTALISTAS" in l)
            fim = next(i for i, l in enumerate(linhas[ini:], start=ini)
                       if "Já tem" in l)
        except StopIteration:
            print(f"⚠️ Histórico não encontrado: {ticker}")
            continue

        bloco = linhas[ini:fim]
        dados = {}

        for i, linha in enumerate(bloco[:-1]):
            for nome_site, nome_csv in MAPA_INDICADORES.items():
                if nome_site in linha.upper():
                    valores = re.findall(r"-?\d+,\d+%?", bloco[i + 1])
                    dados[nome_csv] = [_normalizar(v) for v in valores[:6]]
                    break

        path = f"{output_dir}/{ticker}.csv"
        with open(path, "w", encoding="utf-8") as f:
            f.write("indicador;atual;2024;2023;2022;2021;2020\n")
            for ind, vals in dados.items():
                f.write(ind + ";" + ";".join(vals) + "\n")

        print(f"✅ CSV salvo: {path}")

    driver.quit()
