import os
import logging

from lightrag import LightRAG, QueryParam
from lightrag.llm import zhipu_complete, zhipu_embedding
from lightrag.utils import EmbeddingFunc

from pdf2image import convert_from_path
import pytesseract


os.environ["NEO4J_URI"] = "neo4j://121.43.160.105:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "123456"

# WORKING_DIR = "./kg-pdf-test"

WORKING_DIR = "./local_neo4jWorkDir"


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

api_key = os.environ.get("ZHIPUAI_API_KEY")
if api_key is None:
    raise Exception("Please set ZHIPU_API_KEY in your environment")


rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=zhipu_complete,
    graph_storage="Neo4JStorage",
    llm_model_name="glm-4-flashx",  # Using the most cost/performance balance model, but you can change it here.
    llm_model_max_async=8,
    llm_model_max_token_size=32768,
    vector_storage="MilvusVectorDBStorge",
    embedding_func=EmbeddingFunc(
        embedding_dim=2048,  # Zhipu embedding-3 dimension
        max_token_size=8192,
        func=lambda texts: zhipu_embedding(texts),
    ),
)

# # PDF 文件路径
# file_path = '生物必修一.pdf'

# # 将 PDF 转换为图像
# images = convert_from_path(file_path)

# # 初始化文本内容
# text_content = ''

# # 对每一页进行 OCR
# for image in images:
#     # 提取中文文本
#     text_content += pytesseract.image_to_string(image, lang='chi_sim')

# # 确保 text_content 是字符串类型
# text_content = str(text_content)

# rag.insert(text_content)

# with open("./book.txt", "r", encoding="utf-8") as f:
#     rag.insert(f.read())

# Perform naive search
query_test = "DNA是如何指导生成蛋白质的？让我们一步一步思考。"

print(
    rag.query(query_test, param=QueryParam(mode="naive"))
)

# Perform local search
print(
    rag.query(query_test, param=QueryParam(mode="local"))
)

# Perform global search
print(
    rag.query(query_test, param=QueryParam(mode="global"))
)

# Perform hybrid search
print(
    rag.query(query_test, param=QueryParam(mode="hybrid"))
)
