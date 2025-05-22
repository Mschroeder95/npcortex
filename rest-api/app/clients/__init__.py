import os
from config import CHROMA_HOST, CHROMA_PORT, OLLAMA_URL
import chromadb
import chromadb.config
import ollama
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE
from minio import Minio

chroma_client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    ssl=False,
    settings=chromadb.config.Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)

ollama_client = ollama.Client(host=OLLAMA_URL)

minio_client = Minio(os.getenv('MINIO_HOST'),
    access_key=os.getenv('MINIO_ACCESS_KEY'),
    secret_key=os.getenv('MINIO_SECRET_KEY'),
    secure=False
)
