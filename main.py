from threading import Thread
from flask import Flask
from bot import main

web = Flask(__name__)

@web.route("/")
def home():
    return "OK"

def run_bot():
    import asyncio
    asyncio.run(main())

if __name__ == '__main__':
    Thread(target=web.run, kwargs={'host': '0.0.0.0', 'port': 8000}).start()
    run_bot()
