from google import genai
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import website

api_key = ""
client = ""
message = ""

def load_api_key(llm):
    global client
    global message
    if llm == "GOOGLE":
        api_key = os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)
    elif llm == "OPENAI":
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI()
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Hello, Claude"}
        ]
)
        
system_message = "You are an assistant that is great at telling jokes"
user_prompt = "Tell a light-hearted joke for an audience of Data Scientists"

load_dotenv(override=True)
load_api_key("ANTHROPIC")

response = client.messages.stream(
    model="claude-3-5-sonnet-latest",
    system = system_message,
    max_tokens=1024,
    messages = [{"role": "user", "content": user_prompt}],
)

with response as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)