from openai import OpenAI

client = OpenAI(
    api_key='sk-8269b69d2ffc4c32aab3dd9dfdcfe2e5',
    base_url='https://api.deepseek.com'
)
messages = [{"role": "system", "content": "你是一个专业的加密货币交易员，擅长技术分析和宏观分析"}]

while True:
    user_input = input("你：")

    if user_input.lower() in ['exit','quit']:
        print('结束对话')
        break


    # 用户输入加入上下文
    messages.append({"role":"user","content":user_input})

    try:
        # 请求ai
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=messages
        )

        # 获取ai回复
        api_reply = response.choices[0].message.content
        print('AI:', api_reply)

        # ai回复加入上下文
        messages.append({"role": "assistant", "content": api_reply})

    except Exception as e:
        print("请求失败",e)
        print('👉 可能是网络问题，重试一下')




