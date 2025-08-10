from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
import requests
from dice_roller import DiceRoller

load_dotenv()

mcp = FastMCP("mcp-server")
client = TavilyClient(os.getenv("TAVILY_API_KEY"))

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for information about the given query"""
    search_results = client.get_search_context(query=query)
    return search_results

@mcp.tool()
def roll_dice(notation: str, num_rolls: int = 1) -> str:
    """Roll the dice with the given notation"""
    roller = DiceRoller(notation, num_rolls)
    return str(roller)

@mcp.tool()
def get_random_dog() -> str:
    """Get a random dog image URL"""
    try:
        response = requests.get("https://dog.ceo/api/breeds/image/random")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return f"Random dog image: {data['message']}"
            else:
                return "Failed to get random dog image"
        else:
            return f"Error: HTTP {response.status_code}"
    except Exception as e:
        return f"Error getting random dog: {str(e)}"

@mcp.tool()
def get_dog_breeds() -> str:
    """Get a list of all available dog breeds"""
    try:
        response = requests.get("https://dog.ceo/api/breeds/list/all")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                breeds = list(data["message"].keys())
                return f"Available dog breeds: {', '.join(breeds[:20])}..." if len(breeds) > 20 else f"Available dog breeds: {', '.join(breeds)}"
            else:
                return "Failed to get dog breeds"
        else:
            return f"Error: HTTP {response.status_code}"
    except Exception as e:
        return f"Error getting dog breeds: {str(e)}"

@mcp.tool()
def get_dog_by_breed(breed: str) -> str:
    """Get a random dog image of a specific breed"""
    try:
        response = requests.get(f"https://dog.ceo/api/breed/{breed}/images/random")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return f"Random {breed} image: {data['message']}"
            else:
                return f"Failed to get {breed} image: {data.get('message', 'Unknown error')}"
        else:
            return f"Error: HTTP {response.status_code}"
    except Exception as e:
        return f"Error getting {breed} image: {str(e)}"

@mcp.tool()
def get_dog_breed_info(breed: str) -> str:
    """Get information about a specific dog breed including sub-breeds"""
    try:
        response = requests.get(f"https://dog.ceo/api/breed/{breed}/list")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                sub_breeds = data["message"]
                if sub_breeds:
                    return f"Sub-breeds of {breed}: {', '.join(sub_breeds)}"
                else:
                    return f"{breed} has no sub-breeds"
            else:
                return f"Failed to get {breed} information: {data.get('message', 'Unknown error')}"
        else:
            return f"Error: HTTP {response.status_code}"
    except Exception as e:
        return f"Error getting {breed} information: {str(e)}"

# """
# Add your own tool here, and then use it through Cursor!
# """
# @mcp.tool()
# def YOUR_TOOL_NAME(query: str) -> str:
#     """YOUR_TOOL_DESCRIPTION"""
#     return "YOUR_TOOL_RESPONSE"

if __name__ == "__main__":
    mcp.run(transport="stdio")