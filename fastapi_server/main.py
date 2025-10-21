from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import os
from datetime import datetime
from PIL import Image
import io
import json

app = FastAPI(
    title="Raspberry Pi Backend API",
    description="完整的樹莓派後端 API 服務",
    version="1.0.0"
)

# 允許跨域請求 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定資料儲存路徑
UPLOAD_DIR = "uploads"
DATA_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# 資料模型定義
class SensorData(BaseModel):
    """感測器數據模型"""
    device_id: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    light: Optional[int] = None
    motion: Optional[bool] = None
    custom_data: Optional[Dict[str, Any]] = None

class CommandRequest(BaseModel):
    """指令請求模型"""
    device_id: str
    command: str
    parameters: Optional[Dict[str, Any]] = None

class StatusUpdate(BaseModel):
    """狀態更新模型"""
    device_id: str
    status: str  # online, offline, busy, idle, error
    message: Optional[str] = None
    battery_level: Optional[float] = None

@app.get("/")
async def root():
    """API 根路徑 - 確認服務運行"""
    return {
        "message": "Raspberry Pi Backend API is running",
        "status": "ok",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload_image": "/upload_image",
            "list_images": "/images",
            "get_image": "/images/{filename}",
            "sensor_data": "/sensor_data",
            "device_status": "/device_status",
            "command": "/command",
            "logs": "/logs"
        }
    }

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    """
    接收樹莓派上傳的圖片
    
    參數:
        file: 上傳的圖片檔案
    
    回傳:
        JSON 包含上傳狀態、檔名和路徑
    """
    try:
        # 檢查檔案類型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        # 讀取圖片內容
        content = await file.read()
        
        # 驗證圖片是否有效
        try:
            img = Image.open(io.BytesIO(content))
            img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # 生成檔案名稱 (時間戳+原始檔名)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        filename = f"pi_image_{timestamp}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # 儲存圖片
        with open(filepath, "wb") as f:
            f.write(content)
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Image uploaded successfully",
                "filename": filename,
                "filepath": filepath,
                "size": len(content),
                "timestamp": timestamp,
                "view_url": f"/images/{filename}"
            },
            status_code=200
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "message": f"Failed to upload image: {str(e)}"
            },
            status_code=500
        )

