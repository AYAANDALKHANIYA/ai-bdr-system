from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def research_agent(company, industry):

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vectorstore = Chroma(
        persist_directory="db",
        embedding_function=embeddings
    )

    docs = vectorstore.similarity_search(
        f"{company} {industry}", k=3
    )

    # convert docs → text
    context = "\n".join([doc.page_content for doc in docs])

    return context