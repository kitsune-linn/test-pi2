import os
from PIL import Image
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")

# Configure the Gemini API
genai.configure(api_key=api_key)

def extract_text_from_image(image_path):
    try:
        # Open the image
        image = Image.open(image_path)
        
        # Create a Gemini model instance configured for the flash-lite model
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        # Generate content from the image
        response = model.generate_content(
            [
                "Extract all text visible in this image. Output only the extracted text, no commentary.",
                image
            ]
        )
        
        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"

# Set up a LangChain chain to process the extracted text
def analyze_extracted_text(extracted_text):
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0)
    
    # Get analysis from the LLM
    result = llm.invoke(f"""
    Analyze the following text extracted from an image:
    
    {extracted_text}
    
    Provide a brief summary of what this text contains and its likely context.
    """)
    
    return result.content

# Example usage
if __name__ == "__main__":
    # Path to your image
    image_path = "C:\Program Files\Tesseract-OCR\pictest1.jpg"
    
    # Extract text from the image
    print("Extracting text from image...")
    extracted_text = extract_text_from_image(image_path)
    print(f"Extracted text:\n{extracted_text}\n")
    
    # # Analyze the extracted text
    # print("Analyzing extracted text...")
    # analysis = analyze_extracted_text(extracted_text)
    # print(f"Analysis:\n{analysis}")
