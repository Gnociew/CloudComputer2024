import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import streamlit as st
from streamlit_option_menu import option_menu
import os
import requests
from neo4j import GraphDatabase
from streamlit_echarts import st_pyecharts
from pyecharts import options as opts
from pyecharts.charts import Tree

SERVER_URL = "47.116.205.94"

st.markdown(
    """
    <style>
    /* 主页面样式 */
    .stTitle {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    /* 侧边栏样式 */
    .stExpander > label > div {
        font-size: 48px !important;
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    st.session_state.thread_id = "default"

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

if "flag" not in st.session_state:
    st.session_state.flag = 0  

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
    
def query_text(query, mode='global', only_need_context=False, only_need_prompt=False, only_need_extract_entities=False):
    """
    向API发送请求以查询文本。
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
                
                expanded_query = """
                MATCH (n)-[r1]->(m)-[r2]->(p)
                WHERE elementId(n) = $node_id
                RETURN n, r1, m, r2, p
                ORDER BY r1.weight DESC, r2.weight DESC
                LIMIT 10
                """
                
                nodes = set()
                relationships = set()

                initial_nodes = session.run(initial_nodes_query, keywords=all_keywords)
                
                for record in initial_nodes:
                    start_node = record["n"]
                    expanded_result = session.run(expanded_query, node_id=start_node.element_id)
                    
                    for path in expanded_result:
                        for node_key in ['n', 'm', 'p']:
                            if path[node_key] is not None:
                                node = path[node_key]
                                nodes.add((
                                    node.element_id,
                                    list(node.labels)[0],
                                    frozenset(node.items())
                                ))
                        
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
    cleaned = text.replace('"', '').replace('<SEP>', ' ').strip()
    return cleaned if cleaned else ""

def render_knowledge_graph(graph_data, config_params=None):
    """
    根据查询结果渲染知识图谱
    """
    nodes = []
    edges = []
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

    initial_node_ids = set(str(node["element_id"]) for node in graph_data["nodes"][:5])

    level1_node_ids = set()
    for rel in graph_data["relationships"]:
        source = str(rel["source"])
        target = str(rel["target"])
        if source in initial_node_ids:
            level1_node_ids.add(target)
        elif target in initial_node_ids:
            level1_node_ids.add(source)
    
    for node_data in graph_data["nodes"]:
        node_id = str(node_data["element_id"])
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
    
    for rel_data in graph_data["relationships"]:
        source = str(rel_data["source"])
        target = str(rel_data["target"])
        
        if source in initial_node_ids or target in initial_node_ids:
            edge_color = colors['initial_edge']
        else:
            edge_color = colors['level1_edge']
        
        keywords = clean_label(rel_data.get("properties", {}).get("keywords", ""))
        description = clean_label(rel_data.get("description", ""))
        
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
    """
    创建思维导图
    """
    tree = (
        Tree()
        .add(
            series_name="", 
            data=[data], 
            orient="LR",
            initial_tree_depth=3, 
            layout="orthogonal",  
            pos_left="5%",  
            width="40%", 
            height="50%",  
            edge_fork_position="10%",  
            symbol_size=8, 
            symbol="circle", 
            label_opts=opts.LabelOpts(
                position="right",
                horizontal_align="left",
                vertical_align="middle",
                font_size=14,  
                font_weight="bold",  
                color="black", 
                padding=[0, 0, 0, 0],
            ),
            leaves_opts=opts.TreeLeavesOpts( 
                label_opts=opts.LabelOpts(
                    position="right",
                    horizontal_align="left",
                    vertical_align="middle",
                    font_size=12, 
                    color="darkgreen", 
                ),
            ),
            is_expand_and_collapse=True,  
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"{key}知识点思维导图",
                pos_left="center",  
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=20,  
                    font_weight="bold",
                    color="darkblue",
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                trigger_on="mousemove",
                formatter="{b}",  
            ),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                pos_left="right",
                feature={
                    "zoom": {"is_show": True},
                    "restore": {"is_show": True},
                    "saveAsImage": {"is_show": True},  
                },
            )
        )
    )
    return tree

def generate_mind_map(key, base_url):
    """
    向API发送请求以生成思维导图。
    """
    url = f"{base_url}/generateMindMap"
    response = requests.post(url, json={'key': key})
    print(response.json())  
    return response.json()["message"]

def get_wq_data_optional():
    """
    智慧出题题目
    """
    if st.session_state.wq_data is None:
        page = 1
        wq_data = fetch_wq_data(page)
        if wq_data:
            st.session_state.wq_data = wq_data
            return wq_data
        else:
            return []
    else:
        return st.session_state.wq_data

