import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import streamlit as st
from streamlit_option_menu import option_menu
import os
import requests
from PIL import Image
from io import BytesIO
import time
import base64
from neo4j import GraphDatabase
from streamlit_echarts import st_pyecharts
from pyecharts import options as opts
from pyecharts.charts import Tree


st.markdown(
    """
    <style>
    # /* 侧边栏样式 */
    # .sidebar .sidebar-content {
    #     background-color: #f8f9fa;
    #     padding: 20px;
    #     border-right: 1px solid #e9ecef;
    # }
    # .sidebar .sidebar-content .stButton button {
    #     width: 100%;
    #     margin-bottom: 10px;
    #     background-color: #007bff;
    #     color: white;
    #     border: none;
    #     border-radius: 5px;
    #     padding: 10px;
    #     font-size: 14px;
    # }
    # .sidebar .sidebar-content .stButton button:hover {
    #     background-color: #0056b3;
    # }
    # .sidebar .sidebar-content .stFileUploader {
    #     margin-top: 20px;
    # }
    # .sidebar .sidebar-content .stSelectbox {
    #     margin-top: 20px;
    # }
    # .sidebar .sidebar-content .stCheckbox {
    #     margin-top: 20px;
    # }

    /* 主页面样式 */
    .stTitle {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    # .stChatMessage .user {
    #     background-color: #e9ecef;
    #     padding: 10px;
    #     border-radius: 10px;
    #     margin-bottom: 10px;
    # }
    # .stChatMessage .bot {
    #     background-color: #007bff;
    #     color: white;
    #     padding: 10px;
    #     border-radius: 10px;
    #     margin-bottom: 10px;
    # }
    </style>
    """,
    unsafe_allow_html=True,
)

SERVER_URL = "47.116.205.94"
knowledge_bases = ["中学生物知识点", "中学物理知识点", "中学政治知识点", "中学语文知识点"]

if "current_page" not in st.session_state:
    st.session_state.current_page = "问答页面"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = None

if "use_cot" not in st.session_state:
    st.session_state.use_cot = False

if "use_web_search" not in st.session_state:
    st.session_state.use_web_search = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(int(time.time()))  # 生成新的 thread_id


if "mastered_questions" not in st.session_state:
    st.session_state.mastered_questions = []

if 'graph_data' not in st.session_state:
        st.session_state.graph_data = None

if "wq_data" not in st.session_state:
    st.session_state.wq_data = None

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

if "wrong_questions" not in st.session_state:
    st.session_state.wrong_questions = []
        
if "show_answers" not in st.session_state:
    st.session_state.show_answers = False


def get_bot_response(user_input, thread_id="default"):
    """
    调用后端获取LLM的响应
    """
    url = f"http://{SERVER_URL}:8000/chat"  
    payload = {
        "thread_id": thread_id,
        "message": user_input,
        "role": "user",
        "cot": True,
    }
    print(payload)
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"后端返回错误：{response.status_code}, {response.text}")
    except Exception as e:
        raise Exception(f"调用后端 API 失败：{str(e)}")
    
def fetch_wq_data(page):
    """
    获取整体错题集
    """
    url = f"http://{SERVER_URL}:8000/get_wq" 
    params = {"page": page}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200:
            return data.get("wq_data", [])
        else:
            st.error(f"后端返回错误：{data.get('message')}")
            return None
    else:
        st.error("获取数据失败")
        return None

def fetch_questions(key):
    """
    智慧出题，获取LLM生成的题目
    """
    url = f"http://{SERVER_URL}:3000/generateQA"  
    try:
        response = requests.post(url, json={"key": key})
        if response.status_code == 200:
            return response.json().get("message", [])
        else:
            st.error(f"获取题目失败：{response.json().get('message', '未知错误')}")
            return None
    except Exception as e:
        st.error(f"请求失败：{str(e)}")
        return None
    
def send_wrong_questions(wrong_questions):
    """
    将错题列表发送到后端
    """
    url = f"http://{SERVER_URL}:8000/insert_wg"  
    try:
        response = requests.post(url, json=wrong_questions)
        if response.status_code == 200:
            return response.json()
        else:
            return {"code": response.status_code, "message": "请求失败"}
    except Exception as e:
        return {"code": 500, "message": f"请求异常：{str(e)}"}

def send_mastered_questions(mastered_questions):
    """
    将已掌握题目的 ID 列表发送到后端
    """
    url = f"http://{SERVER_URL}:8000/master_wg"  
    try:
        response = requests.post(url, json={"wg_id_list": mastered_questions})
        if response.status_code == 200:
            return response.json()
        else:
            return {"code": response.status_code, "message": "请求失败"}
    except Exception as e:
        return {"code": 500, "message": f"请求异常：{str(e)}"}
    
# 查询文本示例
def query_text(query, mode='global', only_need_context=False, only_need_prompt=False, only_need_extract_entities=False):
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
    url = f"http://{SERVER_URL}:3000/query"
    response = requests.post(url, json={
        'query': query,
        'mode': mode,
        'only_need_context': only_need_context,
        'only_need_extract_entities': only_need_extract_entities
    })
    return (response.json())  

