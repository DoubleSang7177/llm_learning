from langchain_core.prompts import FewShotPromptTemplate,PromptTemplate
from langchain_community.llms.tongyi import Tongyi
example_template = PromptTemplate.from_template("单词：{word}，反义词：{antonym}")

examples_data = [
    {"word":"上","antonym":"下"},
    {"word":"大","antonym":"小"}
]

few_shot_template = FewShotPromptTemplate(
    example_prompt = example_template,
    examples = examples_data,
    prefix = "请告诉我单词的反义词，我提供的事例如下：",
    suffix = "基于前面的事例告诉我，{input_word}的反义词是？",
    input_variables= ['input_word']
)

prompt_text = few_shot_template.invoke(input={"input_word":"早"}).to_string()
# print(prompt_text)

model = Tongyi(model="qwen-max")
print(model.invoke(input=prompt_text))