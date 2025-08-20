from alpaca_trade_api.rest import REST, TimeFrame
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, OPENAI_API_KEY
from market_data import get_price, get_top_news
import openai

# Alpaca REST initialization (paper trading)
BASE_URL = "https://paper-api.alpaca.markets"
alpaca = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL)

openai.api_key = OPENAI_API_KEY

def get_portfolio_state():
    account = alpaca.get_account()
    positions = alpaca.list_positions()
    return {
        'portfolio_value': account.equity,
        'positions': [{'symbol': p.symbol, 'qty': p.qty, 'unrealized_plpc': p.unrealized_plpc} for p in positions]
    }

def generate_watchlist():
    # Example: combine portfolio symbols and top trending symbols
    portfolio_symbols = [p['symbol'] for p in get_portfolio_state()['positions']]
    trending_symbols = ['AAPL', 'TSLA', 'MSFT']  # placeholder, can be from news scraping
    return list(set(portfolio_symbols + trending_symbols))

def decide_trade(symbol):
    price = get_price(symbol)
    if price is None:
        return {'action': 'HOLD', 'symbol': symbol, 'reasoning': 'No price data', 'executed': False}

    prompt = f"""
    You are an expert trader. Current price for {symbol} is {price}.
    Decide if we should BUY, SELL, or HOLD.
    Give reasoning in JSON with fields: action, symbol, qty, reasoning, executed.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content
    try:
        import json
        return json.loads(content)
    except Exception:
        return {'action': 'HOLD', 'symbol': symbol, 'reasoning': 'Failed parsing GPT output', 'executed': False}

def autonomous_cycle():
    watchlist = generate_watchlist()
    trades = []
    for symbol in watchlist:
        decision = decide_trade(symbol)
        if decision['action'] == 'BUY':
            # Example: buy 1 share
            alpaca.submit_order(symbol, qty=1, side='buy', type='market', time_in_force='day')
            decision['executed'] = True
        elif decision['action'] == 'SELL':
            positions = alpaca.get_position(symbol)
            qty = int(positions.qty)
            if qty > 0:
                alpaca.submit_order(symbol, qty=qty, side='sell', type='market', time_in_force='day')
                decision['executed'] = True
        trades.append(decision)
    return trades
