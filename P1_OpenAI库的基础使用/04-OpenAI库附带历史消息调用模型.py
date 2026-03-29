from openai import OpenAI
import os
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)

response = client.chat.completions.create(
    model='qwen3-max',
    messages=[
        {"role": "system", "content": "你是ai助理，回答很简洁"},
        {"role": "user", "content": "小明有2条宠物狗"},
        {"role": "assistant", 'content': "好的"},
        {"role": "user", "content": "小红有3只条宠物猫咪"},
        {"role": "assistant", 'content': "好的"},
        {"role": "user", "content": "总共有几个宠物 "}
    ],
    stream=True

)

for chunk in response:
    print(chunk.choices[0].delta.content,
          end=" ", # 每一段之间以空格分隔
          flush=True # 立刻刷新缓冲区
          )


# 为什么输出很多None