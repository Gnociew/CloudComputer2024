from supabase import create_client
from dotenv import load_dotenv
import os
from zhipuai import ZhipuAI
import json

# 加载环境变量
load_dotenv()

# 从环境变量获取 Supabase 配置
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    raise ValueError("SUPABASE_URL 和 SUPABASE_KEY 环境变量必须设置")

supabase_client = create_client(url, key)

zhipuai_client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

def convert_chinese_to_english_keys(data: dict) -> dict:
    """将中文键名转换为英文键名"""
    key_mapping = {
        "题目": "content",
        "选项": "options",
        "答案": "answer",
        "解析": "explanation"
    }
    
    converted_data = {}
    for key, value in data.items():
        if key in key_mapping:
            if key == "选项":
                # 处理选项字典
                converted_data[key_mapping[key]] = {
                    k: v for k, v in value.items()
                }
            else:
                converted_data[key_mapping[key]] = value
    
    return converted_data

def get_wq_embedding(wq_data: str):
    response = zhipuai_client.embeddings.create(
        model="embedding-3",
        dimensions=1024,
        input=[wq_data["content"], wq_data["options"]["A"], wq_data["options"]["B"], 
               wq_data["options"]["C"], wq_data["options"]["D"], wq_data["answer"], 
               wq_data["explanation"]],
    )
    return response.data

def get_embedding(data:str):
    response=zhipuai_client.embeddings.create(
        model="embedding-3",
        dimensions=1024,
        input=[data],
    )
    return response.data

def insert_embedding(data: str):
    embeddings = get_wq_embedding(data)
    insert_data = {
        "content": data["content"],
        "options": data["options"],
        "answer": data["answer"],
        "explanation": data["explanation"],
        "content_embedding": embeddings[0].embedding,
        "option_a_embedding": embeddings[1].embedding,
        "option_b_embedding": embeddings[2].embedding,
        "option_c_embedding": embeddings[3].embedding,
        "option_d_embedding": embeddings[4].embedding,
        "answer_embedding": embeddings[5].embedding,
        "explanation_embedding": embeddings[6].embedding,
        "is_mastered": False
    }
    supabase_client.table("wqembeddings").insert(insert_data).execute()

def insert_embeddings(data: list):
    for item in data:
        insert_embedding(item)

def get_related_questions(query_data: str, relate_opt: str="content", top_k: int = 5):
    # 获取查询文本的向量表示
    query_data_embedding = get_embedding(query_data)
    
    query_embedding=query_data_embedding[0].embedding
    
    # 根据搜索选项选择对应的字段
    if relate_opt == "content":
        column = "content_embedding"
    elif relate_opt == "option_a":
        column = "option_a_embedding"
    elif relate_opt == "option_b":
        column = "option_b_embedding"
    elif relate_opt == "option_c":
        column = "option_c_embedding"
    elif relate_opt == "option_d":
        column = "option_d_embedding"
    elif relate_opt == "answer":
        column = "answer_embedding"
    elif relate_opt == "explanation":
        column = "explanation_embedding"
    else:
        raise ValueError("Invalid relate_opt. Supported options are: 'content', 'option_a', 'option_b', 'option_c', 'option_d', 'answer', 'explanation'")

    result = supabase_client.rpc('search_related_questions', {
        'query_vector': query_embedding,
        'column_name': column,
        'top_k': top_k
    }).execute()
    
    return result.data

def insert_wq_by_json(json_file_path: str):
    # 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # 批量处理每个问题
    for question in questions:
        # 转换中英文键名
        converted_question = convert_chinese_to_english_keys(question)
        # 插入数据
        try:
            insert_embedding(converted_question)
            print(f"Successfully inserted question: {converted_question['content']}")
        except Exception as e:
            print(f"Error inserting question: {converted_question['content']}")
            print(f"Error message: {str(e)}")

#根据页码返回10条题目，去除embedding字段
def get_all_wq(page: int = 1):
    result = supabase_client.table("wqembeddings").select("*").range(page*10, (page+1)*10).execute()
    for item in result.data:
        item.pop("content_embedding", None)
        item.pop("option_a_embedding", None)
        item.pop("option_b_embedding", None)
        item.pop("option_c_embedding", None)
        item.pop("option_d_embedding", None)
        item.pop("answer_embedding", None)
        item.pop("explanation_embedding", None)
    return result.data

# 添加新函数：更新题目掌握状态
def update_question_mastery(question_id: list, is_mastered: bool = True):
    """
    更新题目的掌握状态
    :param question_id: 题目ID
    :param is_mastered: 是否已掌握，默认为True
    """
    try:
        result = supabase_client.table("wqembeddings")\
            .update({"is_mastered": is_mastered})\
            .in_("id", question_id)\
            .execute()
        return result.data
    except Exception as e:
        print(f"更新题目状态时出错：{str(e)}")
        return None

if __name__ == "__main__":
    update_question_mastery(["1", "2"], True)


