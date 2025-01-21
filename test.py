from langchain_community.embeddings import DashScopeEmbeddings
embeddings = DashScopeEmbeddings(
    model="text-embedding-v1", dashscope_api_key="sk-a555417cf91347b480be57fe112f59db"
)
text = "This is a test document."
query_result = embeddings.embed_query(text)
print(query_result)
doc_results = embeddings.embed_documents(["foo"])
print(doc_results)