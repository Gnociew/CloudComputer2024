from supabase import create_client
import os
from tools import embedding_supabase

supabase_client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def wq_query(query:str)->str:
    related_questions=embedding_supabase.get_related_questions(query, "content")
    if related_questions:
        print ("[WQ Query Roll] 找到对应错题")
        return related_questions