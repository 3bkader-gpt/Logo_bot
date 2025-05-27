from threading import Thread
from flask import Flask
from bot import main

web = Flask(__name__)

@web.route("/")
def home():
    return "OK"

def run_web():
    web.run(host="0.0.0.0", port=8000)

if __name__ == '__main__':
    Thread(target=main).start()
    run_web()