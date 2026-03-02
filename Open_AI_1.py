import os

#pip install python-dotenv
#pinp install -r requirement.txt
from dotenv import load_dotenv
load_dotenv() 

from openai import OpenAI

def direct_llm_response():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.responses.create(
    model="gpt-4o-mini",
    input="India Partition"
) 

    print(response.output_text)

# Chat completion api usage

def chat_completion_api():

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a one-sentence bedtime story about a unicorn."}
    ]
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    print(completion)

if __name__ == "__main__":
    #direct_llm_response()
    chat_completion_api(