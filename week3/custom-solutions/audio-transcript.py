import os
import requests
from bs4 import BeautifulSoup
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
import anthropic
import gradio as gr
from google.genai.types import GenerateContentConfig

load_dotenv(override=True)
# Set up API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)  
claude = anthropic.Anthropic()
gemini_client = genai.Client(api_key=GOOGLE_API_KEY)  

system_message = "You are a helpful assistant"

def stream_content(prompt,audio_file):
      

      with open(audio_file, "rb") as f:
            transcript = openai_client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=f,
            response_format="text"
        )
            
    
      prompt += f"Please generate the meeting minutes including owners, attendees, description of meeting, action items and the next steps.Here is the final transcript: {transcript}"

      messages =  [
        {"role": "system", "content": "You are a expert in tranacribing audio files and generating meeting minutes."},
        {"role": "user", "content": prompt},
    ]
      
      stream = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
        max_tokens=2000,
        temperature=0.7,
    )
      
      result = ""
      for chunk in stream:
           result += chunk.choices[0].delta.content or ""
           yield result

gr.Interface(
    fn=stream_content,
    inputs=[gr.Textbox(label="Enter a prompt") , gr.Audio(type="filepath",label="Select a file to transcribe")],
    outputs=gr.Markdown(label="Response:"),
    title="Chat Assistant",
    description="A simple app to generate meeting minutes for audio file.",
    flagging_mode="never"
).launch(inbrowser=True)