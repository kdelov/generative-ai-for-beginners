import gradio as gr
import pandas as pd
from trader_assistant import autonomous_cycle, get_portfolio_state

def run_cycle():
    """Run one trading cycle and return results for UI display."""
    result = autonomous_cycle(
        max_watchlist=20,
        max_positions=5,
        notional=1000,
        dry_run=True  # ✅ keep safe in UI
    )
    
    # Convert portfolio and watchlist dicts to DataFrames
    portfolio_df = pd.DataFrame(result["portfolio"]["positions"])
    if portfolio_df.empty:
        portfolio_df = pd.DataFrame(columns=["symbol", "qty", "unrealized_plpc"])
    
    watchlist_df = pd.DataFrame(result["watchlist"])
    if watchlist_df.empty:
        watchlist_df = pd.DataFrame(columns=["symbol", "reason"])
    
    # Trading plan as text
    plan_text = result.get("plan", "No plan generated.")
    
    return portfolio_df, watchlist_df, plan_text

def portfolio_state():
    state = get_portfolio_state()
    df = pd.DataFrame(state["positions"])
    if df.empty:
        df = pd.DataFrame(columns=["symbol", "qty", "unrealized_plpc"])
    return df

with gr.Blocks() as demo:
    gr.Markdown("# 📈 Trader Assistant (Testing UI)")
    
    run_btn = gr.Button("▶️ Run Trading Cycle")
    portfolio_btn = gr.Button("📊 Check Portfolio State")

    portfolio_out = gr.Dataframe(headers=["symbol", "qty", "unrealized_plpc"], label="Portfolio")
    watchlist_out = gr.Dataframe(headers=["symbol", "reason"], label="Watchlist")
    plan_out = gr.Textbox(label="Trading Plan")

    run_btn.click(run_cycle, outputs=[portfolio_out, watchlist_out, plan_out])
    portfolio_btn.click(portfolio_state, outputs=portfolio_out)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)