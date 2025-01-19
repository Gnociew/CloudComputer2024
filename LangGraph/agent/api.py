from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import create_agent, get_agent_response
import uvicorn
from tools.embedding_supabase import get_all_wq, update_question_mastery,insert_embeddings
import json
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

# 在文件开头加载环境变量
load_dotenv()

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建agent实例
graph, pool = create_agent()

class ChatInput(BaseModel):
    message: str
    thread_id: str = "default"
    knowledge_base_id: str = "default"

@app.post("/chat")
async def chat_endpoint(chat_input: ChatInput):
    try:
        response = get_agent_response(
            graph, 
            chat_input.message, 
            chat_input.thread_id,
            knowledge_base_id=chat_input.knowledge_base_id
        )
        return {"thread_id": chat_input.thread_id, "role": "AI", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream_endpoint(chat_input: ChatInput):
    try:
        async def generate():
            for event in graph.stream(
                {"messages": [HumanMessage(content=chat_input.message)]},
                {"configurable": {
                    "thread_id": chat_input.thread_id,
                    "knowledge_base_id": chat_input.knowledge_base_id
                }},
                stream_mode="values"
            ):
                response = event["messages"][-1]
                yield f"data: {json.dumps({'content': response.content})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/insert_wq")
async def insert_wq(wq_data: list):
    insert_embeddings(wq_data)
    return {"code": 200, "message": "success"}

@app.get("/get_wq")
#返回json格式的题目
async def get_wq(page: int = 1):
    wq_data = get_all_wq(page)
    
    return_data = {
        "code": 200,
        "wq_data": wq_data,
        "message": "success"
    }
    return return_data

@app.get("/master_wq")
async def master_wq(wq_id: list):
    result = update_question_mastery(wq_id, True)
    if result:
        return {"code": 200, "message": "success"}
    else:
        return {"code": 500, "message": "failed"}

@app.on_event("shutdown")
async def shutdown_event():
    pool.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 