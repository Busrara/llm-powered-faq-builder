# -*- coding: utf-8 -*-
"""Welcome To Colab

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/notebooks/intro.ipynb
"""

import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import pipeline
import tempfile
from langchain.schema import Document

qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

def load_pdf(pdf_path=None, url=None):
    if pdf_path:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
    elif url:
        response = requests.get(url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(response.content)
            temp_file.close()
            loader = PyPDFLoader(temp_file.name)
            documents = loader.load()
    else:
        raise ValueError("Please provide either a file path or a URL.")
    return documents

def load_web_page(url):
    response = requests.get(url)
    return response.text

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return text

def convert_to_document_format(content):
    return [Document(page_content=content)]

def split_documents(documents):
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)

def create_vector_store(docs):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    db = Chroma.from_documents(docs, embeddings)
    return db

def answer_question(user_input, db):
    results = db.similarity_search(user_input, k=3)
    if not results:
        return "No relevant information found in the content."
    context = " ".join([doc.page_content for doc in results])
    result = qa_pipeline(question=user_input, context=context)
    return result["answer"]