import yfinance as yf


def get_raw_data(ticker):
    """
    Retorna dados brutos do Yahoo Finance.
    Ticker deve ser passado sem .SA (ex: PETR4)
    """
    ticker = f"{ticker}.SA"
    t = yf.Ticker(ticker)

    price = None
    try:
        hist = t.history(period="1d")
        if not hist.empty:
            price = float(hist["Close"].iloc[-1])
    except Exception:
        price = None

    return {
        "price": price,
        "info": t.info or {},
        "income": t.financials,
        "balance": t.balance_sheet,
        "cashflow": t.cashflow,
        "dividends": t.dividends
    }
