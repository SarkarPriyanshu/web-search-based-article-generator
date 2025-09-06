# 🚀 LangGraph AI Article Generator

An intelligent research and article generation system that transforms user queries into comprehensive, well-researched articles through automated web searching, content analysis, and AI-powered writing.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
![LangChain](https://img.shields.io/badge/langchain-latest-green.svg)
![LangGraph](https://img.shields.io/badge/langgraph-latest-orange.svg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Workflow](#workflow)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Overview

The LangGraph AI Article Generator is a multi-stage AI pipeline that conducts research and generates articles by:

1. **Web Search**: Finds relevant sources across the internet
2. **Content Analysis**: Ranks and selects the most relevant sources
3. **Information Extraction**: Summarizes key insights from selected sources as an article editor
4. **Article Generation**: Creates comprehensive, well-structured articles

## Features

### Intelligent Web Search
- **Smart Query Processing**: Optimizes search queries for better results
- **Quality Filtering**: Filters results based on relevance scores (>0.5)
- **Multi-source Aggregation**: Gathers information from diverse web sources

### Advanced Content Ranking
- **AI-Powered Reranking**: Uses machine learning models to rank content relevance
- **Quality Assessment**: Evaluates content quality and credibility
- **Top Source Selection**: Automatically selects the top 5 most relevant sources

### Editorial Processing
- **Content Summarization**: Extracts key insights from each source
- **Information Synthesis**: Combines information from multiple sources
- **Context Building**: Creates coherent context for article generation

### Modern User Interface
- **Real-time Progress**: Live updates with loading spinners for each stage
- **Clean Design**: Modern, responsive card-based layout
- **Interactive Elements**: Clickable source links with favicons
- **Error Handling**: Graceful error messages and recovery options

## Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  LangGraph      │────│   AI Models     │
│                 │    │   Pipeline      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                      │
         │              ┌─────────────────┐             │
         └──────────────│  Search Engine  │─────────────┘
                        │                 │
                        └─────────────────┘
```

### Node Architecture

The system uses a **LangGraph** multi-node architecture:

1. **Web Search Node** (`web_search_node`)
2. **Document Loader & Reranker Node** (`document_loader_and_reranker_node`)
3. **Assistant Editor Node** (`assistant_editor_node`)
4. **Article Writer Node** (`article_writer_node`)

## Workflow

### Stage 1: Web Search
```python
AgentState(query) → web_search_node() → AgentState(query, links)
```
- Takes user query as input
- Searches web using optimized search engine
- Returns list of relevant URLs with quality scores
- Filters results with score > 0.5

### Stage 2: Content Analysis & Ranking
```python
AgentState(links) → document_loader_and_reranker_node() → AgentState(reranked_docs, reranked_urls)
```
- Loads content from discovered URLs
- Uses AI reranking model to assess relevance
- Selects top 5 most relevant documents
- Handles loading timeouts and errors gracefully

### Stage 3: Editorial Processing
```python
AgentState(reranked_docs) → assistant_editor_node() → AgentState(context)
```
- Summarizes each selected document
- Extracts key insights and information
- Creates consolidated context for article generation
- Handles up to 3000 characters per document

### Stage 4: Article Generation
```python
AgentState(context) → article_writer_node() → AgentState(article)
```
- Generates comprehensive article from context
- Creates well-structured, readable content
- Ensures proper formatting and flow
- Returns complete article in markdown format

## Project Structure

```
langgraph-ai-article-generator/
│
├── src/
│    ├── prompts/
│    │   └── search_prompts.py        # Prompts 
│    ├── nodes/
│    │   └── search_nodes.py          # Nodes for graph 
│    ├── states/
│    │   └── search_states.py         # Pydantic models for state management
│    ├── models/
│    │   └── search_models.py         # AI models (reranker, etc.)
│    ├── utils/
│    │   └── search_utils.py          # Utility functions
│    ├── tools/
│    │   └── search_tools.py          # Search engine integration
│    ├── chains/
│    │   └── search_chains.py         # LangChain chains
│    └── graphs/
│        └── search_graphs.py         # LangGraph node definitions
│
│
├── app.py                 # Main Streamlit application
├── requirements.txt                 # Python dependencies
├── README.md                       # Project documentation
```

## Installation

### Prerequisites
- Python 3.8+
- pip or conda
- Internet connection for web searches

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/langgraph-ai-article-generator.git
cd langgraph-ai-article-generator
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Run the application**
```bash
streamlit run streamlit_app.py
```

## Usage

### Basic Usage

1. **Start the Application**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Enter Your Query**
   - Open the web interface (usually http://localhost:8501)
   - Enter your research topic or question
   - Press Enter or click search

3. **Monitor Progress**
   - Watch real-time progress through 4 stages
   - See sources being discovered and analyzed
   - View the final generated article

### Example Queries

```
"Latest developments in artificial intelligence 2024"
"Climate change impact on renewable energy"
"Machine learning applications in healthcare"
"Sustainable urban development strategies"
```

### Advanced Features

- **Clear Results**: Use the "Clear Results" button to start fresh
- **Source Links**: Click on source favicons to visit original articles
- **Error Recovery**: System handles timeouts and errors gracefully

## State Management

The system uses **Pydantic models** for robust state management:

### AgentState
```python
class AgentState(BaseModel):
    query: str              # Original user query
    links: List[str]        # URLs from web search
    reranked_docs: List     # Reranked documents
    reranked_urls: List     # Reranked URLs
    context: str            # Consolidated context
    article: str            # Final generated article
```

### DocumentEditorState
```python
class DocumentEditorState(TypedDict):
    summary: str            # Refined document summary
```

### ArticleWritter
```python
class ArticleWritter(TypedDict):
    article: str            # Final structured article
```

## API Reference

### Core Nodes

#### `web_search_node(state: AgentState) -> AgentState`
Performs web search and returns relevant URLs.

**Parameters:**
- `state`: AgentState with query

**Returns:**
- Updated AgentState with links

**Error Handling:**
- Empty query validation
- Search result filtering
- Quality score thresholding

#### `document_loader_and_reranker_node(state: AgentState) -> AgentState`
Loads and reranks documents based on relevance.

**Parameters:**
- `state`: AgentState with links

**Returns:**
- Updated AgentState with reranked_docs and reranked_urls

**Features:**
- Parallel document loading
- Timeout handling
- Content cleaning
- AI-powered reranking

#### `assistant_editor_node(state: AgentState) -> AgentState`
Processes documents and creates editorial summaries.

**Parameters:**
- `state`: AgentState with reranked_docs

**Returns:**
- Updated AgentState with context

**Processing:**
- Content summarization
- Key insight extraction
- Context consolidation

#### `article_writer_node(state: AgentState) -> AgentState`
Generates final article from processed context.

**Parameters:**
- `state`: AgentState with context

**Returns:**
- Updated AgentState with article

**Output:**
- Well-structured markdown article
- Comprehensive content coverage
- Professional formatting

### Utility Functions

#### `_load_documents_safely(urls, max_workers=3, timeout=30)`
Safely loads documents with error handling and timeouts.

#### `_clean_document_content(content)`
Cleans and normalizes document content for processing.

## Configuration

### Environment Variables

```env
# Search Engine Configuration
SEARCH_API_KEY=your_search_api_key
SEARCH_ENGINE_ID=your_search_engine_id

# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_TOKEN=your_hf_token

# Application Settings
MAX_SEARCH_RESULTS=20
RERANK_TOP_K=5
DOCUMENT_TIMEOUT=30
```

### Customization Options

- **Search Parameters**: Adjust result count and quality thresholds
- **Reranking Models**: Swap reranking models for different domains
- **Content Processing**: Modify summarization and extraction logic
- **UI Styling**: Customize the Streamlit interface appearance

### Typical Performance

- **Search Stage**: 2-5 seconds
- **Document Loading**: 5-10 seconds
- **Content Analysis**: 3-7 minutes
- **Article Generation**: 5-15 seconds
- **Total Time**: 15-40 seconds per query

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **LangChain**: For the powerful AI framework
- **LangGraph**: For the node-based workflow system
- **Streamlit**: For the excellent web interface framework
- **Open Source Community**: For the amazing tools and libraries

## Roadmap

### Upcoming Features

- [ ] Conversation based on article generation
- [ ] Custom source filtering
- [ ] Concurrent document loading
- [ ] Advanced citation management

### Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Enhanced UI and error handling
- **v1.2.0**: Performance optimizations and caching

---

**Built with using LangGraph, LangChain, and Streamlit**

For support, please open an issue on GitHub or contact [priyanshusarkar7895@gmail.com](mailto:priyanshusarkar7895@gmail.com).