import RPi.GPIO as GPIO
import time
import os
import paramiko

# === GPIO 腳位設定 ===
GPIO.setmode(GPIO.BCM)
button_pin = 17
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# === 電腦連線設定 ===
PC_IP = "192.168.1.100"           # 你的電腦 IP
PC_USER = "Norman"                # 你的 Windows 使用者名稱
PC_PASS = "你的登入密碼"          # 你的 Windows 密碼
PC_DESKTOP = "C:/Users/Norman/Desktop/"  # 桌面路徑

print("📸 按下按鈕拍照並傳送到桌面（Ctrl+C 結束）")

try:
    while True:
        if GPIO.input(button_pin) == GPIO.HIGH:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            local_path = f"/home/pi/Pictures/photo_{timestamp}.jpg"

            # 拍照
            os.system(f"libcamera-still -o {local_path} -n")
            print(f"✅ 拍照完成：{local_path}")

            # 建立 SSH/SFTP 傳檔
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(PC_IP, username=PC_USER, password=PC_PASS)

                sftp = ssh.open_sftp()
                remote_path = os.path.join(PC_DESKTOP, f"photo_{timestamp}.jpg")
                sftp.put(local_path, remote_path)
                sftp.close()
                ssh.close()

                print(f"💾 已複製到你的電腦桌面：{remote_path}")
            except Exception as e:
                print(f"⚠️ 傳輸失敗：{e}")

            # 等待放開按鈕
            time.sleep(0.5)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n程式結束")
finally:
    GPIO.cleanup()