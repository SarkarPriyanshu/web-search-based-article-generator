from langgraph.graph import START,END,StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from src.states.search_states import AgentState
from src.nodes.search_nodes import (web_search_node,document_loader_and_reranker_node,assistant_editor_node,article_writer_node)




graph = StateGraph(AgentState)

graph.add_node('web_search_node',web_search_node)
graph.add_node('web_crawler_node',document_loader_and_reranker_node)
graph.add_node('editor_node',assistant_editor_node)
graph.add_node('article_writer_node',article_writer_node)

graph.add_edge(START,'web_search_node')
graph.add_edge('web_search_node','web_crawler_node')
graph.add_edge('web_crawler_node','editor_node')
graph.add_edge('editor_node','article_writer_node')
graph.add_edge('article_writer_node',END)

checkpointer = InMemorySaver()
content_writter_agent = graph.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "3"}}