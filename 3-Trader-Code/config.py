import os
from dotenv import load_dotenv

# Load local .env file if present
load_dotenv()

# Alpaca API keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")