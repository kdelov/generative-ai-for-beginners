import os
import yfinance as yf
import alpaca_trade_api as tradeapi
from openai import OpenAI
from watchlist_builder import build_watchlist

api = tradeapi.REST(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY"),
    os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_portfolio_state():
    acct = api.get_account()
    positions = api.list_positions()
    return {
        "portfolio_value": acct.portfolio_value,
        "positions": [{"symbol": p.symbol, "qty": p.qty, "unrealized_plpc": p.unrealized_plpc} for p in positions]
    }

def fetch_market_data(symbols):
    data = {}
    for s in symbols:
        try:
            hist = yf.Ticker(s).history(period="5d", interval="1d")
            if not hist.empty:
                last = hist.iloc[-1]
                data[s] = {"close": last["Close"], "volume": last["Volume"]}
        except Exception:
            pass
    return data

def ai_decision(portfolio, market_data, watchlist, max_positions=5, notional=1000):
    instructions = """
    You are an expert trader AI. 
    Based only on the given portfolio and market data:
    - Suggest actions: BUY, SELL, or HOLD
    - Only use symbols from the watchlist
    - Do not exceed the max_positions or per-trade notional
    Return JSON in this format:
    [{"action":"BUY/SELL/HOLD","symbol":"TSLA","qty":1,"reasoning":"..."}]
    """
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role":"system","content":instructions},
            {"role":"user","content":f"Portfolio:{portfolio}\nMarket:{market_data}\nWatchlist:{watchlist}"}
        ],
        response_format={"type":"json_object"}
    )
    return response.choices[0].message.parsed

def execute_plan(plan, dry_run=True):
    results = []
    for step in plan:
        try:
            if dry_run or step["action"]=="HOLD":
                results.append({"executed":False, **step})
                continue
            api.submit_order(
                symbol=step["symbol"],
                qty=step["qty"],
                side="buy" if step["action"]=="BUY" else "sell",
                type="market",
                time_in_force="gtc"
            )
            results.append({"executed":True, **step})
        except Exception as e:
            results.append({"executed":False, "error":str(e), **step})
    return results

def autonomous_cycle(max_watchlist=20, max_positions=5, notional=1000, dry_run=True):
    portfolio = get_portfolio_state()
    watchlist = build_watchlist([p["symbol"] for p in portfolio["positions"]], max_size=max_watchlist)
    market_data = fetch_market_data(watchlist)
    plan = ai_decision(portfolio, market_data, watchlist, max_positions, notional)
    results = execute_plan(plan, dry_run=dry_run)
    return {"portfolio":portfolio,"watchlist":watchlist,"plan":results}