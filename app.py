from flask import Flask
import time
import os

app = Flask(__name__)

@app.route('/')
def hello():
    time.sleep(1)
    return f"Hello from {os.uname()[1]}!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
