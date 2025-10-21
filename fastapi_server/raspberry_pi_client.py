"""""""""

樹莓派客戶端 - 完整的 API 呼叫範例

用於從樹莓派與後端 API 進行通訊樹莓派客戶端 - 完整的 API 呼叫範例樹莓派客戶端 - 完整的 API 呼叫範例

"""

用於從樹莓派與後端 API 進行通訊用於從樹莓派與後端 API 進行通訊

import requests

import os""""""

from datetime import datetime

from typing import Dict, Any, Optional

import time

import randomimport requestsimport requests



# ===== 配置 =====import osimport os

SERVER_IP = "192.168.1.100"  # 改成你電腦的實際 IP

SERVER_PORT = 8000from datetime import datetimefrom datetime import datetime

BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

from typing import Dict, Any, Optionalfrom typing import Dict, Any, Optional



class RaspberryPiClient:import timeimport time

    """樹莓派 API 客戶端"""

    import random

    def __init__(self, device_id: str, server_url: str = BASE_URL):

        """# ===== 配置 =====

        初始化客戶端

        # ===== 配置 =====SERVER_IP = "192.168.1.100"  # 改成你電腦的實際 IP

        參數:

            device_id: 樹莓派設備 IDSERVER_IP = "192.168.1.100"  # 改成你電腦的實際 IPSERVER_PORT = 8000

            server_url: 伺服器 URL

        """SERVER_PORT = 8000BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

        self.device_id = device_id

        self.server_url = server_urlBASE_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

        

    def check_connection(self) -> bool:class RaspberryPiClient:

        """檢查與伺服器的連線"""

        try:    """樹莓派 API 客戶端"""

            response = requests.get(f"{self.server_url}/", timeout=5)

            return response.status_code == 200class RaspberryPiClient:    

        except:

            return False    """樹莓派 API 客戶端"""    def __init__(self, device_id: str, server_url: str = BASE_URL):

    

    def upload_image(self, image_path: str) -> Dict[str, Any]:            self.device_id = device_id

        """

        上傳圖片到伺服器    def __init__(self, device_id: str, server_url: str = BASE_URL):        self.server_url = server_url

        

        參數:        """        

            image_path: 本地圖片檔案路徑

                初始化客戶端    def upload_image_to_server(self, image_path: str) -> Dict[str, Any]:

        回傳:

            API 回應 JSON                """

        """

        try:        參數:        上傳圖片到伺服器

            if not os.path.exists(image_path):

                return {"success": False, "error": f"File not found: {image_path}"}            device_id: 樹莓派設備 ID        

            

            url = f"{self.server_url}/upload_image"            server_url: 伺服器 URL        參數:

            with open(image_path, "rb") as f:

                files = {"file": (os.path.basename(image_path), f, "image/jpeg")}        """            image_path: 本地圖片檔案路徑

                response = requests.post(url, files=files, timeout=30)

                        self.device_id = device_id        

                if response.status_code == 200:

                    return response.json()        self.server_url = server_url        回傳:

                else:

                    return {                    API 回應 JSON

                        "success": False,

                        "error": f"Server returned status {response.status_code}",    def check_connection(self) -> bool:        """

                        "details": response.text

                    }        """檢查與伺服器的連線"""        try:

                    

        except requests.exceptions.RequestException as e:        try:            # 檢查檔案是否存在

            return {"success": False, "error": f"Network error: {str(e)}"}

        except Exception as e:            response = requests.get(f"{self.server_url}/", timeout=5)            if not os.path.exists(image_path):

            return {"success": False, "error": f"Unexpected error: {str(e)}"}

                return response.status_code == 200                return {"success": False, "error": f"File not found: {image_path}"}

    def list_images(self) -> Dict[str, Any]:

        """        except:            

        獲取伺服器上所有圖片列表

                    return False            # 開啟檔案並上傳

        回傳:

            圖片列表                url = f"{self.server_url}/upload_image"

        """

        try:    def upload_image(self, image_path: str) -> Dict[str, Any]:            with open(image_path, "rb") as f:

            url = f"{self.server_url}/images"

            response = requests.get(url, timeout=10)        """                files = {"file": (os.path.basename(image_path), f, "image/jpeg")}

            

            if response.status_code == 200:        上傳圖片到伺服器                response = requests.post(url, files=files, timeout=30)

                return response.json()

            else:                    

                return {

                    "success": False,        參數:            if response.status_code == 200:

                    "error": f"Server returned status {response.status_code}"

                }            image_path: 本地圖片檔案路徑                return response.json()

                

        except Exception as e:                    else:

            return {"success": False, "error": str(e)}

            回傳:                return {

    def download_image(self, filename: str, save_path: str) -> Dict[str, Any]:

        """            API 回應 JSON                    "success": False,

        從伺服器下載圖片

                """                    "error": f"Server returned status code {response.status_code}",

        參數:

            filename: 要下載的圖片檔名        try:                    "details": response.text

            save_path: 儲存到本地的路徑

                    if not os.path.exists(image_path):                }

        回傳:

            下載結果                return {"success": False, "error": f"File not found: {image_path}"}                

        """

        try:                except requests.exceptions.RequestException as e:

            url = f"{self.server_url}/images/{filename}"

            response = requests.get(url, timeout=30, stream=True)            url = f"{self.server_url}/upload_image"        return {"success": False, "error": f"Network error: {str(e)}"}

            

            if response.status_code == 200:            with open(image_path, "rb") as f:    except Exception as e:

                with open(save_path, "wb") as f:

                    for chunk in response.iter_content(chunk_size=8192):                files = {"file": (os.path.basename(image_path), f, "image/jpeg")}        return {"success": False, "error": f"Unexpected error: {str(e)}"}

                        f.write(chunk)

                                response = requests.post(url, files=files, timeout=30)

                return {

                    "success": True,                # 使用範例

                    "message": "Image downloaded successfully",

                    "filename": filename,                if response.status_code == 200:if __name__ == "__main__":

                    "save_path": save_path,

                    "size": os.path.getsize(save_path)                    return response.json()    # 改成你的伺服器 IP 和圖片路徑

                }

            else:                else:    SERVER_URL = "http://192.168.1.100:8000/upload_image"  # 改成你電腦的實際 IP

                return {

                    "success": False,                    return {    IMAGE_PATH = "/home/pi/Pictures/test.jpg"  # 改成樹莓派上的圖片路徑

                    "error": f"Server returned status {response.status_code}"

                }                        "success": False,    

                

        except Exception as e:                        "error": f"Server returned status {response.status_code}",    print(f"Uploading image: {IMAGE_PATH}")

            return {"success": False, "error": str(e)}

                            "details": response.text    print(f"To server: {SERVER_URL}")

    def send_sensor_data(self, temperature: Optional[float] = None,

                         humidity: Optional[float] = None,                    }    

                         light: Optional[int] = None,

                         motion: Optional[bool] = None,                        result = upload_image_to_server(IMAGE_PATH, SERVER_URL)

                         custom_data: Optional[Dict] = None) -> Dict[str, Any]:

        """        except requests.exceptions.RequestException as e:    

        發送感測器數據到伺服器

                    return {"success": False, "error": f"Network error: {str(e)}"}    if result.get("success"):

        參數:

            temperature: 溫度 (攝氏)        except Exception as e:        print(f"✓ Upload successful!")

            humidity: 濕度 (%)

            light: 光線強度 (0-1023)            return {"success": False, "error": f"Unexpected error: {str(e)}"}        print(f"  Filename: {result.get('filename')}")

            motion: 是否偵測到移動

            custom_data: 其他自訂資料            print(f"  Size: {result.get('size')} bytes")

        

        回傳:    def send_sensor_data(self, temperature: Optional[float] = None,    else:

            API 回應 JSON

        """                         humidity: Optional[float] = None,        print(f"✗ Upload failed!")

        try:

            url = f"{self.server_url}/sensor_data"                         light: Optional[int] = None,        print(f"  Error: {result.get('error')}")

            data = {

                "device_id": self.device_id,                         motion: Optional[bool] = None,

                "temperature": temperature,                         custom_data: Optional[Dict] = None) -> Dict[str, Any]:

                "humidity": humidity,        """

                "light": light,        發送感測器數據到伺服器

                "motion": motion,        

                "custom_data": custom_data        參數:

            }            temperature: 溫度 (攝氏)

                        humidity: 濕度 (%)

            response = requests.post(url, json=data, timeout=10)            light: 光線強度 (0-1023)

                        motion: 是否偵測到移動

            if response.status_code == 200:            custom_data: 其他自訂資料

                return response.json()        

            else:        回傳:

                return {            API 回應 JSON

                    "success": False,        """

                    "error": f"Server returned status {response.status_code}"        try:

                }            url = f"{self.server_url}/sensor_data"

                            data = {

        except Exception as e:                "device_id": self.device_id,

            return {"success": False, "error": str(e)}                "temperature": temperature,

                    "humidity": humidity,

    def update_status(self, status: str, message: Optional[str] = None,                "light": light,

                     battery_level: Optional[float] = None) -> Dict[str, Any]:                "motion": motion,

        """                "custom_data": custom_data

        更新設備狀態            }

                    

        參數:            response = requests.post(url, json=data, timeout=10)

            status: 狀態 (online, offline, busy, idle, error)            

            message: 狀態訊息            if response.status_code == 200:

            battery_level: 電池電量 (0-100)                return response.json()

                    else:

        回傳:                return {

            API 回應 JSON                    "success": False,

        """                    "error": f"Server returned status {response.status_code}"

        try:                }

            url = f"{self.server_url}/device_status"                

            data = {        except Exception as e:

                "device_id": self.device_id,            return {"success": False, "error": str(e)}

                "status": status,    

                "message": message,    def update_status(self, status: str, message: Optional[str] = None,

                "battery_level": battery_level                     battery_level: Optional[float] = None) -> Dict[str, Any]:

            }        """

                    更新設備狀態

            response = requests.post(url, json=data, timeout=10)        

                    參數:

            if response.status_code == 200:            status: 狀態 (online, offline, busy, idle, error)

                return response.json()            message: 狀態訊息

            else:            battery_level: 電池電量 (0-100)

                return {        

                    "success": False,        回傳:

                    "error": f"Server returned status {response.status_code}"            API 回應 JSON

                }        """

                        try:

        except Exception as e:            url = f"{self.server_url}/device_status"

            return {"success": False, "error": str(e)}            data = {

                    "device_id": self.device_id,

    def get_pending_commands(self) -> Dict[str, Any]:                "status": status,

        """                "message": message,

        獲取待執行的指令                "battery_level": battery_level

                    }

        回傳:            

            待執行指令列表            response = requests.post(url, json=data, timeout=10)

        """            

        try:            if response.status_code == 200:

            url = f"{self.server_url}/commands/{self.device_id}"                return response.json()

            response = requests.get(url, timeout=10)            else:

                            return {

            if response.status_code == 200:                    "success": False,

                return response.json()                    "error": f"Server returned status {response.status_code}"

            else:                }

                return {                

                    "success": False,        except Exception as e:

                    "error": f"Server returned status {response.status_code}"            return {"success": False, "error": str(e)}

                }    

                    def get_pending_commands(self) -> Dict[str, Any]:

        except Exception as e:        """

            return {"success": False, "error": str(e)}        獲取待執行的指令

        

        回傳:

# ===== 使用範例 =====            待執行指令列表

        """

def example_list_and_download_images():        try:

    """範例：查看和下載圖片"""            url = f"{self.server_url}/commands/{self.device_id}"

    print("\n=== 範例: 查看和下載圖片 ===")            response = requests.get(url, timeout=10)

    client = RaspberryPiClient("pi_001")            

                if response.status_code == 200:

    # 列出所有圖片                return response.json()

    result = client.list_images()            else:

                    return {

    if result.get("success"):                    "success": False,

        images = result.get("images", [])                    "error": f"Server returned status {response.status_code}"

        print(f"✓ 找到 {len(images)} 張圖片")                }

                        

        for i, img in enumerate(images[:5], 1):  # 只顯示前 5 張        except Exception as e:

            print(f"\n  [{i}] 檔名: {img['filename']}")            return {"success": False, "error": str(e)}

            print(f"      大小: {img['size']} bytes")    

            print(f"      建立時間: {img['created_time']}")    def list_images(self) -> Dict[str, Any]:

            print(f"      查看網址: http://localhost:8000{img['view_url']}")        """

                獲取伺服器上所有圖片列表

        # 下載第一張圖片（如果有的話）        

        if images:        回傳:

            first_image = images[0]['filename']            圖片列表

            save_path = f"/tmp/{first_image}"  # Linux/樹莓派路徑        """

            # save_path = f"C:/Users/User/Downloads/{first_image}"  # Windows 路徑        try:

                        url = f"{self.server_url}/images"

            print(f"\n  正在下載第一張圖片: {first_image}")            response = requests.get(url, timeout=10)

            download_result = client.download_image(first_image, save_path)            

                        if response.status_code == 200:

            if download_result.get("success"):                return response.json()

                print(f"  ✓ 下載成功! 儲存於: {save_path}")            else:

            else:                return {

                print(f"  ✗ 下載失敗: {download_result.get('error')}")                    "success": False,

    else:                    "error": f"Server returned status {response.status_code}"

        print(f"✗ 查詢失敗: {result.get('error')}")                }

                

        except Exception as e:

def example_upload_image():            return {"success": False, "error": str(e)}

    """範例：上傳圖片"""    

    print("\n=== 範例 1: 上傳圖片 ===")    def download_image(self, filename: str, save_path: str) -> Dict[str, Any]:

    client = RaspberryPiClient("pi_001")        """

            從伺服器下載圖片

    # 這裡改成你的圖片路徑        

    image_path = "/home/pi/Pictures/test.jpg"  # Linux/樹莓派路徑        參數:

    # image_path = "C:/Users/User/Pictures/test.jpg"  # Windows 路徑            filename: 要下載的圖片檔名

                save_path: 儲存到本地的路徑

    result = client.upload_image(image_path)        

            回傳:

    if result.get("success"):            下載結果

        print(f"✓ 圖片上傳成功!")        """

        print(f"  檔名: {result.get('filename')}")        try:

        print(f"  大小: {result.get('size')} bytes")            url = f"{self.server_url}/images/{filename}"

        print(f"  查看網址: http://localhost:8000{result.get('view_url')}")            response = requests.get(url, timeout=30, stream=True)

    else:            

        print(f"✗ 上傳失敗: {result.get('error')}")            if response.status_code == 200:

                with open(save_path, "wb") as f:

                    for chunk in response.iter_content(chunk_size=8192):

def example_send_sensor_data():                        f.write(chunk)

    """範例：發送感測器數據"""                

    print("\n=== 範例 2: 發送感測器數據 ===")                return {

    client = RaspberryPiClient("pi_001")                    "success": True,

                        "message": "Image downloaded successfully",

    # 模擬感測器數據 (實際使用時從感測器讀取)                    "filename": filename,

    result = client.send_sensor_data(                    "save_path": save_path,

        temperature=25.5,                    "size": os.path.getsize(save_path)

        humidity=60.3,                }

        light=512,            else:

        motion=False,                return {

        custom_data={"cpu_temp": 45.2, "uptime": 3600}                    "success": False,

    )                    "error": f"Server returned status {response.status_code}"

                    }

    if result.get("success"):                

        print(f"✓ 數據發送成功!")        except Exception as e:

        print(f"  時間戳: {result.get('timestamp')}")            return {"success": False, "error": str(e)}

    else:

        print(f"✗ 發送失敗: {result.get('error')}")

# ===== 使用範例 =====



def example_update_status():def example_upload_image():

    """範例：更新設備狀態"""    """範例：上傳圖片"""

    print("\n=== 範例 3: 更新設備狀態 ===")    print("\n=== 範例 1: 上傳圖片 ===")

    client = RaspberryPiClient("pi_001")    client = RaspberryPiClient("pi_001")

        

    result = client.update_status(    # 這裡改成你的圖片路徑

        status="online",    image_path = "/home/pi/Pictures/test.jpg"  # Linux/樹莓派路徑

        message="系統運行正常",    # image_path = "C:/Users/User/Pictures/test.jpg"  # Windows 路徑

        battery_level=85.5    

    )    result = client.upload_image(image_path)

        

    if result.get("success"):    if result.get("success"):

        print(f"✓ 狀態更新成功!")        print(f"✓ 圖片上傳成功!")

        print(f"  狀態: {result.get('status')}")        print(f"  檔名: {result.get('filename')}")

    else:        print(f"  大小: {result.get('size')} bytes")

        print(f"✗ 更新失敗: {result.get('error')}")    else:

        print(f"✗ 上傳失敗: {result.get('error')}")



def example_check_commands():

    """範例：檢查待執行指令"""def example_send_sensor_data():

    print("\n=== 範例 4: 檢查待執行指令 ===")    """範例：發送感測器數據"""

    client = RaspberryPiClient("pi_001")    print("\n=== 範例 2: 發送感測器數據 ===")

        client = RaspberryPiClient("pi_001")

    result = client.get_pending_commands()    

        # 模擬感測器數據 (實際使用時從感測器讀取)

    if "pending_commands" in result:    result = client.send_sensor_data(

        commands = result["pending_commands"]        temperature=25.5,

        print(f"✓ 收到 {len(commands)} 個待執行指令")        humidity=60.3,

        for cmd in commands:        light=512,

            print(f"  - 指令: {cmd.get('command')}")        motion=False,

            print(f"    參數: {cmd.get('parameters')}")        custom_data={"cpu_temp": 45.2, "uptime": 3600}

    else:    )

        print(f"✗ 查詢失敗: {result.get('error')}")    

    if result.get("success"):

        print(f"✓ 數據發送成功!")

def example_continuous_monitoring():        print(f"  時間戳: {result.get('timestamp')}")

    """範例：持續監控並發送數據"""    else:

    print("\n=== 範例 5: 持續監控 (每 10 秒發送一次) ===")        print(f"✗ 發送失敗: {result.get('error')}")

    print("按 Ctrl+C 停止")

    

    client = RaspberryPiClient("pi_001")def example_update_status():

        """範例：更新設備狀態"""

    # 先檢查連線    print("\n=== 範例 3: 更新設備狀態 ===")

    if not client.check_connection():    client = RaspberryPiClient("pi_001")

        print("✗ 無法連接到伺服器，請檢查網路和伺服器狀態")    

        return    result = client.update_status(

            status="online",

    print("✓ 已連接到伺服器")        message="系統運行正常",

            battery_level=85.5

    try:    )

        while True:    

            # 模擬感測器讀取 (實際使用時從真實感測器讀取)    if result.get("success"):

            temperature = 20 + random.uniform(-5, 10)        print(f"✓ 狀態更新成功!")

            humidity = 50 + random.uniform(-20, 30)        print(f"  狀態: {result.get('status')}")

            light = random.randint(0, 1023)    else:

                    print(f"✗ 更新失敗: {result.get('error')}")

            # 發送數據

            result = client.send_sensor_data(

                temperature=round(temperature, 1),def example_check_commands():

                humidity=round(humidity, 1),    """範例：檢查待執行指令"""

                light=light    print("\n=== 範例 4: 檢查待執行指令 ===")

            )    client = RaspberryPiClient("pi_001")

                

            if result.get("success"):    result = client.get_pending_commands()

                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ 數據已發送 - "    

                      f"溫度: {temperature:.1f}°C, 濕度: {humidity:.1f}%, 光線: {light}")    if "pending_commands" in result:

            else:        commands = result["pending_commands"]

                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ 發送失敗")        print(f"✓ 收到 {len(commands)} 個待執行指令")

                    for cmd in commands:

            # 檢查是否有新指令            print(f"  - 指令: {cmd.get('command')}")

            commands = client.get_pending_commands()            print(f"    參數: {cmd.get('parameters')}")

            if commands.get("count", 0) > 0:    else:

                print(f"  ⚠ 收到 {commands['count']} 個待執行指令")        print(f"✗ 查詢失敗: {result.get('error')}")

            

            time.sleep(10)  # 等待 10 秒

            def example_continuous_monitoring():

    except KeyboardInterrupt:    """範例：持續監控並發送數據"""

        print("\n\n已停止監控")    print("\n=== 範例 5: 持續監控 (每 10 秒發送一次) ===")

    print("按 Ctrl+C 停止")

    