def query_neo4j_entities(result):
    """
    从Neo4j数据库中查询实体信息及其关系
    """
    uri = "bolt://121.43.160.105:7687"
    username = "neo4j"
    password = "123456"
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    try:
        message = result.get('message', [])
        if len(message) >= 2:
            low_level_keywords = [k.strip() for k in message[0].split(',')]
            high_level_keywords = [k.strip() for k in message[1].split(',')]
            all_keywords = low_level_keywords + high_level_keywords
            
            with driver.session() as session:
                # 首先为每个关键词查找最相关的节点
                initial_nodes_query = """
                MATCH (n)
                WHERE any(keyword IN $keywords 
                    WHERE keyword IN labels(n) 
                    OR any(value IN [prop IN keys(n) | n[prop]] WHERE value CONTAINS keyword))
                WITH n, rand() as r
                ORDER BY r
                LIMIT 5
                RETURN DISTINCT n
                """
                
                # 修改查询以使用elementId而不是id
                expanded_query = """
                MATCH (n)-[r1]->(m)-[r2]->(p)
                WHERE elementId(n) = $node_id
                RETURN n, r1, m, r2, p
                ORDER BY r1.weight DESC, r2.weight DESC
                LIMIT 10
                """
                
                nodes = set()
                relationships = set()
                
                # 获取初始节点
                initial_nodes = session.run(initial_nodes_query, keywords=all_keywords)
                
                for record in initial_nodes:
                    start_node = record["n"]
                    # 获取两层关系
                    expanded_result = session.run(expanded_query, node_id=start_node.element_id)
                    
                    for path in expanded_result:
                        # 添加所有节点
                        for node_key in ['n', 'm', 'p']:
                            if path[node_key] is not None:
                                node = path[node_key]
                                nodes.add((
                                    node.element_id,
                                    list(node.labels)[0],
                                    frozenset(node.items())
                                ))
                        
                        # 添加所有关系
                        for rel_key in ['r1', 'r2']:
                            if path[rel_key] is not None:
                                rel = path[rel_key]
                                relationships.add((
                                    rel.element_id,
                                    rel.start_node.element_id,
                                    rel.end_node.element_id,
                                    type(rel).__name__,
                                    rel.get('weight', 1.0),
                                    rel.get('description', ''),
                                    rel.get('keywords', '')
                                ))
                
                # 转换回列表格式
                nodes_list = [{
                    "element_id": n[0],
                    "label": n[1],
                    "properties": dict(n[2])
                } for n in nodes]
                
                relationships_list = [{
                    "element_id": r[0],
                    "source": r[1],
                    "target": r[2],
                    "type": r[3],
                    "weight": r[4],
                    "description": r[5],
                    "properties": {
                        "keywords": r[6]
                    }
                } for r in relationships]
                
                return {
                    "nodes": nodes_list,
                    "relationships": sorted(relationships_list, key=lambda x: x['weight'], reverse=True)
                }
                
    finally:
        driver.close()
    
    return {"nodes": [], "relationships": []}

def clean_label(text):
    """
    清理标签文本，去除双引号和特殊分隔符
    """
    if not isinstance(text, str):
        return ""
    # 去除双引号和 <SEP>
    cleaned = text.replace('"', '').replace('<SEP>', ' ').strip()
    # 如果清理后为空，返回空字符串
    return cleaned if cleaned else ""

def render_knowledge_graph(graph_data, config_params=None):
    """
    根据查询结果渲染知识图谱
    """
    nodes = []
    edges = []
    
    # 使用传入的配置参数或默认值
    colors = config_params.get('colors', {
        'initial_node': '#FF6B6B',
        'level1_node': '#4ECDC4',
        'level2_node': '#45B7D1',
        'initial_edge': '#FF9F9F',
        'level1_edge': '#96E6E0'
    })
    
    node_config = config_params.get('node', {
        'size': 25,
        'font_size': 12,
        'font_color': '#333333'
    })
    
    edge_config = config_params.get('edge', {
        'font_size': 10,
        'font_color': '#666666'
    })

    # 获取初始节点的ID列表（前5个节点）
    initial_node_ids = set(str(node["element_id"]) for node in graph_data["nodes"][:5])
    
    # 找出与初始节点直接相连的节点ID
    level1_node_ids = set()
    for rel in graph_data["relationships"]:
        source = str(rel["source"])
        target = str(rel["target"])
        if source in initial_node_ids:
            level1_node_ids.add(target)
        elif target in initial_node_ids:
            level1_node_ids.add(source)
    
    # 处理节点
    for node_data in graph_data["nodes"]:
        node_id = str(node_data["element_id"])
        # 确定节点颜色
        if node_id in initial_node_ids:
            color = colors['initial_node']
        elif node_id in level1_node_ids:
            color = colors['level1_node']
        else:
            color = colors['level2_node']
            
        nodes.append(Node(
            id=node_id,
            label=clean_label(node_data["label"]),
            size=node_config['size'],
            shape="circle",
            color=color,
            title=f"类型: {node_data['properties'].get('entity_type', '未知')}\n描述: {clean_label(node_data['properties'].get('description', '无描述'))}"
        ))
    
    # 处理关系
    for rel_data in graph_data["relationships"]:
        source = str(rel_data["source"])
        target = str(rel_data["target"])
        
        # 确定边的颜色
        if source in initial_node_ids or target in initial_node_ids:
            edge_color = colors['initial_edge']
        else:
            edge_color = colors['level1_edge']
        
        # 获取并清理关键词
        keywords = clean_label(rel_data.get("properties", {}).get("keywords", ""))
        description = clean_label(rel_data.get("description", ""))
        
        # 使用关键词，如果为空则使用描述
        edge_label = keywords or description
        
        edges.append(Edge(
            source=source,
            target=target,
            label=edge_label,
            color=edge_color,
            smooth={
                'type': 'curvedCW',
                'roundness': 0.2
            }
        ))
    
    # 更新配置
    config = Config(
        width=config_params.get('width', 750),
        height=config_params.get('height', 950),
        directed=config_params.get('directed', True),
        physics=config_params.get('physics', True),
        hierarchical=False,
        node={
            'font': {
                'size': node_config['font_size'],
                'color': node_config['font_color']
            },
            'borderWidth': 2,
            'borderWidthSelected': 3
        },
        edge={
            'font': {
                'size': edge_config['font_size'],
                'color': edge_config['font_color']
            },
            'width': 2,
            'arrowStrikethrough': False,
            'smooth': {'type': 'curvedCW', 'roundness': 0.2}
        }
    )
    
    # 创建容器并设置样式
    container = st.container()
    with container:
        st.markdown(f"""
        <style>
        .stAgraph {{
            width: {config_params.get('container_width', '100%')} !important;
            margin: 0 auto;
        }}
        </style>
        """, unsafe_allow_html=True)
        return agraph(nodes=nodes, edges=edges, config=config)
    
