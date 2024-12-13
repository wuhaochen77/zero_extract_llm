import jsonlines
import re
import json
def read_jsonl(path):
    content = []
    # 使用jsonlines库以只读模式打开JSON Lines文件
    # 这里使用了with语句，因此不需要显式关闭文件
    with jsonlines.open(path, "r") as json_file:
        # 迭代文件中的每个对象，指定类型为字典，并设置跳过无效JSON对象的选项
        for obj in json_file.iter(type=dict, skip_invalid=True):
            # 将每个有效的JSON对象追加到content列表中
            content.append(obj)

    # 返回包含所有JSON对象的列表
    return content


def write_jsonl(path, content):
    with jsonlines.open(path, "w") as json_file:
        json_file.write_all(content)

def str_dict(text):

    text = text.replace('\n', '')

    # 正则表达式
    pattern = r'<tool_call>(.*?)</tool_call>'

    # 使用re.search查找匹配的内容
    match = re.search(pattern, text, re.DOTALL)
    try:
        # 如果找到匹配的内容，则提取并打印
        if match:
            content = match.group(1)
            content = json.loads(content)
            # print(content)
            return content
        else:
            print("No match found.")
            return None
    except Exception as e:
        print(e)
        return None

def extract_entity_attributes(text):
    """
    根据输入的文本，抽取指定类型的实体及其属性信息。

    该函数解析输入指令，提取实体类型和属性，并定义输出格式，最后返回配置信息和输出格式。

    参数:
    text (dict): 包含指令的字典，指令中包括输入文本和实体-属性结构。

    返回:
    tuple: 包含配置信息和输出格式的元组。
    """
    # 解析指令
    instruction = text["instruction"]
    instruction = json.loads(instruction)
    input = instruction["input"]
    entity_type = instruction["schema"][0]["entity_type"]
    attrubutes = instruction["schema"][0]["attributes"]

    # 初始化实体类型的属性和必需属性列表
    attribute_properties = {entity_type: {"type": "string",
                                          "description": "对输入的文本进行指定实体类型信息的抽取,文本中仅存在一个主要实体值,请不要返回多个值,如果不存在则返回[]"}}
    list_of_attr = [entity_type]

    # 遍历属性，添加到属性字典和必需属性列表中
    for attr_name, attr_desc in attrubutes.items():
        attribute_properties[attr_name] = {"type": "array", "items": {"type": "string"}, "description": attr_desc}
        list_of_attr.append(attr_name)

    # 定义输出格式
    output_format = [{"name": "Extract_entity_attribute",
                      "description": "根据输入的文本内容，从文本中抽取出相应的实体实例和其属性信息，不存在的属性不输出, 实体和属性存在多值就返回列表",
                      "parameters": {"type": "object",
                                     "properties": attribute_properties,
                                     "required": list_of_attr}}]

    # 定义系统和用户消息
    messages = [
        {"role": "system",
         "content": "你是一名高级智能信息抽取助手，请对输入文本内容进行理解，抽取出指定类型的实体和属性信息"},
        {"role": "user", "content": f"请对文本内容进行实体和属性信息抽取,以下是输入的文本内容:{input}"}
    ]

    # 返回配置信息和输出格式
    return messages, output_format


if __name__ == "__main__":
    text = '<tool_call>\n{"name": "Classify", "arguments": {"招股说明书咨询": "1", "数据查询": "0", "其他问题": "0"}}\n</tool_call><|im_end|>'

    # 正则表达式
    pattern = r'<tool_call>(.*?)</tool_call>'
    # 使用re.search查找匹配的内容
    match = re.search(pattern, text, re.DOTALL)
    # 如果找到匹配的内容，则提取并打印
    if match:
        content = match.group(1)
        content = json.loads(content)
        print(content)
    else:
        print("No match found.")