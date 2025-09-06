from src.prompts.search_prompts import (article_writter_prompt,document_editor_prompt)
from src.models.search_models import (article_writter_model,document_editor_model)


article_writter_chain = article_writter_prompt | article_writter_model
document_editor_chain = document_editor_prompt | document_editor_model