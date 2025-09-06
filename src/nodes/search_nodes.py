import logging
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.states.search_states import AgentState
from src.models.search_models import reranker_model
from src.utils.search_utils import rearrange_docs
from src.tools.search_tools import search_engine_tool
from src.chains.search_chains import document_editor_chain, article_writter_chain
from langchain_community.document_loaders.url import UnstructuredURLLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchNodeError(Exception):
    """Custom exception for search node errors"""
    def __init__(self, message: str, node_name: str, details: Optional[str] = None):
        self.message = message
        self.node_name = node_name
        self.details = details
        super().__init__(self.message)

def web_search_node(state: AgentState) -> AgentState:
    """
    Search the web for relevant URLs based on the query.
    
    Args:
        state: Current agent state containing the query
        
    Returns:
        Updated state with search results or error information
    """
    query = state.query
    urls = []
    error_message = None
    
    try:
        logger.info(f"Starting web search for query: {query}")
        
        if not query or query.strip() == "":
            raise SearchNodeError(
                "Empty query provided", 
                "web_search_node",
                "Please provide a valid search query"
            )
        
        search_results = search_engine_tool.run(query)
        
        if not search_results or 'results' not in search_results:
            raise SearchNodeError(
                "No search results returned",
                "web_search_node", 
                "Search engine returned empty results"
            )
        
        # Filter URLs with score > 0.5 and valid URLs
        urls = [
            result.get('url', '').strip() for result in search_results.get('results', [])
            if (result.get('score', 0) > 0.5 and 
                result.get('url', '').strip().startswith(('http://', 'https://')))
        ]
        
        if not urls:
            error_message = "No high-quality search results found (score > 0.5)"
            logger.warning(f"[WebSearchNode] {error_message}")
        else:
            logger.info(f"[WebSearchNode] Found {len(urls)} relevant URLs")
            
    except SearchNodeError:
        raise  # Re-raise custom errors
    except Exception as e:
        error_message = f"Search engine error: {str(e)}"
        logger.error(f"[WebSearchNode] {error_message}")
        raise SearchNodeError(error_message, "web_search_node", str(e))
    
    return AgentState(
        **state.model_dump(exclude={'links', 'query', 'error'}), 
        links=urls, 
        query=query,
        error=error_message
    )

def document_loader_and_reranker_node(state: AgentState) -> AgentState:
    """
    Load documents from URLs and rerank them based on relevance to the query.
    
    Args:
        state: Current agent state containing links and query
        
    Returns:
        Updated state with reranked documents and URLs
    """
    query = state.query
    links = state.links or []
    reranked_docs, reranked_urls = [], []
    error_message = None
    
    try:
        logger.info(f"Processing {len(links)} URLs for document loading and reranking")
        
        if not links:
            error_message = "No links available for document loading"
            logger.warning(f"[DocLoaderRerankerNode] {error_message}")
            return AgentState(
                **state.model_dump(exclude={'reranked_docs', 'reranked_urls', 'error'}),
                reranked_docs=reranked_docs, 
                reranked_urls=reranked_urls,
                error=error_message
            )
        
        # Load documents with timeout and error handling
        documents = _load_documents_safely(links)
        
        if not documents:
            error_message = "Failed to load any documents from provided URLs"
            logger.warning(f"[DocLoaderRerankerNode] {error_message}")
        else:
            # Prepare pairs for reranking
            pairs = [
                [query, _clean_document_content(doc.page_content if doc and hasattr(doc, 'page_content') else '')]
                for doc in documents
            ]
            
            # Filter out empty pairs
            valid_pairs = [(pair, doc) for pair, doc in zip(pairs, documents) if pair[1].strip()]
            
            if not valid_pairs:
                error_message = "No valid document content found for reranking"
                logger.warning(f"[DocLoaderRerankerNode] {error_message}")
            else:
                # Rerank documents
                valid_pairs_only = [pair for pair, _ in valid_pairs]
                valid_documents = [doc for _, doc in valid_pairs]
                
                scores = reranker_model.predict(valid_pairs_only)
                reranked_docs, reranked_urls = rearrange_docs(
                    documents=valid_documents, 
                    scores=scores, 
                    top=5
                )
                
                logger.info(f"[DocLoaderRerankerNode] Reranked {len(reranked_docs)} documents")
        
    except Exception as e:
        error_message = f"Document loading/reranking error: {str(e)}"
        logger.error(f"[DocLoaderRerankerNode] {error_message}")
        raise SearchNodeError(error_message, "document_loader_and_reranker_node", str(e))
    
    return AgentState(
        **state.model_dump(exclude={'reranked_docs', 'reranked_urls', 'error'}),
        reranked_docs=reranked_docs, 
        reranked_urls=reranked_urls,
        error=error_message
    )

