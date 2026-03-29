from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate

model = ChatTongyi(model="qwen3-max")

prompt = PromptTemplate.from_template("我邻居姓：{lastname}，刚生了{gender}, 帮我起名字，进告知我名字，无需其他内容。")

parser = StrOutputParser()
chain = prompt|model|parser|model|parser

print(chain.invoke({"lastname": "张", "gender": "女儿"}))

