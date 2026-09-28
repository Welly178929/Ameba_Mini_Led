import re

LEFT_PATTERNS = [
    r"左邊\s*(?:開|開啟|打開)?燈",
    r"左邊\s*(?:開|開啟|打開)\s*藍燈",
    r"左邊\s*藍燈\s*(?:開|開啟|打開)",
    r"left\s*(?:on|open|turn\s*on)\s*(?:light|lamp)?",
    r"blue\s*(?:on|open|turn\s*on)",
]
RIGHT_PATTERNS = [
    r"右邊\s*(?:開|開啟|打開)?燈",
    r"右邊\s*(?:開|開啟|打開)\s*綠燈",
    r"右邊\s*綠燈\s*(?:開|開啟|打開)",
    r"right\s*(?:on|open|turn\s*on)\s*(?:light|lamp)?",
    r"green\s*(?:on|open|turn\s*on)",
]
LEFT_OFF_PATTERNS = [
    r"左邊\s*(?:關|關掉|關閉)\s*燈",
    r"左邊\s*藍燈\s*(?:關|關掉|關閉)",
    r"left\s*(?:off|turn\s*off|close)\s*(?:light|lamp)?",
    r"blue\s*(?:off|turn\s*off|close)",
]
RIGHT_OFF_PATTERNS = [
    r"右邊\s*(?:關|關掉|關閉)\s*燈",
    r"右邊\s*綠燈\s*(?:關|關掉|關閉)",
    r"right\s*(?:off|turn\s*off|close)\s*(?:light|lamp)?",
    r"green\s*(?:off|turn\s*off|close)",
]
BLINK_PATTERNS = [
    r"閃爍?\s*(?:三|3)\s*(?:次|下)",
    r"blink",
]
LEFT_SIDE_PATTERN = r"左邊|藍燈|left|blue"
RIGHT_SIDE_PATTERN = r"右邊|綠燈|right|green"


def parse_voice_command(text: str):
    """Return a normalized command dict or None for unsupported text."""
    if text is None:
        return None

    normalized = text.strip().lower()
    if not normalized:
        return None

    # 閃爍要先判斷，避免「左邊燈閃爍三次」被當成開燈
    if any(re.search(pattern, normalized) for pattern in BLINK_PATTERNS):
        has_left = re.search(LEFT_SIDE_PATTERN, normalized) is not None
        has_right = re.search(RIGHT_SIDE_PATTERN, normalized) is not None
        if has_left and not has_right:
            return {"side": "left", "action": "blink", "led": "blue", "raw": text}
        if has_right and not has_left:
            return {"side": "right", "action": "blink", "led": "green", "raw": text}
        return {"side": "both", "action": "blink", "led": "both", "raw": text}

    if any(re.search(pattern, normalized) for pattern in LEFT_PATTERNS):
        return {"side": "left", "action": "on", "led": "blue", "raw": text}
    if any(re.search(pattern, normalized) for pattern in RIGHT_PATTERNS):
        return {"side": "right", "action": "on", "led": "green", "raw": text}
    if any(re.search(pattern, normalized) for pattern in LEFT_OFF_PATTERNS):
        return {"side": "left", "action": "off", "led": "blue", "raw": text}
    if any(re.search(pattern, normalized) for pattern in RIGHT_OFF_PATTERNS):
        return {"side": "right", "action": "off", "led": "green", "raw": text}
    return None
