from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv   # <-- ADD THIS
load_dotenv()                      # <-- ADD THIS

# Line 4: Create our MCP server
# We're building a box called "Weather Server" that will hold our weather tool
# Think of it like creating a new appliance with an MCP chip inside
mcp = FastMCP("Weather Server")

# Line 5: The @ symbol means "decorator" - it attaches the function below to our MCP server
# This tells MCP: "The function below is a tool that other programs can call"
@mcp.tool()

# Line 6: Define our tool function
# def means "define a function"
# get_weather is the name of our tool
# (city: str) means this tool takes one input called "city" and it must be a string (text)
# -> str means this function will return a string (text)
def get_weather(city: str) -> str:
    
    # Line 7: The docstring - a description of what this tool does
    # MCP reads this and shows it to the AI so the AI knows when to use this tool
    """Get current weather for any city using OpenWeatherMap."""
    
    # Line 8: Get the API key from environment variables
    # os.environ is like a dictionary of secret keys
    # .get("OPENWEATHER_API_KEY") tries to read the key, returns None if not found
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    
    # Line 9: Check if the API key exists
    # if not api_key means "if api_key is None or empty"
    if not api_key:
        # Line 10: Return an error message if no key found
        return "Error: OPENWEATHER_API_KEY not set in Secrets."
    
    # Line 11: Build the URL for the weather API
    # f"..." is an f-string - it lets us insert variables into text using { }
    # {city} gets replaced with whatever city the user asked for
    # {api_key} gets replaced with our secret key
    # units=metric gives us temperature in Celsius
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    # Line 12: Make the HTTP request (like visiting the URL in a browser)
    # requests.get(url) sends a GET request and waits for the response
    response = requests.get(url)
    
    # Line 13: Convert the response from JSON to a Python dictionary
    # .json() parses the JSON text into something Python can work with
    data = response.json()
    
    # Line 14: Check if the API call was successful
    # data.get("cod") tries to get the "cod" (status code) field
    # 200 means success, anything else means error
    if data.get("cod") != 200:
        # Line 15: Return the error message from the API
        # data.get('message', 'City not found') - if there's a message, show it
        # If no message, show 'City not found' as default
        return f"Error: {data.get('message', 'City not found')}"
    
    # Line 16: Extract the weather description
    # data["weather"] is a list, [0] gets the first item
    # ["description"] gets the description field (like "clear sky", "rain")
    description = data["weather"][0]["description"]
    
    # Line 17: Extract the temperature
    # data["main"]["temp"] navigates into the nested dictionary
    temperature = data["main"]["temp"]
    
    # Line 18: Return a nicely formatted weather report
    # city.title() capitalizes the first letter of the city name
    # The f-string combines everything into one sentence
    return f"Weather in {city.title()}: {description}, {temperature}°C"

# Line 19: This is a Python convention
# __name__ is a special variable
# "__main__" means this file is being run directly (not imported by another file)
if __name__ == "__main__":
    
    # Line 20: Start the MCP server
    # transport="stdio" means it communicates through standard input/output
    # This makes it listen for MCP messages from the terminal
    mcp.run(transport="stdio")