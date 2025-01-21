import os
import base64

os.environ["NEO4J_URI"] = "###" # 替换为你的neo4j的uri
os.environ["NEO4J_USERNAME"] = "###" # 替换为你的neo4j的username
os.environ["NEO4J_PASSWORD"] = "###" # 替换为你的neo4j的password

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from concurrent.futures import ThreadPoolExecutor

import logging

from lightrag import LightRAG, QueryParam
from lightrag.llm import zhipu_complete, zhipu_embedding
from lightrag.utils import EmbeddingFunc

import json
import graphviz
import requests


# Initialize Flask app and API
app = Flask(__name__)
api = Api(app)

# Configure thread pool for handling concurrent requests
executor = ThreadPoolExecutor(max_workers=6)

# 添加 local_storage_dir 常量
LOCAL_STORAGE_DIR = "./local_storage_dir/"

# Initialize LightRAG
rag = None
cur_db_name = None


vector_db_config = {
    "自定义知识库": {
        "uri": "###", # 替换为你的milvus的uri
        "user": "###", # 替换为你的milvus的user
        "password": "###", # 替换为你的milvus的password
        "token": "###", # 替换为你的milvus的token
        "db_name": "base"
    },
    "中学生物": {
        "uri": "###", # 替换为你的milvus的uri
        "user": "###", # 替换为你的milvus的user
        "password": "###", # 替换为你的milvus的password
        "token": "###", # 替换为你的milvus的token
        "db_name": "biology"
    },
    "中学信息技术": {
        "uri": "###", # 替换为你的milvus的uri
        "user": "###", # 替换为你的milvus的user
        "password": "###", # 替换为你的milvus的password
        "token": "###", # 替换为你的milvus的token
        "db_name": "information-technology"
    }    
}

# 添加知识库配置映射
KB_CONFIG = {
    "中学生物": {
        "entity_types": [
            "生物概念",  # 如 "光合作用", "细胞分裂"
            "生物学术语",  # 如 "DNA", "RNA"
            "生物体",  # 如 "人类", "植物", "动物"
            "生物结构",  # 如 "细胞核", "线粒体"
            "生物过程",  # 如 "有氧呼吸", "蛋白质合成"
            "实验方法",  # 如 "显微镜观察", "PCR"
            "科学家",  # 如 "达尔文", "孟德尔"
            "生物理论"  # 如 "进化论", "遗传定律"
        ]
    },
    "中学信息技术": {
        "entity_types": [
            "技术概念",  # 如 "算法", "程序设计"
            "硬件设备",  # 如 "CPU", "内存"
            "软件工具",  # 如 "操作系统", "应用软件"
            "编程语言",  # 如 "Python", "Java"
            "网络技术",  # 如 "互联网", "局域网"
            "数据结构",  # 如 "数组", "链表"
            "信息安全",  # 如 "加密", "防火墙"
            "技术标准"   # 如 "TCP/IP", "HTTP"
        ]
    },
    "自定义知识库": {
        "entity_types": [
            "概念",
            "人物",
            "组织",
            "地点",
            "事件",
            "时间",
            "数值",
            "其他"
        ]
    }
}

# 修改初始化 RAG 的代码部分
def init_rag(kb_name):
    # 获取知识库特定的配置
    if kb_name not in KB_CONFIG.keys():
        kb_name = "中学生物"
    kb_name = "中学生物"
    kb_specific_config = KB_CONFIG.get(kb_name)
    
    # 构建 addon_params
    addon_params = {
        "language": "Simplified Chinese",
        "example_number": 3,
        "insert_batch_size": 10,
        "entity_types": kb_specific_config["entity_types"]
    }
    
    return LightRAG(
        working_dir="./local_neo4jWorkDir",
        llm_model_func=zhipu_complete,
        enable_llm_cache=False,
        graph_storage="Neo4JStorage",
        llm_model_name="glm-4-flashx",
        llm_model_max_async=8,
        llm_model_max_token_size=32768,
        vector_storage="MilvusVectorDBStorge",
        vector_db_storage_cls_kwargs={
            "milvus_config": vector_db_config[kb_name]
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=2048,
            max_token_size=8192,
            func=lambda texts: zhipu_embedding(texts),
        ),
        addon_params=addon_params  # 添加 addon_params
    )

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


