import requests
import random
import json
from hashlib import md5
import traceback
import logging

from .common import Common
from .logger import Configure_logger
from .config import Config


class My_Translate:
    def __init__(self, config_path):
        self.config = Config(config_path)
        self.common = Common()

        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        self.baidu_config = self.config.get("translate", "baidu")


    # 重载config
    def reload_config(self, config_path):
        self.config = Config(config_path)

        
    def baidu_trans(self, text):
        """百度翻译

        Args:
            text (str): 待翻译的文本

        Return:
            (str)：翻译后的文本
        """

        # Set your own appid/appkey.
        appid = self.baidu_config["appid"]
        appkey = self.baidu_config["appkey"]

        captions_config = self.config.get("captions")

        # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
        from_lang = self.baidu_config["from_lang"]
        to_lang =  self.baidu_config["to_lang"]

        endpoint = 'http://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        url = endpoint + path

        # Generate salt and sign
        def make_md5(s, encoding='utf-8'):
            return md5(s.encode(encoding)).hexdigest()

        salt = random.randint(32768, 65536)
        sign = make_md5(appid + text + str(salt) + appkey)

        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': text, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

        try:
            # Send request
            r = requests.post(url, params=payload, headers=headers)
            result = r.json()

            logging.info(f"百度翻译结果={result}")
            translation = result["trans_result"][0]["dst"]
            translation = translation.replace("先生", "せんせい")
            translation = translation.replace("パパパパ", "パンパカパーン")
            translation = translation.replace("ボンボン", "パンパカパーン")
            translation = translation.replace("カトパンカトパン", "パンパカパーン")
            translation = translation.replace("パンパカパーンカパン", "パンパカパーン")
            translation = translation.replace("RPG", "アールピージー")
            translation = translation.replace("HP", "エイチピー")
            translation = translation.replace("桃井さん", "モモイ")
            translation = translation.replace("桃ちゃん", "モモイ")
            translation = translation.replace("緑ちゃん", "ミドリ")
            translation = translation.replace("緑さん", "ミドリ")
            translation = translation.replace("みどりちゃん", "ミドリ")
            translation = translation.replace("ゆずさん", "ユズ")
            translation = translation.replace("優香さん", "ユウカ")
            translation = translation.replace("優香", "ユウカ")
            translation = translation.replace("孥", "ヌ")
            translation = translation.replace("日鞠", "ヒマリ")
            translation = translation.replace("日奈", "ヒナ")
            translation = translation.replace("Kei", "ケイ")
            translation = translation.replace("真理部", "ヴェリタス")

            return translation
            # Show response
            # print(json.dumps(result, indent=4, ensure_ascii=False))
        except Exception as e:
            logging.error(traceback.format_exc())

            return None
