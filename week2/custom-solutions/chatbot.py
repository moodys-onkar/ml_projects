
import os
import requests
from bs4 import BeautifulSoup
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
import anthropic
import gradio as gr
from website import Website
from google.genai.types import GenerateContentConfig

# Load environment variables from .env file
load_dotenv(override=True)
# Set up API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)  
claude = anthropic.Anthropic()
gemini_client = genai.Client(api_key=GOOGLE_API_KEY)  

system_message = "You are a helpful assistant"

def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]

    print("History is:")
    print(history)
    print("And messages is:")
    print(messages)


    completion = openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.7, stream=True)
    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ''
        yield response


gr.ChatInterface(fn=chat,type="messages").launch(inbrowser=True)