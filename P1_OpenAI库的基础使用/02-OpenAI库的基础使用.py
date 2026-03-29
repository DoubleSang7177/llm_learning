from openai import OpenAI
import os
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)

response = client.chat.completions.create(
    model='deepseek-r1',
    messages=[
        {"role": "system", "content": "你是一个Python编程专家，并且不说废话"},
        {"role": "assistant", 'content': "好的，我是编程专家，并且话不多，你要问什么？"},
        {"role": "user", "content": "输出1-10的数字，使用python代码"}
    ]
)
print(response.choices[0].message.content)