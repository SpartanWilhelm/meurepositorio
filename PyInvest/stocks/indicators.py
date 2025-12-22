def color_pl(pl, pl_medio):
    if not pl or not pl_medio:
        return None
    if pl <= 0.9 * pl_medio:
        return "green"
    elif pl <= 1.1 * pl_medio:
        return "yellow"
    return "red"


def color_dy(dy, dy_medio, is_commodity=False):
    if not dy or not dy_medio:
        return None

    if dy >= dy_medio:
        color = "green"
    elif dy >= 0.8 * dy_medio:
        color = "yellow"
    else:
        color = "red"

    # Commodities nunca ficam verde
    if is_commodity and color == "green":
        return "yellow"

    return color


def color_payout(payout, setor=None):
    if not payout:
        return None

    payout *= 100  # trabalhar em %

    if setor == "seguro":
        return "green" if payout <= 95 else "red"

    if 30 <= payout <= 70:
        return "green"
    elif payout <= 90:
        return "yellow"
    return "red"


def color_roe(roe):
    if not roe:
        return None

    roe *= 100

    if roe >= 15:
        return "green"
    elif roe >= 10:
        return "yellow"
    return "red"


def color_roic(roic):
    if not roic:
        return "red"

    roic *= 100

    if roic >= 12:
        return "green"
    elif roic >= 8:
        return "yellow"
    return "red"


def color_divida(divida, setor):
    # Bancos / seguradoras não usam Dívida / EBITDA
    if setor in ["banco", "seguro"]:
        return "neutral"

    if divida is None:
        return "neutral"

    try:
        # Corrige string com vírgula
        if isinstance(divida, str):
            divida = divida.replace(",", ".")
        divida = float(divida)
    except Exception:
        return "neutral"

    if divida <= 2.5:
        return "green"
    elif divida <= 3.5:
        return "yellow"
    else:
        return "red"



def color_dividendos(anos):
    if anos >= 10:
        return "green"
    elif anos >= 5:
        return "yellow"
    return "red"
