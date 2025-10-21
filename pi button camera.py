import RPi.GPIO as GPIO
import os
import time

# 腳位設定（一次搞定）
GPIO.setmode(GPIO.BCM)
button_pin = 17
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("📸 按下按鈕拍照（Ctrl+C 結束）")

try:
    while True:
        if GPIO.input(button_pin) == GPIO.HIGH:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"/home/pi/Pictures/photo_{timestamp}.jpg"
            os.system(f"libcamera-still -o {filename} -n")
            print(f"拍照完成：{filename}")
            time.sleep(0.5)  # 防止重複觸發
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n程式結束")
finally:
    GPIO.cleanup()