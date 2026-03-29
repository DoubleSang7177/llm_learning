from langchain_core.prompts import PromptTemplate,FewShotPromptTemplate,ChatPromptTemplate

prompt_template = PromptTemplate.from_template("我的邻居是： {lastname},我的爱好是： {hobby}")
res = prompt_template.format(lastname="张大爷", hobby="钓鱼")
res2 = prompt_template.invoke(input={"lastname": "张大爷", "hobby": "钓鱼"})
print(res,type(res))
print(res2, type(res2))