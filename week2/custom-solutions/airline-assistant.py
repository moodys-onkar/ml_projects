
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
import json


# Load environment variables from .env file
load_dotenv(override=True)
# Set up API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)  
claude = anthropic.Anthropic()
gemini_client = genai.Client(api_key=GOOGLE_API_KEY)  

system_message = "You are a helpful assistant for an airline company called AirforceAI. Give short, simple, 1 sentence answers to customer queries. Always be accurate" \
"If you don't know the answer, say so. If the customer asks for a discounted price for a city, calculate the discounted price."



ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}
discounted_ticket_percent = {"london": 5, "tokyo": 15}

def get_ticket_price_discounts(destination_city):
    print(f"Tool get_ticket_price_discounts called for city: ${destination_city}")
    city = destination_city.lower()
    return discounted_ticket_percent.get(city,0)

def get_ticket_price(destination_city):
    print(f"Tool get_ticket_price called for city: ${destination_city}")
    city = destination_city.lower()
    return ticket_prices.get(city, 'Unknown')

# Define the tool dictionary for get_ticket_prices
price_function = {
    "name": "get_ticket_price",
    "description": "Fetches the ticket price for a given destination city. Returns 'Unknown' if the city is not in the database.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The name of the destination city for which the ticket price is requested.",
            }
        },
        "required": ["destination_city"]
    },
  
}

# Define the tool dictionary for get_ticket_price_discounts
discount_function = {
    "name": "get_ticket_price_discounts",
    "description": "Fetches the discount percentage for a given destination city. Returns 0 if the city does not have a discount.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The name of the destination city for which the discount percentage is requested.",
            }
        },
        "required": ["destination_city"]
    }
}

tools = [{"type": "function", "function": price_function}, {"type":"function", "function": discount_function}]

def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]

    # print("History is:")
    # print(history)
    # print("And messages is:")
    # print(messages)


    response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.7, tools=tools)

    # Check if the response contains a function call
    if response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        # print(message)
        response, city = handle_tool_call(message)
        messages.append(message)
        messages.append(response)
        response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
    
    return response.choices[0].message.content

def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    print(tool_call.function.name)
    response, city= "", ""
    try:
        if tool_call.function.name == "get_ticket_price":
            arguments = json.loads(tool_call.function.arguments)
            city = arguments.get('destination_city')
            price = get_ticket_price(city)
            response = {
                "role": "tool",
                "content": json.dumps({"destination_city": city, "price": price}),
                "tool_call_id": message.tool_calls[0].id
            }
        elif tool_call.function.name == "get_ticket_price_discounts":
            arguments = json.loads(tool_call.function.arguments)
            city = arguments.get('destination_city')
            discount = get_ticket_price_discounts(city)
            response = {
                "role": "tool",
                "content": json.dumps({"destination_city": city, "discount": discount}),
                "tool_call_id": message.tool_calls[0].id
            }
        else:
            # Handle unexpected tool names
            print(f"Unknown tool name: {tool_call.function.name}")
            response = {
                "role": "tool",
                "content": json.dumps({"error": "Unknown tool name"}),
                "tool_call_id": message.tool_calls[0].id
            }
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred. Please try again later."

    return response, city

       

gr.ChatInterface(fn=chat, type="messages").launch(inbrowser=True)