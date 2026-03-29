from langchain_community.llms.tongyi import Tongyi

model = Tongyi(model="qwen-max")

res = model.stream(input="who are you and what can you do ?")

for chunk in res:
    print(chunk, end=" ",flush=True)
