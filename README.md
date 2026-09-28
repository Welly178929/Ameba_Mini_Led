# Ameba Mini 語音控制 LED 系統

- 示範影片：<https://www.youtube.com/watch?v=aBHIVRHJqzE>
- 專題報告：[docs/專題報告.pdf](docs/專題報告.pdf)

以 Vibe Coding（生成式 AI 輔助開發）完成的專題：使用者在網頁上用麥克風說出指令，電腦端辨識並解析後，經 USB 序列埠傳送到 Ameba AMB82-MINI，控制板上的藍燈與綠燈，並把開發板的回傳結果顯示在網頁上。

## 系統流程

```
麥克風 ─▶ 瀏覽器 Web Speech API（語音轉文字, zh-TW）
        ─▶ Flask 伺服器 POST /command
             ├─ voice_controller.py：規則比對 → {side, action, led}，無法辨識則拒絕
             └─ ameba_serial.py：轉成 left_on / right_off / both_blink … 送到 COM port
        ─▶ AMB82-MINI（ameba_led_control.ino）：控制 LED_B / LED_G，回傳執行結果
        ─▶ 網頁顯示辨識結果、板子回應；只有收到板子回應才更新 LED 狀態
```

## 目錄結構

| 路徑 | 說明 |
|---|---|
| `src/voice_controller.py` | 語音文字 → 控制指令的解析規則 |
| `src/ameba_serial.py` | 與 Ameba 的序列埠通訊（預設 COM7，可用環境變數 `AMEBA_PORT` 修改） |
| `src/server.py` | Flask Web 伺服器與 `/command` API |
| `src/demo.py` | 不接硬體的指令解析示範 |
| `static/index.html` | 操作介面（文字輸入、麥克風、LED 狀態、錯誤提示） |
| `arduino/ameba_led_control/` | 燒錄到 AMB82-MINI 的控制程式 |
| `arduino/ameba_blink_test/` | 確認板子與燒錄流程正常的閃燈測試程式 |
| `tests/` | pytest 單元測試（不需接硬體） |
| `docs/` | 專題報告 |

## 硬體

- 開發板：Realtek **AMB82-MINI**（AmebaPro2，USB 轉序列晶片 CH340）
- LED：使用板載 LED，不需額外接線
  - 藍燈 `LED_B` = D23（左邊）
  - 綠燈 `LED_G` = D24（右邊）
  - `HIGH` 亮、`LOW` 滅
- 通訊：USB 序列埠，115200 baud，一行一個指令（`\n` 結尾）

| 序列埠指令 | 動作 | 板子回應 |
|---|---|---|
| `left_on` / `left_off` | 藍燈亮 / 滅 | `left_on: blue LED ON` … |
| `right_on` / `right_off` | 綠燈亮 / 滅 | `right_on: green LED ON` … |
| `left_blink` / `right_blink` / `both_blink` | 閃爍三次後恢復原狀態 | `left_blink: blue LED blinked 3 times` … |
| 其他 | 不動作 | `ignored` |

## 環境設定

### 1. Python（已於 Python 3.13 / Windows 11 測試）

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
```

### 2. Arduino 開發板套件

使用 Arduino IDE 2.x（或其內附的 `arduino-cli`）：

1. 在「偏好設定 → 額外的開發板管理員網址」加入
   `https://github.com/Ameba-AIoT/ameba-arduino-pro2/raw/main/Arduino_package/package_realtek_amebapro2_index.json`
2. 開發板管理員搜尋 **Realtek Ameba Boards (AmebaPro2)** 並安裝（本專案使用 4.1.0）
3. 開發板選 **AMB82-MINI**

命令列等效作法：

```powershell
$url = "https://github.com/Ameba-AIoT/ameba-arduino-pro2/raw/main/Arduino_package/package_realtek_amebapro2_index.json"
arduino-cli core update-index --additional-urls $url
arduino-cli core install realtek:AmebaPro2 --additional-urls $url
```

### 3. 燒錄

```powershell
arduino-cli compile --fqbn realtek:AmebaPro2:Ameba_AMB82-MINI arduino/ameba_led_control
arduino-cli upload  -p COM7 --fqbn realtek:AmebaPro2:Ameba_AMB82-MINI arduino/ameba_led_control
```

- 若上傳出現 `ping fail`：板子沒有自動進入燒錄模式。**按住 BOOT → 按一下 RST → 放開 BOOT** 後再上傳。
- 上傳成功後 **按一下 RST**，程式才會開始執行（序列埠會印出 `Ameba Mini LED ready`）。
- 燒錄前請先關閉 Flask 伺服器與序列埠監控視窗，COM port 同時只能被一個程式使用。

## 執行

```powershell
.\.venv\Scripts\Activate.ps1
python src/server.py                      # 預設使用 COM7
# 或：$env:AMEBA_PORT="COM8"; python src/server.py
```

用 Chrome 或 Edge 開啟 <http://localhost:5000>，輸入文字或按「🎤 使用麥克風」說出指令。

其他：

```powershell
python -m src.demo     # 只測試指令解析，不需接板子（中文亂碼時先設定 $env:PYTHONUTF8=1）
python -m pytest -q    # 單元測試
```

## 支援指令

| 說法（範例） | 動作 |
|---|---|
| 左邊開燈、左邊開藍燈、left on、blue on | 藍燈亮 |
| 右邊開燈、右邊開綠燈、right on、green on | 綠燈亮 |
| 左邊關燈、左邊藍燈關掉、left off | 藍燈滅 |
| 右邊關燈、右邊綠燈關閉、right off | 綠燈滅 |
| 左邊閃爍三次 / 右邊閃3下 / 閃爍三次、blink | 指定的燈（未指定則兩顆）閃三次後恢復原狀 |
| 其他語句（例如「今天天氣很好」） | 拒絕，不送出任何指令、LED 不變 |

## 異常處理

| 狀況 | 系統行為 |
|---|---|
| 非控制語句 | API 回傳 `rejected`，不送指令到板子，LED 不變 |
| COM port 無法開啟（USB 拔除、被其他程式占用） | API 回傳錯誤原因，網頁顯示「板子控制失敗」，LED 狀態顯示不變；重新接上後下一個指令會自動重新連線 |
| 板子沒有回應（例如燒錄後未按 RST） | 等待 3 秒逾時，網頁提示「板子沒有回應」 |
| 網頁無法連到伺服器 | 網頁提示「無法連線到控制伺服器」 |
| 瀏覽器不支援語音辨識 | 提示改用文字輸入 |
