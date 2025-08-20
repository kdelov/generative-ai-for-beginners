import os
import gradio as gr
from trader_assistant import run_trading_loop, get_portfolio_state

def trade_interface():
    portfolio = get_portfolio_state()
    decision = run_trading_loop(symbol="AAPL")
    return f"📊 Portfolio:\n{portfolio}\n\n🤖 GPT Decision:\n{decision}"

with gr.Blocks() as demo:
    gr.Markdown("## 🧑‍💻 Trader Assistant (Alpaca + OpenAI)")
    
    output = gr.Textbox(label="Results", lines=20)

    run_button = gr.Button("Run Trading Loop")
    run_button.click(fn=trade_interface, outputs=output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", 8080)))