def create_mind_map(key, data):
    # 创建思维导图结构
    mind_map = {
        "name": data["labels"][0],
        "children": [
            {"name": "知识点", "children": [{"name": desc} for desc in data["properties"]["description"]]}
        ]
    }

    # 将思维导图结构保存为JSON文件
    with open(f"static/MindMap/{key}_mind_map.json", 'w', encoding='utf-8') as f:
        json.dump(mind_map, f, ensure_ascii=False, indent=4)

    print("Mind map structure has been saved to mind_map.json")

    # 创建 Graphviz 图像，并指定字体
    dot = graphviz.Digraph(comment=f"{key} Information Map")

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
    output_file = f"static/MindMap/{key}_mind_map"
    dot.render(output_file, format='png', view=False)

    return output_file, mind_map

# 查询文本示例
def query_text_mindmap(key):
    
    json_style = """
{
    "labels": ["ADP"],
    "properties": {
        "description": [
            "ADP 是 ATP 水解后形成的产物，参与细胞内能量代谢，是能量转移的中间形式。",
            "ADP 是 ATP 水解后形成的产物，参与能量代谢。",
            "ADP是光合作用中的一种能量载体，参与能量转换。",
            "ADP是腺苷二磷酸，是一种能量储存和传递的分子。",
            "ADP（二磷酸腺苷）是文中提到的能量分子，与ATP相关。",
            "ADP（腺苷二磷酸）是ATP分解后的产物，可以在细胞内重新合成ATP。",
            "ADP（腺苷二磷酸）是一种含有高能磷酸键的核苷酸，在此过程中，它与Pi（无机磷酸盐）反应生成AITP。"
        ]
    }
}
    """
    
    # json_style = {
    #     "labels": [key],
    #     "properties": {
    #         "description": [
    #             "请在此处填写关于{key}的第一个描述。",
    #             "请在此处填写关于{key}的第二个描述。",
    #             "请在此处填写关于{key}的第三个描述。"
    #         ]
    #     }
    # }

    query = f"请帮我总结出关于{key}的相关知识点，按照下面的json格式返回给我:{json_style}, 注意只需要抽取与{key}相关的实体，并且labels中只包含{key}"

    global cur_db_name
    global rag
        
    if rag is None:
        rag = init_rag(cur_db_name)
    
    response = rag.query(
        query,
        QueryParam(
            mode='hybrid',
            only_need_context=False,
            only_need_prompt=False
        )
    )

    # 提取 JSON 字符串部分
    json_str = response.split('```json')[1].split('```')[0].strip()

    # 去除首尾的引号（如果有的话）
    json_str = json_str.strip('"')

    # 解析 JSON 字符串
    MindMapContent = json.loads(json_str)

    # 将解析后的数据保存到文件中
    with open(f"static/MindMap/{key}_mind_map.json", 'w', encoding='utf-8') as f:
        json.dump(MindMapContent, f, ensure_ascii=False, indent=4)

    # 打印解析后的数据（可选）
    print(MindMapContent)

    return MindMapContent


def create_mind_map_from_key(key): # 用户传入一个关键词
    MindMapContent = query_text_mindmap(key)
    output_path, mind_map = create_mind_map(key, MindMapContent)
    return mind_map

# 查询文本示例
def generate_QA(key):
    json_style = """
    {
  "题目": "草履虫、衣藻、变形虫和细菌都是单细胞生物。尽管它们的大小和形状各不相同，但它们都有相似的结构，即都具有             (  )",
  "选项": {
    "A": "细胞膜、细胞质、细胞核、液泡",
    "B": "细胞壁、细胞膜、细胞质、细胞核",
    "C": "细胞膜、细胞质、细胞核、染色体",
    "D": "细胞膜、细胞质、储存遗传物质的场所"
  },
  "答案": "D",
  "解析": "所有细胞生物，包括单细胞生物如草履虫、衣藻、变形虫和细菌，都拥有基本的细胞结构：细胞膜（用于分隔细胞内外环境），细胞质（细胞内的液体介质，其中含有各种细胞器和分子）。此外，所有的细胞都需要有储存遗传信息的地方，以指导其生命活动和繁殖。对于真核细胞来说，遗传物质通常储存在细胞核内；而原核细胞如细菌则没有成型的细胞核，它们的遗传物质（DNA）直接存在于细胞质中，但也被视为一种储存遗传物质的场所。因此，选项D是正确的。其他选项中提到的细胞核、液泡、细胞壁和染色体，并不是所有这些单细胞生物共有的特征。例如，细菌没有真正的细胞核或膜包裹的细胞器，也不是所有的单细胞生物都有细胞壁或液泡。"
    }
    """
    query = f"请帮我出5道有关{key}的无需图表的选择题，包含选项，按照下面的json格式返回给我{json_style}, 注意只需要抽取与{key}相关的实体"
    
    global cur_db_name
        
    if rag is None:
        rag = init_rag(cur_db_name)
    
    response = rag.query(
        query,
        QueryParam(
            mode='hybrid',
            only_need_context=False,
            only_need_prompt=False
        )
    )

    # 提取 JSON 字符串部分
    json_str = response.split('```json')[1].split('```')[0].strip()

    # 去除首尾的引号（如果有的话）
    json_str = json_str.strip('"')

    # 解析 JSON 字符串
    question_data_in_json = json.loads(json_str)

    file_path = f"static/QA/{key}_QA.json"

    # 将解析后的数据保存到文件中
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(question_data_in_json, f, ensure_ascii=False, indent=4)

    # 打印解析后的数据（可选）
    # print(question_data)
    return question_data_in_json



