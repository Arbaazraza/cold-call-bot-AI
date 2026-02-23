from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import os

app = FastAPI()

# This allows your React app (running on port 3000) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run-bot")
async def run_bot():
    try:
        # Run bot with a 60-second absolute timeout to prevent "ghost" processes
        process = subprocess.run(
            ["python", "bot.py"], 
            capture_output=True, 
            text=True, 
            timeout=60 
        )
        
        if os.path.exists("outcome.json"):
            with open("outcome.json", "r") as f:
                return json.load(f)
        return {"error": "Bot finished but no outcome found"}
        
    except subprocess.TimeoutExpired:
        # If it hangs, kill it manually
        return {"error": "Call timed out", "status": "disregarded"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)