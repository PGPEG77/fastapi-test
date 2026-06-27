import yfinance as yf

# Stora bolag på Stockholmsbörsen (Yahoo Finance-ticker)
STOCKS = {
    "Ericsson": "ERIC-B.ST",
    "Volvo": "VOLV-B.ST",
    "H&M": "HM-B.ST",
    "Atlas Copco": "ATCO-A.ST",
    "AstraZeneca": "AZN.ST",
    "Swedbank": "SWED-A.ST",
    "SEB": "SEB-A.ST",
    "Handelsbanken": "SHB-A.ST",
    "Nordea": "NDA-SE.ST",
    "Sandvik": "SAND.ST",
    "ABB": "ABB.ST",
    "Hexagon": "HEXA-B.ST",
    "Investor": "INVE-B.ST",
    "Sinch": "SINCH.ST",
    "Nibe": "NIBE-B.ST",
}

def get_performance():
    results = []
    for name, ticker in STOCKS.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")
            if len(hist) < 2:
                continue

            price_now = hist["Close"].iloc[-1]
            price_1d = hist["Close"].iloc[-2]
            price_1w = hist["Close"].iloc[-6] if len(hist) >= 6 else hist["Close"].iloc[0]
            price_1m = hist["Close"].iloc[0]

            results.append({
                "name": name,
                "ticker": ticker,
                "price": round(price_now, 2),
                "day_pct": round((price_now - price_1d) / price_1d * 100, 2),
                "week_pct": round((price_now - price_1w) / price_1w * 100, 2),
                "month_pct": round((price_now - price_1m) / price_1m * 100, 2),
            })
        except Exception:
            continue

    return sorted(results, key=lambda x: x["month_pct"], reverse=True)