# 車用儀表板 CAN 模擬器

此專案會：
- 讀取 Dashboard.dbc
- 產生模擬車輛訊號
- 透過 TCP (127.0.0.1:9999) 持續送出 JSON
- 讓客戶端即時顯示訊號值

## 檔案說明

- can_simulator.py: 主程式，負責訊號模擬與 TCP 廣播
- can_client.py: 客戶端，連線後顯示收到的 JSON 訊號
- Dashboard.dbc: CAN 訊號定義
- dbc_analyzer.py: DBC 詳細解析與編解碼示範
- test_all.py: 一鍵測試腳本
- start.sh: 啟動選單腳本（會檢查並安裝 cantools）

## 環境需求

- Linux / macOS / Windows（Python 3）
- Python 3.8 以上（建議）
- pip

必要套件：
- cantools

## 快速開始

### 方式 A：使用啟動腳本（推薦）

```bash
bash start.sh
```

選單說明：
1. 啟動模擬器
2. 啟動客戶端（需另一個終端）
3. 嘗試同時開兩個終端啟動
4. 查看本 README
5. 離開

### 方式 B：手動開兩個終端

終端 1：
```bash
python3 can_simulator.py
```

終端 2：
```bash
python3 can_client.py
```

## 模擬器互動指令

在模擬器執行後，可在同一終端輸入：

- start: 開啟引擎狀態
- stop: 關閉引擎，目標速度歸零
- speed 60: 設定目標速度（0~180 km/h）
- quit 或 exit: 結束模擬器

## 輸出資料格式

模擬器每約 100ms 廣播一筆 JSON 行資料（以換行分隔），結構如下：

```json
{
  "timestamp": 1718000000.123,
  "messages": {
    "EngineStatus": {
      "frame_id": 256,
      "name": "EngineStatus",
      "timestamp": 1718000000.123,
      "signals": {
        "EngineRPM": {"value": 820.5, "unit": "rpm"}
      }
    }
  }
}
```

你也可以用 netcat 直接觀察資料：

```bash
nc 127.0.0.1 9999
```

## 測試

執行完整測試：

```bash
python3 test_all.py
```

測試項目包含：
- 依賴是否安裝
- DBC 可否載入
- 模擬器/客戶端可否匯入
- 訊號編解碼是否正常
- 可選：TCP 連線測試（需先啟動模擬器）

## DBC 分析工具

執行：

```bash
python3 dbc_analyzer.py
```

功能包含：
- 顯示訊息與信號明細
- 編碼/解碼示範
- 產生 signal_mapping.json

## 常見問題

1. 提示找不到 cantools

安裝：
```bash
pip install cantools
```

若系統有多個 Python，改用：
```bash
python3 -m pip install cantools
```

2. 客戶端連不上 127.0.0.1:9999

- 先確認模擬器是否正在跑
- 檢查是否有其他程式占用 9999 port

3. start.sh 開雙終端失敗

- 腳本會優先使用 gnome-terminal，其次 xterm
- 若環境沒有這些終端，請手動開兩個終端分別執行模擬器和客戶端

## 結束程式

- 模擬器與客戶端都可用 Ctrl+C 停止
- 或在模擬器輸入 quit / exit
