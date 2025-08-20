import requests
from bs4 import BeautifulSoup
import yfinance as yf

def yahoo_top_symbols():
    url = "https://finance.yahoo.com/most-active"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "lxml")
    symbols = [a.text for a in soup.select("td[aria-label='Symbol'] a")[:10]]
    return symbols

def marketwatch_trending():
    url = "https://www.marketwatch.com/tools/screener"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "lxml")
    symbols = [a.text for a in soup.select("a") if a.text.isupper() and len(a.text) <= 5][:10]
    return symbols

def build_watchlist(portfolio_symbols=None, max_size=20):
    portfolio_symbols = portfolio_symbols or []
    combined = set(yahoo_top_symbols() + marketwatch_trending() + portfolio_symbols)
    return list(combined)[:max_size]
