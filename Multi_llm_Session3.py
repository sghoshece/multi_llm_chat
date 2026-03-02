from openai import OpenAI
from dotenv import load_dotenv
import os
#pip install google-generativeai
import google.generativeai as genai

load_dotenv() 

#Initialize OpenAI
OpenAI_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))