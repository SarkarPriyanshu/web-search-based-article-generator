import streamlit as st
from urllib.parse import urlparse
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
    spinner_html = f"""
    <div class="loading-container" style="
        display: flex; 
        align-items: center; 
        gap: 12px; 
        padding: 16px 20px; 
        margin: 12px 0; 
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    ">
        <div class="spinner-{stage}" style="
            width: 20px; 
            height: 20px; 
            border: 2px solid #dee2e6; 
            border-top: 2px solid #007bff; 
            border-radius: 50%; 
            animation: spin-{stage} 1s linear infinite;
            flex-shrink: 0;
        "></div>
        <span style="
            font-size: 14px; 
            font-weight: 500; 
            color: #495057;
            line-height: 1.4;
        ">{message}</span>
    </div>
    <style>
        @keyframes spin-{stage} {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
    """
    container.markdown(spinner_html, unsafe_allow_html=True)

def show_error_message(error_message):
    """Display error message in a styled container"""
    error_html = f"""
    <div style="
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    ">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: #721c24; font-size: 16px;">⚠️</span>
            <span style="color: #721c24; font-weight: 500; font-size: 14px;">{error_message}</span>
        </div>
    </div>
    """
    st.markdown(error_html, unsafe_allow_html=True)

# --- Force Clear All Content ---
def clear_all():
    """Force clear all Streamlit elements"""
    # Clear all keys that might persist
    keys_to_clear = [k for k in st.session_state.keys() if not k.startswith('_')]
    for key in keys_to_clear:
        del st.session_state[key]

# --- UI Setup ---
st.set_page_config(
    page_title="AI Article Generator", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Main title
st.markdown("""
<div style="text-align: center; padding: 20px 0 30px 0;">
    <h1 style="
        font-size: 36px;
        font-weight: 700;
        color: #212529;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    ">LangGraph AI Article Generator</h1>
    <p style="
        font-size: 16px;
        color: #6c757d;
        margin: 0;
        font-weight: 400;
    ">Transform your queries into comprehensive, well-researched articles</p>
</div>
""", unsafe_allow_html=True)

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

# Query input
st.markdown('<div class="query-section">', unsafe_allow_html=True)
st.markdown('<div class="query-label">What would you like to research?</div>', unsafe_allow_html=True)
user_query = st.text_input("", placeholder="Enter your research topic or question...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Clear everything first
clear_all()

# Process query
if user_query and user_query.strip():
    # Force clear by creating completely new structure
    content_area = st.container()
    
    with content_area:
        try:
            # Track what we've shown (reset for each run)
            shown_cards = {'links': False, 'reranked': False, 'context': False, 'article': False}
            
            # Start with loading
            current_display = st.empty()
            show_loading_spinner(current_display, "Searching the web for relevant information...", "search")
            
            # Stream responses
            for state_chunk in content_writter_agent.stream(
                {"query": user_query.strip()},
                config=config,
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
                    current_display.empty()
                    show_error_message(current_state.error)
                    break

                # Show Web Search Results
                if current_state.links and not shown_cards['links']:
                    current_display.empty()
                    
                    # Create new container for links
                    links_card = st.empty()
                    links_html = f"""
                    <div class="card-section">
                        <div class="section-title">Web Search Results</div>
                        <div class="section-subtitle">Found {len(current_state.links)} relevant sources</div>
                        {display_links_horizontal(current_state.links)}
                    </div>
                    """
                    links_card.markdown(links_html, unsafe_allow_html=True)
                    shown_cards['links'] = True
                    
                    # New loading for next stage
                    current_display = st.empty()
                    show_loading_spinner(current_display, "Analyzing and ranking the most relevant sources...", "rerank")

                # Show Reranked Sources
                elif current_state.reranked_urls and not shown_cards['reranked']:
                    current_display.empty()
                    
                    # Create new container for reranked
                    reranked_card = st.empty()
                    reranked_html = f"""
                    <div class="card-section">
                        <div class="section-title">Selected Sources</div>
                        <div class="section-subtitle">Top {len(current_state.reranked_urls)} most relevant sources</div>
                        {display_links_horizontal(current_state.reranked_urls)}
                    </div>
                    """
                    reranked_card.markdown(reranked_html, unsafe_allow_html=True)
                    shown_cards['reranked'] = True
                    
                    # New loading for next stage
                    current_display = st.empty()
                    show_loading_spinner(current_display, "Extracting and summarizing key information...", "context")

                # Show Editorial Summary
                elif current_state.context and not shown_cards['context']:
                    current_display.empty()
                    
                    # Create new container for context
                    context_card = st.empty()
                    context_html = """
                    <div class="card-section">
                        <div class="section-title">Editorial Summary</div>
                        <div class="section-subtitle">Key insights extracted from selected sources</div>
                    </div>
                    """
                    context_card.markdown(context_html, unsafe_allow_html=True)
                    
                    # Add context content
                    context_content = st.empty()
                    context_content.markdown("---")
                    context_content.markdown(current_state.context)
                    shown_cards['context'] = True
                    
                    # New loading for final stage
                    current_display = st.empty()
                    show_loading_spinner(current_display, "Generating comprehensive article...", "article")

                # Show Generated Article
                elif current_state.article and not shown_cards['article']:
                    current_display.empty()
                    
                    # Create new container for article
                    article_card = st.empty()
                    article_html = """
                    <div class="card-section">
                        <div class="section-title">Generated Article</div>
                        <div class="section-subtitle">Comprehensive article based on research findings</div>
                    </div>
                    """
                    article_card.markdown(article_html, unsafe_allow_html=True)
                    
                    # Add article content
                    article_content = st.empty()
                    article_content.markdown("---")
                    article_content.markdown(current_state.article)
                    shown_cards['article'] = True

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Try refreshing the page or rephrasing your query.")

elif user_query and not user_query.strip():
    show_error_message("Please enter a valid research topic or question.")

# Footer
st.markdown("""
<div style="text-align: center; padding: 40px 0 20px 0; color: #6c757d; font-size: 14px;">
    <hr style="border: none; height: 1px; background-color: #dee2e6; margin-bottom: 20px;">
    Powered by LangGraph AI • Built with Streamlit
</div>
""", unsafe_allow_html=True)