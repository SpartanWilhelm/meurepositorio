import re
import time
import pyperclip
import configparser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# =========================
# CONFIG
# =========================
INI_FILE = "stocks.ini"
TEMP_TXT = "temp.txt"

MAPA_INDICADORES = {
    "P/L": "PL",
    "P/RECEITA (PSR)": "PSR",
    "P/VP": "PVP",
    "DIVIDEND YIELD (DY)": "DY",
    "PAYOUT": "PAYOUT",
    "MARGEM LÍQUIDA": "MARGEM_LIQ",
    "MARGEM BRUTA": "MARGEM_BRUTA",
    "MARGEM EBIT": "MARGEM_EBIT",
    "MARGEM EBITDA": "MARGEM_EBITDA",
    "EV/EBITDA": "EV_EBITDA",
    "EV/EBIT": "EV_EBIT",
    "P/EBITDA": "P_EBITDA",
    "P/EBIT": "P_EBIT",
    "P/ATIVO": "P_ATIVO",
    "P/CAP.GIRO": "P_CAP_GIRO",
    "P/ATIVO CIRC LIQ": "P_ATIVO_CIRC_LIQ",
    "VPA": "VPA",
    "LPA": "LPA",
    "GIRO ATIVOS": "GIRO_ATIVOS",
    "ROE": "ROE",
    "ROIC": "ROIC",
    "ROA": "ROA",
    "DÍVIDA LÍQUIDA / PATRIMÔNIO": "DIV_LIQ_PATR",
    "DÍVIDA LÍQUIDA / EBITDA": "DIV_LIQ_EBITDA",
    "DÍVIDA LÍQUIDA / EBIT": "DIV_LIQ_EBIT",
    "DÍVIDA BRUTA / PATRIMÔNIO": "DIV_BRUTA_PATR",
    "PATRIMÔNIO / ATIVOS": "PATR_ATIVOS",
    "PASSIVOS / ATIVOS": "PASSIVOS_ATIVOS",
    "LIQUIDEZ CORRENTE": "LIQ_CORRENTE",
    "CAGR RECEITAS 5 ANOS": "CAGR_RECEITA_5A",
    "CAGR LUCROS 5 ANOS": "CAGR_LUCRO_5A",
}

# =========================
# HELPERS
# =========================
def normalizar(valor):
    return (
        valor.replace("%", "")
             .replace(".", "")
             .replace(",", ".")
             .strip()
    )

def carregar_tickers_ini():
    config = configparser.ConfigParser()
    config.read(INI_FILE, encoding="utf-8")

    tickers = [
        t.strip().upper()
        for t in config["STOCKS"]["tickers"].splitlines()
        if t.strip()
    ]
    return tickers

# =========================
# MAIN
# =========================
tickers = carregar_tickers_ini()
driver = webdriver.Chrome()

for ticker in tickers:
    print(f"🔎 Processando {ticker}")
    url = f"https://investidor10.com.br/acoes/{ticker.lower()}"
    driver.get(url)
    time.sleep(6)

    body = driver.find_element("tag name", "body")
    body.send_keys(Keys.CONTROL, "a")
    body.send_keys(Keys.CONTROL, "c")
    time.sleep(1)

    with open(TEMP_TXT, "w", encoding="utf-8") as f:
        f.write(pyperclip.paste())

    with open(TEMP_TXT, "r", encoding="utf-8") as f:
        linhas = [l.strip() for l in f.readlines() if l.strip()]

    try:
        ini = next(i for i,l in enumerate(linhas)
                   if "HISTÓRICO DE INDICADORES FUNDAMENTALISTAS" in l)
        fim = next(i for i,l in enumerate(linhas[ini:], start=ini)
                   if "Já tem" in l)
    except StopIteration:
        print(f"⚠️ Histórico não encontrado para {ticker}")
        continue

    bloco = linhas[ini:fim]
    dados = {}

    i = 0
    while i < len(bloco) - 1:
        linha = bloco[i].upper()
        for nome_site, nome_csv in MAPA_INDICADORES.items():
            if nome_site in linha:
                prox = bloco[i + 1]
                valores = re.findall(r"-?\d+,\d+%?", prox)
                valores = [normalizar(v) for v in valores]

                if len(valores) >= 2:
                    while len(valores) < 6:
                        valores.append("")
                    dados[nome_csv] = valores[:6]
                break
        i += 1

    csv_out = f"{ticker}.csv"
    with open(csv_out, "w", encoding="utf-8") as f:
        f.write("Indicador;Atual;2024;2023;2022;2021;2020\n")
        for ind, vals in dados.items():
            f.write(ind + ";" + ";".join(vals) + "\n")

    print(f"✅ CSV gerado: {csv_out}")

driver.quit()
print("🚀 Processo finalizado")
