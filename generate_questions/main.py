import requests
import json

base_url = "http://47.116.205.94:5000"

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


# 示例调用
if __name__ == "__main__":

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
    key = "光合作用"
    # 查询文本
    query_text(f"请帮我出有关{key}的无需图表的选择题，包含选项，按照下面的json格式返回给我{json_style}, 注意只需要抽取与{key}相关的实体", mode='hybrid', only_need_context=False, only_need_prompt=False)