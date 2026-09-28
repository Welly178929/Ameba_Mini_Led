from src.voice_controller import parse_voice_command


def test_left_on_command():
    result = parse_voice_command("左邊開燈")
    assert result is not None
    assert result["side"] == "left"
    assert result["action"] == "on"
    assert result["led"] == "blue"


def test_right_on_command():
    result = parse_voice_command("右邊開燈")
    assert result is not None
    assert result["side"] == "right"
    assert result["action"] == "on"
    assert result["led"] == "green"


def test_invalid_command():
    result = parse_voice_command("今天天氣很好")
    assert result is None


def test_left_off_command():
    result = parse_voice_command("左邊關燈")
    assert result is not None
    assert result["side"] == "left"
    assert result["action"] == "off"
    assert result["led"] == "blue"


def test_left_blink_command():
    result = parse_voice_command("左邊閃爍三次")
    assert result is not None
    assert result["side"] == "left"
    assert result["action"] == "blink"
    assert result["led"] == "blue"


def test_right_blink_command():
    result = parse_voice_command("右邊綠燈閃3下")
    assert result is not None
    assert result["side"] == "right"
    assert result["action"] == "blink"
    assert result["led"] == "green"


def test_blink_without_side_blinks_both():
    result = parse_voice_command("閃爍三次")
    assert result is not None
    assert result["side"] == "both"
    assert result["action"] == "blink"
