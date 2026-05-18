from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv   # <-- ADD THIS
load_dotenv()                      # <-- ADD THIS
# Create our MCP server
mcp = FastMCP("News Server")

# Mark this function as an MCP tool
@mcp.tool()

# Define the news tool
# country: str = "us" - optional parameter, defaults to "us" (United States)
# category: str = "general" - optional parameter, defaults to "general" news
# When a parameter has = something, it means "if not provided, use this default"
def get_top_headlines(country: str = "us", category: str = "general") -> str:
    
    # Description for the AI
    """Get top 5 news headlines for a country and category."""
    
    # Get the API key from secrets
    api_key = os.environ.get("NEWS_API_KEY")
    
    # Check if key exists
    if not api_key:
        return "Error: NEWS_API_KEY not set in Secrets."
    
    # Build the NewsAPI URL
    # This asks for top headlines from a specific country and category
    url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={api_key}"
    
    # Make the request
    response = requests.get(url)
    
    # Parse JSON response
    data = response.json()
    
    # Check if the request was successful
    # "ok" is NewsAPI's way of saying success
    if data.get("status") != "ok":
        # Return the error message
        return f"Error: {data.get('message', 'Failed to fetch news')}"
    
    # Get the articles list, but only the first 5
    # data.get("articles", []) gets articles or returns empty list if not found
    # [:5] takes only the first 5 items
    articles = data.get("articles", [])[:5]
    
    # If no articles were found
    if not articles:
        return "No news articles found."
    
    # Create an empty list to hold our formatted headlines
    headlines = []
    
    # Loop through each article
    # enumerate(articles, 1) gives us both the article AND a counter starting at 1
    # i is the number (1, 2, 3, 4, 5)
    # article is the actual article data
    for i, article in enumerate(articles, 1):
        # Add a formatted headline to our list
        # article['title'] gets the title of the article
        # f"{i}. {article['title']}" creates "1. Article Title Here"
        headlines.append(f"{i}. {article['title']}")
    
    # Join all headlines with newlines (\n) between them
    # "\n".join(list) connects all items with newline characters
    return "\n".join(headlines)

# Run the server if this file is executed directly
if __name__ == "__main__":
    mcp.run(transport="stdio")