# 修改 InsertText 类
class InsertText(Resource):
    def post(self):
        data = request.get_json()
        texts = data.get('texts', [""])
        kb_name = data.get('kb_name', '中学生物')
        
        print(f"kb_name: {kb_name}")
        print(f"texts: {texts[:2000]}")
        
        if not texts:
            return {'message': 'No texts provided', 'code': 400}
        
        global cur_db_name
        global rag
        
        if cur_db_name != kb_name or rag is None:
            cur_db_name = kb_name
            rag = init_rag(kb_name)
            
        result = executor.submit(rag.insert, texts)
        return {'message': 'Batch text insertion initiated', 'code': 200}
    

# 插入自定义知识图谱
class InsertCustomKG(Resource):
    def post(self):
        data = request.get_json()
        custom_kg = data.get('custom_kg', {})
        if not custom_kg:
            return {'message': 'No custom KG provided', 'code': 400}
        executor.submit(rag.insert_custom_kg, custom_kg)
        return {'message': 'Custom KG insertion initiated', 'code': 200}
    
    
# 查询文本
class QueryText(Resource):
    def post(self):
        data = request.get_json()
        query_text = data.get('query', '')
        mode = data.get('mode', 'naive')
        kb_name = data.get('kb_name', '中学生物')
        only_need_context = data.get('only_need_context', False)
        only_need_prompt = data.get('only_need_prompt', False)
        only_need_extract_entities = data.get('only_need_extract_entities', False)
        
        if not query_text:
            return {'message': 'No query provided', 'code': 400}
        
        if mode not in ['naive', 'local', 'global', 'hybrid']:
            return {'message': 'Invalid mode provided', 'code': 401}
        
        global cur_db_name
        global rag
        
        print("="*50)
        # 打印信息
        print(mode)
        print(query_text)
        print(kb_name)
        print("="*50)
        
        if rag is None or cur_db_name != kb_name:
            cur_db_name = kb_name
            rag = init_rag(kb_name)
        
        result = executor.submit(rag.query, query_text, param=QueryParam(
            mode=mode, 
            only_need_context=only_need_context, 
            only_need_prompt=only_need_prompt, 
            only_need_extract_entities=only_need_extract_entities
        )).result()
        return {'message': result, 'code': 200}

# 删除实体
class DeleteEntity(Resource):
    def post(self):
        data = request.get_json()
        entity_name = data.get('entity_name', '')
        if not entity_name:
            return {'message': 'No entity name provided', 'code': 400}
        
        executor.submit(rag.delete_by_entity, entity_name)
        return {'message': f'Entity {entity_name} deletion initiated', 'code': 200}

# 生成QA
class GenerateQA(Resource):
    def post(self):
        data = request.get_json()
        key = data.get('key', '')
        if not key:
            return {'message': 'No key provided', 'code': 400}
        
        # if mode not in ['naive', 'local', 'global', 'hybrid']:
        #     return {'message': 'Invalid mode provided', 'code': 401}

        print(key)
        
        result = executor.submit(generate_QA, key).result()
        return {'message': result, 'code': 200}

# 生成思维导图
class GenerateMindMap(Resource):
    def post(self):
        data = request.get_json()
        key = data.get('key', '')
        if not key:
            return {'message': 'No key provided', 'code': 400}
        
        # if mode not in ['naive', 'local', 'global', 'hybrid']:
        #     return {'message': 'Invalid mode provided', 'code': 401}
        
        result = executor.submit(create_mind_map_from_key, key).result()

        # image_path = f'{result}.png'

        # with open(image_path, "rb") as image_file:
        #     encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        return {'message': result, 'code': 200}

# Add resources to API
api.add_resource(InsertText, '/insert')
api.add_resource(InsertCustomKG, '/insert_custom_kg')
api.add_resource(QueryText, '/query')
api.add_resource(DeleteEntity, '/delete_entity')
api.add_resource(GenerateQA, '/generateQA')
api.add_resource(GenerateMindMap, '/generateMindMap')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)