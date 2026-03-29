from langchain_community.embeddings import DashScopeEmbeddings

# 创建模型对象 不传model默认使用的是embeddings-v1 。
model = DashScopeEmbeddings()

print(model.embed_query("我喜欢你"))

print(model.embed_documents(["我喜欢你","晚上吃什么","我稀罕你"]))