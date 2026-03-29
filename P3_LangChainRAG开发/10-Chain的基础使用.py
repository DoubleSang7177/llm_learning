from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
chat_prompt_template = ChatPromptTemplate.from_messages(
    [
    ("system", "你是一个边塞诗人，可以作诗。 "),
     MessagesPlaceholder("history"),
     ("human", "请再来一首唐诗")
     ]
)

history_data = [
    ("human","写一首唐诗"),
    ("ai","锄禾日当午，汗滴禾下土，谁知盘中餐，粒粒皆辛苦"),
    ("human","好诗，再来一首"),
    ("ai","窗前明月光，疑是地上霜，举头望明月，低头思故乡"),
]


model = ChatTongyi(model="qwen3-max")

# 要求每一个组件都是Runnable接口的子类
chain = chat_prompt_template | model

res = chain.stream({"history": history_data})

for chunk in res:
    print(chunk.content , end =" ",flush=True)