markdown
Копировать код
# Webhook Bot for Binance Futures Trading

## Description

This bot processes webhook requests to automatically place orders on Binance Futures using FastAPI. The bot accepts data such as ticker, price, action (long/short), and time, then creates limit orders with the specified leverage and stop-loss.

## Features

- Supports futures trading on Binance via API.
- Automatically places limit orders (buy/sell) with the specified leverage.
- Sets a stop-loss to minimize potential losses.
- Uses Binance Testnet for safe testing.

## Requirements

- Python 3.8+
- Installed dependencies:
  - `fastapi`
  - `pydantic`
  - `python-binance`
  - `uvicorn`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/pivovaizer/webhook.git
Navigate to the project directory:

2. cd webhook

3. Install the required dependencies:
   pip install -r requirements.txt

4. Add your API key and secret to the code:
   api_key = 'your_api_key'
   api_secret = 'your_api_secret'

## Running the Bot

1. Start the application: 
uvicorn main:app --reload

2. Install ngrok to get a public URL: Download it from ngrok.com.

3. Run ngrok to create a tunnel for your local server:
   ngrok http 8000

4. ngrok will generate a public URL (e.g., https://abcd1234.ngrok.io), which you can use for sending webhook requests.

5. The webhook endpoint will be accessible via the ngrok URL, for example:
https://abcd1234.ngrok.io/webhook

## Important

1. The bot uses Binance Testnet by default. To switch to   the live Binance network, replace the API URL in the code:
client.API_URL = 'https://fapi.binance.com'
