import os
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete
#########
# Uncomment the below two lines if running in a jupyter notebook to handle the async nature of rag.insert()
# import nest_asyncio
# nest_asyncio.apply()
#########

os.environ["OPENAI_API_KEY"] = "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"  # 替换成你的实际 API key

WORKING_DIR = "./dickens"

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=gpt_4o_mini_complete,  # Use gpt_4o_mini_complete LLM model
    # llm_model_func=gpt_4o_complete  # Optionally, use a stronger model
)

with open("./dickens/book.txt", "r", encoding="utf-8") as f:
    rag.insert(f.read())

# Perform naive search
print(
    rag.query("What are the top themes in this story?", param=QueryParam(mode="naive"))
)

# Perform local search
print(
    rag.query("What are the top themes in this story?", param=QueryParam(mode="local"))
)

# Perform global search
print(
    rag.query("What are the top themes in this story?", param=QueryParam(mode="global"))
)

# Perform hybrid search
print(
    rag.query("What are the top themes in this story?", param=QueryParam(mode="hybrid"))
)
