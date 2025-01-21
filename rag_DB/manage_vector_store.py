import json
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.schema import Document
import os

# 设置嵌入模型
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DATABASE_PATH = "hand_signs_knowledge_DS.faiss"

def json_to_faiss(json_file, db_path):
    """
    将 JSON 文件转换为 FAISS 数据库。
    :param json_file: JSON 文件路径
    :param db_path: FAISS 数据库保存路径
    """
    # 加载 JSON 数据
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 初始化嵌入模型
    embeddings = DashScopeEmbeddings(model="text-embedding-v1", dashscope_api_key="sk-a555417cf91347b480be57fe112f59db")

    # 创建文档和向量
    documents = []
    texts = []
    for item in data:
        doc = Document(
            page_content=item["question"],
            metadata={"id": item["id"], "answer": item["answer"]}
        )
        documents.append(doc)
        texts.append(item["question"])
    
    # 生成嵌入向量
    vectors = embeddings.embed_documents(texts)
    
    # 初始化 InMemoryDocstore
    docstore = InMemoryDocstore(dict(enumerate(documents)))

    # 构建 FAISS 索引
    dimension = len(vectors[0])
    index = faiss.IndexFlatL2(dimension)
    vector_store = FAISS(embedding_function=embeddings, index=index, docstore=docstore, index_to_docstore_id={i: i for i in range(len(documents))})
    
    # 添加向量到 FAISS
    vector_store.add_documents(documents)

    # 保存到本地
    vector_store.save_local(db_path)
    print(f"FAISS 数据库已保存到: {db_path}")

if __name__ == "__main__":
    # 输入 JSON 文件路径
    json_file = "data/hand_signs.json"  # 替换为你的 JSON 文件路径
    json_to_faiss(json_file, DATABASE_PATH)