def create_mindmap(data, key):
    """创建思维导图"""
    tree = (
        Tree()
        .add(
            series_name="",  # 系列名称
            data=[data],  # 数据
            orient="LR",  # 从左到右布局
            initial_tree_depth=3,  # 初始展开深度
            layout="orthogonal",  # 正交布局
            pos_left="5%",  # 左边距
            width="40%",  # 缩小图表宽度
            height="50%",  # 缩小图表高度
            edge_fork_position="10%",  # 分叉点位置
            symbol_size=8,  # 缩小节点大小
            symbol="circle",  # 节点形状为圆形
            label_opts=opts.LabelOpts(
                position="right",
                horizontal_align="left",
                vertical_align="middle",
                font_size=14,  # 缩小字体大小
                font_weight="bold",  # 字体加粗
                color="black",  # 字体颜色
                padding=[0, 0, 0, 0],
            ),
            leaves_opts=opts.TreeLeavesOpts(  # 叶子节点样式
                label_opts=opts.LabelOpts(
                    position="right",
                    horizontal_align="left",
                    vertical_align="middle",
                    font_size=12,  # 缩小叶子节点字体大小
                    color="darkgreen",  # 叶子节点字体颜色
                ),
            ),
            is_expand_and_collapse=True,  # 允许展开和折叠节点
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"{key}知识点思维导图",
                pos_left="center",  # 标题居中
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=20,  # 缩小标题字体大小
                    font_weight="bold",
                    color="darkblue",
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                trigger_on="mousemove",
                formatter="{b}",  # 显示节点名称
            ),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                pos_left="right",
                feature={
                    "zoom": {"is_show": True},
                    "restore": {"is_show": True},
                    "saveAsImage": {"is_show": True},  # 添加保存为图片功能
                },
            )
        )
    )
    return tree

# 生成思维导图
def generate_mind_map(key, base_url):
    """
    向API发送请求以生成思维导图。
    
    参数:
    key (str): 生成思维导图的键。
    mode (str): 生成模式，可选值为 'naive', 'local', 'global', 'hybrid'。
    
    返回:
    dict: 包含API响应的字典，通常包括以下字段：
        - message (str): 生成的思维导图结果或错误信息。
        - code (int): HTTP状态码，200表示成功，400表示请求错误，401表示模式无效。
    """
    url = f"{base_url}/generateMindMap"
    response = requests.post(url, json={'key': key})
    print(response.json())  # 打印API返回的响应
    return response.json()["message"]

def get_wq_data_optional():
    wq_data_optional = [
        #     # {
        #     #     "题目": "以下哪个实体是光合作用的场所？",
        #     #     "选项": {
        #     #         "A": "叶绿体",
        #     #         "B": "细胞核",
        #     #         "C": "线粒体",
        #     #         "D": "液泡"
        #     #     },
        #     #     "答案": "A",
        #     #     "解析": "叶绿体是进行光合作用的场所，其中含有叶绿素等色素，能够吸收光能并将其转化为化学能，用于合成有机物和释放氧气。细胞核主要负责储存遗传信息，线粒体则参与细胞呼吸过程，液泡则主要储存水分和营养物质。因此，选项A是正确的。"
        #     # },
            {'题目': '以下哪项不是细胞的基本结构？（  ）', '选项': {'A': '细胞膜', 'B': '细胞质', 'C': '细胞核', 'D': '细胞壁'}, '答案': 'D', '解析': '细胞膜、细胞质和细胞核是所有细胞的基本结构。细胞壁是一些细胞如植物细胞和某些细菌细胞所特有的结构，但并非所有细胞都拥有细胞壁。因此，细胞壁不是细胞的基本结构。'}, {'题目': '下列哪个选项不是细胞器的功能？（  ）', '选项': {'A': '线粒体 - 产生能量', 'B': '叶绿体 - 光合作用', 'C': '高尔基体 - 分泌和修饰蛋白质', 'D': '细胞核 - 储存遗传信息'}, '答案': 'B', '解析': '叶绿体确实参与光合作用，这是其功能之一。线粒体产生能量，高尔基体参与蛋白质的分泌和修饰，细胞核储存遗传信息。因此，选项B中的描述不符合题意，因为它描述的是叶绿体的功能，而不是一个非细胞器的功能。'}, {'题目': '以下哪项不是构成细胞膜的主要成分？（  ）', '选项': {'A': '蛋白质', 'B': '脂质', 'C': '糖类', 'D': '核酸'}, '答案': 'D', '解析': '细胞膜主要由脂质（如磷脂）和蛋白质组成，糖类有时也参与形成糖蛋白，但核酸并不是细胞膜的组成部分。因此，选项D是不正确的。'}, {'题目': '以下哪项不是细胞分裂过程中的阶段？（  ）', '选项': {'A': '有丝分裂', 'B': '无丝分裂', 'C': '减数分裂', 'D': '细胞凋亡'}, '答案': 'D', '解析': '有丝分裂、无丝分裂和减数分裂都是细胞分裂的不同类型。细胞凋亡是一种程序性细胞死亡的过程，不属于细胞分裂的范畴。因此，选项D是不正确的。'}, {'题目': '以下哪项不是细胞内的一种化合物？（  ）', '选项': {'A': '蛋白质', 'B': '脂肪', 'C': 'DNA', 'D': '声波'}, '答案': 'D', '解析': '蛋白质、脂肪和DNA都是细胞内的化合物。声波是一种机械波，不是由化学物质组成的，因此不属于细胞内的化合物。因此，选项D是不正确的。'}]
    time.sleep(2)
    return wq_data_optional

