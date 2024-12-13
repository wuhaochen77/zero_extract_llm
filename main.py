import os,json,sys
from transformers import AutoModelForCausalLM, AutoTokenizer
from utility import read_jsonl
from utility import str_dict, extract_entity_attributes
os.chdir(sys.path[0])

class QwenChatModel:
    def __init__(self, model_path):
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype="auto",

            device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

    def apply_chat_template(self, messages, tools=None, max_new_tokens=512):
        if tools:
            # 使用tokenizer应用带有工具的聊天模板，并准备生成提示，但不进行分词
            text = self.tokenizer.apply_chat_template(messages,
                                                      tools=tools,
                                                      add_generation_prompt=True, tokenize=False)
            # 将文本转换为模型输入张量
            inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
            # 根据输入张量生成响应，限制生成的最大新令牌数
            outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
            # 解码生成的令牌ID为文本，并去除输入部分
            output_text = self.tokenizer.batch_decode(outputs)[0][len(text):]
        else:
            # 如果没有工具，使用tokenizer应用聊天模板，并准备生成提示，但不进行分词
            text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            # 将文本转换为模型输入张量
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            # 根据输入张量生成响应，限制生成的最大新令牌数
            generated_ids = self.model.generate(**model_inputs, max_new_tokens=max_new_tokens)
            # 去除输入部分的令牌ID
            generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
            # 解码处理后的令牌ID为文本，并跳过特殊令牌
            output_text = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return output_text

if __name__ == '__main__':

    # 定义模型路径
    model_path = "./model/Qwen--Qwen2.5-7B-Instruct"
    # 实例化Qwen聊天模型
    qwen_model = QwenChatModel(model_path)

    # 定义问题文件路径
    question_file_path = "./data/ccks2024复赛/ccks2024复赛.json"
    # 读取JSONL格式的文件内容
    contents = read_jsonl(question_file_path)

    # 开始预测过程
    print("开始预测...")
    for content in contents:
        # 提取实体属性
        messages, tools = extract_entity_attributes(content)
        # 应用聊天模板并获取响应
        response = qwen_model.apply_chat_template(messages, tools)
        # 将响应转换为字典格式
        dic_con = str_dict(response)
        # 如果转换失败，则尝试重新获取响应
        if dic_con == None:
            for i in range(3):
                response = qwen_model.apply_chat_template(messages, tools)
                dic_con = str_dict(response)
                if dic_con != None:
                    break
        else:
            # 获取参数
            arguments = dic_con['arguments']
            # 获取实体类型和实体名称
            entity_type = list(arguments.keys())[0]
            # 如果实体名称为空，则尝试重新获取响应
            if arguments[entity_type] == '':
                for i in range(3):
                    response = qwen_model.apply_chat_template(messages, tools)
                    dic_con = str_dict(response)
                    arguments = dic_con['arguments']
                    # 获取实体类型和实体名称
                    entity_type = list(arguments.keys())[0]
                    # 如果实体名称不为空，则停止尝试
                    if arguments[entity_type] != '':
                        break

        # 打印结果
        print(dic_con)
        # 将结果保存到文件中
        with open("./data/model_res_12.11.json", 'a+',encoding='utf-8') as f:
            json.dump(dic_con, f, ensure_ascii=False)
            f.write('\n')

