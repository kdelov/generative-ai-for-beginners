import yfinance as yf
from newspaper import Article
import requests

def get_price(symbol):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    if not data.empty:
        return data['Close'][-1]
    return None

def get_top_news(symbols, n=3):
    news_articles = []
    for symbol in symbols:
        url = f"https://finance.yahoo.com/quote/{symbol}?p={symbol}"
        # Fetch the page
        resp = requests.get(url)
        if resp.status_code == 200:
            news_articles.append(f"{symbol} latest market info")
        # You can expand here to use Newspaper for real article parsing
    return news_articles
