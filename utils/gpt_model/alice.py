import json
import logging
from random import random
from typing import Dict
import requests
import re
import datetime
import pyautogui

from utils.common import Common
from utils.logger import Configure_logger
from utils.gpt_model.alice_embedding import vector_search

tools = [
    {
                'name_for_human': '光之剑',
                'name_for_model': 'sword_of_light',
                'description_for_model': '光之剑是爱丽丝的武器，可以用光之剑发射电磁炮攻击敌人，当遭遇敌人时使用。',
                'parameters': [
                    {
                        'name': 'target',
                        'description': '攻击目标的名字',
                        'required': True,
                        'schema': {'type': 'string'},
                    }
                ],
            },
            {
                'name_for_human': '移动到其他地点',
                'name_for_model': 'move',
                'description_for_model': '离开当前场景，去往其他地点。',
                'parameters': [
                    {
                        'name': 'to',
                        'description': '接下来要前往的场景或地点的名称',
                        'required': False,
                        'schema': {'type': 'string'},
                    }
                ],
            },
]


def remove_emotion(message: str, emoji: bool) -> str:
    """
    去除描述表情的部分（如【开心】，要求AI输出格式固定）
    """
    pattern = r'\【[^\】^\]]*[\]\】]'
    match = re.findall(pattern, message)
    if not len(match) == 0:
        print(match)
        print(f"emotion:{match[0]}")
        # 表情转动作（通过AutoHotKey读取键盘操作）
        if emoji:
            emojis = {
                "【认真】": "num1",
                "【坚定】": "num1",
                "【承诺】": "num1",
                "【生气】": "num1",
                "【烦恼】": "num1",
                "【诚实】": "substract",
                "【期待】": "num8",
                "【回答】": "substract",
                "【回忆】": "num5",
                "【发愣】": "substract",
                "【察觉】": "substract",
                "【建议】": "num8",
                "【好奇】": "substract",
                "【自信】": "add",
                "【自豪】": "add",
                "【解释】": "num8",
                "【失望】": "num3",
                "【委屈】": "num3",
                "【伤心】": "num3",
                "【高兴】": "num8",
                "【开心】": "num4",
                "【欢迎】": "num8",
                "【崇拜】": "num8",
                "【愉快】": "num8",
                "【贴心】": "num8",
                "【赞同】": "num8",
                "【邀请】": "num8",
                "【兴奋】": "num4",
                "【快乐】": "num4",
                "【为难】": "num3",
                "【紧张】": "num3",
                "【困惑】": "del",
                "【困扰】": "del",
                "【疑惑】": "del",
                "【害怕】": "num3",
                "【平和】": "num0",
                "【无聊】": "num0",
                "【慌张】": "num3",
                "【害羞】": "num3",
                "【羞涩】": "num3",
                "【微笑】": "numpadadd",
                "【惊喜】": "num8",
                "【理解】": "num8",
                "【喜悦】": "num8",
                "【流汗】": "num3",
                "【犹豫】": "num3",
                "【震惊】": "multiply",
                "【惊讶】": "multiply",
                "【思考】": "num5",
                "【沉思】": "num5",
                "【否认】": "num5",
                "【睡觉】": "num5",
                "【熟睡】": "num5",
                "【困倦】": "num5",
                "【陈述】": "num0",
                "【祈祷】": "num5",
                "【拒绝】": "num1",
                "【感动】": "add",
                "【感激】": "add",
                "【道歉】": "num3",
            }
            if emojis.get(match[0]) is not None:
                pyautogui.press(emojis.get(match[0]))
            else:
                pyautogui.press("num0")
        return message.replace(match[0], "")
    else:
        return message


def remove_action(line: str) -> str:
    """
    去除括号里描述动作的部分（要求AI输出格式固定）
    :param line:
    :return:
    """
    line = line.replace("(", "（")
    line = line.replace(")", "）")
    pattern = r'\（[^\（^\）]*\）'
    match = re.findall(pattern, line)
    if len(match) == 0:
        return line
    else:
        print(f"有{len(match)+1}段描述动作的语句")
        for i in range(len(match)):
            print(match[i])
            line = line.replace(match[i], "")
        return line


