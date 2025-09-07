from src.states.search_states import (ArticleWritter,DocumentEditorState)
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from sentence_transformers import CrossEncoder
from dotenv import load_dotenv
import os

# load_dotenv()

# gemini_api_key = os.getenv('GEMINI_API_KEY')
# model_name = os.getenv('MODEL_NAME')

gemini_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite",api_key="AIzaSyD0uwxfexF4e3lE-SEDJnwyfiGsZSyutfA")
reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

article_writter_model = gemini_model.with_structured_output(ArticleWritter)
document_editor_model = gemini_model.with_structured_output(DocumentEditorState)