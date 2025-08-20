import gradio as gr
from trader_assistant import autonomous_cycle

def run_cycle(max_watchlist, max_positions, notional, dry_run):
    out = autonomous_cycle(max_watchlist, max_positions, notional, dry_run)
    return out

with gr.Blocks() as demo:
    gr.Markdown("## 🤖 Autonomous Trader Assistant")
    max_watchlist = gr.Slider(5,50,20,label="Max watchlist size")
    max_positions = gr.Slider(1,20,5,label="Max portfolio positions")
    notional = gr.Number(1000,label="Notional per trade ($)")
    dry_run = gr.Checkbox(True,label="Dry run mode")
    run_btn = gr.Button("🚀 Run autonomous cycle")
    output = gr.JSON()
    run_btn.click(fn=run_cycle,inputs=[max_watchlist,max_positions,notional,dry_run],outputs=output)

demo.launch()
