from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os

# Load the .env file variables into os.environ
# load_dotenv()

# tavily_api_key = os.getenv('TAVILY_API_KEY') 

search_engine_tool = TavilySearch(
    max_results=30,
    tavily_api_key = "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"
)    