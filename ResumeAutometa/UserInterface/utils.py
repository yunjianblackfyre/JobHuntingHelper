#   AUTHOR: Sibyl System
#     DATE: 2019-01-13
#     DESC: 小助手专用基础方法、变量、类

import random
import time
from ResumeAutometa.Foundations.utils import read_lines
from PyQt4 import QtGui, QtCore

TUTORIAL_INFO = {

    "init": "您好，欢迎使用简历投递小助手！\n\
小助手可以帮助您在多个招聘网站自动投递，免除您海投的麻烦。\n\n\
* 首先，请点击【我要抓职位】按钮，随后点击【添加抓取任务】。\n\
* 您可以抓取多个招聘网站的职位，例如腾讯社招，前程无忧，智联招聘等。\n\
* 添加好任务后，您可以通过下拉窗口，文本输入框定制您的抓取任务。\n\
* 完成抓取任务的定制后，点击按钮【开始抓取】即可以启动浏览器开始抓取任务。\n\
* 浏览器可以代替您完成职位搜索页面的搜索词输入，条件过滤，翻页等动作。",

    "crawl": "浏览器已经运行起来了！在浏览器自动运行过程中，还请不要干扰浏览器工作哦。\n\
浏览器自动退出后，请点击【我要投简历】进入下一个环节。",

    "load": "如果浏览器完成了抓取任务，就让我们来看看抓取的职位吧！\n\
点击【读取职位】，应该能看到刚才抓取的职位了。\n\
来自各大招聘网站的职位都以统一的格式呈现在您面前了，这样才简单！",

    "browse": "每一个职位后面都有一个可选框哦，如果想要试一试，就点击选定吧！\n\
* 当然，若您觉得麻烦，您也可以点击【全选本页职位】批量选定。\n\
* 若您希望查看该职位的详情，请随便点击一个职位（哪都可以）就行了。\n\
* 选定好您想投递的职位后，别忘了点击【投递职位】通知浏览器为您自动投递哦！\n\n\
为了能缓解您浏览大量职位的麻烦，小助手准备了智能排序功能！\n\
* 请您将您的简历做成一个txt文件，并点击【读取简历】读取简历。\n\
* 勾选【智能职位排序】，小助手便可以将最适合您的职位往前排！",

    "throw": "浏览器已经开始准备为您投递简历了，还请麻烦您在小助手提示出现后，\n\
在浏览器上完成登陆操作（提示出现后，可以操作浏览器）。\n\
登陆完成后，请点击【登陆确认】。待所有招聘网站登陆成功后，浏览器就可以为您自动投递简历了！\n\
在投递过程中，还请不要干扰浏览器工作哦"

}


def read_json_list_safe(file_path):
    try:
        history = read_file_json(file_path)
        if not isinstance(history, list):
            return []
        for url in history:
            if not isinstance(url, str):
                return []
    except:
        return []


def sleep_random(upper, lower):
    second = random.uniform(upper, lower)
    time.sleep(second)


def get_chrome_path(file_path):
    lines = read_lines(file_path)
    return lines[0].strip()


def check_grand_setting(setting):
    def check_action(fine_grain_action):
        if set(fine_grain_action.keys()) != {"action", "arg"}:
            raise Exception
        action_value = fine_grain_action["action"]
        if action_value not in ["element_click", "to_website", "input_click"]:
            raise Exception
        if action_value != "element_click":
            allowed_args = [str]
        else:
            allowed_args = [str, dict]

        action_value = fine_grain_action["arg"]

        if type(action_value) not in allowed_args:
            print(type(action_value), action_value)
            raise Exception

        if isinstance(action_value, dict):
            for sel_key, sel_value in action_value.items():
                if not isinstance(sel_key, str):
                    raise Exception
                if not isinstance(sel_value, str):
                    raise Exception

    for site_name, site_detail in setting.items():
        if not isinstance(site_name, str):
            raise Exception
        if not isinstance(site_detail["登陆页面"], str):
            raise Exception

        for setting_name, search_setting in site_detail["搜索选项"].items():
            if setting_name not in ["搜索页地址", "工作地点", "工作经验", "工作类型", "搜索关键词"]:
                raise Exception

            for action in search_setting:
                check_action(action)

        if set(site_detail["抓取内容"].keys()) != {"table_path", "item_fields"}:
            raise Exception
        for text_key, text_value in site_detail["抓取内容"].items():
            if text_key == "table_path":
                if not isinstance(text_value, str):
                    raise Exception
            if text_key == "item_fields":
                if set(text_value.keys()) != {"职位名称", "职位描述"}:
                    raise Exception
                for text_detail_value in text_value.values():
                    if not isinstance(text_detail_value, str):
                        raise Exception

        if not isinstance(site_detail["翻页按钮"]["pagination_path"], str):
            raise Exception


class QuickInterface(object):
    def __init__(self):
        pass

    @classmethod
    def gen_main_button(cls, label):
        button = QtGui.QPushButton()
        button.setStyleSheet('QPushButton{'
                               'background-color:#C2C7CB;'
                               'selection-color:black;'
                               'color:black;'
                               'font:bold large "Times New Roman"}')
        button.setText(label)
        return button

    @classmethod
    def gen_default_button(cls, label):
        button = QtGui.QPushButton()
        button.setStyleSheet('QPushButton{'
                               'background-color:#C2C7CB;'
                               'selection-color:black;'
                               'color:black;}')
        button.setText(label)
        return button

    @classmethod
    def gen_red_label(cls, text):
        label = QtGui.QLabel(text)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.red)
        label.setPalette(palette)
        return label


if __name__ == '__main__':
    from ResumeAutometa.Foundations.utils import read_file_json
    from ResumeAutometa.Config.file_paths import WEB_DRIVER_ACTION_SETTINGS
    grand_settings = read_file_json(WEB_DRIVER_ACTION_SETTINGS)
    check_grand_setting(grand_settings)
