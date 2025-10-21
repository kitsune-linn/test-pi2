import os
import glob
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")

# Configure the Gemini API
genai.configure(api_key=api_key)

def extract_text_with_gemini(image_path):
    """
    使用 Gemini 模型從圖片中提取文字。
    :param image_path: 圖片檔案路徑。
    :return: 提取的文字內容或錯誤訊息。
    """
    try:
        image = Image.open(image_path)
        # 使用 gemini-2.5-flash-preview-09-2025 模型來確保兼容性和可靠性，並讓模型專注於 OCR 任務。
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([
            "Extract all text visible in this image. Output only the extracted text, strictly no commentary or formatting.",
            image
        ])
        return response.text
    except Exception as e:
        return f"Error processing image with Gemini API: {str(e)}"

def get_next_file_number(download_dir):
    """
    獲取下一個 testpic 檔案編號。
    此版本已修正：能夠正確處理帶有副檔名的檔案 (例如 testpic1.txt) 以進行編號。
    """
    # 搜尋所有以 'testpic' 開頭的檔案
    existing_files = glob.glob(os.path.join(download_dir, "testpic*"))
    nums = []
    
    for file in existing_files:
        base_with_ext = os.path.basename(file)
        
        # 💡 關鍵修正：將檔名與副檔名分離
        base_name, _ = os.path.splitext(base_with_ext) 
        
        try:
            # 💡 從不含副檔名的檔名中移除 'testpic'
            num_str = base_name.replace("testpic", "")
            
            # 確保移除 'testpic' 後剩下的部分是有效的數字
            if num_str.isdigit():
                 num = int(num_str)
                 nums.append(num)
            
        except ValueError:
            # 忽略無法轉換為數字的檔名 (例如 testpicA.txt)
            continue
            
    # 如果找到現有編號，則回傳最大編號 + 1；否則從 1 開始
    return max(nums) + 1 if nums else 1


def process_image_and_save(image_path, download_dir):
    """處理圖片並保存提取的文字"""
    try:
        print(f"正在處理圖片: {image_path}")
        
        # 1. 執行 OCR
        extracted_text = extract_text_with_gemini(image_path)
        
        # 2. 獲取下一個可用編號
        next_num = get_next_file_number(download_dir)
        
        # 3. 構建檔案名稱 (固定使用 .txt 副檔名)
        filename = f"testpic{next_num}.txt"
        file_path = os.path.join(download_dir, filename)
        
        # 4. 儲存文字結果
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
            
        print(f"文字已儲存至: {file_path}")
        
        return {
            "status": "success",
            "filename": filename,
            "file_path": file_path
        }
    except Exception as e:
        print(f"處理失敗: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

def read_saved_text(file_path):
    """讀取已儲存的文字檔案"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# 主程式
if __name__ == "__main__":
    # 建議使用 r'' 原始字串來處理 Windows 路徑，避免轉義問題
    # 請將此處的路徑替換為您圖片的實際路徑
    image_path = r"D:\Python-training\fastapi_server\uploads\pi_image_20251021_182551.jpg"
    
    # 使用 os.path.expanduser 確保 download_dir 是正確的下載目錄路徑
    download_dir = os.path.expanduser("~/Downloads")

    if os.path.isfile(image_path):
        result = process_image_and_save(image_path, download_dir)
        
        if result["status"] == "success":
            print(f"處理成功！檔案名為 : {result['filename']}")
            saved_text = read_saved_text(result['file_path'])
            print("\n--- 儲存的文字內容 ---\n")
            print(saved_text)
        else:
            print(f"處理失敗: {result['error']}")
    else:
        print(f"無效的路徑或檔案不存在: {image_path}")