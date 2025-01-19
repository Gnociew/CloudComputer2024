import base64
from request import insert_texts

from request import query_text

def test_query():
    # 指定知识库名称
    kb_name = "中学生物"
    
    try:
        # 测试不同模式的查询
        test_queries = [
            {
                "query": "DNA是怎么执导蛋白质合成的？",
                "mode": "hybrid"
            }
        ]
        
        for test_case in test_queries:
            print(f"\n测试查询：{test_case['query']}")
            print(f"查询模式：{test_case['mode']}")
            
            # 调用query_text函数
            query_text(
                query=test_case['query'],
                mode=test_case['mode'],
                kb_name=kb_name,
                only_need_context=False,
                only_need_prompt=False
            )
            
    except Exception as e:
        print(f"发生错误：{str(e)}")



def test_insert_pdf():
    # 指定知识库名称
    kb_name = "中学信息技术"
    
    try:
        with open("数据结构.docx", "rb") as docx_file:
            docx_content = docx_file.read()
            docx_base64 = base64.b64encode(docx_content).decode('utf-8')
            
        # 调用insert_texts函数
        response = insert_texts(
            message=docx_base64,
            file_type='docx',
            kb_name=kb_name
        )
        
        if response['code'] == 200:
            print("docx文件内容插入成功！")
        else:
            print("docx文件内容插入失败！")
            
    except FileNotFoundError:
        print("错误：找不到'中学信息技术.docx'文件，请确保文件存在于当前目录")
    except Exception as e:
        print(f"发生错误：{str(e)}")

def test_insert_txt():
    # 指定知识库名称
    kb_name = "中学信息技术"
    
    try:
        with open("temp.txt", "rb") as txt_file:
            txt_content = txt_file.read()
            txt_base64 = base64.b64encode(txt_content).decode('utf-8')
            
        # 调用insert_texts函数
        response = insert_texts(
            message=txt_base64,
            file_type='txt',
            kb_name=kb_name
        )
        
        if response['code'] == 200:
            print("txt文件内容插入成功！")
        else:
            print("txt文件内容插入失败！")
            print(f"错误信息：{response.get('message', '未知错误')}")
            
    except FileNotFoundError:
        print("错误：找不到'temp.txt'文件，请确保文件存在于当前目录")
    except Exception as e:
        print(f"发生错误：{str(e)}")

if __name__ == "__main__":
    # test_insert_txt()
    # test_insert_pdf()
    test_query()