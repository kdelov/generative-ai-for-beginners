import os
import json
from openai import OpenAI
import alpaca_trade_api as tradeapi

# Load API keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Init clients
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
client = OpenAI(api_key=OPENAI_API_KEY)

# === Portfolio state ===
def get_portfolio_state():
    account = api.get_account()
    positions = api.list_positions()
    return {
        "portfolio_value": account.portfolio_value,
        "positions": [
            {"symbol": p.symbol, "qty": p.qty, "unrealized_plpc": p.unrealized_plpc}
            for p in positions
        ]
    }

# === Market snapshot ===
def get_market_snapshot(symbol="AAPL"):
    bars = api.get_bars(symbol, "1Day", limit=5)
    return [bar._raw for bar in bars]  # convert to JSON-safe dicts

# === Trading loop with GPT ===
def run_trading_loop(symbol="AAPL"):
    portfolio = get_portfolio_state()
    market = get_market_snapshot(symbol)

    prompt = f"""
    You are an expert trader. 
    Decide whether to BUY, SELL, or HOLD {symbol}.
    Respond in JSON with fields: action, symbol, qty, reasoning.
    Portfolio: {json.dumps(portfolio)}
    Market: {json.dumps(market)}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # upgrade/downgrade if needed
        messages=[
            {"role": "system", "content": "You are a trading assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    decision_str = response.choices[0].message.content
    try:
        decision = json.loads(decision_str)
    except json.JSONDecodeError:
        decision = {"action": "hold", "symbol": symbol, "qty": 0, "reasoning": "Invalid JSON"}

    action = decision.get("action", "").lower()
    qty = int(decision.get("qty", 0))

    # Execute trade if not HOLD
    if action in ["buy", "sell"] and qty > 0:
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side=action,
            type="market",
            time_in_force="gtc"
        )
        decision["executed"] = True
    else:
        decision["executed"] = False

    return decision
