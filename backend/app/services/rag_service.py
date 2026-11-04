
import chromadb
from pypdf import PdfReader
import uuid

# Create ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create or access collection
collection = chroma_client.get_or_create_collection(
    name="podcast_documents"
)


# 1. Extract text from PDF
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# 2. Split extracted text into chunks
def split_text(text, chunk_size=500):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


# 3. Store document chunks in ChromaDB
def store_document(file_path):
    text = extract_text_from_pdf(file_path)

    if not text.strip():
        raise ValueError("No readable text found in PDF")

    chunks = split_text(text)

    collection.add(
        ids=[str(uuid.uuid4()) for _ in chunks],
        documents=chunks
    )

    return len(chunks)


# 4. Retrieve relevant documents from ChromaDB
def retrieve_relevant_documents(query, n_results=3):

    total_documents = collection.count()

    if total_documents == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, total_documents)
    )

    documents = results.get("documents", [[]])[0]

    return documents
