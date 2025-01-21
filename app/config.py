class Config:
    CORS_HEADERS = 'Content-Type'
    ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    ARK_AK = ""  # 从环境变量获取
    ARK_SK = ""  # 从环境变量获取
    VECTOR_DB_PATH = "data/hand_signs_knowledge_DS.faiss"
    DB_PATH = "./data/media_store.db"