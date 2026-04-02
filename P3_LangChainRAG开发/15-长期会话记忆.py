import os,json
from typing import Sequence

from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser 
# message_to_dict: 单个消息对象（BaseMessage类实 例）转化为字典
# messages_from_dict：[字典,字典,字典....]转化为[消息,消息,消息....]

class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self,session_id,storage_path):
        self.session_id = session_id
        self.storage_path = storage_path
        self.file_path = os.path.join(self.storage_path,self.session_id)
        os.makedirs(os.path.dirname(self.file_path),exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        all_messages = list(self.messages ) # 已有的消息列表
        all_messages.extend(messages)

        new_messages = [message_to_dict(message) for message in all_messages]

        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump(new_messages,f)

    @property
    def messages(self) -> list[BaseMessage]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                message_data = json.load(f)
                return  messages_from_dict(message_data)
        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([],f)


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
    return FileChatMessageHistory(session_id,"./chat_history")

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
    # res = conversation_chain.invoke({"input": "小明有2只猫"}, session_config)
    # print("第一次执行：",res)
    # res2 = conversation_chain.invoke({"input": "小刚有一只狗"}, session_config)
    # print("第2次执行：",res2)
    res3 = conversation_chain.invoke({"input": "总共有几个宠物"}, session_config)
    print("第3次执行：", res3)