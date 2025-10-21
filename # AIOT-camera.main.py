# AIOT-camera
import os
import argparse
import base64
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv  # 導入 load_dotenv
import glob


# 載入 .env 檔案
load_dotenv(override=True)

def get_next_file_number(download_dir, prefix="testpic"):
    """獲取下一個檔案編號"""
    existing_files = glob.glob(os.path.join(download_dir, f"{prefix}*"))
    
    if not existing_files:
        return 1
    
    nums = []
    for file in existing_files:
        base = os.path.basename(file)
        try:
            num = int(base.replace(prefix, ""))
            nums.append(num)
        except ValueError:
            continue
    
    return max(nums) + 1 if nums else 1
    
def extract_text_with_gemini(image_path):
    """使用 Gemini 模型從圖片提取文字"""
    # 初始化 Gemini 模型
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",  # 使用支援圖片的模型
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
        temperature=0
    )
    
    # 開啟並處理圖片
    try:
        # 將圖片轉換為 base64 格式
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # 獲取圖片的 MIME 類型
        image = Image.open(image_path)
        image_format = image.format
        if image_format:
            image_format = image_format.lower()
            if image_format == 'jpeg':
                image_format = 'jpg'
        else:
            # 如果無法獲取格式，從檔案副檔名推測
            _, ext = os.path.splitext(image_path.lower())
            image_format = ext[1:] if ext else 'jpg'
        mime_type = f"image/{image_format}"
        
    except Exception as e:
        raise Exception(f"無法開啟圖片 {image_path}: {e}")
    
    # 構建消息
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "你是一個專業的 OCR 助手。請分析這張圖片中的所有文字內容，並提取出所有可見文字。只需返回提取到的文字內容，保持原始格式和結構，不要添加任何解釋或說明。如果圖像中有表格，請盡量保持表格結構。保持段落和行的分隔，確保文字按照圖像中的順序排列。"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_data}"
                }
            }
        ]
    )
    
    # 調用模型
    try:
        response = model.invoke([message])
        return response.content
    except Exception as e:
        raise Exception(f"API 調用失敗: {e}")

def process_image_and_save(image_path, download_dir, prefix="testpic"):
    """處理圖片並保存提取的文字"""
    try:
        # 提取文字
        print(f"正在處理圖片: {image_path}")
        extracted_text = extract_text_with_gemini(image_path)
        
        # 獲取下一個檔案編號
        next_num = get_next_file_number(download_dir, prefix)
        filename = f"{prefix}{next_num}"
        file_path = os.path.join(download_dir, filename)
        
        # 將文字儲存到檔案
        with open(file_path, "w", encoding="utf-8") as f:
            # 確保 extracted_text 是字串格式
            if isinstance(extracted_text, str):
                f.write(extracted_text)
            else:
                f.write(str(extracted_text))
        
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

def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description="AIOT Camera - 使用 Gemini AI 從圖片中提取文字",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python main.py image.jpg
  python main.py image.jpg -o ~/Documents
  python main.py image.jpg -o ~/Documents -p extracted_text
        """
    )
    
    parser.add_argument(
        "image_path",
        help="要處理的圖片檔案路徑"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        default=os.path.expanduser("~/Downloads"),
        help="輸出目錄 (預設: ~/Downloads)"
    )
    
    parser.add_argument(
        "-p", "--prefix",
        default="testpic",
        help="輸出檔案名稱前綴 (預設: testpic)"
    )
    
    return parser.parse_args()

# 主程式
if __name__ == "__main__":
    # 解析命令列參數
    args = parse_arguments()
    args.image_path = "C:\\Users\\Ethan\\Pictures\\test.jpg"
    image_path = "D:\\user\\test.jpg"
    # 設定 Google API 金鑰
    # 使用 load_dotenv 讀取 .env 檔案中的金鑰
    load_dotenv(override=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    else:
        print("錯誤: 找不到 GOOGLE_API_KEY 環境變數")
        print("請在 .env 檔案中設定 GOOGLE_API_KEY")
        exit(1)
    
    # 驗證圖片路徑
    if not os.path.isfile(args.image_path):
        print(f"錯誤: 找不到圖片檔案: {args.image_path}")
        exit(1)
    
    # 確保輸出目錄存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 處理圖片
    result = process_image_and_save(args.image_path, args.output_dir, args.prefix)
    if result["status"] == "success":
        print(f"處理成功！文字已儲存為: {result['filename']}")
        print(f"完整路徑: {result['file_path']}")
    else:
        print(f"處理失敗: {result['error']}")
        exit(1)