import json
import os
import sys

from flask import Flask, jsonify, request, send_from_directory

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.ameba_serial import AmebaLink, to_serial_command
from src.voice_controller import parse_voice_command

app = Flask(__name__, static_folder=os.path.join(ROOT_DIR, "static"), static_url_path="")
ameba = AmebaLink()


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/command", methods=["POST"])
def command():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    command = parse_voice_command(text)

    if command is None:
        return jsonify({
            "status": "rejected",
            "message": "無法辨識的語音指令，未改變 LED 狀態",
            "raw_text": text,
        })

    device = ameba.send(to_serial_command(command))

    return jsonify({
        "status": "accepted",
        "command": command,
        "device": device,
        "message": f"將控制 {command['led']} LED {command['action']}",
        "raw_text": text,
    })


if __name__ == "__main__":
    # 關閉 reloader，避免兩個行程同時搶用同一個 COM port
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
