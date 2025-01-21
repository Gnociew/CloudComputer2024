import requests
import json
from lightrag import LightRAG, QueryParam
from lightrag.llm import zhipu_complete, zhipu_embedding
from lightrag.utils import EmbeddingFunc

base_url = "http://###:5000" # 替换为你的服务器地址

rag = LightRAG(
    working_dir="./local_neo4jWorkDir",
    llm_model_func=zhipu_complete,
    enable_llm_cache=False,
    graph_storage="Neo4JStorage",
    llm_model_name="glm-4-flashx",
    llm_model_max_async=8,
    llm_model_max_token_size=32768,
    vector_storage="MilvusVectorDBStorge",
    embedding_func=EmbeddingFunc(
        embedding_dim=2048,
        max_token_size=8192,
        func=lambda texts: zhipu_embedding(texts),
    ),
)

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


# 示例调用
if __name__ == "__main__":

    
    key = "光合作用"
    # 查询文本
    # query_text(f"请帮我出有关{key}的无需图表的选择题，包含选项，按照下面的json格式返回给我{json_style}, 注意只需要抽取与{key}相关的实体", mode='hybrid', only_need_context=False, only_need_prompt=False)