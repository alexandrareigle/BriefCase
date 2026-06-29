import yfinance as yf

tickers={
    "10-Year Treasury": "^TNX",
    "2-Year Treasury": "^IRX",
    "S&P 500": "^GSPC",
    "VIX": "^VIX",
    "Gold": "GC=F",
    "Crude Oil": "CL=F",
    "Dollar Index": "DX-Y.NYB"
}

for name, ticker in tickers.items():
    try:
        hist=yf.Ticker(ticker).history(period="5d")
        if not hist.empty:
            print(f"{name} : ${hist['Close'].iloc[-1]:.2f}")
        else:
            print(f' {name}: Empty data')
    except Exception as e:
        print(f' {name}: {str(e)}')