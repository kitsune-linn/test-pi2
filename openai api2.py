import os
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv  # 導入 load_dotenv
import glob


# 載入 .env 檔案
load_dotenv()

def get_next_file_number(download_dir):
    """獲取下一個 testpic 檔案編號"""
    existing_files = glob.glob(os.path.join(download_dir, "testpic*"))
    
    if not existing_files:
        return 1
    
    nums = []
    for file in existing_files:
        base = os.path.basename(file)
        try:
            num = int(base.replace("testpic", ""))
            nums.append(num)
        except ValueError:
            continue
    
    return max(nums) + 1 if nums else 1
    
def extract_text_with_gemini(image_path):
    """使用 Gemini 模型從圖片提取文字"""
    # 初始化 Gemini 模型
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",  # 使用 gemini-2.0-flash-lite 模型
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
        temperature=0
    )
    
    # 開啟圖片
    try:
        image = Image.open(image_path)
    except Exception as e:
        raise Exception(f"無法開啟圖片 {image_path}: {e}")
    
    # 構建提示
    prompt = PromptTemplate(
        input_variables=["image_data"],
        template="""你是一個專業的 OCR 助手。請分析這張圖片中的所有文字內容，並提取出所有可見文字。
只需返回提取到的文字內容，保持原始格式和結構，不要添加任何解釋或說明。
如果圖像中有表格，請盡量保持表格結構。
保持段落和行的分隔，確保文字按照圖像中的順序排列。"""
    )
    
    # 創建 LangChain 鏈
    chain = LLMChain(llm=model, prompt=prompt)
    
    # 執行鏈，直接傳遞圖片物件
    result = chain.run(image_data=image)
    
    return result

def process_image_and_save(image_path, download_dir):
    """處理圖片並保存提取的文字"""
    try:
        # 提取文字
        print(f"正在處理圖片: {image_path}")
        extracted_text = extract_text_with_gemini(image_path)
        
        # 獲取下一個檔案編號
        next_num = get_next_file_number(download_dir)
        filename = f"testpic{next_num}"
        file_path = os.path.join(download_dir, filename)
        
        # 將文字儲存到檔案
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

# 主程式
if __name__ == "__main__":
    # 設定 Google API 金鑰
    # 使用 load_dotenv 讀取 .env 檔案中的金鑰
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY") 
    
    # 設定圖片路徑和下載目錄
    image_path = "C:\\Program Files\\Tesseract-OCR\\pictest1.jpg" # 提示用戶輸入圖片路徑
    download_dir = os.path.expanduser("~/Downloads")
    
    if os.path.isfile(image_path):
        # 處理單張圖片
        result = process_image_and_save(image_path, download_dir)
        if result["status"] == "success":
            print(f"處理成功！文字已儲存為: {result['filename']}")
        else:
            print(f"處理失敗: {result['error']}")
    else:
        print(f"無效的路徑: {image_path}")