st.markdown(
    """
    <style>
    .stExpander > label > div {
        font-size: 48px !important;
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.session_state.current_page == "问答页面":
    st.markdown("### 💬 知识问答")

    with st.sidebar:
        # 创建导航菜单
        selected = option_menu(
            menu_title="🚀 导航",  # 菜单标题
            options=["问答页面", "知识点查询", "问题图谱", "智慧出题", "错题集"],  # 菜单选项
            icons=["chat", "search", "diagram-3", "lightbulb", "file-earmark-text"],  # 每个选项的图标
            menu_icon="cast",  # 菜单图标
            default_index=0,  # 默认选中的选项索引
        )

        # 更新当前页面
        st.session_state.current_page = selected

        with st.expander("📚 **知识库管理**", expanded=True):  # 默认展开
            # 上传 PDF 文件
            uploaded_file = st.file_uploader("上传 PDF 文件", type="pdf")
            if uploaded_file is not None:
                file_name = uploaded_file.name
                file_path = os.path.join("knowledge_bases", uploaded_file.name)
                # with open(file_path, "wb") as f:
                #     f.write(uploaded_file.getbuffer())
                st.session_state.knowledge_base = file_path
                st.success(f"已上传知识库: {uploaded_file.name}")
                knowledge_bases.append(file_name)

            # 使用 CoT 润色问题和联网搜索
            col1, col2 = st.columns(2)
            with col1:
                use_cot = st.toggle("使用 CoT", value=st.session_state.use_cot, key="use_cot_toggle")
                st.session_state.use_cot = use_cot
            with col2:
                use_web_search = st.toggle("联网搜索", value=st.session_state.use_web_search, key="web_search_toggle")
                st.session_state.use_web_search = use_web_search

            # 选择知识库
            selected_knowledge_base = st.selectbox("选择知识库", knowledge_bases)
            st.session_state.knowledge_base = selected_knowledge_base

    # 显示聊天记录
    for chat in st.session_state.chat_history:
        # 自定义图标
        icon = "💡" if chat["role"] == "bot" else "🙋"  # 使用emoji作为图标
        with st.chat_message(chat["role"], avatar=icon):  # 添加avatar参数
            if chat["type"] == "text":
                st.markdown(chat["message"])
            elif chat["type"] == "image":
                st.image(chat["message"], caption="生成的思维导图", use_container_width=True)

    # 输入框和发送按钮
    user_input = st.chat_input("请输入你的问题：", key="user_input")
    if user_input:
        # 将用户输入添加到聊天记录
        st.session_state.chat_history.append({"role": "user", "message": user_input, "type": "text"})

        try:
            # 调用后端 API 获取响应
            bot_response = get_bot_response(user_input, st.session_state.thread_id)
            st.session_state.chat_history.append({"role": "bot", "message": bot_response, "type": "text"})

            # 刷新页面，确保最新的聊天记录被显示
            st.rerun()  # 替换为 st.rerun()
        except Exception as e:
            st.error(f"发生错误：{str(e)}")

    # 清空聊天记录按钮（仅在聊天记录不为空时显示）
    if st.session_state.chat_history:
        st.markdown("---")
        col1, col2, col3 = st.columns([1.2, 1, 1])  # 创建 3 列布局
        with col2:  # 在中间列放置按钮
            if st.button("清空聊天记录", key="clear_chat_button"):
                st.session_state.chat_history = []
                st.session_state.thread_id = str(int(time.time()))  # 生成新的 thread_id
                st.rerun()  # 刷新页面

elif st.session_state.current_page == "知识点查询":
    st.markdown("### 📖 知识点查询")
    base_url = "http://47.116.205.94:3000"

    with st.sidebar:
        # 创建导航菜单
        selected = option_menu(
            menu_title="🚀 导航",  # 菜单标题
            options=["问答页面", "知识点查询", "问题图谱", "智慧出题", "错题集"],  # 菜单选项
            icons=["chat", "search", "diagram-3", "lightbulb", "file-earmark-text"],  # 每个选项的图标
            menu_icon="cast",  # 菜单图标
            default_index=0,  # 默认选中的选项索引
        )

        # 更新当前页面
        st.session_state.current_page = selected

        with st.expander("📚 **知识库管理**", expanded=True):  # 默认展开
            # 上传 PDF 文件
            uploaded_file = st.file_uploader("上传 PDF 文件", type="pdf", label_visibility="collapsed", help="请选择要上传的PDF文件")
            if uploaded_file is not None:
                file_name = uploaded_file.name
                file_path = os.path.join("knowledge_bases", uploaded_file.name)
                # with open(file_path, "wb") as f:
                #     f.write(uploaded_file.getbuffer())
                st.session_state.knowledge_base = file_path
                st.success(f"已上传知识库: {uploaded_file.name}")
                knowledge_bases.append(file_name)

            # 使用 CoT 润色问题和联网搜索
            col1, col2 = st.columns(2)
            with col1:
                use_cot = st.toggle("使用 CoT", value=st.session_state.use_cot, key="use_cot_toggle")
                st.session_state.use_cot = use_cot
            with col2:
                use_web_search = st.toggle("联网搜索", value=st.session_state.use_web_search, key="web_search_toggle")
                st.session_state.use_web_search = use_web_search

            # 选择知识库
            selected_knowledge_base = st.selectbox("选择知识库", knowledge_bases)
            st.session_state.knowledge_base = selected_knowledge_base

    key = st.text_input("请输入知识点", "")
    mind_map = None

    if st.button("生成思维导图"):
        try:
            with st.spinner('思维导图生成中...'):
                mind_map = generate_mind_map(key, base_url)
                if mind_map:
                    tree = create_mindmap(mind_map, key)
                    st_pyecharts(
                        tree,
                        height="900px",
                        width="100%",
                        key="mindmap"
                    )
                else:
                    st.warning("未获取到相关思维导图")
                
        except Exception as e:
            st.error(f"发生错误：{str(e)}")
            st.exception(e)
    
elif st.session_state.current_page == "问题图谱":
    st.markdown("### 🌐 问题图谱")

    query = st.text_input("请输入查询的问题", "")

    with st.sidebar:
        # 创建导航菜单
        selected = option_menu(
            menu_title="🚀 导航",  # 菜单标题
            options=["问答页面", "知识点查询", "问题图谱", "智慧出题", "错题集"],  # 菜单选项
            icons=["chat", "search", "diagram-3", "lightbulb", "file-earmark-text"],  # 每个选项的图标
            menu_icon="cast",  # 菜单图标
            default_index=0,  # 默认选中的选项索引
        )

        # 更新当前页面
        st.session_state.current_page = selected

        with st.expander("", expanded=True):  # expanded=True 表示默认展开
            st.markdown("""
            <style>
            .sidebar-config {
                background-color: #f0f2f6;
                padding: 5px;
                border-radius: 10px;
                margin: 10px 0;
            }
            </style>
            """, unsafe_allow_html=True)

            # 基础设置
            # st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
            st.subheader("基本设置")
            width = st.slider("宽度", 400, 2000, 750)
            height = st.slider("高度", 400, 1200, 950)
            directed = st.checkbox("显示箭头", value=True)
            physics = st.checkbox("物理引擎", value=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # 节点设置
            st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
            st.subheader("节点设置")
            node_size = st.slider("节点大小", 10, 50, 25)
            st.markdown('</div>', unsafe_allow_html=True)

            # 颜色设置
            st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
            st.subheader("颜色设置")
            if 'graph_colors' not in st.session_state:
                st.session_state.graph_colors = {
                    'initial_node': '#FF6B6B',
                    'level1_node': '#4ECDC4',
                    'level2_node': '#45B7D1',
                    'initial_edge': '#FF9F9F',
                    'level1_edge': '#96E6E0'
                }

            st.session_state.graph_colors['initial_node'] = st.color_picker(
                "初始节点颜色", 
                st.session_state.graph_colors['initial_node']
            )
            st.session_state.graph_colors['level1_node'] = st.color_picker(
                "一级节点颜色", 
                st.session_state.graph_colors['level1_node']
            )
            st.session_state.graph_colors['level2_node'] = st.color_picker(
                "二级节点颜色", 
                st.session_state.graph_colors['level2_node']
            )
            st.session_state.graph_colors['initial_edge'] = st.color_picker(
                "主要边颜色", 
                st.session_state.graph_colors['initial_edge']
            )
            st.session_state.graph_colors['level1_edge'] = st.color_picker(
                "次要边颜色", 
                st.session_state.graph_colors['level1_edge']
            )
            st.markdown('</div>', unsafe_allow_html=True)

            # 节点文字设置
            st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
            st.subheader("节点文字设置")
            node_font_size = st.slider("节点文字大小", 8, 24, 12)
            node_font_color = st.color_picker("节点文字颜色", "#333333")
            st.markdown('</div>', unsafe_allow_html=True)

            # 边文字设置
            st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
            st.subheader("边文字设置")
            edge_font_size = st.slider("边文字大小", 6, 20, 10)
            edge_font_color = st.color_picker("边文字颜色", "#666666")
            st.markdown('</div>', unsafe_allow_html=True)

            # 容器设置
            st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
            st.subheader("容器设置")
            container_width = st.slider("容器宽度占比", 50, 100, 100, format="%d%%")
            st.markdown('</div>', unsafe_allow_html=True)

    # 修改查询逻辑，只在点击查询按钮时执行
    if st.button("查询"):
        try:
            with st.spinner('处理中...'):
                result = query_text(query=query, mode='global', only_need_extract_entities=True)
                st.session_state.graph_data = query_neo4j_entities(result)
        except Exception as e:
            st.error(f"发生错误：{str(e)}")
            st.exception(e)

    # 如果有图谱数据，则渲染图谱
    if st.session_state.graph_data and (st.session_state.graph_data.get("nodes") or st.session_state.graph_data.get("relationships")):
        config_params = {
            'width': width,
            'height': height,
            'directed': directed,
            'physics': physics,
            'colors': st.session_state.graph_colors,
            'node': {
                'size': node_size,
                'font_size': node_font_size,
                'font_color': node_font_color
            },
            'edge': {
                'font_size': edge_font_size,
                'font_color': edge_font_color
            },
            'container_width': f"{container_width}%"
        }
        render_knowledge_graph(st.session_state.graph_data, config_params)
    elif st.session_state.graph_data is not None:
        st.warning("未获取到图谱数据")

elif st.session_state.current_page == "智慧出题":
    with st.sidebar:
        # 创建导航菜单
        selected = option_menu(
            menu_title="🚀 导航",  # 菜单标题
            options=["问答页面", "知识点查询", "问题图谱", "智慧出题", "错题集"],  # 菜单选项
            icons=["chat", "search", "diagram-3", "lightbulb", "file-earmark-text"],  # 每个选项的图标
            menu_icon="cast",  # 菜单图标
            default_index=0,  # 默认选中的选项索引
        )

        # 更新当前页面
        st.session_state.current_page = selected

        with st.expander("📚 **知识库管理**", expanded=True):  # 默认展开
            # 上传 PDF 文件
            uploaded_file = st.file_uploader("上传 PDF 文件", type="pdf", label_visibility="collapsed", help="请选择要上传的PDF文件")
            if uploaded_file is not None:
                file_name = uploaded_file.name
                file_path = os.path.join("knowledge_bases", uploaded_file.name)
                # with open(file_path, "wb") as f:
                #     f.write(uploaded_file.getbuffer())
                st.session_state.knowledge_base = file_path
                st.success(f"已上传知识库: {uploaded_file.name}")
                knowledge_bases.append(file_name)

            # 使用 CoT 润色问题和联网搜索
            col1, col2 = st.columns(2)
            with col1:
                use_cot = st.toggle("使用 CoT", value=st.session_state.use_cot, key="use_cot_toggle")
                st.session_state.use_cot = use_cot
            with col2:
                use_web_search = st.toggle("联网搜索", value=st.session_state.use_web_search, key="web_search_toggle")
                st.session_state.use_web_search = use_web_search

            # 选择知识库
            selected_knowledge_base = st.selectbox("选择知识库", knowledge_bases)
            st.session_state.knowledge_base = selected_knowledge_base

    st.markdown("### ✏️ 智慧出题")

    key = st.text_input("请输入 key", placeholder="输入 key 后按回车或点击获取题目")

    if key:
        # 调用函数获取题目列表
        # st.session_state.wq_data = fetch_questions(key)
        print(st.session_state.wq_data)
        wq_data_optional = get_wq_data_optional()
        # wq_data_optional = [
        #     # {
        #     #     "题目": "以下哪个实体是光合作用的场所？",
        #     #     "选项": {
        #     #         "A": "叶绿体",
        #     #         "B": "细胞核",
        #     #         "C": "线粒体",
        #     #         "D": "液泡"
        #     #     },
        #     #     "答案": "A",
        #     #     "解析": "叶绿体是进行光合作用的场所，其中含有叶绿素等色素，能够吸收光能并将其转化为化学能，用于合成有机物和释放氧气。细胞核主要负责储存遗传信息，线粒体则参与细胞呼吸过程，液泡则主要储存水分和营养物质。因此，选项A是正确的。"
        #     # },
        #     {'题目': '以下哪项不是细胞的基本结构？（  ）', '选项': {'A': '细胞膜', 'B': '细胞质', 'C': '细胞核', 'D': '细胞壁'}, '答案': 'D', '解析': '细胞膜、细胞质和细胞核是所有细胞的基本结构。细胞壁是一些细胞如植物细胞和某些细菌细胞所特有的结构，但并非所有细胞都拥有细胞壁。因此，细胞壁不是细胞的基本结构。'}, {'题目': '下列哪个选项不是细胞器的功能？（  ）', '选项': {'A': '线粒体 - 产生能量', 'B': '叶绿体 - 光合作用', 'C': '高尔基体 - 分泌和修饰蛋白质', 'D': '细胞核 - 储存遗传信息'}, '答案': 'B', '解析': '叶绿体确实参与光合作用，这是其功能之一。线粒体产生能量，高尔基体参与蛋白质的分泌和修饰，细胞核储存遗传信息。因此，选项B中的描述不符合题意，因为它描述的是叶绿体的功能，而不是一个非细胞器的功能。'}, {'题目': '以下哪项不是构成细胞膜的主要成分？（  ）', '选项': {'A': '蛋白质', 'B': '脂质', 'C': '糖类', 'D': '核酸'}, '答案': 'D', '解析': '细胞膜主要由脂质（如磷脂）和蛋白质组成，糖类有时也参与形成糖蛋白，但核酸并不是细胞膜的组成部分。因此，选项D是不正确的。'}, {'题目': '以下哪项不是细胞分裂过程中的阶段？（  ）', '选项': {'A': '有丝分裂', 'B': '无丝分裂', 'C': '减数分裂', 'D': '细胞凋亡'}, '答案': 'D', '解析': '有丝分裂、无丝分裂和减数分裂都是细胞分裂的不同类型。细胞凋亡是一种程序性细胞死亡的过程，不属于细胞分裂的范畴。因此，选项D是不正确的。'}, {'题目': '以下哪项不是细胞内的一种化合物？（  ）', '选项': {'A': '蛋白质', 'B': '脂肪', 'C': 'DNA', 'D': '声波'}, '答案': 'D', '解析': '蛋白质、脂肪和DNA都是细胞内的化合物。声波是一种机械波，不是由化学物质组成的，因此不属于细胞内的化合物。因此，选项D是不正确的。'}]
        st.session_state.wq_data = wq_data_optional

        # 显示题目
        if st.session_state.wq_data is None:
            st.session_state.wq_data = wq_data_optional
        else:
            print(st.session_state.wq_data)
            for index, item in enumerate(st.session_state.wq_data):
                with st.container():
                    st.markdown(
                        f"""
                        <div style="
                            padding: 10px;
                            border-radius: 10px;
                            border: 1px solid #ddd;
                            margin-bottom: 20px;
                            background-color: #f9f9f9;
                        ">
                            <h4 style="color: blue;">📝 题目 {index + 1}</h4>
                            <p><strong>题目：</strong>{item['题目']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # 显示选项（如果是选择题）
                    if "选项" in item:
                        options = item["选项"]
                        # 将选项的键和值拼接成字符串列表
                        option_list = [f"{key}：{value}" for key, value in options.items()]
                        # 使用 st.radio 显示选项
                        user_answer = st.radio(
                            f"请选择答案（题目 {index + 1}）",
                            options=option_list,  # 传入拼接后的选项列表
                            key=f"answer_{index}"
                        )
                        # 将用户答案保存到 session_state
                        st.session_state.user_answers[index] = user_answer

            # 提交按钮
            if st.button("提交答案"):
                st.session_state.show_answers = True  # 允许显示答案和解析
                wrong_questions = []
                for index, item in enumerate(st.session_state.wq_data):
                    if "选项" in item:
                        user_answer = st.session_state.user_answers.get(index, "")
                        correct_answer = item["答案"]
                        if user_answer != correct_answer:
                            wrong_questions.append(item)  # 将错题添加到错题列表

                # 显示答题结果
                if wrong_questions:
                    st.warning(f"❌ 你答错了 {len(wrong_questions)} 道题。")
                    for wrong_item in wrong_questions:
                        st.markdown(f"**题目：** {wrong_item['题目']}")
                        st.markdown(f"**✅ 正确答案：** {wrong_item['答案']}")
                        if wrong_item["解析"]:
                            st.markdown(f"**📖 解析：** {wrong_item['解析']}")
                else:
                    st.success("🎉 恭喜你，全部答对了！")

                # 调用函数保存错题
                # if wrong_questions:
                #     result = send_wrong_questions(wrong_questions)
                #     if result.get("code") == 200:
                #         st.success("错题已保存到错题集！")
                #     else:
                #         st.error(f"保存错题失败：{result.get('message')}")


elif st.session_state.current_page == "错题集":
    with st.sidebar:
        # 创建导航菜单
        selected = option_menu(
            menu_title="🚀 导航",  # 菜单标题
            options=["问答页面", "知识点查询", "问题图谱", "智慧出题", "错题集"],  # 菜单选项
            icons=["chat", "search", "diagram-3", "lightbulb", "file-earmark-text"],  # 每个选项的图标
            menu_icon="cast",  # 菜单图标
            default_index=0,  # 默认选中的选项索引
        )

        # 更新当前页面
        st.session_state.current_page = selected


    # 页面标题和分页输入框
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 📚 错题重做")
    with col2:
        page = st.number_input("页码", min_value=1, value=1)

    page = int(page)
    print(page)
    print(type(page))

    # 刷新按钮
    if st.button("🔄 刷新数据"):
        st.rerun()

    try:
        # wq_data = fetch_wq_data(page)
        # 模拟数据加载
        wq_data = [{
                "ID": "27",
                "Question": "以下哪个实体是光合作用的场所？",
                "Type": "选择题",
                "Options": {
                    "A": "叶绿体",
                    "B": "细胞核",
                    "C": "线粒体",
                    "D": "液泡"
                },
                "Answer": "A",
                "Analysis": "叶绿体是进行光合作用的场所，其中含有叶绿素等色素，能够吸收光能并将其转化为化学能，用于合成有机物和释放氧气。细胞核主要负责储存遗传信息，线粒体则参与细胞呼吸过程，液泡则主要储存水分和营养物质。因此，选项A是正确的。"
            },
            {
                "ID": "12",
                "Question": "根据磷脂分子的特点解释，为什么磷脂在空气—水界面上铺展成单分子层？科学家是如何推导出“脂质在细胞膜中必然排列为连续的两层”这一结论的？",
                "Type": "简答题",
                "Options": {},
                "Answer": "磷脂分子具有亲水头部和疏水尾部，在空气—水界面上，亲水头部与水分子相互作用，而疏水尾部则朝向空气，从而铺展成单分子层。科学家通过实验发现，细胞膜的表面积是磷脂单分子层的两倍，因此推导出脂质在细胞膜中必然排列为连续的两层，即磷脂双分子层。",
                "Analysis": ""
            },
            {
                "ID": "72",
                "Question": "磷脂分子在水中能自发地形成双分子层，你如何解释这一现象？由此，你能否就细胞膜是由磷脂双分子层构成的原因作出分析？",
                "Type": "简答题",
                "Options": {},
                "Answer": "磷脂分子在水中自发形成双分子层是因为其亲水头部与水分子相互作用，而疏水尾部则相互聚集，避免与水接触。这种排列方式使磷脂分子形成稳定的双分子层。细胞膜由磷脂双分子层构成，是因为这种结构既能有效分隔细胞内外环境，又能为膜蛋白提供嵌入的基质，从而实现细胞膜的选择透过性和其他功能。",
                "Analysis": ""
            },
            {
                "ID": "7",
                "Question": "如果将磷脂分子置于水—苯的混合溶剂中，磷脂分子将会如何分布？",
                "Type": "简答题",
                "Options": {},
                "Answer": "如果将磷脂分子置于水—苯的混合溶剂中，磷脂分子的亲水头部会朝向水相，而疏水尾部会朝向苯相。磷脂分子会在水—苯界面上形成单分子层，或者在水相中形成胶束结构。",
                "Analysis": ""
            },
            {
                "ID": "3",
                "Question": "染色体的高度螺旋化与其物质组成有关。组成染色体的主要物质是（A）蛋白质和DNA（B）DNA和RNA（C）蛋白质和RNA（D）DNA和脂质",
                "Type": "选择题",
                "Options": {
                    "A": "蛋白质和DNA",
                    "B": "DNA和RNA",
                    "C": "蛋白质和RNA",
                    "D": "DNA和脂质"
                },
                "Answer": "A",
                "Analysis": "染色体主要由DNA和蛋白质组成，其中DNA是遗传信息的载体，而蛋白质（如组蛋白）则帮助DNA高度螺旋化，形成染色体结构。"
                },

                {
                "ID": "11",
                "Question": "在一个长颈漏斗的漏斗口外密封上一层玻璃纸，往漏斗内注入蔗糖溶液，然后将漏斗浸入盛有清水的烧杯中，使漏斗管内外的液面高度相等。过一段时间后，会出现如右图所示现象。玻璃纸（又叫赛璐玢）是一种半透膜，水分子可以自由透过它，而蔗糖分子则不能。讨论1.漏斗管内的液面为什么会升高？如果漏斗管足够长，管内的液面会无限升高吗？为什么？2.如果用一层纱布代替玻璃纸，还会出现原来的现象吗？3.如果烧杯中不是清水，而是同样浓度的蔗糖溶液，结果会怎样？",
                "Type": "简答题",
                "Options": {},
                "Answer": "1. 漏斗管内的液面升高是因为水分子可以通过半透膜从烧杯进入漏斗，而蔗糖分子不能通过，导致漏斗内液面上升。如果漏斗管足够长，管内的液面不会无限升高，因为最终两边的渗透压会达到平衡。2. 如果用纱布代替玻璃纸，不会出现原来的现象，因为纱布不能作为半透膜阻止蔗糖分子的通过。3. 如果烧杯中是同样浓度的蔗糖溶液，由于两边溶液浓度相同，不会有水分子的净移动，因此漏斗管内的液面不会发生变化。",
                "Analysis": ""
                },

                {
                "ID": "28",
                "Question": "探究植物细胞的吸水和失水。将有些萎蔫的菜叶浸泡在清水中，不久，菜叶就会变得硬挺。将白菜剁碎做馅时，常常要放一些盐，稍过一会儿就可见到有水分渗出。对农作物施肥过多，会造成“烧苗”现象。这些现象都说明，植物细胞也像动物细胞一样，会发生吸水或失水现象，吸水或失水同样与外界溶液的浓度有关。提出问题：水分进出植物细胞是通过渗透作用吗？原生质层是否相当于一层半透膜？作出假设：假设是对问题所作的尝试性回答。作假设不是凭空猜测，而是根据已有的知识和经验作出合理的推断。请结合上文介绍的植物细胞的结构特点和自己的生活经验，与本小组同学讨论这个问题的合理答案。本小组的假设是【 】。实验设计思路：设计实验时可以思考和讨论以下问题。1. 如果假设是正确的，当外界溶液的浓度高于细胞液的浓度时，细胞就会【 】；当外界溶液的浓度低于细胞液的浓度时，细胞就会【 】。2. 如何使细胞外溶液的浓度提高或降低？3. 如何看到细胞？需要用到什么材料和器具？4. 对实验结果作出预测——细胞失水或吸水后可能出现哪些可观察的变化？参考案例：下面是可供参考的实验方案，或许可以帮你在细节上完善自己的实验设计。当然，你也可以对这个方案作出适当的修改。材料用具：紫色的洋葱鳞片叶。刀片，镊子，滴管，载玻片，盖玻片，吸水纸，显微镜。质量浓度为0.3 g/mL的蔗糖溶液，清水。方法步骤：1. 选取新鲜洋葱鳞片叶，用刀片在外表皮上划一方框，用镊子撕下表皮。在洁净的载玻片上滴一滴清水，将撕下的表皮放在水滴中展平，盖上盖玻片，制成临时装片。2. 用低倍显微镜观察洋葱鳞片叶外表皮细胞中紫色的中央液泡的大小，以及原生质层的位置。3. 从盖玻片的一侧滴入蔗糖溶液，在盖玻片的另一侧用吸水纸引流。这样重复几次，洋葱鳞片叶表皮就浸润在蔗糖溶液中。4. 用低倍显微镜观察，看细胞的中央液泡是否逐渐变小，原生质层在什么位置，细胞大小是否变化。5. 在盖玻片的一侧滴入清水，在盖玻片的另一侧用吸水纸引流。这样重复几次，洋葱鳞片叶表皮又浸润在清水中。6. 用低倍显微镜观察，看中央液泡是否逐渐变大，原生质层的位置有没有变化，细胞的大小有没有变化。",
                "Type": "简答题",
                "Options": {},
                "Answer": "本小组的假设是：水分进出植物细胞是通过渗透作用，原生质层相当于一层半透膜。实验设计思路：1. 如果外界溶液的浓度高于细胞液的浓度，细胞会失水；如果外界溶液的浓度低于细胞液的浓度，细胞会吸水。2. 可以通过改变溶液中的溶质浓度来调节细胞外溶液的浓度。3. 需要用到的材料和器具包括显微镜、载玻片、盖玻片等，以便观察细胞的变化。4. 细胞失水或吸水后可能出现的可观察变化包括中央液泡的大小变化、原生质层的位置变化以及细胞大小的变化。",
                "Analysis": ""
                },

                {
                "ID": "33",
                "Question": "一、概念检测1.物质跨膜运输的方式与物质的特点和细胞膜的结构有关。判断下列有关物质跨膜运输的表述是否正确。（1）细胞膜和液泡膜都相当于半透膜。（2）水分子进入细胞，是通过自由扩散方式进行的。（3）载体蛋白和通道蛋白在转运分子和离子时，其作用机制是一样的。2.基于对植物细胞质壁分离原理的理解判断，下列各项无法通过质壁分离实验证明的是（A）成熟植物细胞的死活（B）原生质层比细胞壁的伸缩性大（C）成熟的植物细胞能进行渗透吸水（D）水分子可以通过通道蛋白进入细胞",
                "Type": "判断题",
                "Options": {},
                "Answer": "正确，正确，错误",
                "Analysis": "（1）正确，细胞膜和液泡膜都具有选择性通透性，可以看作是半透膜。（2）正确，水分子进入细胞主要是通过自由扩散方式进行的。（3）错误，载体蛋白和通道蛋白在转运分子和离子时的作用机制不同，载体蛋白需要与被转运物质结合后发生构象变化，而通道蛋白则形成水分子或离子通过的通道。"
                }
        ]

        if not wq_data:
            st.info("当前页码没有错题数据，试试其他页码吧！")
        else:
            for item in wq_data:
                # 使用卡片式布局
                with st.container():
                    st.markdown(
                        f"""
                        <div style="
                            padding: 10px;
                            border-radius: 10px;
                            border: 1px solid #ddd;
                            margin-bottom: 20px;
                            background-color: #f9f9f9;
                        ">
                            <h4 style="color: blue;">📝 题目编号：{item['ID']}</h4>
                            <p><strong>题型：</strong>{item['Type']}</p>
                            <p><strong>题目：</strong>{item['Question']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # 根据题型展示选项
                    if item["Type"] == "选择题":
                        st.markdown("**选项：**")
                        for option, text in item["Options"].items():
                            st.markdown(f"- {option}: {text}")

                    # 使用 expander 折叠答案和解析
                    with st.expander("🔍 查看答案和解析"):
                        st.markdown(f"**✅ 正确答案：** {item['Answer']}")
                        if item["Analysis"]:
                            st.markdown(f"**📖 解析：** {item['Analysis']}")

                    # 标记为已掌握按钮
                    if st.button(f"✔️ 标记为已掌握（题目 {item['ID']}）", key=f"mark_{item['ID']}"):
                        if item["ID"] not in st.session_state.mastered_questions:
                            st.session_state.mastered_questions.append(item["ID"])
                        st.success(f"题目 {item['ID']} 已标记为已掌握！")

                    st.markdown("---")  # 题目之间的分隔线
                
                print(st.session_state.mastered_questions)

            # 分页按钮
            col_prev, col_next = st.columns(2)
            with col_prev:
                if page > 1:
                    if st.button("⬅️ 上一页"):
                        # 发送已掌握题目列表到后端
                        if st.session_state.mastered_questions != []:
                            result = send_mastered_questions(st.session_state.mastered_questions)
                            if result.get("code") == 200:
                                st.success("已掌握题目已同步到后端！")
                            else:
                                st.error(f"同步失败：{result.get('message')}")
                        page -= 1
                        st.rerun()
            with col_next:
                if st.button("➡️ 下一页"):
                    # 发送已掌握题目列表到后端
                    if st.session_state.mastered_questions != []:
                        result = send_mastered_questions(st.session_state.mastered_questions)
                        if result.get("code") == 200:
                            st.success("已掌握题目已同步到后端！")
                        else:
                            st.error(f"同步失败：{result.get('message')}")
                    page += 1
                    st.rerun()
    except Exception as e:
        st.error(f"❌ 请求失败：{str(e)}")