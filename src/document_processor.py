import tempfile
import os
import glob
from typing import List
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document

from .config import Config

class DocumentProcessor:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=Config.GOOGLE_API_KEY
        )
        self.vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
    
    def load_static_content(self) -> int:
        documents = []
        static_path = "static_content"
        
        if os.path.exists(static_path):
            for file_path in glob.glob(f"{static_path}/**/*", recursive=True):
                if os.path.isfile(file_path):
                    if file_path.endswith('.pdf'):
                        documents.extend(self._load_static_pdf(file_path))
                    elif file_path.endswith('.txt'):
                        documents.extend(self._load_static_text(file_path))
        
        if documents:
            self._create_vectorstore(documents)
            
        return len(documents)
    
    def load_context_files(self, files) -> int:
        documents = []
        
        for uploaded_file in files:
            if uploaded_file.type == "application/pdf":
                documents.extend(self._load_pdf_file(uploaded_file))
            elif uploaded_file.type == "text/plain":
                documents.extend(self._load_text_file(uploaded_file))
        
        if documents:
            self._create_vectorstore(documents)
            
        return len(documents)
    
    def _load_pdf_file(self, uploaded_file) -> List[Document]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            loader = PyPDFLoader(tmp_file_path)
            docs = loader.load()
            return docs
        finally:
            os.unlink(tmp_file_path)
    
    def _load_text_file(self, uploaded_file) -> List[Document]:
        content = uploaded_file.getvalue().decode("utf-8")
        return [Document(page_content=content)]
    
    def _load_static_pdf(self, file_path) -> List[Document]:
        try:
            loader = PyPDFLoader(file_path)
            return loader.load()
        except Exception:
            return []
    
    def _load_static_text(self, file_path) -> List[Document]:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return [Document(page_content=content)]
        except Exception:
            return []
    
    def _create_vectorstore(self, documents: List[Document]):
        splits = self.text_splitter.split_documents(documents)
        self.vectorstore = FAISS.from_documents(splits, self.embeddings)
    
    def search_similar_documents(self, query: str) -> str:
        if not self.vectorstore:
            return ""
        
        relevant_docs = self.vectorstore.similarity_search(
            query, 
            k=Config.MAX_SIMILARITY_SEARCH_RESULTS
        )
        
        if relevant_docs:
            return "\n\n".join([doc.page_content for doc in relevant_docs])
        
        return ""
