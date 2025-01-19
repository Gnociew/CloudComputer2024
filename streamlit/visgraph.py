import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

import requests
from neo4j import GraphDatabase

# 设置API的URL
base_url = "http://###:5000" # 替换为你的服务器地址



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
    url = f"{base_url}/query"
    response = requests.post(url, json={
        'query': query,
        'mode': mode,
        'only_need_context': only_need_context,
        'only_need_extract_entities': only_need_extract_entities
    })
    return (response.json())  # 打印API返回的响应


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
    清理标签文本，去除双引号和特殊分隔符，并每4个字符添加换行
    """
    if not isinstance(text, str):
        return ""
    # 去除双引号和 <SEP>
    cleaned = text.replace('"', '').replace('<SEP>', ' ').strip()
    # 如果清理后为空，返回空字符串
    if not cleaned:
        return ""
    
    # 每4个字符添加换行符
    chars = list(cleaned)
    result = []
    for i in range(0, len(chars), 4):
        result.append(''.join(chars[i:i+4]))
    return '\n'.join(result)

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

# 将主要代码放在这个条件下
if __name__ == "__main__":
    # 初始化 session state 存储查询结果
    if 'graph_data' not in st.session_state:
        st.session_state.graph_data = None

    # 添加页面标题
    st.title("知识图谱可视化")
    
    # 添加查询输入框
    query = st.text_input("请输入查询内容", "请描述DNA转录和翻译的过程")
    
    # 添加侧边栏配置
    with st.sidebar:
        st.header("图谱设置", divider="rainbow")        
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
        st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
        st.subheader("基本设置")
        width = st.slider("宽度", 400, 2000, 750)
        height = st.slider("高度", 400, 1200, 950)
        directed = st.checkbox("显示箭头", value=True)
        physics = st.checkbox("物理引擎", value=True)
        
        # 节点设置
        st.subheader("节点设置")
        node_size = st.slider("节点大小", 10, 50, 25)
        
        # 颜色设置
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
        
        # 节点文字设置
        st.subheader("节点文字设置")
        node_font_size = st.slider("节点文字大小", 8, 24, 12)
        node_font_color = st.color_picker("节点文字颜色", "#333333")
        
        # 边文字设置
        st.subheader("边文字设置")
        edge_font_size = st.slider("边文字大小", 6, 20, 10)
        edge_font_color = st.color_picker("边文字颜色", "#666666")
        
        # 容器设置
        st.subheader("容器设置")
        container_width = st.slider("容器宽度占比", 50, 100, 100, format="%d%%")

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
