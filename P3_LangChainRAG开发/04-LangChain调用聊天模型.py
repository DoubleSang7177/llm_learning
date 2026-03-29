from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage

model = ChatTongyi(model="qwen3-max")

message = [
    SystemMessage(content="你是一个边塞诗人"),
    HumanMessage(content="写一首唐诗"),
    AIMessage(content="锄禾日当午，汗滴禾下土，谁知盘中餐，粒粒皆辛苦"),
    HumanMessage(content="按照你上一个回复的格式，在写一首唐诗 ")
]

# 简写形式
# message = [
#     ("system","你是一个边塞诗人"),
#     ("human","写一首唐诗"),
#     ("ai","锄禾日当午，汗滴禾下土，谁知盘中餐，粒粒皆辛苦"),
#     ("human","按照你上一个回复的格式，在写一首唐诗 ")
# ]

for chunk in model.stream(input=message):
    print(chunk.content,end=" ",flush=True)