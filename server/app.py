import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import SecretStr # <-- IMPORT ADDED HERE

# LangChain components
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain

# --- 1. Load Environment Variables ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# --- 2. Perform the Indexing Step (runs only once on startup) ---
print("Loading and indexing document... This may take a moment.")
loader = TextLoader("my_document.txt")
document = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(document)

# Use SecretStr to wrap the API key
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=SecretStr(api_key))

vector_store = FAISS.from_documents(chunks, embedding=embeddings)
print("Indexing complete. Server is ready.")

# --- 3. Define the QA Chain (reusable) ---
prompt_template = """
Answer the question as detailed as possible from the provided context. If the answer is not in the
provided context, just say, "The answer is not available in the context". Do not provide a wrong answer.

Context:
{context}

Question:
{question}

Answer:
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# Use SecretStr to wrap the API key
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", api_key=SecretStr(api_key), temperature=0.3)

chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

# --- 4. Set up the Flask App ---
app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing

@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        similar_docs = vector_store.similarity_search(query, k=3)
        response = chain.run(input_documents=similar_docs, question=query)
        return jsonify({"answer": response})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Failed to process the query"}), 500

# --- 5. Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)