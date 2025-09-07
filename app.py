import streamlit as st
import sys
import os
from urllib.parse import urlparse

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


from src.states.search_states import AgentState
from src.graphs.search_graphs import content_writter_agent, config

# --- Utility Functions ---
def get_favicon_url(link):
    domain = urlparse(link).netloc
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"

def truncate_middle(text, max_length=13):
    return text if len(text) <= max_length else text[:6] + "..." + text[-3:]

def display_links_horizontal(links):
    if not links:
        return '<div style="padding: 16px; text-align: center; color: #666; font-style: italic;">No links available</div>'
    
    html = ['<div style="display:flex; flex-wrap: wrap; gap:8px; padding:12px 0; margin-top: 12px;">']
    for link in links:
        domain = urlparse(link).netloc
        display_domain = truncate_middle(domain)
        favicon_url = get_favicon_url(link)
        capsule = (
            f'<a href="{link}" target="_blank" style="text-decoration:none;">'
            f'<div style="flex: 0 0 auto; min-width: 6rem; max-width: 10rem; '
            f'display: flex; align-items: center; justify-content: center; '
            f'background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; '
            f'padding: 6px 10px; gap: 6px; white-space: nowrap; '
            f'transition: all 0.2s ease; cursor: pointer; '
            f'box-shadow: 0 1px 2px rgba(0,0,0,0.05);" '
            f'onmouseover="this.style.backgroundColor=\'#e9ecef\'; this.style.transform=\'translateY(-1px)\'; this.style.boxShadow=\'0 2px 4px rgba(0,0,0,0.1)\';" '
            f'onmouseout="this.style.backgroundColor=\'#f8f9fa\'; this.style.transform=\'translateY(0)\'; this.style.boxShadow=\'0 1px 2px rgba(0,0,0,0.05)\';">'
            f'<img src="{favicon_url}" alt="{display_domain}" width="16" height="16" '
            f'style="border-radius: 2px;">'
            f'<span title="{domain}" style="font-size: 12px; color: #495057; font-weight: 500;">{display_domain}</span>'
            f'</div></a>'
        )
        html.append(capsule)
    html.append('</div>')
    return ''.join(html)

def show_loading_spinner(container, message, stage):
    """Display a loading spinner with message for specific stage"""
    spinner_html = (
        f'<div class="loading-container" style="'
        f'display: flex; align-items: center; gap: 12px; padding: 16px 20px; '
        f'margin: 12px 0; background-color: #f8f9fa; border: 1px solid #e9ecef; '
        f'border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">'
        
        f'<div class="spinner-{stage}" style="'
        f'width: 20px; height: 20px; border: 2px solid #dee2e6; '
        f'border-top: 2px solid #007bff; border-radius: 50%; '
        f'animation: spin-{stage} 1s linear infinite; flex-shrink: 0;"></div>'
        
        f'<span style="font-size: 14px; font-weight: 500; color: #495057; '
        f'line-height: 1.4;">{message}</span>'
        f'</div>'
        
        f'<style>'
        f'@keyframes spin-{stage} {{'
        f'0% {{ transform: rotate(0deg); }}'
        f'100% {{ transform: rotate(360deg); }}'
        f'}}'
        f'</style>'
    )

    container.markdown(spinner_html, unsafe_allow_html=True)

def show_error_message(error_message):
    """Display error message in a styled container"""
    error_html = (
        f'<div style="background-color: #f8d7da; border: 1px solid #f5c6cb; '
        f'border-radius: 8px; padding: 16px 20px; margin: 12px 0; '
        f'box-shadow: 0 2px 4px rgba(0,0,0,0.05);">'
        
        f'<div style="display: flex; align-items: center; gap: 8px;">'
        f'<span style="color: #721c24; font-size: 16px;">⚠️</span>'
        f'<span style="color: #721c24; font-weight: 500; font-size: 14px;">{error_message}</span>'
        f'</div>'
        f'</div>'
    )

    st.markdown(error_html, unsafe_allow_html=True)

