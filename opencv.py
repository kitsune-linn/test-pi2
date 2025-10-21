import cv2
import pytesseract
import re

# Tesseract 路徑
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 修正路徑（請將圖片路徑替換為你的實際路徑）
image = cv2.imread(r'C:\Program Files\Tesseract-OCR\pictest4.jpg')

if image is None:
    print("❌ 圖片載入失敗，請檢查路徑")
    exit()

# 放大圖片 (可調整縮放比例)
resized = cv2.resize(image, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

# 1. 強力去噪：中值濾波 (較大的 kernel size)
denoised = cv2.medianBlur(gray, 7)

# 2. 二值化 (嘗試不同的自適應閾值參數)
thresh = cv2.adaptiveThreshold(denoised, 255,
                                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV,
                                     blockSize=19,
                                     C=5)

# # 3. 強力形態學開運算 (較大的 kernel 和多次迭代)
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
# opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

# 4. 再次中值濾波 (去除形態學操作可能引入的細小噪點)
final_denoised = cv2.medianBlur(thresh, 3)

# 顯示最終預處理結果
cv2.imshow("Final Preprocessed", final_denoised)
cv2.waitKey(5000)
cv2.destroyAllWindows()

# OCR 辨識
config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789+-*=?='
ocr_result = pytesseract.image_to_string(final_denoised, config=config)
print("原始識別：\n", ocr_result)

# 提取算式 (按行分割)
expressions = [line.strip() for line in ocr_result.splitlines() if line.strip()]
print("提取的算式（按行）：")
for expression in expressions:
    print(expression)

# 嘗試計算
print("\n計算結果：")
for expression in expressions:
    try:
        if "=" in expression:
            parts = expression.split("=")
            if len(parts) >= 2:
                left_side = parts[0]
                try:
                    result = eval(left_side)
                    print(f"✅ {left_side} = {result}")
                except Exception as e:
                    print(f"⚠️ 無法計算 {left_side} (eval 錯誤): {e}")
            else:
                print(f"⚠️ 無法計算（提取結果格式不符 - 沒有等號後的部分）: {expression}")
        elif expression:
            print(f"⚠️ 提取到算式，但沒有等號：{expression}")
        else:
            print("⚠️ 無法計算（提取結果為空）")
    except Exception as e:
        print(f"⚠️ 計算 {expression} 時發生錯誤: {e}")