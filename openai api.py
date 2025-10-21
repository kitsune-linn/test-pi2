import os
import glob
import base64
from PIL import Image
from io import BytesIO
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def encode_image_to_base64(image_path):
    """将图片编码为base64字符串"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_next_file_number(download_dir):
    """获取下一个testpic文件编号"""
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
    """使用Gemini 2.0 Flash-Lite模型从图片提取文本"""
    # 初始化Gemini模型
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",  # 使用Flash-Lite版本
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
        temperature=0
    )
    
    # 读取图片并编码为base64
    base64_image = encode_image_to_base64(image_path)
    
    # 构建提示
    prompt = PromptTemplate(
        input_variables=["image_data"],
        template="""你是一个专业的OCR助手。请分析这张图片中的所有文本内容，并提取出所有可见文字。
只需返回提取到的文本内容，保持原始格式和结构，不要添加任何解释或说明。
如果图像中有表格，请尽量保持表格结构。
保持段落和行的分隔，确保文本按照图像中的顺序排列。

图片数据: {image_data}"""
    )
    
    # 创建LangChain链
    chain = LLMChain(llm=model, prompt=prompt)
    
    # 执行链
    result = chain.run(image_data=f"data:image/jpeg;base64,{base64_image}")
    
    return result

def process_image_and_save(image_path, download_dir):
    """处理图片并保存提取的文本"""
    try:
        # 提取文本
        print(f"正在处理图片: {image_path}")
        extracted_text = extract_text_with_gemini(image_path)
        
        # 获取下一个文件编号
        next_num = get_next_file_number(download_dir)
        filename = f"testpic{next_num}"
        file_path = os.path.join(download_dir, filename)
        
        # 保存文本到文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        
        print(f"文本已保存至: {file_path}")
        return {
            "status": "success",
            "filename": filename,
            "file_path": file_path
        }
    except Exception as e:
        print(f"处理失败: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

def batch_process_images(image_dir, download_dir):
    """批量处理目录中的所有图片"""
    # 支持的图片扩展名
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
    
    # 获取所有图片文件
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(image_dir, f"*{ext}")))
        image_files.extend(glob.glob(os.path.join(image_dir, f"*{ext.upper()}")))
    
    if not image_files:
        print(f"在 {image_dir} 中未找到图片文件")
        return []
    
    print(f"找到 {len(image_files)} 个图片文件")
    results = []
    
    for image_path in image_files:
        result = process_image_and_save(image_path, download_dir)
        results.append({
            "image": os.path.basename(image_path),
            **result
        })
    
    return results

# 主程序
if __name__ == "__main__":
    # 设置Google API密钥
    # 请替换为您的实际API密钥
    os.environ["GOOGLE_API_KEY"] = "your-google-api-key"
    
    # 设置图片路径和下载目录
    image_path = input("请输入图片路径 (单个图片): ")
    download_dir = os.path.expanduser("~/Downloads")
    
    if os.path.isfile(image_path):
        # 处理单个图片
        result = process_image_and_save(image_path, download_dir)
        if result["status"] == "success":
            print(f"处理成功！文本已保存为: {result['filename']}")
        else:
            print(f"处理失败: {result['error']}")
    elif os.path.isdir(image_path):
        # 批量处理目录
        results = batch_process_images(image_path, download_dir)
        success_count = sum(1 for r in results if r["status"] == "success")
        print(f"批量处理完成: {success_count}/{len(results)} 个文件处理成功")
    else:
        print(f"无效的路径: {image_path}")