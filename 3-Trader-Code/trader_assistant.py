import os
import pandas as pd
import yfinance as yf
import feedparser
from newspaper import Article
from alpaca_trade_api import REST
from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

# Load secrets
load_dotenv()
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize clients
alpaca = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# --- Market & news scraping functions ---

def fetch_trending_tickers_yahoo(n=10):
    """Fetch trending tickers from Yahoo Finance."""
    url = "https://finance.yahoo.com/trending-tickers"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    tickers = []
    for row in soup.select("table tr")[1:n+1]:
        cols = row.find_all("td")
        if cols:
            tickers.append(cols[0].text.strip())
    return tickers

def fetch_rss_tickers(feed_urls):
    """Extract tickers mentioned in finance/news RSS feeds."""
    tickers = set()
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:  # top 10 articles
            text = entry.title + " " + entry.get("summary", "")
            # Simple ticker extractor: $ followed by 1-5 uppercase letters
            tickers.update([word[1:] for word in text.split() if word.startswith("$") and word[1:].isupper()])
    return list(tickers)

def fetch_news_articles(tickers, max_articles=3):
    """Scrape headlines/content for tickers."""
    news = []
    for symbol in tickers:
        search_url = f"https://finance.yahoo.com/quote/{symbol}?p={symbol}&.tsrc=fin-srch"
        resp = requests.get(search_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        headlines = [h.get_text() for h in soup.select("h3")]
        news.append({"symbol": symbol, "headlines": headlines[:max_articles]})
    return news

# --- Portfolio functions ---

def get_portfolio_state():
    """Return current Alpaca portfolio and positions."""
    portfolio = alpaca.get_account()
    positions = alpaca.list_positions()
    positions_list = [
        {"symbol": p.symbol, "qty": p.qty, "unrealized_plpc": p.unrealized_plpc}
        for p in positions
    ]
    return {"portfolio_value": portfolio.equity, "positions": positions_list}

# --- Autonomous trading cycle ---

def autonomous_cycle(max_watchlist=20, max_positions=5, notional=1000, dry_run=True):
    """Run one autonomous trading loop."""
    portfolio = get_portfolio_state()
    portfolio_symbols = [p["symbol"] for p in portfolio["positions"]]

    # --- Dynamic watchlist building ---
    yahoo_trending = fetch_trending_tickers_yahoo(n=max_watchlist)
    rss_tickers = fetch_rss_tickers([
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://www.reutersagency.com/feed/?best-topics=business-finance"
    ])
    dynamic_watchlist = list(set(yahoo_trending + rss_tickers + portfolio_symbols))[:max_watchlist]

    # --- Example GPT decision (mock, replace with real GPT call) ---
    plan = []
    for symbol in dynamic_watchlist:
        plan.append({
            "action": "HOLD",
            "symbol": symbol,
            "qty": 0,
            "reasoning": f"No data yet for {symbol}. Holding.",
            "executed": False
        })

    return {"portfolio": portfolio, "watchlist": [{"symbol": s, "reason": "Trending / portfolio"} for s in dynamic_watchlist], "plan": plan}
