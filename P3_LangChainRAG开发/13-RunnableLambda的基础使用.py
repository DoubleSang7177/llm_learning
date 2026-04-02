from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

model = ChatTongyi(model="qwen3-max")

first_prompt = PromptTemplate.from_template("我邻居姓：{lastname}，刚生了{gender}, 帮我起名字，仅生成一个名字，仅告知名字，不需要额外信息")
second_prompt = PromptTemplate.from_template("姓名{name}，请帮我解析含义。")


str_parser = StrOutputParser()
runnable_lambda = RunnableLambda(lambda ai_msg: {"name": ai_msg.content})
chain = first_prompt | model |runnable_lambda|second_prompt| model |str_parser

for chunk in chain.stream({"lastname": "陆", "gender": "女儿"}):
    print(chunk, end = " ", flush = True)

