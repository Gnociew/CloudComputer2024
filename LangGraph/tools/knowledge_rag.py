from api_request.knowledge_rag_api import query_text

def query_knowledge_base(query: str) -> str:
    """查询知识库工具"""
    print(f"\n[Knowledge Base Tool] 查询: {query}")
    response = query_text(
        query=query,
        mode='hybrid',
        only_need_context=False,
        only_need_prompt=False,
        kb_name='中学生物'
    )
    if isinstance(response, dict) and 'message' in response:
        print("[Knowledge Base Tool] 找到相关信息")
        return response['message']
    print("[Knowledge Base Tool] 未找到相关信息")
    return "知识库中没有找到相关信息。"