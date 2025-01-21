import os
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatTongyi  # 使用通义千问模型
from langchain_community.embeddings import HuggingFaceEmbeddings  # 替代 OpenAIEmbeddings
from langchain_community.embeddings import DashScopeEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain

# 设置通义千问 API 密钥
os.environ["DASHSCOPE_API_KEY"] = "sk-a555417cf91347b480be57fe112f59db"

def load_faiss_vector_store(folder_path):
    """
    加载 FAISS 向量数据库
    """
    # 检查目录是否存在
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"向量数据库目录未找到: {folder_path}")
    
    # 检查目录是否包含必要文件
    faiss_file = os.path.join(folder_path, "index.faiss")
    pkl_file = os.path.join(folder_path, "index.pkl")
    if not os.path.exists(faiss_file) or not os.path.exists(pkl_file):
        raise FileNotFoundError(f"FAISS 数据库文件不完整，请检查目录: {folder_path}")
    
    embeddings = DashScopeEmbeddings(model="text-embedding-v1", dashscope_api_key="sk-a555417cf91347b480be57fe112f59db")
    
    # 加载向量数据库，允许危险反序列化
    vector_store = FAISS.load_local(folder_path, embeddings, allow_dangerous_deserialization=True)
    return vector_store


def answer_question(question, faiss_path):
    # faiss_path = "../../data/hand_signs_knowledge.faiss"
    """
    使用 RAG 技术回答问题
    """
    try:
        # 加载向量数据库
        vector_store = load_faiss_vector_store(faiss_path)
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

        # 初始化通义千问语言模型
        llm = ChatTongyi(
            model="qwen-turbo",
            temperature=0.7,
            dashscope_api_key=os.environ["DASHSCOPE_API_KEY"]
        )

        # 自定义 Prompt 模板
        prompt_template = """
        你是一个手语知识专家，请根据以下检索到的文档内容回答用户的问题。
        
        任务：
        1. 根据以下文档内容回答问题。
        2. 如果文档中包含相关信息，仅使用文档内容作答，无需添加其他知识。
        3. 如果文档中没有相关信息，请基于你的知识作答，并在回答末尾标注：“知识库中没有相关信息”。
        
        注意：
        优先使用文档内容作为答案的来源。
        如果需要使用自己的知识补充，请确保你的回答简洁、准确。

        文档内容:
        {context}

        问题: {question}
        """
        prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

        # 加载问答链，设置为 "stuff"
        qa_chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)

        # 使用检索器获取相关文档
        retrieved_docs = retriever.get_relevant_documents(question)

        # 打印调试信息
        # print("检索到的文档:")
        # for doc in retrieved_docs:
        #     print(f"知识库内容：{doc.page_content}")
        #     print(f"元数据：{doc.metadata}")

        # # 如果没有检索到文档
        # if not retrieved_docs:
        #     return "未能检索到相关内容，请检查知识库是否正确存储。", []

        # 执行问答链，传入检索到的文档和问题
        result = qa_chain({"input_documents": retrieved_docs, "question": question})

        # 提取答案
        answer = result["output_text"]
        return answer

    except Exception as e:
        print(f"Error during processing: {e}")
        return None


# if __name__ == "__main__":
#     # 提问内容
#     question = "如何用手语表示对不起"
    
#     # FAISS 文件路径
#     faiss_path = "../../data/hand_signs_knowledge_DS.faiss"  # 确保路径正确

#     # 调用问答功能
#     answer = answer_question(question, faiss_path)

#     if answer:
#         print(f"回答: {answer}")
#     else:
#         print("未能生成回答，请检查错误日志。")