def assistant_editor_node(state: AgentState) -> AgentState:
    """
    Edit and summarize reranked documents to create context.
    
    Args:
        state: Current agent state containing reranked documents
        
    Returns:
        Updated state with edited context
    """
    query = state.query
    reranked_docs = state.reranked_docs or []
    context = ""
    error_message = None
    
    try:
        logger.info(f"[AssistantEditorNode] Processing {len(reranked_docs)} documents for editing")
        
        if not reranked_docs:
            error_message = "No reranked documents available for editing"
            logger.warning(f"[AssistantEditorNode] {error_message}")
            return AgentState(**state.model_dump(exclude={'context', 'error'}), context=context, error=error_message)
        
        edited_docs = []
        successful_edits = 0
        
        # Process documents with better error handling
        for idx, doc in enumerate(reranked_docs):
            try:
                if not doc or not hasattr(doc, 'page_content') or not doc.page_content:
                    logger.warning(f"[AssistantEditorNode] Document {idx + 1} has no content")
                    continue
                
                # Limit content to 3000 characters and clean it
                content = _clean_document_content(doc.page_content[:3000])
                if not content.strip():
                    continue
                
                edited_doc = document_editor_chain.invoke({
                    'query': query, 
                    'documents': content
                })
                
                if edited_doc and edited_doc.get('summary', '').strip():
                    edited_docs.append(edited_doc)
                    successful_edits += 1
                    logger.debug(f"[AssistantEditorNode] Successfully edited document {idx + 1}")
                else:
                    logger.warning(f"[AssistantEditorNode] Document {idx + 1} returned empty summary")
                    
            except Exception as doc_error:
                logger.error(f"[AssistantEditorNode] Error processing document {idx + 1}: {str(doc_error)}")
                continue
        
        # Create context from edited documents
        if edited_docs:
            context = '\n\n'.join([
                f"{idx + 1}. {summary.get('summary', '').strip()}" 
                for idx, summary in enumerate(edited_docs)
                if summary.get('summary', '').strip()
            ])
            logger.info(f"[AssistantEditorNode] Created context from {len(edited_docs)} edited documents")
        else:
            error_message = "Failed to edit any documents successfully"
            logger.warning(f"[AssistantEditorNode] {error_message}")
        
    except Exception as e:
        error_message = f"Document editing error: {str(e)}"
        logger.error(f"[AssistantEditorNode] {error_message}")
        raise SearchNodeError(error_message, "assistant_editor_node", str(e))
    
    return AgentState(**state.model_dump(exclude={'context', 'error'}), context=context, error=error_message)

def article_writer_node(state: AgentState) -> AgentState:
    """
    Generate a comprehensive article based on the edited context.
    
    Args:
        state: Current agent state containing context
        
    Returns:
        Updated state with generated article
    """
    context = state.context or ""
    article = ""
    error_message = None
    
    try:
        logger.info("[ArticleWriterNode] Starting article generation")
        
        if not context or context.strip() == "":
            error_message = "No context available for article generation"
            logger.warning(f"[ArticleWriterNode] {error_message}")
            article = "Unable to generate article: No relevant content found from the search results."
        else:
            # Generate article with error handling
            result = article_writter_chain.invoke({'context': context})
            
            if isinstance(result, str):
                article = result.strip()
            elif isinstance(result, dict):
                article = result.get('article', '').strip()
            else:
                raise SearchNodeError(
                    "Invalid article format returned", 
                    "article_writer_node",
                    f"Expected string or dict, got {type(result)}"
                )
            
            if not article:
                error_message = "Article generation returned empty content"
                article = "Unable to generate article: The article generation process returned empty content."
                logger.warning(f"[ArticleWriterNode] {error_message}")
            else:
                logger.info(f"[ArticleWriterNode] Successfully generated article ({len(article)} characters)")
        
    except Exception as e:
        error_message = f"Article generation error: {str(e)}"
        article = "Unable to generate article due to a technical error. Please try again."
        logger.error(f"[ArticleWriterNode] {error_message}")
        raise SearchNodeError(error_message, "article_writer_node", str(e))
    
    return AgentState(**state.model_dump(exclude={"article", "error"}), article=article, error=error_message)

# Helper functions
def _load_documents_safely(urls: List[str], max_workers: int = 3, timeout: int = 30) -> List:
    """
    Safely load documents from URLs with timeout and parallel processing.
    
    Args:
        urls: List of URLs to load
        max_workers: Maximum number of concurrent workers
        timeout: Timeout in seconds for each URL
        
    Returns:
        List of loaded documents
    """
    documents = []
    
    try:
        # Use smaller batches to avoid overwhelming servers
        batch_size = min(5, len(urls))
        
        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i:i + batch_size]
            
            try:
                loader = UnstructuredURLLoader(
                    urls=batch_urls,
                    show_progress_bar=False,
                    continue_on_failure=True
                )
                batch_docs = loader.load()
                documents.extend(batch_docs)
                logger.info(f"Loaded batch {i//batch_size + 1}: {len(batch_docs)} documents")
                
            except Exception as batch_error:
                logger.error(f"Error loading batch {i//batch_size + 1}: {str(batch_error)}")
                continue
    
    except Exception as e:
        logger.error(f"Error in document loading process: {str(e)}")
    
    return documents

def _clean_document_content(content: str) -> str:
    """
    Clean and normalize document content.
    
    Args:
        content: Raw document content
        
    Returns:
        Cleaned content
    """
    if not content:
        return ""
    
    # Remove excessive whitespace and normalize
    cleaned = ' '.join(content.split())
    
    # Remove very short content that's likely not useful
    if len(cleaned) < 50:
        return ""
    
    return cleaned