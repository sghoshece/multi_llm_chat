import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('OPENAI_API_KEY')
print(f'OPENAI_API_KEY loaded: {bool(key)}')
if key:
    print(f'OPENAI_API_KEY starts with: {key[:30]}...')
else:
    print('OPENAI_API_KEY not found')
