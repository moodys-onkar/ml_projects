import os
import requests
import json
from typing import List
from dotenv import load_dotenv
from IPython.display import Markdown, display, update_display
from openai import OpenAI

MODEL_GPT = 'gpt-4o-mini'
MODEL_LLAMA = 'llama3.2'

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

if api_key and api_key.startswith('sk-proj-') and len(api_key)>10:
    print("API key looks good so far")
else:
    print("There might be a problem with your API key? Please visit the troubleshooting notebook!")
    
MODEL = 'gpt-4o-mini'
openai = OpenAI()


question = """
Please explain what this code does and why:
yield from {book.get("author") for book in books if book.get("author")}
"""

# Get gpt-4o-mini to answer, with streaming
system_prompt = "You are an expert in python and your job is to help users with the questions related to python code. For any query that the user is posting, provide an indepth explanation of the answer with 3-4 examples and best practices."

def get_user_prompt(query):
    user_prompt = f"Please explain the below code.\n {query}"
    return user_prompt



def get_query_response(query, stream=False):
    response = openai.chat.completions.create(
        model = MODEL_GPT,
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_user_prompt(query)}
        ],
        stream=stream
    )

    if stream:
         streaming = ""
         display_handle = display(Markdown(""), display_id=True)
         for chunk in response:
            streaming += chunk.choices[0].delta.content or ''
            streaming = streaming.replace("```","").replace("markdown", "")
            update_display(Markdown(streaming), display_id=display_handle.display_id)
    else:
        result =  response.choices[0].message.content
        display(Markdown(result))


get_query_response(question,True)

