import re
import pyautogui

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