from alpaca_trade_api.rest import REST, TimeFrame
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, OPENAI_API_KEY
from market_data import get_price, get_top_news
from openai import OpenAI

# Alpaca REST initialization (paper trading)
BASE_URL = "https://paper-api.alpaca.markets"
alpaca = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL)

client = OpenAI(api_key=OPENAI_API_KEY)

def get_portfolio_state():
    account = alpaca.get_account()
    positions = alpaca.list_positions()
    return {
        'portfolio_value': account.equity,
        'positions': [{'symbol': p.symbol, 'qty': p.qty, 'unrealized_plpc': p.unrealized_plpc} for p in positions]
    }

def generate_watchlist():
    """Generate a comprehensive watchlist of stocks to monitor."""
    # Get current portfolio positions
    portfolio_symbols = [p['symbol'] for p in get_portfolio_state()['positions']]
    
    # Major tech stocks
    tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSM', 'AVGO', 'ASML', 'AMD']
    
    # Financial sector
    financial_stocks = ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'BLK', 'C', 'SCHW', 'AXP', 'V']
    
    # Healthcare sector
    healthcare_stocks = ['JNJ', 'UNH', 'LLY', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY']
    
    # Industrial sector
    industrial_stocks = ['CAT', 'BA', 'HON', 'UPS', 'RTX', 'UNP', 'DE', 'GE', 'MMM', 'LMT']
    
    # Consumer sector
    consumer_stocks = ['PG', 'KO', 'PEP', 'COST', 'WMT', 'MCD', 'NKE', 'SBUX', 'HD', 'TGT']
    
    # Energy sector
    energy_stocks = ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'PSX', 'VLO', 'MPC', 'OXY']
    
    # Combine all sectors and portfolio
    all_symbols = list(set(
        portfolio_symbols +
        tech_stocks +
        financial_stocks +
        healthcare_stocks +
        industrial_stocks +
        consumer_stocks +
        energy_stocks
    ))
    
    # Optionally, you can limit the number of stocks to analyze if needed
    max_stocks = 30  # Adjust this number based on your needs
    if len(all_symbols) > max_stocks:
        # Prioritize portfolio stocks and randomly select others
        import random
        non_portfolio = list(set(all_symbols) - set(portfolio_symbols))
        selected_non_portfolio = random.sample(non_portfolio, min(max_stocks - len(portfolio_symbols), len(non_portfolio)))
        return portfolio_symbols + selected_non_portfolio
    
    return all_symbols

def decide_trade(symbol):
    price = get_price(symbol)
    if price is None:
        return {'action': 'HOLD', 'symbol': symbol, 'reasoning': 'No price data', 'executed': False}

    prompt = f"""
    You are an expert trader. Current price for {symbol} is {price}.
    Decide if we should BUY, SELL, or HOLD.
    Give reasoning in JSON with fields: action, symbol, qty, reasoning, executed.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
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