import requests
import pywhatkit
import datetime
import time

# Dados do usuário
btc_quantidade = float(input("Quantos BTCs você possui? "))
preco_compra = float(input("Qual foi o preço de compra por BTC (em R$)? "))
destino = '+5519994012999'  # substitua pelo seu número com DDD

# Configurações
variacao = 10000  # R$10.000 de variação
intervalo = 60  # 1 minuto
historico_precos = []

def obter_preco():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=brl'
    resposta = requests.get(url)
    return resposta.json()['bitcoin']['brl']

def enviar_alerta(mensagem):
    agora = datetime.datetime.now()
    hora = agora.hour
    minuto = agora.minute + 1
    pywhatkit.sendwhatmsg(destino, mensagem, hora, minuto)
    print("Mensagem agendada:", mensagem)

def verificar_tendencia():
    if len(historico_precos) < 10:
        return False, None

    subidas = 0
    quedas = 0

    for i in range(1, len(historico_precos)):
        if historico_precos[i] > historico_precos[i - 1]:
            subidas += 1
        elif historico_precos[i] < historico_precos[i - 1]:
            quedas += 1

    if subidas >= 8:
        return True, "🔼 Tendência de alta detectada: 8 ou mais subidas consecutivas."
    elif quedas >= 8:
        return True, "🔽 Tendência de queda detectada: 8 ou mais quedas consecutivas."
    else:
        return False, None

def monitorar():
    preco_atual = obter_preco()
    diferenca_inicial = preco_atual - preco_compra
    lucro_inicial = diferenca_inicial * btc_quantidade

    print(f"\n📊 Situação atual:")
    print(f"- Preço atual do BTC: R${preco_atual:.2f}")
    print(f"- Preço de compra: R${preco_compra:.2f}")
    print(f"- Lucro/prejuízo estimado: R${lucro_inicial:.2f}\n")

    alerta_variacao_enviado = False
    alerta_tendencia_enviado = False

    while True:
        preco_atual = obter_preco()
        print(f"Preço atual: R${preco_atual:.2f}")

        historico_precos.append(preco_atual)
        if len(historico_precos) > 10:
            historico_precos.pop(0)

        diferenca = preco_atual - preco_compra
        lucro_total = diferenca * btc_quantidade

        # Alerta por variação de R$10.000
        if not alerta_variacao_enviado:
            if diferenca >= variacao:
                mensagem = (
                    f"🚨 O Bitcoin subiu R${diferenca:.2f} desde sua compra!\n"
                    f"Preço atual: R${preco_atual:.2f}\n"
                    f"Lucro estimado: R${lucro_total:.2f}\n"
                    f"Considere vender."
                )
                enviar_alerta(mensagem)
                alerta_variacao_enviado = True

            elif diferenca <= -variacao:
                mensagem = (
                    f"📉 O Bitcoin caiu R${abs(diferenca):.2f} desde sua compra!\n"
                    f"Preço atual: R${preco_atual:.2f}\n"
                    f"Prejuízo estimado: R${lucro_total:.2f}\n"
                    f"Pode ser hora de comprar."
                )
                enviar_alerta(mensagem)
                alerta_variacao_enviado = True

        # Alerta por tendência
        if not alerta_tendencia_enviado:
            tendencia_detectada, mensagem_tendencia = verificar_tendencia()
            if tendencia_detectada:
                mensagem = (
                    f"{mensagem_tendencia}\n"
                    f"Preço atual: R${preco_atual:.2f}\n"
                    f"Lucro/prejuízo estimado: R${lucro_total:.2f}"
                )
                enviar_alerta(mensagem)
                alerta_tendencia_enviado = True

        time.sleep(intervalo)

monitorar()
