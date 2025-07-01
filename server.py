from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

@app.route('/log', methods=['POST'])
def log():
    data = request.json
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("log.txt", "a") as f:
        f.write(f"[{timestamp}] {data}\n")

    return {"status": "logged"}, 200

if __name__ == "__main__":
    app.run(port=5000)
