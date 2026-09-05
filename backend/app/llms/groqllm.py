#======================================================
# This file is to get the groq llm 
#======================================================
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
import os 
from dotenv import load_dotenv

#create class to get the groq llm
class GetGroqLLM:
    def __init__(self):
        load_dotenv()

    def get_groq_llm(self):
        try:
            raw_key = os.getenv("GROQ_API_KEY")
            if not raw_key:
                raise ValueError("GROQ_API_KEY not found in environment variables.")
            self.groq_api_key = raw_key.strip().splitlines()[0].strip()
            os.environ["GROQ_API_KEY"] = self.groq_api_key
            model_name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
            llm = ChatGroq(
                groq_api_key=self.groq_api_key,
                model_name=model_name,
                max_tokens=700,
            )
            return llm 
        except Exception as e:
            raise ValueError(f"Error in groqllm : {e}")  

            
                
        
        

