import os
import gradio as gr
from alpaca_trade_api.rest import REST, TimeFrame

# Read Alpaca API keys from environment variables (Codespaces secrets)
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading for safety

# Verify that the secrets are set
if not API_KEY or not API_SECRET:
    raise ValueError("Alpaca API keys are not set! Make sure Codespaces secrets are configured.")

# Initialize Alpaca API
api = REST(API_KEY, API_SECRET, BASE_URL)

# Function to submit orders
def trade_action(symbol, qty, action):
    try:
        qty = int(qty)
        if action.lower() == "buy":
            order = api.submit_order(symbol=symbol, qty=qty, side="buy", type="market", time_in_force="gtc")
        else:
            order = api.submit_order(symbol=symbol, qty=qty, side="sell", type="market", time_in_force="gtc")
        return f"Order submitted: {order.side} {order.qty} {order.symbol}"
    except Exception as e:
        return f"Error: {str(e)}"

# Gradio interface
iface = gr.Interface(
    fn=trade_action,
    inputs=["text", "number", gr.Dropdown(["buy", "sell"])],
    outputs="text",
    title="Alpaca Trading Playground",
    description="Type a stock symbol, quantity, and action to place a paper trade."
)

# Launch Gradio server in Codespaces
iface.launch(server_name="0.0.0.0", server_port=7860, share=True)
