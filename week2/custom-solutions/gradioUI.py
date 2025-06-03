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

# Initialize clients

openai_client = OpenAI(api_key=OPENAI_API_KEY)  
claude = anthropic.Anthropic()
gemini_client = genai.Client(api_key=GOOGLE_API_KEY)  

system_message = "You are a helpful assistant"

def messages_gpt(prompt):
    # Example messages for GPT-3.5
    messages =  [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt},
    ]

    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
    )
    response = completion.choices[0].message.content
    return response

def messages_gemini(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    print(response.text)

def stream_gpt(prompt,tone="professional"):
      messages =  [
        {"role": "system", "content": system_message + f"Keep the tone ${tone}"},
        {"role": "user", "content": prompt},
    ]

      stream = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1024,
        stream=True,
        temperature=0.7,
    )
      
      result = ""
      for chunk in stream:
           result += chunk.choices[0].delta.content or ""
           yield result

def stream_claude(prompt, tone="professional"):
    result = claude.messages.stream(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0.7,
        system=system_message,
        messages=[
            {"role": "assistant", "content":system_message + f"Keep the tone ${tone}"},
            {"role": "user", "content": prompt},
        ],
    )
    response = ""
    with result as stream:
        for text in stream.text_stream:
            response += text or ""
            yield response

def stream_gemini(prompt,tone="professional"):
#     model = genai.GenerativeModel('gemini-1.5-flash')
#     response = model.generate_content(
#     contents=[prompt],
#     stream=True
# )
#     result = ""
#     for chunk in response:
#         result += chunk.candidates[0].content.text or ""
#         yield result
      
    response = gemini_client.models.generate_content_stream(
    model="gemini-1.5-flash", contents=prompt,
    config=GenerateContentConfig(
        system_instruction=[
            system_message + f"Keep the tone ${tone}"
        ]
))
    result = ""
    for chunk in response:
        result += chunk.text
        yield result

def shout(text):
    print("Shout has been converted to upper case:", text)
    # Example function to shout the text
    return text.upper()

shout("Hello, Onkar!")


# GPT response
# gr.Interface(
#     fn=stream_gpt,
#     inputs=gr.Textbox(label="Enter text to ask GPT"),
#     outputs=gr.Markdown(label="Response:"),
#     title="Shout Box",
#     description="A simple app to ask Q&A with ChatGPT.",
#     flagging_mode="never"
# ).launch(inbrowser=True)

#Claude Response


def stream_content(prompt,model,tone):
    if model == "GPT":
        result = stream_gpt(prompt,tone)
    elif model == "Claude":
        result = stream_claude(prompt,tone)
    elif model=="Gemini":
        result = stream_gemini(prompt,tone)
    else:
        result = ValueError("unknown model")
    yield from result

# With massive thanks to Bill G. who noticed that a prior version of this had a bug! Now fixed.

system_message_brochure = "You are an assistant that analyzes the contents of a company website landing page \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown."

def stream_brochure(company_name, url, model):
    prompt = f"Please generate a company brochure for {company_name}. Here is their landing page:\n"
    prompt += Website(url).get_contents()
    if model=="GPT":
        result = stream_gpt(prompt)
    elif model=="Claude":
        result = stream_claude(prompt)
    elif model=="Gemini":
        result = stream_gemini(prompt)
    else:
        raise ValueError("Unknown model")
    yield from result


gr.Interface(
    fn=stream_content,
    inputs=[gr.Textbox(label="Enter text to ask Chatbot"), gr.Dropdown(["GPT", "Claude", "Gemini"], label="Select Model", value="GPT"),gr.Dropdown(["Humorous", "Professional", "Friendly"], label="Choose a tone")],
    outputs=gr.Markdown(label="Response:"),
    title="Chat Assistant",
    description="A simple app to ask Q&A with Claude.",
    flagging_mode="never"
).launch(inbrowser=True)

# gr.Interface(
#     fn=stream_brochure,
#     inputs=[gr.Textbox(label="Enter company name to search"), gr.Textbox(label="Enter url"), gr.Dropdown(["GPT", "Claude", "Gemini"], label="Select Model", value="GPT")],
#     outputs=gr.Markdown(label="Response:"),
#     title="Chat Assistant",
#     description="A simple app to ask Q&A with Claude.",
#     flagging_mode="never"
# ).launch(inbrowser=True)






