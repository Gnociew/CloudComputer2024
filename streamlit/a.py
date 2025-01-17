import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

import requests
from neo4j import GraphDatabase

# 设置API的URL
base_url = "http://###:5000" # 替换为你的服务器地址

# 添加页面标题

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
    清理标签文本，去除双引号和特殊分隔符
    """
    if not isinstance(text, str):
        return ""
    # 去除双引号和 <SEP>
    cleaned = text.replace('"', '').replace('<SEP>', ' ').strip()
    # 如果清理后为空，返回空字符串
    return cleaned if cleaned else ""

def render_knowledge_graph(graph_data):
    # 初始化 session_state 中的颜色配置
    if 'graph_colors' not in st.session_state:
        st.session_state.graph_colors = {
            'initial_node': '#FF6B6B',
            'level1_node': '#4ECDC4',
            'level2_node': '#45B7D1',
            'initial_edge': '#FF9F9F',
            'level1_edge': '#96E6E0'
        }
    
    # 创建节点和边的列表
    nodes = []
    edges = []
    
    # 获取初始节点的ID列表（前5个节点）
    initial_node_ids = set(str(node["element_id"]) for node in graph_data.get("nodes", [])[:5])
    
    # 找出与初始节点直接相连的节点ID
    level1_node_ids = set()
    for rel in graph_data.get("relationships", []):
        source = str(rel["source"])
        target = str(rel["target"])
        if source in initial_node_ids:
            level1_node_ids.add(target)
        elif target in initial_node_ids:
            level1_node_ids.add(source)
    
    # 添加侧边栏配置
    with st.sidebar:
        st.markdown("""
        <style>
        .sidebar-config {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
        st.header("图谱设置")
        
        # 基础设置
        st.subheader("基本设置")
        width = st.slider("宽度", 400, 2000, 1500)
        height = st.slider("高度", 400, 1200, 800)
        directed = st.checkbox("显示箭头", value=True)
        physics = st.checkbox("物理引擎", value=True)
        
        # 节点设置
        st.subheader("节点设置")
        node_size = st.slider("节点大小", 10, 50, 25)
        
        # 颜色设置
        st.subheader("颜色设置")
        # 使用 session_state 存储颜色值
        st.session_state.graph_colors['initial_node'] = st.color_picker(
            "初始节点颜色", 
            st.session_state.graph_colors['initial_node'],
            key='initial_node_color'
        )
        st.session_state.graph_colors['level1_node'] = st.color_picker(
            "一级节点颜色", 
            st.session_state.graph_colors['level1_node'],
            key='level1_node_color'
        )
        st.session_state.graph_colors['level2_node'] = st.color_picker(
            "二级节点颜色", 
            st.session_state.graph_colors['level2_node'],
            key='level2_node_color'
        )
        st.session_state.graph_colors['initial_edge'] = st.color_picker(
            "主要边颜色", 
            st.session_state.graph_colors['initial_edge'],
            key='initial_edge_color'
        )
        st.session_state.graph_colors['level1_edge'] = st.color_picker(
            "次要边颜色", 
            st.session_state.graph_colors['level1_edge'],
            key='level1_edge_color'
        )
        
        # 布局设置
        st.subheader("布局设置")
        layout_iterations = st.slider("布局迭代次数", 50, 300, 100)
        st.markdown('</div>', unsafe_allow_html=True)

    # 主要内容区域
    try:
        # 处理节点
        for node in graph_data.get("nodes", []):
            node_id = str(node["element_id"])
            # 根据节点类型选择颜色
            if node_id in initial_node_ids:
                node_color = st.session_state.graph_colors['initial_node']
            elif node_id in level1_node_ids:
                node_color = st.session_state.graph_colors['level1_node']
            else:
                node_color = st.session_state.graph_colors['level2_node']
                
            nodes.append(
                Node(
                    id=node_id,
                    label=str(node["label"]),
                    size=node_size,
                    color=node_color
                )
            )

        # 处理边
        for edge in graph_data.get("relationships", []):
            source = str(edge["source"])
            target = str(edge["target"])
            # 根据连接的节点类型选择边的颜色
            if source in initial_node_ids or target in initial_node_ids:
                edge_color = st.session_state.graph_colors['initial_edge']
            else:
                edge_color = st.session_state.graph_colors['level1_edge']
                
            edges.append(
                Edge(
                    source=source,
                    target=target,
                    label=str(edge.get("type", "")),
                    color=edge_color
                )
            )

        # 创建配置
        config = Config(
            width=width,
            height=height,
            directed=directed,
            physics={
                "enabled": physics,
                "stabilization": {
                    "enabled": True,
                    "iterations": layout_iterations
                }
            },
            hierarchical=False,
            node={
                "borderWidth": 2,
                "borderWidthSelected": 3,
                "font": {
                    "size": 14,
                    "color": "#333333"
                }
            },
            edge={
                "width": 2,
                "smooth": {
                    "type": "curvedCW",
                    "roundness": 0.2
                },
                "font": {
                    "size": 12,
                    "color": "#666666"
                }
            }
        )

        # 渲染图谱
        return agraph(nodes=nodes, edges=edges, config=config)

    except Exception as e:
        st.error(f"渲染图谱时出错：{str(e)}")
        st.write("节点数量：", len(nodes))
        st.write("边数量：", len(edges))
        return None

# 主程序部分
if __name__ == "__main__":
    # 将查询输入框放在主内容区域
    st.title("知识图谱可视化")
    query = st.text_input("请输入查询内容", "请描述DNA转录和翻译的过程")
    
    if st.button("查询") or query:
        try:
            with st.spinner('正在查询数据...'):
                result = query_text(
                    query=query,
                    mode='global',
                    only_need_context=False,
                    only_need_prompt=False,
                    only_need_extract_entities=True
                )
                
                graph_data = query_neo4j_entities(result)
                
                if graph_data and (graph_data.get("nodes") or graph_data.get("relationships")):
                    render_knowledge_graph(graph_data)
                else:
                    st.warning("未获取到图谱数据")
                    st.write("查询结果：", result)
                    st.write("图谱数据：", graph_data)
        
        except Exception as e:
            st.error(f"查询过程出错：{str(e)}")
            st.exception(e)
