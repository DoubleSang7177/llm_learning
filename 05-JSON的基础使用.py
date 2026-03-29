import json

d = {
    "name": "蔡依林",
    "age": "22",
    "gender": "女"
}

# 转化为json对象
s = json.dumps(d, ensure_ascii = False)

print(s,type(json))

l = [
{
    "name": "蔡依林",
    "age": "22",
    "gender": "女"
},
{
    "name": "王源",
    "age": "27",
    "gender": "男"
},
{
    "name": "吴亦凡",
    "age": "32",
    "gender": "男"
}
]
# 转化为json对象
print(json.dumps(l, ensure_ascii=False))


json_str = '{"name": "蔡依林", "age": "22", "gender": "女"}'
json_array_str = '[{"name": "蔡依林", "age": "22", "gender": "女"}, {"name": "王源", "age": "27", "gender": "男"}, {"name": "吴亦凡", "age": "32", "gender": "男"}]'

res_dict = json.loads(json_str)
print(res_dict,type(res_dict))

res_list = json.loads(json_array_str)
print(res_list,type(res_list))