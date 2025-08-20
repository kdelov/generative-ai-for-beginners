import gradio as gr
from trader_assistant import autonomous_cycle, get_portfolio_state

def run_trader():
    portfolio = get_portfolio_state()
    trades = autonomous_cycle()
    return portfolio, trades

with gr.Blocks() as demo:
    gr.Markdown("## GPT Autonomous Trader Assistant")
    with gr.Row():
        run_btn = gr.Button("Run Trading Loop")
    with gr.Row():
        portfolio_output = gr.JSON()
        trades_output = gr.JSON()

    run_btn.click(run_trader, outputs=[portfolio_output, trades_output])

demo.launch()