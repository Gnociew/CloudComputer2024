from langchain.prompts import PromptTemplate

recommendation_template = PromptTemplate(
    input_variables=["recent_words"],
    template=(
        "以下是用户最近学习的十个手语词语：{recent_words}。\n"
        "请根据这些词语，推荐五个相关且用户可能想学习的手语词语。"
        "要求推荐词语与输入词语语义相关，并适合进一步学习。"
        "不需要给出理由，只要五个词，每个词之间用空格分隔。"
    )
)
