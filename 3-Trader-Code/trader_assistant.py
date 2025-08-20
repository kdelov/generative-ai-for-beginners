import os
import json
import openai
import alpaca_trade_api as tradeapi
import pandas as pd

# Load API keys from environment
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Init clients
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
openai.api_key = OPENAI_API_KEY

# === Portfolio state ===
def get_portfolio_state():
    account = api.get_account()
    positions = api.list_positions()
    portfolio_value = account.portfolio_value
    pos_summary = [{"symbol": p.symbol, "qty": p.qty, "unrealized_plpc": p.unrealized_plpc} for p in positions]
    return {"portfolio_value": portfolio_value, "positions": pos_summary}

# === Market snapshot ===
def get_market_snapshot(symbol="AAPL"):
    barset = api.get_bars(symbol, "1Day", limit=5).df
    return barset.reset_index().to_dict(orient="records")

# === Trading loop with GPT ===
def run_trading_loop(symbol="AAPL"):
    portfolio = get_portfolio_state()
    market = get_market_snapshot(symbol)

    prompt = f"""
    You are an expert trader. Given the current portfolio and recent market data,
    decide whether to BUY, SELL, or HOLD {symbol}.
    Always respond in JSON with fields: action, symbol, qty, reasoning.
    Portfolio: {json.dumps(portfolio)}
    Market: {json.dumps(market)}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4.1-mini",   # or gpt-4.1 depending on what you enabled
        messages=[{"role": "system", "content": "You are a trading assistant."},
                  {"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    decision = json.loads(response.choices[0].message["content"])
    action = decision.get("action")
    qty = int(decision.get("qty", 0))

    # Execute trade if not HOLD
    if action in ["buy", "sell"] and qty > 0:
        side = "buy" if action == "buy" else "sell"
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type="market",
            time_in_force="gtc"
        )
        decision["executed"] = True
    else:
        decision["executed"] = False

    return decision
