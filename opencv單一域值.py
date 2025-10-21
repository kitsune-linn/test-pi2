import cv2
import pytesseract
import re

# Tesseract 路徑
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 修正路徑（方法 A：raw string）
image = cv2.imread(r'C:\Program Files\Tesseract-OCR\pictest1.jpg')

if image is None:
    print("❌ 圖片載入失敗，請檢查路徑")
    exit()

# 放大圖片 (可調整縮放比例)
resized = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

# 預處理：灰階 + 強化對比 (嘗試不同的 threshold 方法和參數)
# thresh = cv2.adaptiveThreshold(gray, 255,
#                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                 cv2.THRESH_BINARY_INV, 11, 2)
_, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# 顯示預處理結果
cv2.imshow("預處理", thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()

# OCR 辨識 (嘗試不同的 config)
config = r'--oem 3 --psm 6' # 嘗試不同的 psm 值 (3, 6, 7, 😎
ocr_result = pytesseract.image_to_string(thresh, config=config)
print("原始識別：\n", ocr_result)

# 提取算式
expression = re.sub(r'[^0-9+\-*/=]', '', ocr_result) # 包含 '='
expression = re.sub(r'[\+\-\*/]{2,}', '', expression)
print("提取的算式：", expression)

# 嘗試計算
try:
    if "=" in expression:
        parts = expression.split("=")
        if len(parts) == 2:
            left_side = parts[0]
            # 注意：這裡直接 eval 有安全風險，如果輸入來源不可信，請勿使用 eval
            result = eval(left_side)
            print("✅ 計算結果：", result)
        else:
            print("⚠️ 無法計算（提取結果格式不符）")
    elif expression:
        # 如果沒有 '=', 則只顯示提取的算式
        print("⚠️ 提取到算式，但沒有等號：", expression)
    else:
        print("⚠️ 無法計算（提取結果為空）")
except Exception as e:
    print("⚠️ 無法計算（格式錯誤）")
    print("錯誤原因：", e)