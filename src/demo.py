from src.voice_controller import parse_voice_command


def simulate_command(text: str):
    parsed = parse_voice_command(text)
    if parsed is None:
        return {"status": "rejected", "message": "無法辨識的語音，未改變 LED 狀態"}
    return {"status": "accepted", "command": parsed, "message": f"執行 {parsed['led']} LED {parsed['action']}"}


if __name__ == "__main__":
    samples = [
        "左邊開燈",
        "右邊開燈",
        "左邊關燈",
        "右邊關燈",
        "今天天氣很好",
    ]
    for sample in samples:
        print(sample, "->", simulate_command(sample))
