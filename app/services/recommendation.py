from .langchain_service import generate_recommendations

def get_recommendations(user_behavior):
    """
    根据用户行为生成推荐内容
    """
    # 从用户行为中提取最近学习的词语
    recent_words = extract_recent_words(user_behavior)
    
    # 使用 LangChain 生成推荐
    if recent_words:
        recommendations = generate_recommendations(recent_words)
        return recommendations
    
    # 默认推荐
    return ["你好", "谢谢", "再见"]

def extract_recent_words(user_behavior):
    """
    从用户行为中提取最近学习的词语
    """
    # TODO: 实现词语提取逻辑
    return []