def fetch_wrong_questions(page):
    """
    获取错题集
    """
    url = f"http://{SERVER_URL}:8000/get_wg"  
    params = {"page": page}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200:
            return data.get("wg_data", [])
        else:
            st.error(f"后端返回错误：{data.get('message')}")
            return None
    else:
        st.error("获取数据失败")
        return None

with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; font-size: 32px; font-weight: bold; color:rgb(223, 74, 111); margin-bottom: 20px;">
            Glimmer
        </div>
        """,
        unsafe_allow_html=True
    )

    selected = option_menu(
        menu_title="",  
        options=["问答页面", "知识点查询", "知识图谱", "智慧出题", "错题集"], 
        icons=["chat", "search", "diagram-3", "lightbulb", "file-earmark-text"], 
        menu_icon="cast", 
        default_index=0, 
    )

    st.session_state.current_page = selected

if st.session_state.current_page == "问答页面":
    st.markdown("### 💬 知识问答")

    with st.sidebar:
        with st.expander("📚 **知识库管理**", expanded=True):  
            uploaded_file = st.file_uploader("上传 PDF 文件", type="pdf")
            if uploaded_file is not None:
                file_name = uploaded_file.name
                file_path = os.path.join("knowledge_bases", uploaded_file.name)
                st.session_state.knowledge_base = file_path
                st.success(f"已上传知识库: {uploaded_file.name}")
                knowledge_bases.append(file_name)

            col1, col2 = st.columns(2)
            with col1:
                use_cot = st.toggle("思维链", value=st.session_state.use_cot, key="use_cot_toggle")
                st.session_state.use_cot = use_cot
            with col2:
                use_web_search = st.toggle("联网搜索", value=st.session_state.use_web_search, key="web_search_toggle")
                st.session_state.use_web_search = use_web_search

            selected_knowledge_base = st.selectbox("选择知识库", knowledge_bases)
            st.session_state.knowledge_base = selected_knowledge_base

    for chat in st.session_state.chat_history:
        icon = "💡" if chat["role"] == "bot" else "🙋" 
        with st.chat_message(chat["role"], avatar=icon): 
            if chat["type"] == "text":
                st.markdown(chat["message"])
            elif chat["type"] == "image":
                st.image(chat["message"], caption="生成的思维导图", use_container_width=True)

    user_input = st.chat_input("请输入你的问题：", key="user_input")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "message": user_input, "type": "text"})

        try:
            bot_response = get_bot_response(user_input, st.session_state.thread_id)
            st.session_state.chat_history.append({"role": "bot", "message": bot_response, "type": "text"})

            st.rerun()  
        except Exception as e:
            st.error(f"发生错误：{str(e)}")

    if st.session_state.chat_history:
        st.markdown("---")
        col1, col2, col3 = st.columns([1.2, 1, 1]) 
        with col2:  
            if st.button("清空聊天记录", key="clear_chat_button"):
                st.session_state.chat_history = []
                st.rerun()  

elif st.session_state.current_page == "知识点查询":
    st.markdown("### 📖 知识点查询")
    base_url = f"http://{SERVER_URL}:3000"

    with st.sidebar:

        with st.expander("📚 **知识库管理**", expanded=True):  
            uploaded_file = st.file_uploader("上传 PDF 文件", type="pdf")
            if uploaded_file is not None:
                file_name = uploaded_file.name
                file_path = os.path.join("knowledge_bases", uploaded_file.name)
                st.session_state.knowledge_base = file_path
                st.success(f"已上传知识库: {uploaded_file.name}")
                knowledge_bases.append(file_name)

            col1, col2 = st.columns(2)
            with col1:
                use_cot = st.toggle("思维链", value=st.session_state.use_cot, key="use_cot_toggle")
                st.session_state.use_cot = use_cot
            with col2:
                use_web_search = st.toggle("联网搜索", value=st.session_state.use_web_search, key="web_search_toggle")
                st.session_state.use_web_search = use_web_search

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
    
elif st.session_state.current_page == "知识图谱":
    st.markdown("### 🌐 知识图谱")

    query = st.text_input("请输入查询的问题", "")

    with st.sidebar:
        with st.expander("", expanded=True): 
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
            st.subheader("基本设置")
            width = st.slider("宽度", 400, 2000, 750)
            height = st.slider("高度", 400, 1200, 950)
            directed = st.checkbox("显示箭头", value=True)
            physics = st.checkbox("物理引擎", value=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
            st.subheader("节点设置")
            node_size = st.slider("节点大小", 10, 50, 25)
            st.markdown('</div>', unsafe_allow_html=True)

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

            st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
            st.subheader("节点文字设置")
            node_font_size = st.slider("节点文字大小", 8, 24, 12)
            node_font_color = st.color_picker("节点文字颜色", "#333333")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
            st.subheader("边文字设置")
            edge_font_size = st.slider("边文字大小", 6, 20, 10)
            edge_font_color = st.color_picker("边文字颜色", "#666666")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
            st.subheader("容器设置")
            container_width = st.slider("容器宽度占比", 50, 100, 100, format="%d%%")
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("查询"):
        try:
            with st.spinner('处理中...'):
                result = query_text(query=query, mode='global', only_need_extract_entities=True)
                st.session_state.graph_data = query_neo4j_entities(result)
        except Exception as e:
            st.error(f"发生错误：{str(e)}")
            st.exception(e)

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

        with st.expander("📚 **知识库管理**", expanded=True):  
            uploaded_file = st.file_uploader("上传 PDF 文件", type="pdf")
            if uploaded_file is not None:
                file_name = uploaded_file.name
                file_path = os.path.join("knowledge_bases", uploaded_file.name)
                st.session_state.knowledge_base = file_path
                st.success(f"已上传知识库: {uploaded_file.name}")
                knowledge_bases.append(file_name)

            col1, col2 = st.columns(2)
            with col1:
                use_cot = st.toggle("思维链", value=st.session_state.use_cot, key="use_cot_toggle")
                st.session_state.use_cot = use_cot
            with col2:
                use_web_search = st.toggle("联网搜索", value=st.session_state.use_web_search, key="web_search_toggle")
                st.session_state.use_web_search = use_web_search

            selected_knowledge_base = st.selectbox("选择知识库", knowledge_bases)
            st.session_state.knowledge_base = selected_knowledge_base

    st.markdown("### ✏️ 智慧出题")
    key = st.text_input("请输入题目的知识点", placeholder="")
    if key:
        st.session_state.wq_data = fetch_questions(key)
        wq_data_optional = get_wq_data_optional()

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

                    if "选项" in item:
                        options = item["选项"]
                        option_list = [f"{key}：{value}" for key, value in options.items()]
                        user_answer = st.radio(
                            f"请选择答案（题目 {index + 1}）",
                            options=option_list, 
                            key=f"answer_{index}"
                        )
                        st.session_state.user_answers[index] = user_answer

            if st.button("提交答案"):
                st.session_state.show_answers = True  
                wrong_questions = []
                for index, item in enumerate(st.session_state.wq_data):
                    if "选项" in item:
                        user_answer = st.session_state.user_answers.get(index, "")
                        correct_answer = item["答案"]
                        user_answer = user_answer.split("：")[0]
                        if user_answer != correct_answer:
                            print(user_answer)
                            print(correct_answer)
                            wrong_questions.append(item)  

                if wrong_questions:
                    st.warning(f"❌ 你答错了 {len(wrong_questions)} 道题。")
                    for wrong_item in wrong_questions:
                        st.markdown(f"**题目：** {wrong_item['题目']}")
                        st.markdown(f"**✅ 正确答案：** {wrong_item['答案']}")
                        if wrong_item["解析"]:
                            st.markdown(f"**📖 解析：** {wrong_item['解析']}")
                else:
                    st.success("🎉 恭喜你，全部答对了！")

elif st.session_state.current_page == "错题集":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 📚 错题重做")
    with col2:
        page = st.number_input("页码", min_value=1, value=1)

    page = int(page)
    print(page)
    print(type(page))

    if st.button("🔄 刷新数据"):
        st.rerun()

    try:
        wq_data = fetch_wrong_questions(page)

        if not wq_data:
            st.info("当前页码没有错题数据，试试其他页码吧！")
        else:
            for item in wq_data:
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

                    if item["Type"] == "选择题":
                        st.markdown("**选项：**")
                        for option, text in item["Options"].items():
                            st.markdown(f"- {option}: {text}")

                    with st.expander("🔍 查看答案和解析"):
                        st.markdown(f"**✅ 正确答案：** {item['Answer']}")
                        if item["Analysis"]:
                            st.markdown(f"**📖 解析：** {item['Analysis']}")

                    if st.button(f"✔️ 标记为已掌握（题目 {item['ID']}）", key=f"mark_{item['ID']}"):
                        if item["ID"] not in st.session_state.mastered_questions:
                            st.session_state.mastered_questions.append(item["ID"])
                        st.success(f"题目 {item['ID']} 已标记为已掌握！")

                    st.markdown("---") 
                
                print(st.session_state.mastered_questions)

            col_prev, col_next = st.columns(2)
            with col_prev:
                if page > 1:
                    if st.button("⬅️ 上一页"):
                    
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
