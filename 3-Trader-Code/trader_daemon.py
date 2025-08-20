import time
import schedule
from datetime import datetime
from trader_assistant import autonomous_cycle

# How often to run (e.g., every 15 minutes)
INTERVAL_MINUTES = 15

def job():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n⏰ Running trading cycle at {now}")
    try:
        result = autonomous_cycle(
            max_watchlist=20,
            max_positions=5,
            notional=1000,
            dry_run=False   # change to False to execute real trades
        )
        print("📊 Portfolio:", result["portfolio"])
        print("👀 Watchlist:", result["watchlist"])
        print("🤖 Plan:", result["plan"])
    except Exception as e:
        print("❌ Error during cycle:", e)

# Schedule job
schedule.every(INTERVAL_MINUTES).minutes.do(job)

print(f"🚀 Trader daemon started — running every {INTERVAL_MINUTES} minutes...")
job()  # run once immediately on startup

while True:
    schedule.run_pending()
    time.sleep(1)