class Qwen_alice:

    def __init__(self, data):
        self.common = Common()
        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        self.api_ip_port = data["api_ip_port"]
        self.max_length = data["max_length"]
        self.top_p = data["top_p"]
        self.temperature = data["temperature"]
        self.history_enable = data["history_enable"]
        self.history_max_len = data["history_max_len"]
        self.functions = tools
        self.preset = data["preset"]
        self.history = []
        self.setting_document = data["setting_document"]
        self.memory_clear_sign = False
        self.emoji_enable = data["autohotkey_enable"]


    def construct_query(self, user_name, prompt: str, **kwargs) -> Dict:
        """构造请求体
        """
        embedding = ""
        for key, value in kwargs.items():
            if key == "embedding":
                embedding = value
        # 获取当前时间
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        if prompt == "/记忆清除术" and user_name == "悪魔sama":
            self.memory_clear_sign = True
        else:
            self.memory_clear_sign = False
        # 获取说话人
        if user_name == "悪魔sama":
            user_name = "老师"
            tips = ""
        elif user_name == "闲时任务":
            tips = ""
        else:
            user_name = "名为“" + user_name + "”的观众"
            tips = ""
        if user_name == "闲时任务":
            self.common.write_content_to_file("log/回复对象.txt", f"{prompt}", write_log=False)
        else:
            self.common.write_content_to_file("log/回复对象.txt", f"{user_name}说：{prompt}", write_log=False)
        if user_name == "闲时任务":
            message = f"{prompt}\n（当前时间：{current_time_str}。{tips}）"
        else:
            message = f"（{user_name}说）{prompt}\n（当前时间：{current_time_str}。{tips}）"

        messages = self.history + [{"role": "user", "content": message}]
        query = {
            "functions": self.functions,
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "embeddings": embedding,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stream": False,  # 不启用流式API
        }
        # 查找提示信息的位置，不加入历史
        tip_p = message.rfind("\n（当前时间：")
        if tip_p >= 0:
            raw_prompt = message[:tip_p]
        else:
            raw_prompt = message

        self.history = self.history + [{"role": "user", "content": raw_prompt}]
        return query


    def construct_observation(self, prompt: str, **kwargs) -> Dict:
        """构造请求体
        """
        embedding = ""
        for key, value in kwargs.items():
            if key == "embedding":
                embedding = value
        messages = self.history + [{"role": "function", "content": prompt}]
        query = {
            "functions": self.functions,
            "system": self.system,
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stream": False,  # 不启用流式API
        }
        self.history = messages
        return query


    # 调用chatglm接口，获取返回内容
    def get_resp(self, user_name, prompt):
        # 向量查询获取知识
        knowledge = vector_search(self.setting_document, prompt, 1)
        # print("embedding" + knowledge)
        # construct query
        query = self.construct_query(user_name, prompt, embedding=f"{knowledge}{self.preset}不要重复之前的回答，回答不要超过150个字。\n爱丽丝的状态栏：职业：勇者；经验值：0/100；生命值：1000；攻击力：100；持有的财富：100点信用积分；装备：“光之剑”（电磁炮）；持有的道具：['光之剑']。")

        try:
            response = requests.post(url=self.api_ip_port, json=query)
            response.raise_for_status()  # 检查响应的状态码

            result = response.content
            ret = json.loads(result)
            predictions = "..."

            logging.debug(ret)
            finish_reason = ret['choices'][0]['finish_reason']
            if finish_reason != "":
                predictions = ret['choices'][0]['message']['content'].strip()
                thought = ret['choices'][0]['thought'].strip()
                self.history = self.history + [
                    {"role": "assistant", "content": f"Thought: {thought}\nFinal Answer: {predictions}"}]

                # 启用历史就给我记住！
                if self.history_enable and not self.memory_clear_sign:
                    if len(self.history) > self.history_max_len:
                        temp_history = self.history[-self.history_max_len:]
                        if temp_history[0].get("role") != "function":
                            self.history = self.history[-self.history_max_len:]
                else:
                    self.history = []

            return remove_action(remove_emotion(predictions, self.emoji_enable))
        except Exception as e:
            logging.info(e)
            return None


if __name__ == "__main__":
    llm = Qwen_alice
    llm.__init__(llm,
                 {"api_ip_port": "http://localhost:8000/v1/chat/completions",
                    "max_length": 4096,
                    "top_p": 0.5,
                    "temperature": 0.9,
                    "max_new_tokens": 250,
                    "history_enable": True,
                    "history_max_len": 20})
    resp = llm.get_resp(self=llm, prompt="（老师说）邦邦咔邦")
    print(resp)