# --- UI Setup ---
st.set_page_config(
    page_title="AI Article Generator", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Main title
st.markdown(
    (
        f'<div style="text-align: center; padding: 20px 0 30px 0;">'
        f'<h1 style="font-size: 36px; font-weight: 700; color: #212529; '
        f'margin-bottom: 8px; letter-spacing: -0.5px;">'
        f'LangGraph AI Article Generator</h1>'
        f'<p style="font-size: 16px; color: #6c757d; margin: 0; font-weight: 400;">'
        f'Transform your queries into comprehensive, well-researched articles</p>'
        f'</div>'
    ),
    unsafe_allow_html=True,
)

# CSS Styling
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #f8f9fa;
    }
    
    .query-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border: 1px solid #e9ecef;
    }
    
    .card-section {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
        transition: box-shadow 0.3s ease;
    }
    
    .card-section:hover {
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }
    
    .query-label {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 12px;
        margin-top: 0;
        color: #495057;
        line-height: 1.4;
    }
    
    .section-title {
        font-size: 22px;
        font-weight: 650;
        margin-bottom: 16px;
        margin-top: 0;
        color: #343a40;
        line-height: 1.3;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .section-subtitle {
        font-size: 14px;
        font-weight: 500;
        color: #6c757d;
        margin-bottom: 8px;
        margin-top: -8px;
        line-height: 1.4;
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #dee2e6;
        padding: 12px;
        font-size: 16px;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #007bff;
        box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for query tracking
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Query input
st.markdown('<div class="query-section">', unsafe_allow_html=True)
st.markdown('<div class="query-label">What would you like to research?</div>', unsafe_allow_html=True)
user_query = st.text_input("", placeholder="Enter your research topic or question...", label_visibility="collapsed", key="query_input")
st.markdown('</div>', unsafe_allow_html=True)

# Check if this is a new query
is_new_query = user_query and user_query.strip() and user_query.strip() != st.session_state.last_query

# Clear previous content if new query
if is_new_query and not st.session_state.processing:
    st.session_state.last_query = user_query.strip()
    st.session_state.processing = True
    # Force page refresh to clear old content
    st.rerun()

# Process query - ONLY when user enters a new query and we're ready to process
if user_query and user_query.strip() and st.session_state.processing:
    
    # Create results container that will hold ALL content
    results_container = st.container()
    
    with results_container:
        try:
            # Initialize fresh state for this query
            links_displayed = False
            reranked_displayed = False
            context_displayed = False
            article_displayed = False
            
            # Create placeholders for each section
            links_placeholder = st.empty()
            reranked_placeholder = st.empty() 
            context_placeholder = st.empty()
            article_placeholder = st.empty()
            loading_placeholder = st.empty()
            
            # Start with loading
            show_loading_spinner(loading_placeholder, "Searching the web for relevant information...", "search")
            
            # Stream responses with fresh config
            fresh_config = config() if callable(config) else {"configurable": {"thread_id": str(__import__('uuid').uuid4())}}
            for state_chunk in content_writter_agent.stream(
                {"query": user_query.strip()},
                config=fresh_config,
                stream_mode="values"
            ):
                # Parse state
                current_state = None
                if isinstance(state_chunk, dict):
                    try:
                        current_state = AgentState.model_validate(state_chunk)
                    except Exception:
                        pass
                else:
                    current_state = state_chunk

                if not current_state:
                    continue

                # Handle errors
                if hasattr(current_state, 'error') and current_state.error:
                    loading_placeholder.empty()
                    show_error_message(current_state.error)
                    st.session_state.processing = False
                    break

                # Show Web Search Results
                if current_state.links and not links_displayed:
                    loading_placeholder.empty()
                    
                    with links_placeholder.container():
                        st.markdown('<div class="card-section">', unsafe_allow_html=True)
                        st.markdown('<div class="section-title">Web Search Results</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="section-subtitle">Found {len(current_state.links)} relevant sources</div>', unsafe_allow_html=True)
                        st.markdown(display_links_horizontal(current_state.links), unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    links_displayed = True
                    show_loading_spinner(loading_placeholder, "Analyzing and ranking the most relevant sources...", "rerank")

                # Show Reranked Sources
                elif current_state.reranked_urls and not reranked_displayed:
                    loading_placeholder.empty()
                    
                    with reranked_placeholder.container():
                        st.markdown('<div class="card-section">', unsafe_allow_html=True)
                        st.markdown('<div class="section-title">Selected Sources</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="section-subtitle">Top {len(current_state.reranked_urls)} most relevant sources</div>', unsafe_allow_html=True)
                        st.markdown(display_links_horizontal(current_state.reranked_urls), unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    reranked_displayed = True
                    show_loading_spinner(loading_placeholder, "Extracting and summarizing key information...", "context")

                # Show Editorial Summary
                elif current_state.context and not context_displayed:
                    loading_placeholder.empty()
                    
                    with context_placeholder.container():
                        st.markdown('<div class="card-section">', unsafe_allow_html=True)
                        st.markdown('<div class="section-title">Editorial Summary</div>', unsafe_allow_html=True)
                        st.markdown('<div class="section-subtitle">Key insights extracted from selected sources</div>', unsafe_allow_html=True)
                        st.markdown("---")
                        st.markdown(current_state.context)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    context_displayed = True
                    show_loading_spinner(loading_placeholder, "Generating comprehensive article...", "article")

                # Show Generated Article
                elif current_state.article and not article_displayed:
                    loading_placeholder.empty()
                    
                    with article_placeholder.container():
                        st.markdown('<div class="card-section">', unsafe_allow_html=True)
                        st.markdown('<div class="section-title">Generated Article</div>', unsafe_allow_html=True)
                        st.markdown('<div class="section-subtitle">Comprehensive article based on research findings</div>', unsafe_allow_html=True)
                        st.markdown("---")
                        st.markdown(current_state.article)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    article_displayed = True
                    st.session_state.processing = False

        except Exception as e:
            loading_placeholder.empty()
            st.error(f"An error occurred: {str(e)}")
            st.info("Try refreshing the page or rephrasing your query.")
            st.session_state.processing = False

elif user_query and not user_query.strip():
    show_error_message("Please enter a valid research topic or question.")

# Footer
st.markdown(
    (
        f'<div style="text-align: center; padding: 40px 0 20px 0; '
        f'color: #6c757d; font-size: 14px;">'
        f'<hr style="border: none; height: 1px; background-color: #dee2e6; margin-bottom: 20px;">'
        f'Powered by LangGraph AI • Built with Streamlit'
        f'</div>'
    ),
    unsafe_allow_html=True,
)