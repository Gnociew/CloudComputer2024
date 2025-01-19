import sys
import os

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from typing import Annotated
from typing_extensions import TypedDict
from langchain.tools import Tool
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from tools.knowledge_rag import query_knowledge_base
from tools.wq_search import wq_query
from tools.tavilysearch import MonitoredTavilySearch

class State(TypedDict):
    messages: Annotated[list, add_messages]
    thread_id: str

def filter_messages(messages: list, MAX_TURNS: int) -> list:
    """过滤消息历史"""
    filtered_messages = []
    for msg in messages:
        if isinstance(msg, (HumanMessage, AIMessage)) and not msg.additional_kwargs.get('tool_calls'):
            filtered_messages.append(msg)
    if len(filtered_messages) > MAX_TURNS * 2:
        filtered_messages = filtered_messages[-(MAX_TURNS * 2):]
    return filtered_messages

def build_graph(tools, llm_with_tools, checkpointer):
    """构建对话图"""
    def chatbot(state: State):
        """处理对话的函数"""
        system_message = SystemMessage(content="""你是一个智能助手。你可以：
        1. 使用knowledge_base工具查询专业的生物知识库，这个工具会给你问题的答案，将这个答案不做任何修改地作为你回答的开头，任何和生物有关的知识只可以从这个工具中获得。
        
        2. 使用knowledge_base工具的同时必须使用wq_query_tool，你必须：
           a. 使用wq_query_tool查询相关错题
           b. 先完整回答用户的问题
           c. 如果wq_query_tool返回了错题，在回答后加上："另外，我发现你之前在这个知识点上有以下错题记录："，然后完整展示错题内容
           d. 如果wq_query_tool没有返回错题，直接继续对话，不要提及错题查询
        
        3. 使用search_with_tavily工具搜索网络信息

        重要规则：
        - 每个工具在一次回答中最多只能调用一次
        - 如果工具返回的结果不理想，直接告诉用户无法找到相关信息，不要重复调用工具
        - 展示错题时，必须完整展示wq_query_tool返回的所有内容，不要修改或省略
        
        请根据问题类型选择合适的工具。如果使用了知识库或搜索工具，请说明信息来源。
        """)
        
        # 限制历史消息数量
        MAX_TURNS = 5
        messages = state["messages"]
        
        # # 检查最近的消息是否包含工具调用
        # recent_messages = messages[-3:] if len(messages) > 3 else messages
        # tool_calls_count = sum(1 for msg in recent_messages if isinstance(msg, AIMessage) and msg.additional_kwargs.get('tool_calls'))
        
        # # 如果最近的消息中已经有工具调用，添加警告提示
        # if tool_calls_count > 0:
        #     system_message = SystemMessage(content=system_message.content + "\n警告：你已经使用过工具，请直接使用工具返回的结果回答用户，不要再次调用工具。")

        #filtered_messages = filter_messages(messages, MAX_TURNS)
        messages = [system_message] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)

    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )

    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    graph = graph_builder.compile(checkpointer=checkpointer)
    return graph

def create_agent():
    """创建并返回agent实例"""
    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": None,
    }

    DB_URI = os.getenv("SUPABASE_POSTGRES_URL")

    pool = ConnectionPool(
        conninfo=DB_URI,
        max_size=5,
        kwargs=connection_kwargs,
    )
    checkpointer = PostgresSaver(pool)
    checkpointer.setup()
        
    search_with_tavily = MonitoredTavilySearch(
        max_results=2,
        description="用于搜索网络信息。注意：每次查询只能调用一次此工具，获得结果后直接使用结果回答用户。"
    )

    knowledge_base_tool = Tool(
        name="knowledge_base",
        description="用于查询专业的生物知识库。当需要生物相关的专业知识时使用此工具。所有生物相关的知识必须从这里获取。注意：每次查询只能调用一次此工具。",
        func=query_knowledge_base
    )

    wq_query_tool=Tool(
        name="wq_query_tool",
        description="""用于查询用户的错题记录。使用规则：
        1. 必须在使用knowledge_base工具后调用
        2. 如果返回了错题，必须在回答用户问题后完整展示所有错题内容
        3. 如果没有返回错题，直接继续回答，不要提及错题查询
        4. 每次对话只能调用一次此工具""",
        func=wq_query
    )

    tools = [search_with_tavily, knowledge_base_tool, wq_query_tool]
    llm = ChatZhipuAI(model="glm-4-plus", api_key=os.getenv("ZHIPU_API_KEY"))
    llm_with_tools = llm.bind_tools(tools)

    graph = build_graph(tools, llm_with_tools, checkpointer)
    
    return graph, pool

def get_agent_response(graph, user_input: str, thread_id: str, knowledge_base_id: str) -> str:
    """处理用户输入并返回回复"""
    responses = []
    
    for event in graph.stream(
        {"messages": [HumanMessage(content=user_input)]},
        {"configurable": {"thread_id": thread_id, "knowledge_base_id": knowledge_base_id}},
        stream_mode="values"
    ):
        print(f'当前线程:{thread_id}')
        response = event["messages"][-1]
        
        responses.append(response.content)
    
    return responses[-1] if responses else ""