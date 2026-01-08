from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

import google.generativeai as genai

# ---------------- CONFIG ----------------

UPLOAD_FOLDER = "uploads"
VECTOR_DB_PATH = "vectorstore"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# Note: In a real app, use environment variables for keys
genai.configure(api_key="AIzaSyAlTvqEGnhYnXbVnRXrRu0bcXPUrdItmmA")

app = Flask(__name__)
CORS(app)

# ---------------- GLOBALS ----------------

vector_db = None

# Initialize embeddings once to save memory/time
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ---------------- PROMPT BUILDER ----------------

def exam_prompt(context, question, mode):
    mode_instruction = {
        "2-mark": (
            "Provide 2-3 crisp, high-impact technical points. "
            "Focus on definitions and core concepts. Keep it concise but professional."
        ),
        "5-mark": (
            "Provide a structured answer. Begin with a brief 1-line introduction. "
            "Use 5-7 numbered points. Each point should have a **BOLD HEADING** on its own line, "
            "followed by a 1-2 sentence explanation on the next line. "
            "End with a short concluding thought."
        ),
        "10-mark": (
            "Provide an extensive, comprehensive academic response. "
            "Structure: **INTRODUCTION**, **DETAILED ANALYSIS** (with sub-sections), and **CONCLUSION**. "
            "Enlarge the matter by explaining 'Why', 'How', and 'Impact'. "
            "Use a mix of numbered lists for primary points and bullet points for sub-features. "
            "Ensure every heading and every list item starts on a completely new line with a blank line between them."
        ),
        "viva": (
            "Explain this like a teacher speaking to a student. "
            "Use simple analogies. Provide a 'Key Points to Remember' bulleted list at the end."
        ),
        "summary": (
            "Provide a high-level executive summary of the provided content. "
            "Highlight the main theme, 3-4 critical pillars of the document, and a final summary statement."
        )
    }

    return f"""
You are a high-level AI Academic Professor and Exam Specialist. 
Your goal is to transform the provided Source Material into a perfectly structured, line-wise exam answer.

STRICT FORMATTING PROTOCOL (MANDATORY):
1. **NO PARAGRAPH DUMPS**: Never output more than 2 lines of text without a blank line or a bullet point.
2. **LINE-WISE STRUCTURE**: Every single point must start on its own new line.
3. **HEADING ISOLATION**: If you use a bold heading, the text describing it MUST start on the next line.
4. **QUESTION-ANSWER PAIRS**: If you are generating questions, list the Question first, then a blank line, then the Answer.
5. **PROFESSIONAL MARKDOWN**: Use **Bold** for emphasis. Use numerical lists (1., 2.) for main ideas and dashes (-) for supporting details.
6. **WHITE SPACE**: Use double line breaks (blank lines) between different sections, headings, and individual points.
7. **NO HASH SYMBOLS**: Do not use '#' for headers. Use **BOLD UPPERCASE TITLES** on their own isolated lines.
8. **SOURCE MATERIAL**: The information below comes from multiple sources (uploaded documents and user-provided notes). Use ALL relevant details to form the answer.

SOURCE MATERIAL:
{context}

USER QUESTION:
{question}

EXAM MODE: {mode.upper()}
SPECIFIC INSTRUCTIONS:
{mode_instruction.get(mode, "Provide a well-structured, professional response.")}
"""

# ---------------- GEMINI CALL ----------------

def generate_answer(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash") 
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error calling AI Model: {str(e)}"

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_docs():
    global vector_db

    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    documents = []
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        loader = PyPDFLoader(file_path)
        documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)
    
    # FAISS allows adding to existing index, but for simplicity, we re-index all uploaded files
    vector_db = FAISS.from_documents(chunks, embeddings)
    vector_db.save_local(VECTOR_DB_PATH)

    return jsonify({
        "message": f"Successfully indexed {len(files)} documents",
        "chunks": len(chunks)
    })

@app.route("/ask", methods=["POST"])
def ask():
    global vector_db

    data = request.json
    question = data.get("question")
    mode = data.get("mode", "5-mark")
    pasted_text = data.get("text", "").strip() 

    if not question:
        return jsonify({"error": "Question is required"}), 400

    # --- HYBRID CONTEXT GATHERING ---
    combined_context_parts = []
    sources_used = []

    # 1. Pull from Pasted Text (if present)
    if pasted_text:
        combined_context_parts.append(f"--- FROM USER NOTES ---\n{pasted_text}")
        sources_used.append("Pasted Notes")

    # 2. Pull from Uploaded Documents (if present)
    if vector_db:
        docs = vector_db.similarity_search(question, k=6)
        pdf_context = "\n\n".join([doc.page_content for doc in docs])
        combined_context_parts.append(f"--- FROM UPLOADED DOCUMENTS ---\n{pdf_context}")
        sources_used.append("PDF Documents")

    # 3. Check if we have any context at all
    if not combined_context_parts:
        return jsonify({"error": "Please provide context by uploading a PDF or pasting text."}), 400

    # Join all sources together
    final_context = "\n\n".join(combined_context_parts)
    
    prompt = exam_prompt(final_context, question, mode)
    answer = generate_answer(prompt)

    return jsonify({
        "answer": answer,
        "source": " + ".join(sources_used)
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)