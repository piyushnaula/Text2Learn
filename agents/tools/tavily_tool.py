import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

tavily_search = TavilySearchResults(
    api_key=TAVILY_API_KEY,
    max_results=5,
    name="tavily_search",
    description=(
        "Search the web using Tavily. "
        "Use this to find up-to-date information about any topic. "
        "Input: a search query string. "
        "Output: top 5 search results with title, URL, and content."
    ),
)