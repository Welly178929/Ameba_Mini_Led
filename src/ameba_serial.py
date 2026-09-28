import os
import threading

import serial

DEFAULT_PORT = os.environ.get("AMEBA_PORT", "COM7")
DEFAULT_BAUDRATE = int(os.environ.get("AMEBA_BAUDRATE", "115200"))


def to_serial_command(command: dict) -> str:
    """Map a parsed voice command to the Ameba serial protocol, e.g. 'left_on'."""
    return f"{command['side']}_{command['action']}"


class AmebaLink:
    """Keeps one serial connection to the Ameba board and sends LED commands."""

    def __init__(self, port: str = DEFAULT_PORT, baudrate: int = DEFAULT_BAUDRATE, timeout: float = 3.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None
        self._lock = threading.Lock()

    def _ensure_open(self):
        if self._serial is not None and self._serial.is_open:
            return
        ser = serial.Serial()
        ser.port = self.port
        ser.baudrate = self.baudrate
        ser.timeout = self.timeout
        # 不拉 DTR/RTS，避免開啟連接埠時讓板子重置或進入燒錄模式
        ser.dtr = False
        ser.rts = False
        ser.open()
        self._serial = ser

    def send(self, serial_command: str) -> dict:
        with self._lock:
            try:
                self._ensure_open()
                self._serial.reset_input_buffer()
                self._serial.write((serial_command + "\n").encode("ascii"))
                self._serial.flush()
                reply = self._serial.readline().decode("utf-8", errors="replace").strip()
            except serial.SerialException as exc:
                self.close()
                return {"ok": False, "port": self.port, "sent": serial_command, "error": f"無法與開發板通訊：{exc}"}

            if not reply:
                # 連線可能已失效（例如 USB 被拔除），下次指令重新開啟
                self.close()
                return {"ok": False, "port": self.port, "sent": serial_command, "error": "板子沒有回應，請確認 USB 連線並已按 RST 啟動程式"}
        return {"ok": reply != "ignored", "port": self.port, "sent": serial_command, "reply": reply}

    def close(self):
        if self._serial is not None:
            try:
                self._serial.close()
            except serial.SerialException:
                pass
            self._serial = None
