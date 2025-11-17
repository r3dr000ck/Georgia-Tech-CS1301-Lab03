import google.generativeai as genai
import requests

GEMINI_API_KEY = "AIzaSyCQNy4vivWIVBlvT1hqRzz2VXs5nLuvPMU"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

url = "http://www.omdbapi.com/?apikey=89d15140&"

# Example
response = model.generate_content("Tell me a joke about lions.")
print(response.text)