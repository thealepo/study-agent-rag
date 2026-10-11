# StudyAgent

A small, from-scratch **RAG-powered AI Study Agent** that lets you upload a PDF, 
ask questions about it, and turn the material into an interactive study session.

<img width="5414" height="3909" alt="Image" src="https://github.com/user-attachments/assets/a7339cae-c87d-4de8-966b-f0d5fa11841c" />

## What it does

- Extracts text from a PDF with PyMuPDF
- Splits the document into overlapping chunks
- Embeds the chunks with `all-MiniLM-L6-v2`
- Retrieves the relevant chunks with a cosine similarity
- Exposes retrieval to Gemini as a `search_notes` tool
- Preserves the conversation history
- Serves the final experience through a Gradio frontend

## Quick Start

Clone
```
git clone https://github.com/thealepo/study-agent-rag.git
cd study-agent-rag
```

Create a Virtual Environment
```
python -m venv .venv
```

Install
```
pip install -r requirements.txt
```

Configure you .env
```
.env
```