@app.get("/images")
async def list_images():
    """
    列出所有已上傳的圖片
    
    回傳:
        圖片列表及詳細資訊
    """
    try:
        images = []
        if os.path.exists(UPLOAD_DIR):
            for filename in sorted(os.listdir(UPLOAD_DIR), reverse=True):
                filepath = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(filepath) and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    stat = os.stat(filepath)
                    images.append({
                        "filename": filename,
                        "size": stat.st_size,
                        "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "view_url": f"/images/{filename}",
                        "download_url": f"/images/{filename}?download=true"
                    })
        
        return {
            "success": True,
            "count": len(images),
            "images": images
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list images: {str(e)}")

@app.get("/images/{filename}")
async def get_image(filename: str, download: bool = False):
    """
    查看或下載特定圖片
    
    參數:
        filename: 圖片檔名
        download: 是否下載 (預設為 False，直接顯示)
    
    回傳:
        圖片檔案
    """
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # 安全檢查：防止路徑穿越攻擊
    if not os.path.abspath(filepath).startswith(os.path.abspath(UPLOAD_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    
    # 判斷 MIME 類型
    ext = os.path.splitext(filename)[1].lower()
    media_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp'
    }
    media_type = media_type_map.get(ext, 'application/octet-stream')
    
    if download:
        return FileResponse(
            filepath,
            media_type=media_type,
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        return FileResponse(filepath, media_type=media_type)

@app.post("/sensor_data")
async def receive_sensor_data(data: SensorData):
    """
    接收樹莓派的感測器數據
    
    參數:
        data: 感測器數據 (溫度、濕度、光線等)
    
    回傳:
        接收確認
    """
    try:
        # 儲存數據到檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sensor_{data.device_id}_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        data_dict = data.dict()
        data_dict["timestamp"] = datetime.now().isoformat()
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": "Sensor data received",
            "device_id": data.device_id,
            "timestamp": data_dict["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save sensor data: {str(e)}")

@app.post("/device_status")
async def update_device_status(status: StatusUpdate):
    """
    更新樹莓派設備狀態
    
    參數:
        status: 設備狀態資訊
    
    回傳:
        狀態更新確認
    """
    try:
        # 儲存狀態到檔案
        status_file = os.path.join(DATA_DIR, f"status_{status.device_id}.json")
        
        status_dict = status.dict()
        status_dict["last_updated"] = datetime.now().isoformat()
        
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status_dict, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": "Status updated",
            "device_id": status.device_id,
            "status": status.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")

@app.get("/device_status/{device_id}")
async def get_device_status(device_id: str):
    """
    查詢特定設備的狀態
    
    參數:
        device_id: 設備 ID
    
    回傳:
        設備當前狀態
    """
    status_file = os.path.join(DATA_DIR, f"status_{device_id}.json")
    
    if not os.path.exists(status_file):
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    
    try:
        with open(status_file, "r", encoding="utf-8") as f:
            status_data = json.load(f)
        return status_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read status: {str(e)}")

@app.post("/command")
async def send_command(cmd: CommandRequest):
    """
    向樹莓派發送指令 (此範例儲存指令到檔案，實際應用可用 WebSocket 或 MQTT)
    
    參數:
        cmd: 指令內容
    
    回傳:
        指令接收確認
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cmd_file = os.path.join(DATA_DIR, f"cmd_{cmd.device_id}_{timestamp}.json")
        
        cmd_dict = cmd.dict()
        cmd_dict["timestamp"] = datetime.now().isoformat()
        cmd_dict["status"] = "pending"
        
        with open(cmd_file, "w", encoding="utf-8") as f:
            json.dump(cmd_dict, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": "Command queued",
            "device_id": cmd.device_id,
            "command": cmd.command,
            "command_id": timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue command: {str(e)}")

@app.get("/commands/{device_id}")
async def get_pending_commands(device_id: str):
    """
    獲取特定設備的待執行指令
    
    參數:
        device_id: 設備 ID
    
    回傳:
        待執行的指令列表
    """
    try:
        commands = []
        for filename in os.listdir(DATA_DIR):
            if filename.startswith(f"cmd_{device_id}_") and filename.endswith(".json"):
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    cmd_data = json.load(f)
                    if cmd_data.get("status") == "pending":
                        commands.append(cmd_data)
        
        return {
            "device_id": device_id,
            "pending_commands": commands,
            "count": len(commands)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve commands: {str(e)}")

@app.get("/logs/{device_id}")
async def get_device_logs(device_id: str, limit: int = 10):
    """
    獲取設備的感測器歷史資料
    
    參數:
        device_id: 設備 ID
        limit: 返回最近幾筆資料 (預設 10)
    
    回傳:
        歷史資料列表
    """
    try:
        logs = []
        for filename in sorted(os.listdir(DATA_DIR), reverse=True):
            if filename.startswith(f"sensor_{device_id}_") and filename.endswith(".json"):
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
                    logs.append(log_data)
                
                if len(logs) >= limit:
                    break
        
        return {
            "device_id": device_id,
            "logs": logs,
            "count": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "upload_dir": UPLOAD_DIR,
        "data_dir": DATA_DIR,
        "upload_dir_exists": os.path.exists(UPLOAD_DIR),
        "data_dir_exists": os.path.exists(DATA_DIR),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # host="0.0.0.0" 讓外部裝置可以連接
    # port=8000 預設端口
    print("🚀 Starting Raspberry Pi Backend API Server...")
    print("📡 Server will be accessible at: http://0.0.0.0:8000")
    print("📖 API Documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
