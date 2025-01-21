import json
import graphviz
import requests

# 假设这是你的输入数据
# data = {
#     "labels": ["ADP"],
#     "properties": {
#         "entity_type": "CATEGORY",
#         "description": "ADP 是 ATP 水解后形成的产物，参与细胞内能量代谢，是能量转移的中间形式。<SEP>ADP 是 ATP 水解后形成的产物，参与能量代谢。<SEP>ADP是光合作用中的一种能量载体，参与能量转换。<SEP>ADP是腺苷二磷酸，是一种能量储存和传递的分子。<SEP>ADP（二磷酸腺苷）是文中提到的能量分子，与ATP相关。<SEP>ADP（腺苷二磷酸）是ATP分解后的产物，可以在细胞内重新合成ATP。<SEP>ADP（腺苷二磷酸）是一种含有高能磷酸键的核苷酸，在此过程中，它与Pi（无机磷酸盐）反应生成AITP。",
#         "source_id": "chunk-5920eee6b8dc738c14050b03e4d650ae<SEP>chunk-30903a363c8cff77e46d526adfbbea9a<SEP>chunk-a2de2ce7c7d1ccfb1c6ad6e2a03e4402<SEP>chunk-f06120f60a755e084424e8b042826758<SEP>chunk-b2866cee4c2aff84b3027e90206fc43c<SEP>chunk-a800c38a333f2bad1de3fd7fd3e770f4"
#     }
# }

base_url = "http://47.116.205.94:5000"

# 函数用于递归添加子节点
def add_nodes(dot, parent_name, children):
    for child in children:
        node_name = parent_name + '_' + child['name'].replace(' ', '_').replace('(', '').replace(')', '')
        dot.node(node_name, child['name'], fontname='SimSun')  # 为每个节点单独设置字体
        dot.edge(parent_name, node_name)
        if 'children' in child:
            add_nodes(dot, node_name, child['children'])
        elif 'value' in child:
            value_node_name = node_name + '_value'
            dot.node(value_node_name, child['value'], fontname='SimSun')  # 为值节点设置字体
            dot.edge(node_name, value_node_name)

# def create_mind_map(key, data): # 这里的data需要传一个从搜索结果返回的json数据

#     # 创建思维导图结构
#     mind_map = {
#         "name": data["labels"][0],
#         "children": [
#             {"name": "Descriptions", "children": [{"name": desc.strip()} for desc in data["properties"]["description"].split("<SEP>") if desc.strip()]}
#         ]
#     }

#     # 将思维导图结构保存为JSON文件
#     with open('mind_map.json', 'w', encoding='utf-8') as f:
#         json.dump(mind_map, f, ensure_ascii=False, indent=4)

#     print("Mind map structure has been saved to mind_map.json")

#     # 创建 Graphviz 图像，并指定字体
#     dot = graphviz.Digraph(comment='ADP Information Map')

#     dot.attr(fontname='WenQuanYi Micro Hei', encoding='utf-8')  # 改为系统中的中文字体
#     dot.node_attr.update(fontname='WenQuanYi Micro Hei')  # 设置节点字体
#     dot.edge_attr.update(fontname='WenQuanYi Micro Hei')  # 设置边字体

#     # 添加根节点
#     dot.node('root', mind_map['name'])

#     # 添加思维导图中的节点和边
#     add_nodes(dot, 'root', mind_map['children'])

#     # 调整布局参数
#     dot.graph_attr.update(rankdir='LR', nodesep='1.0', ranksep='1.0')

#     # 渲染并保存为文件
#     output_file = f"{key}_mind_map"
#     dot.render(output_file, format='png', view=False)
            
import json
import graphviz

def create_mind_map(key, data):
    # 创建思维导图结构
    mind_map = {
        "name": data["labels"][0],
        "children": [
            {"name": "Descriptions", "children": [{"name": desc.strip()} for desc in data["properties"]["description"].split("<SEP>") if desc.strip()]}
        ]
    }

    # 将思维导图结构保存为JSON文件
    with open('mind_map.json', 'w', encoding='utf-8') as f:
        json.dump(mind_map, f, ensure_ascii=False, indent=4)

    print("Mind map structure has been saved to mind_map.json")

    # 创建 Graphviz 图像，并指定字体
    dot = graphviz.Digraph(comment='ADP Information Map')

    # 设置全局样式
    dot.attr(fontname='WenQuanYi Micro Hei', encoding='utf-8')  # 改为系统中的中文字体
    dot.attr('node', fontname='WenQuanYi Micro Hei', fontsize='12', shape='box', style='rounded,filled', fillcolor='#E0F7FA', color='#00796B')
    dot.attr('edge', fontname='WenQuanYi Micro Hei', color='#00796B', arrowsize='0.5')

    # 添加根节点
    dot.node('root', mind_map['name'], shape='ellipse', fillcolor='#00796B', fontcolor='white', fontsize='14')

    # 添加思维导图中的节点和边
    add_nodes(dot, 'root', mind_map['children'])

    # 调整布局参数
    dot.graph_attr.update(rankdir='LR', nodesep='1.0', ranksep='1.5', splines='ortho')

    # 渲染并保存为文件
    output_file = f"{key}_mind_map"
    dot.render(output_file, format='png', view=False)

# 查询文本示例
def query_text(query, mode='naive', only_need_context=False, only_need_prompt=False):
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
        'only_need_prompt': only_need_prompt
    })
    print(response.json())  # 打印API返回的响应
    # 提取出response中的message字段
    # 假设 message 是从 response.json() 中获取的字符串
    message = response.json()['message']

    # 提取 JSON 字符串部分
    json_str = message.split('```json')[1].split('```')[0].strip()

    # 去除首尾的引号（如果有的话）
    json_str = json_str.strip('"')

    # 解析 JSON 字符串
    question_data = json.loads(json_str)

    # 将解析后的数据保存到文件中
    with open('question_data.json', 'w', encoding='utf-8') as f:
        json.dump(question_data, f, ensure_ascii=False, indent=4)

    # 打印解析后的数据（可选）
    print(question_data)

    return question_data


def create_mind_map_from_json(key): # 用户传入一个关键词
    json_style = """
    {
    "labels": ["ADP"],
    "properties": {
        "description": "ADP 是 ATP 水解后形成的产物，参与细胞内能量代谢，是能量转移的中间形式。<SEP>ADP 是 ATP 水解后形成的产物，参与能量代谢。<SEP>ADP是光合作用中的一种能量载体，参与能量转换。<SEP>ADP是腺苷二磷酸，是一种能量储存和传递的分子。<SEP>ADP（二磷酸腺苷）是文中提到的能量分子，与ATP相关。<SEP>ADP（腺苷二磷酸）是ATP分解后的产物，可以在细胞内重新合成ATP。<SEP>ADP（腺苷二磷酸）是一种含有高能磷酸键的核苷酸，在此过程中，它与Pi（无机磷酸盐）反应生成AITP。"
        }
    }
    """
    question_data = query_text(f"请帮我总结出关于{key}的相关知识点，按照下面的json格式返回给我:{json_style}, 注意只需要抽取与{key}相关的实体，并且labels中只包含{key}", mode='hybrid', only_need_context=False)
    create_mind_map(key, question_data)

if __name__ == '__main__':
    # 创建思维导图
    create_mind_map_from_json("光合作用")