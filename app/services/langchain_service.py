from langchain_community.llms import Tongyi
from langchain.chains import LLMChain
from app.utils.prompt_templates import recommendation_template

# 初始化通义千问 LLM
llm = Tongyi(
    dashscope_api_key="sk-a555417cf91347b480be57fe112f59db",
    model="qwen-turbo",
    temperature=0.7                    # 可选参数：温度
)

def generate_recommendations(recent_words):
    """
    根据用户最近学习的词语生成推荐内容。
    """
    # 创建 LangChain 的 LLMChain
    chain = LLMChain(llm=llm, prompt=recommendation_template)

    # 输入用户最近学习的手语词语
    result = chain.run({
        "recent_words": ", ".join(recent_words)
    })
    return result

