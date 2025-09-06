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

def show_error_message(container, error_message):
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
    container.markdown(error_html, unsafe_allow_html=True)

def clear_all_session_data():
    """Clear all session state data for fresh start"""
    keys_to_clear = [key for key in st.session_state.keys() if key not in ['query_input']]
    for key in keys_to_clear:
        del st.session_state[key]

# --- UI Setup ---
st.set_page_config(
    page_title="AI Article Generator", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Main title with better styling
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

# Enhanced CSS styling
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom styles */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Query input section */
    .query-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border: 1px solid #e9ecef;
    }
    
    /* Card sections */
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
    
    /* Typography hierarchy */
    .main-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 12px;
        margin-top: 0;
        color: #212529;
        line-height: 1.3;
        letter-spacing: -0.3px;
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
    
    .content-body {
        font-size: 16px;
        line-height: 1.7;
        margin-top: 12px;
        margin-bottom: 0;
        color: #495057;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #dc3545;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #c82333;
        box-shadow: 0 2px 4px rgba(220,53,69,0.2);
    }
    
    /* Input styling */
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

# Clear button with better positioning
col1, col2, col3 = st.columns([1, 1, 1])
with col3:
    def clear_results():
        clear_all_session_data()
        st.rerun()

    if st.button("Clear Results", help="Clear all previous results and start fresh"):
        clear_results()

# Query input with enhanced styling
st.markdown('<div class="query-section">', unsafe_allow_html=True)
st.markdown('<div class="query-label">What would you like to research?</div>', unsafe_allow_html=True)

# Handle query input and reset logic
user_query = st.text_input("", placeholder="Enter your research topic or question...", label_visibility="collapsed", key="query_input")

# Check if query has changed and clear session data
if user_query:
    if "current_query" not in st.session_state or st.session_state.get("current_query") != user_query:
        # Clear all previous data for fresh start
        clear_all_session_data()
        st.session_state["current_query"] = user_query

st.markdown('</div>', unsafe_allow_html=True)

# --- Handle Query ---
if user_query:
    try:
        # Create containers for each stage
        links_container = st.empty()
        reranked_container = st.empty()
        context_container = st.empty()
        article_container = st.empty()

        # Track processing stages
        if "stages_completed" not in st.session_state:
            st.session_state["stages_completed"] = {
                'search': False,
                'rerank': False,
                'context': False,
                'article': False
            }

        # Show initial loading
        if not st.session_state["stages_completed"]['search']:
            show_loading_spinner(links_container, "Searching the web for relevant information...", "search")

        for state_chunk in content_writter_agent.stream(
            {"query": user_query},
            config=config,
            stream_mode="values"
        ):
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

            # Check for errors in current state
            if hasattr(current_state, 'error') and current_state.error:
                show_error_message(st.empty(), current_state.error)
                continue

            # Handle Links from Web Search (Stage 1)
            if current_state.links and not st.session_state["stages_completed"]['search']:
                # Show links within the same card
                links_html = (
                    f'<div class="card-section">'
                    f'    <div class="section-title">Web Search Results</div>'
                    f'    <div class="section-subtitle">Found {len(current_state.links)} relevant sources</div>'
                    f'    {display_links_horizontal(current_state.links)}'
                    f'</div>'
                )

                links_container.markdown(links_html, unsafe_allow_html=True)
                
                st.session_state["stages_completed"]['search'] = True
                
                # Show next stage loading
                if not st.session_state["stages_completed"]['rerank']:
                    show_loading_spinner(reranked_container, "Analyzing and ranking the most relevant sources...", "rerank")

            # Handle Reranked Links (Stage 2)
            if current_state.reranked_urls and not st.session_state["stages_completed"]['rerank']:
                # Show reranked links within the same card
                reranked_html = (
                    f'<div class="card-section">'
                    f'    <div class="section-title">Selected Sources</div>'
                    f'    <div class="section-subtitle">Top {len(current_state.reranked_urls)} most relevant sources selected</div>'
                    f'    {display_links_horizontal(current_state.reranked_urls)}'
                    f'</div>'
                )

                reranked_container.markdown(reranked_html, unsafe_allow_html=True)
                
                st.session_state["stages_completed"]['rerank'] = True
                
                # Show next stage loading
                if not st.session_state["stages_completed"]['context']:
                    show_loading_spinner(context_container, "Extracting and summarizing key information...", "context")

            # Handle Editorial Summary (Stage 3)
            if current_state.context and not st.session_state["stages_completed"]['context']:
                # Display context as markdown
                context_html = (
                    f'<div class="card-section">'
                    f'    <div class="section-title">Editorial Summary</div>'
                    f'    <div class="section-subtitle">Key insights extracted from selected sources</div>'
                    f'</div>'
                )

                context_container.markdown(context_html, unsafe_allow_html=True)
                
                # Display context content as markdown
                with context_container.container():
                    st.markdown("---")
                    st.markdown(current_state.context)
                
                st.session_state["stages_completed"]['context'] = True
                
                # Show final stage loading
                if not st.session_state["stages_completed"]['article']:
                    show_loading_spinner(article_container, "Generating comprehensive article...", "article")

            # Handle Generated Article (Stage 4)
            if current_state.article and not st.session_state["stages_completed"]['article']:
                # Display article header
                article_html = (
                    f'<div class="card-section">'
                    f'    <div class="section-title">Generated Article</div>'
                    f'    <div class="section-subtitle">Comprehensive article based on research findings</div>'
                    f'</div>'
                )

                article_container.markdown(article_html, unsafe_allow_html=True)
                
                # Display article content as proper markdown
                with article_container.container():
                    st.markdown("---")
                    st.markdown(current_state.article)
                
                st.session_state["stages_completed"]['article'] = True

    except Exception as e:
        # Clear any remaining loading indicators and show error
        st.error(f"An error occurred: {str(e)}")
        st.info("Try refreshing the page or rephrasing your query.")

# Footer
st.markdown(
    (
        f'<div style="text-align: center; padding: 40px 0 20px 0; color: #6c757d; font-size: 14px;">'
        f'    <hr style="border: none; height: 1px; background-color: #dee2e6; margin-bottom: 20px;">'
        f'    Powered by LangGraph AI • Built with Streamlit'
        f'</div>'
    ),
    unsafe_allow_html=True
)