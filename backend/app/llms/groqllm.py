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
            llm = ChatGroq(
                groq_api_key=self.groq_api_key,
                model_name="qwen/qwen3.6-27b",
                max_tokens=600,
                model_kwargs={"extra_body": {"reasoning_format": "hidden"}},
            )
            return llm 
        except Exception as e:
            raise ValueError(f"Error in groqllm : {e}")  

            
                
        
        

