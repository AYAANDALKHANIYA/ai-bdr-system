import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -----------------------------
# LOAD DOCUMENTS
# -----------------------------
def load_documents():
    documents = []

    folder_path = "data"

    if not os.path.exists(folder_path):
        print("❌ 'data' folder not found")
        return []

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            loader = TextLoader(os.path.join(folder_path, file))
            documents.extend(loader.load())

    return documents


# -----------------------------
# CREATE VECTOR DB
# -----------------------------
def create_vector_store():
    docs = load_documents()

    if not docs:
        print("❌ No documents found in /data folder")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    splits = text_splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # ✅ FIX: remove persist() issue (new version auto saves)
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="db"
    )

    print("✅ Vector DB created successfully!")


# -----------------------------
# QUERY + GENERATE (RAG)
# -----------------------------
def query_vector_store(query):
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vectorstore = Chroma(
        persist_directory="db",
        embedding_function=embeddings
    )

    docs = vectorstore.similarity_search(query, k=3)

    # ✅ FIX: safe extraction (prevents your error)
    context_list = []
    for doc in docs:
        if hasattr(doc, "page_content"):
            context_list.append(doc.page_content)
        else:
            context_list.append(str(doc))

    context = "\n\n".join(context_list)

    # Prompt
    prompt = f"""
You are an AI assistant.

Answer the question using ONLY the context below.

Context:
{context}

Question:
{query}

Answer:
"""

    # ✅ GROQ MODEL (WORKING + UPDATED)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content