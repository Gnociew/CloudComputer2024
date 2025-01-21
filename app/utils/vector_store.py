from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

def load_vector_store(db_path):
    """
    加载向量数据库
    """
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(db_path, embeddings)

def save_vector_store(vector_store, db_path):
    """
    保存向量数据库
    """
    vector_store.save_local(db_path)
