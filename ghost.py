from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from jinja2 import Template
from web3 import Web3
from dotenv import load_dotenv
import subprocess, os, time, threading, logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

# === Load Environment Variables ===
load_dotenv()
wallets = [os.getenv("WALLET_1"), os.getenv("WALLET_2")]
usdt = os.getenv("USDT_CONTRACT")
w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))

# === Logging Setup ===
logging.basicConfig(filename="revenue.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# === FastAPI App ===
app = FastAPI()

# === Middleware: IP Logging + Basic Rate Limiting ===
class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.ip_hits = {}

    async def dispatch(self, request: StarletteRequest, call_next):
        ip = request.client.host
        self.ip_hits[ip] = self.ip_hits.get(ip, 0) + 1
        if self.ip_hits[ip] > 100:
            return HTMLResponse("Too many requests", status_code=429)
        response = await call_next(request)
        return response

app.add_middleware(SecurityMiddleware)

# === Wallet Monitor ===
def check_balances():
    try:
        abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],
                "name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],
                "type":"function"}]
        contract = w3.eth.contract(address=w3.toChecksumAddress(usdt), abi=abi)
        balances = []
        total = 0
        for wallet in wallets:
            balance = contract.functions.balanceOf(wallet).call()
            eth_balance = w3.fromWei(balance, 'ether')
            balances.append(f"{wallet} → {eth_balance} USDT")
            total += float(eth_balance)
        logging.info(f"Total Revenue: {total:.2f} USDT")
        return balances
    except Exception as e:
        return [f"Error: {e}"]

# === Background Revenue Logger ===
def log_revenue():
    while True:
        check_balances()
        time.sleep(3600)  # Every hour

threading.Thread(target=log_revenue, daemon=True).start()

# === Quantum Strategy ===
def optimize_strategy(data):
    return "Quantum-optimized plan for: " + data

# === Chatboard UI ===
chatboard_html = """
<!DOCTYPE html>
<html>
<head>
  <title>Brian4.0 Chatboard</title>
  <style>
    body { background: #0d0d0d; color: #00ffcc; font-family: monospace; padding: 20px; }
    input, button { font-size: 16px; padding: 10px; margin-top: 10px; width: 100%; }
    #response { margin-top: 20px; white-space: pre-wrap; }
  </style>
</head>
<body
