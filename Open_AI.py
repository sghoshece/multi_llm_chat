import pandas as pd
import numpy as np
import os

#pip install python-dotenv
from dotenv import load_dotenv
load_dotenv() 

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {"role": "user", "content": "Write a one-sentence bedtime story about a unicorn."}
    ]
)

print(response.choices[0].message.content)

