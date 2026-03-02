#Text Summarization

from transformers import pipeline
#This package holds the pipeline function
from langchain_community.document_loaders import ArxivLoader

task='translation'
model='Mitsua/elan-mt-bt-en-ja'
translator=pipeline(task=task,model=model)

text='I love you Paramita.'
result=translator(text)

result[0]['translation_text']

print(result[0]['translation_text'])