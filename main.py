from src.graphs.search_graphs import content_writter_agent,config
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv

load_dotenv()

user_input = input('Enter query: ')
response = content_writter_agent.invoke({'query':user_input},config=config)
md = Markdown(response['article'])

console = Console()
console.print(md)