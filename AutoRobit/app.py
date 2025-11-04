from flask import Flask, render_template, request
import threading
import requests
import pywhatkit
import datetime
import time
import logging
import socket
import configparser
import matplotlib.pyplot as plt
from babel.numbers import format_currency

app = Flask(__name__)

# Configuração de log
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)


# Leitura do arquivo de configuração
config = configparser.ConfigParser()
config.read('config.ini')

# Dados do usuário (lidos do arquivo)
destino = config.get('usuario', 'telefone')
preco_compra = float(config.get('usuario', 'preco_compra'))
btc_quantidade = float(config.get('usuario', 'btc_quantidade'))

# Configurações
variacao = 10000
intervalo = 60
historico_precos = []
ultimo_preco = None

# Flags e mensagens
alerta_variacao_enviado = False
alerta_tendencia_enviado = False
monitorando = False
mensagem_variacao_html = None
cor_variacao_html = None

def obter_preco():
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=brl'
        resposta = requests.get(url, timeout=10)
        dados = resposta.json()
        return dados['bitcoin']['brl']
    except Exception as e:
        logging.error(f"Erro ao obter preço do BTC: {e}")
        return None

def enviar_alerta(mensagem):
    agora = datetime.datetime.now()
    hora = agora.hour
    minuto = agora.minute + 2
    pywhatkit.sendwhatmsg(destino, mensagem, hora, minuto)
    logging.info(f"Mensagem agendada: {mensagem}")

def verificar_tendencia():
    if len(historico_precos) < 10:
        return False, None

    subidas = sum(historico_precos[i] > historico_precos[i - 1] for i in range(1, len(historico_precos)))
    quedas = sum(historico_precos[i] < historico_precos[i - 1] for i in range(1, len(historico_precos)))

    if subidas >= 8:
        return True, "🔼 Tendência de alta detectada: 8 ou mais subidas consecutivas."
    elif quedas >= 8:
        return True, "🔽 Tendência de queda detectada: 8 ou mais quedas consecutivas."
    return False, None

def estilo_por_tendencia():
    if len(historico_precos) < 2:
        return "black", None

    subidas = sum(historico_precos[i] > historico_precos[i - 1] for i in range(1, len(historico_precos)))
    quedas = sum(historico_precos[i] < historico_precos[i - 1] for i in range(1, len(historico_precos)))

    intensidade = min(max(subidas, quedas), 8)

    if subidas >= quedas and subidas >= 1:
        cor = f"rgb(0,{intensidade * 30},0)"
        mensagem = "🚀 Tendência forte de alta!" if subidas == 8 else None
    elif quedas > subidas and quedas >= 1:
        cor = f"rgb({intensidade * 30},0,0)"
        mensagem = "⚠️ Tendência forte de queda!" if quedas == 8 else None
    else:
        cor = "black"
        mensagem = None

    return cor, mensagem

def monitorar():
    global alerta_variacao_enviado, alerta_tendencia_enviado, monitorando
    global mensagem_variacao_html, cor_variacao_html

    monitorando = True
    logging.info("Monitoramento iniciado.")

    while monitorando:
        preco_atual = obter_preco()
        if preco_atual is None:
            time.sleep(intervalo)
            continue

        historico_precos.append(preco_atual)
        if len(historico_precos) > 10:
            historico_precos.pop(0)

        diferenca = preco_atual - preco_compra
        lucro_total = diferenca * btc_quantidade
        resultado = "💰 Lucro" if lucro_total >= 0 else "📉 Prejuízo"
        valor_formatado = format_currency(abs(lucro_total), 'BRL', locale='pt_BR')

        if not alerta_variacao_enviado:
            if diferenca >= variacao:
                mensagem = (
                    f"🚨 O Bitcoin subiu {format_currency(diferenca, 'BRL', locale='pt_BR')} desde sua compra!\n"
                    f"Preço atual: {format_currency(preco_atual, 'BRL', locale='pt_BR')}\n"
                    f"{resultado} estimado: {valor_formatado}\n"
                    f"Considere vender."
                )
                enviar_alerta(mensagem)
                mensagem_variacao_html = mensagem
                cor_variacao_html = "green"
                alerta_variacao_enviado = True

            elif diferenca <= -variacao:
                mensagem = (
                    f"📉 O Bitcoin caiu {format_currency(abs(diferenca), 'BRL', locale='pt_BR')} desde sua compra!\n"
                    f"Preço atual: {format_currency(preco_atual, 'BRL', locale='pt_BR')}\n"
                    f"{resultado} estimado: {valor_formatado}\n"
                    f"Pode ser hora de comprar."
                )
                enviar_alerta(mensagem)
                mensagem_variacao_html = mensagem
                cor_variacao_html = "red"
                alerta_variacao_enviado = True

        if not alerta_tendencia_enviado:
            tendencia_detectada, mensagem_tendencia = verificar_tendencia()
            if tendencia_detectada:
                mensagem = (
                    f"{mensagem_tendencia}\n"
                    f"Preço atual: {format_currency(preco_atual, 'BRL', locale='pt_BR')}\n"
                    f"{resultado} estimado: {valor_formatado}"
                )
                enviar_alerta(mensagem)
                alerta_tendencia_enviado = True

        time.sleep(intervalo)

