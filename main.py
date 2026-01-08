import os
import asyncio
from threading import Thread
from flask import Flask
from bot import main as start_bot

web = Flask(__name__)

@web.route("/")
def home():
    return "Bot is running!"

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot(local=True))

if __name__ == "__main__":
    if os.getenv("KOYEB") == "1":
        Thread(target=run_bot).start()
        web.run(host="0.0.0.0", port=8000)
    else:
        run_bot()
