import requests
import os

base_url = os.getenv("KNOWLEDGE_RAG_API_URL")

# 插入文本示例
def insert_texts(texts):
    """
    向API发送请求以插入一组文本。
    
    参数:
    texts (list): 要插入的文本列表。
    
    返回:
    dict: 包含API响应的字典，通常包括以下字段：
        - message (str): 描述操作结果的消息。
        - code (int): HTTP状态码，200表示成功，400表示请求错误。
    """
    url = f"{base_url}/insert"
    response = requests.post(url, json={'texts': texts})
    print(response.json())  # 打印API返回的响应

# 插入自定义知识图谱示例
def insert_custom_kg(custom_kg):
    """
    向API发送请求以插入自定义知识图谱。
    
    参数:
    custom_kg (dict): 自定义知识图谱的数据，包含以下结构：
        - entities (list): 实体列表，每个实体是一个字典，包含以下字段：
            - entity_name (str): 实体的名称。
            - entity_type (str): 实体的类型，例如 "Organization" 或 "Product"。
            - description (str): 对实体的描述。
            - source_id (str): 数据来源的标识符。
        - relationships (list): 关系列表，每个关系是一个字典，包含以下字段：
            - src_id (str): 关系的源实体标识符。
            - tgt_id (str): 关系的目标实体标识符。
            - description (str): 对关系的描述。
            - keywords (str): 描述关系的关键词。
            - weight (float): 关系的权重。
            - source_id (str): 数据来源的标识符。
        - chunks (list): 文本块列表，每个文本块是一个字典，包含以下字段：
            - content (str): 文本内容。
            - source_id (str): 数据来源的标识符。
    
    返回:
    dict: 包含API响应的字典，通常包括以下字段：
        - message (str): 描述操作结果的消息。
        - code (int): HTTP状态码，200表示成功，400表示请求错误。
    """
    url = f"{base_url}/insert_custom_kg"
    response = requests.post(url, json={'custom_kg': custom_kg})
    print(response.json())  # 打印API返回的响应

# 查询文本示例
def query_text(query, mode='hybrid', only_need_context=False, only_need_prompt=False, kb_name=None):
    """
    向API发送请求以查询文本。
    
    参数:
    query (str): 查询的文本。
    mode (str): 查询模式，可选值为 'naive', 'local', 'global', 'hybrid'。
    only_need_context (bool): 是否只需要上下文。
    only_need_prompt (bool): 是否只需要提示。
    
    返回:
    dict: 包含API响应的字典，通常包括以下字段：
        - message (str): 查询结果或错误信息。
        - code (int): HTTP状态码，200表示成功，400表示请求错误，401表示模式无效。
    """
    url = "http://47.116.205.94:3000/query"
    response = requests.post(url, json={
        'query': query,
        'mode': mode,
        'only_need_context': only_need_context,
        'only_need_prompt': only_need_prompt,
        'kb_name': kb_name
    })
    return response.json()  # 打印API返回的响应

# 删除实体示例
def delete_entity(entity_name):
    """
    向API发送请求以删除指定的实体。
    
    参数:
    entity_name (str): 要删除的实体名称。
    
    返回:
    dict: 包含API响应的字典，通常包括以下字段：
        - message (str): 描述操作结果的消息。
        - code (int): HTTP状态码，200表示成功，400表示请求错误。
    """
    url = f"{base_url}/delete_entity"
    response = requests.post(url, json={'entity_name': entity_name})
    print(response.json())  # 打印API返回的响应


# 示例调用
if __name__ == "__main__":
    

    
    # # # 插入文本
    # insert_texts(["文本1", "文本2"])

    # # 插入自定义知识图谱
    # custom_kg = {
    #     "entities": [{"entity_name": "节点1", "entity_type": "类型1", "description": "描述1", "source_id": "来源1"}],
    #     "relationships": [{"src_id": "节点1", "tgt_id": "节点2", "description": "描述2", "keywords": "关键词1", "weight": 0.5, "source_id": "来源2"}],
    #     "chunks": [{"content": "文本1", "source_id": "来源1"}, {"content": "文本2", "source_id": "来源2"}]
    # }
    
    # insert_custom_kg(custom_kg)

    query_text("DNA是如何指导生成蛋白质的？", mode='global', only_need_context=False, only_need_prompt=True)

    # # 删除实体
    # delete_entity("节点1")