Exam-Guide ChatBot: RAG-Powered Study Assistant

This ChatBot is an advanced educational platform designed to transform static study materials into dynamic, exam-ready knowledge. By leveraging Retrieval-Augmented Generation (RAG), This Chatbot allows students to ground AI responses in their own verified sources—whether through PDF uploads or raw text pasting.

The system is specifically engineered for academic success, featuring a specialized engine that "enlarges" matter into professional formats suitable for 2-mark, 5-mark, and 10-mark examination requirements.

🚀 Key Features

Dual-Stream RAG Vault:

PDF Indexing: Upload multiple PDFs to be chunked and indexed into a local FAISS vector store.

Text Lab: Paste raw notes, web articles, or snippets directly into the sidebar for instant context-aware querying.

Exam-Optimized Generation:

2-Mark Mode: Crisp, high-impact technical definitions.

5-Mark Mode: Structured answers with bold headings and 1-2 sentence explanations.

10-Mark Mode: Extensive academic responses with Introduction, Detailed Analysis, and Conclusions.

Viva Mode: Conversational, analogy-based explanations for oral exams.

Master Summary: A holistic synthesis engine that aggregates information across all indexed files and pasted text.

Premium UI/UX:

Glassmorphic design with Dark/Light mode support.

Integrated Pomodoro Timer for focused study sessions.

Fully responsive sidebar and chat interface.

🛠️ Tech Stack

Frontend

HTML5/Tailwind CSS: Modern, responsive styling.

JavaScript (Vanilla): State management and asynchronous API handling.

Lucide Icons: High-quality vector iconography.

Backend

Flask: Lightweight Python web framework.

LangChain: Framework for developing applications powered by language models.

Google Gemini API: Advanced LLM for reasoning and generation.

FAISS: High-performance vector database for local similarity search.

HuggingFace Embeddings: sentence-transformers/all-MiniLM-L6-v2 for semantic indexing.


📖 Usage Guide

Populate the Vault: Upload your course PDFs or paste text into the Text Lab in the sidebar.

Select Mode: Choose your target exam format (2, 5, or 10 marks).

Query: Ask specific questions based on your notes.

Summarize: Click Master Summary to get an executive overview of all provided material.

🛡️ Architecture Note

This application follows a strict Offline-First Indexing strategy for PDF files using FAISS, ensuring that your document structure is preserved locally before being retrieved for the LLM. The prompts are governed by a Strict Formatting Protocol to prevent "paragraph dumping" and ensure readability.
