# FastAPI 樹莓派後端 API 伺服器

這是一個完整的 FastAPI 後端伺服器，讓樹莓派可以呼叫各種 API 進行通訊。

## 功能特色

- ✅ 接收樹莓派上傳的圖片
- ✅ 收集感測器數據 (溫度、濕度、光線等)
- ✅ 設備狀態監控
- ✅ 指令發送與接收
- ✅ 歷史資料查詢
- ✅ 自動驗證與錯誤處理
- ✅ CORS 支援 (跨域請求)
- ✅ 完整的 API 文件 (Swagger UI)

## 安裝步驟

### 1. 在伺服器端（你的電腦）

```powershell
# 進入專案資料夾
cd d:\Python-training\fastapi_server

# 安裝依賴套件
pip install -r requirements.txt

# 啟動伺服器
python main.py
```

伺服器會在 `http://0.0.0.0:8000` 啟動

### 2. 在樹莓派端

```bash
# 安裝 requests 套件
pip install requests

# 編輯 raspberry_pi_client.py，修改：
# - SERVER_URL: 改成你電腦的 IP (例如 http://192.168.1.100:8000/upload_image)
# - IMAGE_PATH: 改成要上傳的圖片路徑

# 執行上傳
python raspberry_pi_client.py
```

## API 端點

### 📷 POST /upload_image
上傳圖片

**參數:**
- `file`: 圖片檔案 (multipart/form-data)

**回應範例:**
```json
{
  "success": true,
  "message": "Image uploaded successfully",
  "filename": "pi_image_20251021_143025.jpg",
  "size": 123456
}
```

### 📊 POST /sensor_data
發送感測器數據

**參數:**
```json
{
  "device_id": "pi_001",
  "temperature": 25.5,
  "humidity": 60.3,
  "light": 512,
  "motion": false,
  "custom_data": {"cpu_temp": 45.2}
}
```

### 📱 POST /device_status
更新設備狀態

**參數:**
```json
{
  "device_id": "pi_001",
  "status": "online",
  "message": "系統運行正常",
  "battery_level": 85.5
}
```

### 🔍 GET /device_status/{device_id}
查詢設備狀態

### 📝 POST /command
發送指令給樹莓派

**參數:**
```json
{
  "device_id": "pi_001",
  "command": "take_photo",
  "parameters": {"quality": 95}
}
```

### 📥 GET /commands/{device_id}
獲取待執行的指令

### 📜 GET /logs/{device_id}
查詢設備歷史資料

**參數:**
- `limit`: 返回最近幾筆資料 (預設 10)

### 🏥 GET /health
健康檢查

### 🏠 GET /
API 資訊與所有端點列表

## 如何找到你電腦的 IP

**Windows PowerShell:**
```powershell
ipconfig
# 找 IPv4 位址，例如 192.168.1.100
```

**Linux/Mac:**
```bash
ifconfig
# 或
ip addr show
```

## 注意事項

1. 確保防火牆允許 8000 port
2. 伺服器和樹莓派需在同一網路
3. 上傳的圖片會儲存在 `uploads` 資料夾

## 自動 API 文件

啟動伺服器後，可以訪問：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

這些頁面提供互動式 API 文件，可以直接測試所有端點！

## 快速測試

### 使用樹莓派客戶端
```bash
cd fastapi_server
python raspberry_pi_client.py
# 根據提示選擇要執行的範例
```

### 使用 curl 測試
```bash
# 檢查伺服器狀態
curl http://localhost:8000/

# 發送感測器數據
curl -X POST http://localhost:8000/sensor_data \
  -H "Content-Type: application/json" \
  -d '{"device_id":"pi_001","temperature":25.5,"humidity":60}'
```

### 使用 PowerShell 測試
```powershell
# 檢查伺服器狀態
Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get

# 發送感測器數據
$body = @{
    device_id = "pi_001"
    temperature = 25.5
    humidity = 60
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/sensor_data" -Method Post -Body $body -ContentType "application/json"
```

## 整合到樹莓派專案

### 範例 1: 拍照後自動上傳
```python
from gpiozero import Button
from picamera import PiCamera
from raspberry_pi_client import RaspberryPiClient

camera = PiCamera()
button = Button(17)
client = RaspberryPiClient("pi_001")

def take_and_upload():
    # 拍照
    filename = f"/tmp/photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    camera.capture(filename)
    
    # 上傳
    result = client.upload_image(filename)
    if result.get("success"):
        print("✓ 照片已上傳!")

button.when_pressed = take_and_upload
```

### 範例 2: 定時發送感測器數據
```python
from raspberry_pi_client import RaspberryPiClient
import Adafruit_DHT
import time

client = RaspberryPiClient("pi_001")
sensor = Adafruit_DHT.DHT22

while True:
    # 讀取溫濕度
    humidity, temperature = Adafruit_DHT.read_retry(sensor, 4)
    
    # 發送到伺服器
    client.send_sensor_data(
        temperature=temperature,
        humidity=humidity
    )
    
    time.sleep(60)  # 每分鐘發送一次
```

## 資料儲存結構

伺服器會自動建立以下資料夾：
```
fastapi_server/
├── uploads/          # 上傳的圖片
├── data/            # 感測器數據、狀態、指令
│   ├── sensor_pi_001_*.json
│   ├── status_pi_001.json
│   └── cmd_pi_001_*.json
└── ...
```

## 進階設定

### 修改伺服器 Port
編輯 `main.py` 最後一行：
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # 改成其他 port
```

### 設定多個樹莓派
每個樹莓派使用不同的 `device_id`：
```python
client = RaspberryPiClient("pi_001")  # 客廳
client = RaspberryPiClient("pi_002")  # 房間
client = RaspberryPiClient("pi_003")  # 廚房

def take_and_upload_photo():
    # 拍照
    subprocess.run(["libcamera-still", "-o", "/tmp/photo.jpg"])
    
    # 上傳
    with open("/tmp/photo.jpg", "rb") as f:
        files = {"file": f}
        response = requests.post("http://你的IP:8000/upload_image", files=files)
        print(response.json())

button.when_pressed = take_and_upload_photo
```
