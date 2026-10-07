import os
import json
from openai import OpenAI
from transformers import pipeline
import requests

# Load OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key from environment: {api_key}")
if not api_key:
    raise ValueError("OpenAI API key not found. Set it as an environment variable.")

client = OpenAI(api_key=api_key)

# Initialize the text-generation pipeline
chatbot = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")

# OpenWeatherMap API details
API_KEY = "your_openweathermap_api_key"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history.json")

try:
    with open(HISTORY_FILE, "r", encoding="utf-8") as history_file:
        saved_history = json.load(history_file)
    if isinstance(saved_history, list):
        chat_history = [
            exchange for exchange in saved_history
            if isinstance(exchange, dict)
            and isinstance(exchange.get("user"), str)
            and isinstance(exchange.get("assistant"), str)
        ]
    else:
        chat_history = []
except (FileNotFoundError, json.JSONDecodeError):
    chat_history = []

def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as history_file:
        json.dump(chat_history, history_file, ensure_ascii=False, indent=2)

def get_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        weather = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        return f"The weather in {city} is {weather} with a temperature of {temperature}°C."
    else:
        return "Sorry, I couldn't fetch the weather data."

print("Chatbot started! Type 'exit' to stop.\n")

if chat_history:
    print("Previous chat:")
    for exchange in chat_history:
        print(f"You: {exchange['user']}")
        print(f"Chatbot: {exchange['assistant']}")
    print()

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Chatbot: Goodbye!")
        break

    if "weather" in user_input.lower():
        city = user_input.split("weather in")[-1].strip()
        response = get_weather(city)
    else:
        response = chatbot(user_input, max_length=100, num_return_sequences=1)[0]['generated_text']

    print("Chatbot:", response)
    chat_history.append({"user": user_input, "assistant": response})
    save_history()