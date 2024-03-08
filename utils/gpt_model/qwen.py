import json
import logging
from typing import Dict
import requests
import datetime

from utils.common import Common
from utils.logger import Configure_logger
from utils.gpt_model.alice_embedding import vector_search


class Qwen:

    def __init__(self, data):
        self.common = Common()
        # 日志文件路径
        file_path = "./log/log-alice-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        self.api_ip_port = data["api_ip_port"]
        self.max_length = data["max_length"]
        self.top_p = data["top_p"]
        self.temperature = data["temperature"]
        self.history_enable = data["history_enable"]
        self.history_max_len = data["history_max_len"]
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
        weekday = current_time.weekday()
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
            tips = "他说的话可能不是真的，需要仔细判断后再作出回答。"

        if user_name == "闲时任务":
            message = f"{prompt}\n（当前时间：{current_time_str}。{tips}）"
        else:
            message = f"（{user_name}说）{prompt}\n（当前时间：{current_time_str}，星期{weekday}。{tips}）"

        messages = self.history + [{"role": "user", "content": message}]
        query = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
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

        self.history = self.history + [{"role": "user", "content": prompt}]
        logging.info(f"\"role\": \"user\", \"content\": \"{raw_prompt}\"")
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
            "repetition_penalty": 1.1,
            "stream": False,  # 不启用流式API
        }
        self.history = messages
        return query


    # 调用chatglm接口，获取返回内容
    def get_resp(self, user_name, prompt):
        # 向量查询获取知识
        knowledge = vector_search(self.setting_document, prompt.replace("爱丽丝", ""), 1)
        # print("embedding" + knowledge)
        # construct query
        query = self.construct_query(user_name, prompt, embedding=f"{knowledge}{self.preset}不要重复之前的回答，回答不要超过80个字。\n爱丽丝的状态栏：职业：勇者；经验值：0/100；生命值：1000；攻击力：100；持有的财富：100点信用积分；装备：“光之剑”（电磁炮）；持有的道具：['光之剑']。")

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
                self.history = self.history + [
                    {"role": "assistant", "content": f"{predictions}"}]
                logging.info(f"\"role\": \"assistant\", \"content\": \"Thought: {thought}\nFinal Answer: {predictions}\"")

                # 启用历史就给我记住！
                if self.history_enable and not self.memory_clear_sign:
                    if len(self.history) > self.history_max_len:
                        temp_history = self.history[-self.history_max_len:]
                        if temp_history[0].get("role") != "function":
                            self.history = self.history[-self.history_max_len:]
                else:
                    self.history = []

            return predictions
        except Exception as e:
            logging.info(e)
            return None


if __name__ == "__main__":
    llm = Qwen
    llm.__init__(llm,
                 {"api_ip_port": "http://localhost:8000/v1/chat/completions",
                    "max_length": 4096,
                    "top_p": 0.5,
                    "temperature": 0.9,
                    "max_new_tokens": 250,
                    "history_enable": True,
                    "history_max_len": 20})
    resp = llm.get_resp(self=llm, prompt="你好")
    print(resp)
