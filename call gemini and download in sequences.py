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
    try:
        image = Image.open(image_path)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        response = model.generate_content([
            "Extract all text visible in this image. Output only the extracted text, no commentary.",
            image
        ])
        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"

def get_next_file_number(download_dir):
    """獲取下一個 testpic 檔案編號"""
    existing_files = glob.glob(os.path.join(download_dir, "testpic*"))
    nums = []
    for file in existing_files:
        base = os.path.basename(file)
        try:
            num = int(base.replace("testpic", ""))
            nums.append(num)
        except ValueError:
            continue
    return max(nums) + 1 if nums else 1

def process_image_and_save(image_path, download_dir):
    """處理圖片並保存提取的文字"""
    try:
        print(f"正在處理圖片: {image_path}")
        extracted_text = extract_text_with_gemini(image_path)
        next_num = get_next_file_number(download_dir)
        filename = f"testpic{next_num}.txt"
        file_path = os.path.join(download_dir, filename)
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
    image_path = "D:\\user\\test.jpg"
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
        print(f"無效的路徑: {image_path}")