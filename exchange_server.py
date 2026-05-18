from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv   # <-- ADD THIS
load_dotenv()                      # <-- ADD THIS

# Create the MCP server named "Exchange Rate Server"
mcp = FastMCP("Exchange Rate Server")

# Decorator: tells MCP this function is a tool
@mcp.tool()

# Define the convert_currency tool
# amount: float - a decimal number (like 100.50)
# from_currency: str - the currency you have (like "USD")
# to_currency: str - the currency you want (like "JPY")
# -> str means it returns text
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    
    # Description that MCP shows to the AI
    """Convert an amount from one currency to another."""
    
    # Read the API key from environment variables
    api_key = os.environ.get("EXCHANGE_RATE_API_KEY")
    
    # If no API key found, return error
    if not api_key:
        return "Error: EXCHANGE_RATE_API_KEY not set in Secrets."
    
    # Build the API URL
    # .upper() converts currency codes to uppercase (usd -> USD)
    # Example URL: https://v6.exchangerate-api.com/v6/KEY/pair/USD/JPY/100
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency.upper()}/{to_currency.upper()}/{amount}"
    
    # Make the HTTP request
    response = requests.get(url)
    
    # Parse the JSON response
    data = response.json()
    
    # Check if the conversion was successful
    # data.get("result") tries to get the "result" field
    if data.get("result") == "success":
        # Get the converted amount from the response
        converted = data["conversion_result"]
        # Return a formatted string showing the conversion
        return f"{amount} {from_currency.upper()} = {converted} {to_currency.upper()}"
    else:
        # If conversion failed, return the error
        # data.get('error-type', 'Conversion failed') shows error type or default message
        return f"Error: {data.get('error-type', 'Conversion failed')}"

# If this file is run directly (not imported)
if __name__ == "__main__":
    # Start the MCP server listening for messages
    mcp.run(transport="stdio")