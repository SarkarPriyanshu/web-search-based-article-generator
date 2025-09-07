from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
import uuid
from src.states.search_states import AgentState
from src.nodes.search_nodes import (
    web_search_node,
    document_loader_and_reranker_node,
    assistant_editor_node,
    article_writer_node
)

# Build the graph
graph = StateGraph(AgentState)

graph.add_node('web_search_node', web_search_node)
graph.add_node('web_crawler_node', document_loader_and_reranker_node)
graph.add_node('editor_node', assistant_editor_node)
graph.add_node('article_writer_node', article_writer_node)

graph.add_edge(START, 'web_search_node')
graph.add_edge('web_search_node', 'web_crawler_node')
graph.add_edge('web_crawler_node', 'editor_node')
graph.add_edge('editor_node', 'article_writer_node')
graph.add_edge('article_writer_node', END)

# Compile agent without checkpointer to prevent state persistence
content_writter_agent = graph.compile()

# Function to generate fresh config for each query
def get_fresh_config():
    """Generate a fresh config with unique thread_id for each query execution"""
    return {"configurable": {"thread_id": str(uuid.uuid4())}}

# For backward compatibility with existing frontend code
config = get_fresh_config