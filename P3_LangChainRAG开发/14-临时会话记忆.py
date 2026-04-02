from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate,MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

model = ChatTongyi(model="qwen3-max")

# prompt = PromptTemplate.from_template("你需要根据会话历史回应用户问题。对话历史：{chat_history}，用户提问：{input}，请回答。")
prompt = ChatPromptTemplate.from_messages( [
    ("system","你需要根据会话历史回应用户问题。对话历史: "),
    MessagesPlaceholder("chat_history"),
    ("human","请回答以下问题：{input}")
    ]
)


str_parser = StrOutputParser()

def print_prompt(full_prompt):
    print("=" * 20, full_prompt.to_string(), "=" * 20)
    return full_prompt

chain = prompt |print_prompt| model | str_parser

store = {}

def get_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

conversation_chain = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)


if __name__ == "__main__":
    session_config = {
        "configurable":{
            "session_id":"user_001"
        }
    }
    res = conversation_chain.invoke({"input": "小明有2只猫"}, session_config)
    print("第一次执行：",res)
    res2 = conversation_chain.invoke({"input": "小刚有一只狗"}, session_config)
    print("第2次执行：",res2)
    res3 = conversation_chain.invoke({"input": "总共有几个宠物"}, session_config)
    print("第3次执行：", res3)

