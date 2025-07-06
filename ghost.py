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
<body>
  <h1>💬 Brian4.0 Chatboard</h1>
  <input id="prompt" placeholder="Ask Brian anything..." />
  <button onclick="send()">Send</button>
  <div id="response"></div>
  <script>
    async function send() {
      const prompt = document.getElementById("prompt").value;
      const res = await fetch("/code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
      const data = await res.json();
      document.getElementById("response").innerText = data.response;
    }
  </script>
</body>
</html>
"""

# === Dashboard Template ===
dashboard_template = Template("""
<html>
<head><title>Brian4.0 Dashboard</title></head>
<body style="font-family:Arial;background:#111;color:#0f0;padding:20px;">
    <h1>🧠 Brian4.0: Ghost Protocol</h1>
    <h2>Wallet Balances</h2>
    <pre>{{ balances }}</pre>
    <h2>Status Logs</h2>
    <pre>{{ logs }}</pre>
</body>
</html>
""")

# === Routes ===
@app.get("/", response_class=HTMLResponse)
async def chat_ui():
    return HTMLResponse(content=chatboard_html)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    try:
        with open("revenue.log", "r") as f:
            logs = f.read().splitlines()[-20:]
    except FileNotFoundError:
        logs = ["No logs found."]
    balances = check_balances()
    return dashboard_template.render(logs="\n".join(logs), balances="\n".join(balances))

@app.post("/code")
async def code(data: Request):
    body = await data.json()
    prompt = body.get("prompt", "")
    result = subprocess.run(["ollama", "run", "codellama"], input=prompt.encode(), stdout=subprocess.PIPE)
    return {"response": result.stdout.decode()}

@app.post("/quantum")
async def quantum(data: Request):
    body = await data.json()
    goal = body.get("goal", "")
    return {"strategy": optimize_strategy(goal)}
