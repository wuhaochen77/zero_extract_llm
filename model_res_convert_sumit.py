import json
import jsonlines
def convert_entity_format_new(input_data):
    """
    将给定的实体格式转换为新的格式。

    此函数的目的是根据输入数据中的实体信息，生成一个特定格式的JSON字符串。
    它首先检查输入数据是否为空，如果不为空，则提取实体类型和实体名称，
    然后构建一个包含这些信息的字典，并将其转换为JSON字符串。

    参数:
    input_data (dict): 包含实体信息的字典。

    返回:
    str: 转换后的JSON字符串，如果输入数据为空，则返回空字典字符串"{}"。
    """
    if input_data != {}:
        # 提取实体类型和实体名称
        arguments = input_data['arguments']
        entity_type = list(arguments.keys())[0]
        if arguments[entity_type] == []:
            entity_name = "未提取"
        else:
            entity_name = arguments[entity_type]

        # 构建属性字典
        attributes = {}
        for key, value in arguments.items():
            if key != entity_type:
                if len(value) > 1:
                    attributes[key] = value
                elif len(value) == 1:
                    attributes[key] = value[0]
                else:
                    attributes[key] = "未提取"

        # 构建嵌套字典
        output_dict = {
            entity_type: {
                entity_name: attributes
            }
        }

        # 转换为JSON字符串
        output_json = json.dumps(output_dict, ensure_ascii=False)
        # 将普通的引号替换为 **\"**
        escaped_json = output_json.replace('"', '\"')
        # 构建最终输出
        return escaped_json
    else:
        # 如果输入数据为空，返回空字典字符串
        return "{}"


def read_jsonl_answer(path):
    content = []
    # 使用jsonlines库以只读模式打开JSON Lines文件
    # 这里使用了with语句，因此不需要显式关闭文件
    with jsonlines.open(path, "r") as json_file:
        # 迭代文件中的每个对象，指定类型为字典，并设置跳过无效JSON对象的选项
        for i,obj in enumerate(json_file.iter(type=dict, skip_invalid=True)):
            # 将每个有效的JSON对象追加到content列表中
            content.append(obj)
            # print(obj)
    # 返回包含所有JSON对象的列表
    return content

def read_jsonl_new(path):
    content = []
    # 使用jsonlines库以只读模式打开JSON Lines文件
    # 这里使用了with语句，因此不需要显式关闭文件
    with jsonlines.open(path, "r") as json_file:
        # 迭代文件中的每个对象，指定类型为字典，并设置跳过无效JSON对象的选项
        for i,obj in enumerate(json_file.iter(type=dict, skip_invalid=False)):
            # 将每个有效的JSON对象追加到content列表中
            content.append(obj)
            print(obj)
    # 返回包含所有JSON对象的列表
    return content

# 定义问题文件路径
question_file_path = "/data/chuangchuang/project_learn/tianchi-llm-qurey/zero_extract_llm/data/ccks2024复赛/ccks2024复赛.json"
# 读取原始数据
original_data = read_jsonl_answer(question_file_path)
# 读取提取的数据
extract_data= read_jsonl_answer("/data/chuangchuang/project_learn/tianchi-llm-qurey/zero_extract_llm/data/model_res_002.json")

# 遍历原始数据
for i, item in enumerate(original_data):
    # 转换实体格式
    result = convert_entity_format_new(extract_data[i])
    # 将转换后的数据添加到原始数据的输出字段
    item["output"] = result
    # 打印处理后的项
    print(item)
    # 将处理后的数据写入最终结果文件
    with open("/data/chuangchuang/project_learn/tianchi-llm-qurey/zero_extract_llm/data/sumit_final_res_002.json", "a+", encoding="utf-8") as f:
        json.dump(item, f, ensure_ascii=False)
        f.write('\n')


