from src import server
from src.ameba_serial import to_serial_command


class FakeLink:
    def __init__(self):
        self.sent = []

    def send(self, serial_command):
        self.sent.append(serial_command)
        return {"ok": True, "port": "FAKE", "sent": serial_command, "reply": f"{serial_command}: ok"}


def test_to_serial_command():
    assert to_serial_command({"side": "left", "action": "on"}) == "left_on"
    assert to_serial_command({"side": "right", "action": "off"}) == "right_off"


def test_accepted_command_is_sent_to_board(monkeypatch):
    fake = FakeLink()
    monkeypatch.setattr(server, "ameba", fake)
    res = server.app.test_client().post("/command", json={"text": "右邊開燈"})
    data = res.get_json()
    assert data["status"] == "accepted"
    assert fake.sent == ["right_on"]
    assert data["device"]["ok"] is True


def test_rejected_command_is_not_sent(monkeypatch):
    fake = FakeLink()
    monkeypatch.setattr(server, "ameba", fake)
    res = server.app.test_client().post("/command", json={"text": "今天天氣很好"})
    assert res.get_json()["status"] == "rejected"
    assert fake.sent == []


def test_unavailable_port_reports_error_instead_of_crashing():
    from src.ameba_serial import AmebaLink

    result = AmebaLink(port="COM_DOES_NOT_EXIST").send("left_on")
    assert result["ok"] is False
    assert "error" in result


def test_communication_failure_is_reported_to_ui(monkeypatch):
    class BrokenLink:
        def send(self, serial_command):
            return {"ok": False, "port": "COM7", "sent": serial_command, "error": "無法與開發板通訊"}

    monkeypatch.setattr(server, "ameba", BrokenLink())
    data = server.app.test_client().post("/command", json={"text": "左邊開燈"}).get_json()
    assert data["device"]["ok"] is False
    assert data["device"]["error"]
