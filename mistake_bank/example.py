import asyncio
from vector_db import MistakeVectorDB
from your_embedding import get_embedding # 替换为你的embedding函数

async def main():
    # 1. 初始化错题库
    mistake_db = MistakeVectorDB(
        embedding_func=get_embedding
    )
    
    # 2. 插入错题
    mistake_id = await mistake_db.insert_mistake({
        "content": "已知函数f(x)=x²+ax+b在点(1,2)处的切线方程为y=4x-2,求a,b的值。",
        "answer": "a=2, b=-1",
        "analysis": """解析步骤:
1. 由题意知f(1)=2, 即1+a+b=2 ①
2. f'(x)=2x+a, 在x=1处的导数为4, 即2+a=4 ②
3. 由②得a=2
4. 代入①得b=-1
所以a=2,b=-1""",
        "knowledge_points": ["导数", "切线方程"],
        "kp_descriptions": {
            "导数": "导数表示函数在某一点处的瞬时变化率",
            "切线方程": "切线是曲线在某点处的最佳局部线性逼近"
        },
        "difficulty": 0.7,
        "subject": "数学",
        "grade": "高二"
    })
    
    # 3. 搜索相似错题
    similar_mistakes = await mistake_db.search_similar_mistakes(
        "求函数f(x)=x²+1在x=2处的切线方程",
        top_k=3,
        filters={
            "subject": "数学",
            "min_difficulty": 0.6
        }
    )
    
    # 4. 搜索相关知识点
    related_kps = await mistake_db.search_knowledge_points(
        "如何求函数的切线方程",
        top_k=3,
        filters={
            "subject": "数学",
            "grade": "高二"
        }
    )
    
    print("Similar mistakes:", similar_mistakes)
    print("Related knowledge points:", related_kps)

if __name__ == "__main__":
    asyncio.run(main()) 