import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm(temperature=0.7):
    return ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=temperature,
        api_key=os.getenv("GROQ_API_KEY"),
        max_tokens=4096,
    )

llm_outline = get_llm(temperature=0.7)   
llm_content = get_llm(temperature=0.7)   
llm_quiz = get_llm(temperature=0.6)      
llm_keywords = get_llm(temperature=0.5)  