if __name__ == "__main__":    client = RaspberryPiClient("pi_001")

    print("🤖 樹莓派 API 客戶端範例")    

    print(f"📡 伺服器位址: {BASE_URL}")    # 先檢查連線

    print("\n請選擇要執行的範例:")    if not client.check_connection():

    print("1. 上傳圖片")        print("✗ 無法連接到伺服器，請檢查網路和伺服器狀態")

    print("2. 發送感測器數據")        return

    print("3. 更新設備狀態")    

    print("4. 檢查待執行指令")    print("✓ 已連接到伺服器")

    print("5. 持續監控 (每 10 秒發送一次)")    

    print("6. 查看和下載圖片 ⭐ 新功能")    try:

    print("0. 全部執行 (範例 2-4, 6)")        while True:

                # 模擬感測器讀取 (實際使用時從真實感測器讀取)

    choice = input("\n請輸入選項 (0-6): ").strip()            temperature = 20 + random.uniform(-5, 10)

                humidity = 50 + random.uniform(-20, 30)

    if choice == "1":            light = random.randint(0, 1023)

        example_upload_image()            

    elif choice == "2":            # 發送數據

        example_send_sensor_data()            result = client.send_sensor_data(

    elif choice == "3":                temperature=round(temperature, 1),

        example_update_status()                humidity=round(humidity, 1),

    elif choice == "4":                light=light

        example_check_commands()            )

    elif choice == "5":            

        example_continuous_monitoring()            if result.get("success"):

    elif choice == "6":                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ 數據已發送 - "

        example_list_and_download_images()                      f"溫度: {temperature:.1f}°C, 濕度: {humidity:.1f}%, 光線: {light}")

    elif choice == "0":            else:

        example_send_sensor_data()                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ 發送失敗")

        example_update_status()            

        example_check_commands()            # 檢查是否有新指令

        example_list_and_download_images()            commands = client.get_pending_commands()

        print("\n提示: 範例 1 需要實際圖片路徑，請單獨執行")            if commands.get("count", 0) > 0:

    else:                print(f"  ⚠ 收到 {commands['count']} 個待執行指令")

        print("無效的選項")            

            time.sleep(10)  # 等待 10 秒
            
    except KeyboardInterrupt:
        print("\n\n已停止監控")


if __name__ == "__main__":
    print("🤖 樹莓派 API 客戶端範例")
    print(f"📡 伺服器位址: {BASE_URL}")
    print("\n請選擇要執行的範例:")
    print("1. 上傳圖片")
    print("2. 發送感測器數據")
    print("3. 更新設備狀態")
    print("4. 檢查待執行指令")
    print("5. 持續監控 (每 10 秒發送一次)")
    print("0. 全部執行 (範例 1-4)")
    
    choice = input("\n請輸入選項 (0-5): ").strip()
    
    if choice == "1":
        example_upload_image()
    elif choice == "2":
        example_send_sensor_data()
    elif choice == "3":
        example_update_status()
    elif choice == "4":
        example_check_commands()
    elif choice == "5":
        example_continuous_monitoring()
    elif choice == "0":
        example_send_sensor_data()
        example_update_status()
        example_check_commands()
        print("\n提示: 範例 1 需要實際圖片路徑，請單獨執行")
    else:
        print("無效的選項")