import os

def gerar_grafico_variacao():
    try:
        if len(historico_precos) < 2:
            logging.info("Gráfico não gerado: histórico insuficiente.")
            return None

        # Garante que a pasta static existe
        os.makedirs('static', exist_ok=True)

        caminho = os.path.join('static', 'variacao.png')

        plt.figure(figsize=(10, 5))
        plt.plot(historico_precos, marker='o', linestyle='-', color='blue')
        plt.title('Variação do Preço do Bitcoin')
        plt.xlabel('Últimas medições')
        plt.ylabel('Preço (BRL)')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(caminho)
        plt.close()

        logging.info(f"Gráfico gerado com sucesso em: {caminho}")
        return caminho
    except Exception as e:
        logging.error(f"Erro ao gerar gráfico: {e}")
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    preco_atual = obter_preco()
    if preco_atual is None:
        return "Erro ao obter preço do Bitcoin."

    diferenca = preco_atual - preco_compra
    lucro_total = diferenca * btc_quantidade
    resultado = "Lucro" if lucro_total >= 0 else "Prejuízo"
    cor_resultado = "positivo" if lucro_total >= 0 else "negativo"

    if request.method == 'POST' and not monitorando:
        thread = threading.Thread(target=monitorar)
        thread.daemon = True
        thread.start()

    global ultimo_preco
    direcao_preco = "neutro"

    if ultimo_preco is not None:
        if preco_atual > ultimo_preco:
            direcao_preco = "positivo"
        elif preco_atual < ultimo_preco:
            direcao_preco = "negativo"

    ultimo_preco = preco_atual

    cor_tendencia, mensagem_tendencia = estilo_por_tendencia()
    ip_local = socket.gethostbyname(socket.gethostname())
    grafico_path = gerar_grafico_variacao()


    return render_template('index.html',
                           preco=format_currency(preco_atual, 'BRL', locale='pt_BR'),
                           preco_compra=format_currency(preco_compra, 'BRL', locale='pt_BR'),
                           btc=f"{btc_quantidade:.8f}",
                           lucro=format_currency(abs(lucro_total), 'BRL', locale='pt_BR'),
                           resultado=resultado,
                           cor_resultado=cor_resultado,
                           direcao_preco=direcao_preco,
                           ip_local=ip_local,
                           cor_tendencia=cor_tendencia,
                           mensagem_tendencia=mensagem_tendencia,
                           mensagem_variacao=mensagem_variacao_html,
                           cor_variacao=cor_variacao_html,
                           grafico=grafico_path
)

@app.route('/logs')
def logs():
    try:
        with open('log.txt', 'r', encoding='utf-8', errors='replace') as f:
            conteudo = f.read()
        return f"<pre style='white-space: pre-wrap; word-wrap: break-word; background:#111; color:#0f0; padding:20px;'>{conteudo}</pre>"
    except Exception as e:
        return f"Erro ao ler o log: {e}"

if __name__ == '__main__':
    logging.info("Servidor Flask iniciado...")
    app.run(host='0.0.0.0', port=5000, debug=True)
