# -*- coding:utf-8 -*-
from ResumeAutometa.Foundations.utils import *
from selenium import webdriver
from ResumeAutometa.UserInterface.utils import get_chrome_path
from ResumeAutometa.BrowserAutoMeta.foundations.human_actions import HumanActions
from ResumeAutometa.Config.file_paths import CHROME_WEBDRIVER_PATH_FILE


DYNAMIC_SETTINGS = {
    "搜索选项": [
        ["搜索页地址", ""],
        ["工作地点", "深圳"],
        ["工作类型", "技术"],
        ["搜索关键词", "前端"]
    ],
    "翻页次数": 4
}


class JobScraper(object):

    def __init__(self, mission_name, static_settings, dynamic_sequence):
        self.main_page_title = ""
        self.static_settings = static_settings
        self.dynamic_sequence = dynamic_sequence
        self.mission_name = mission_name
        self.bucket = []
        self.action_handler = HumanActions()
        self.driver_handler = None

    def auto_meta_on(self):
        chrome_webdriver_path = get_chrome_path(CHROME_WEBDRIVER_PATH_FILE)
        self.driver_handler = webdriver.Chrome(executable_path=chrome_webdriver_path)

    def deal_meta_action(self, dyn_choice, actions):
        for action in actions:
            action_name = action["action"]
            arg = action["arg"]
            action_method = getattr(self.action_handler, action_name)

            if action_name in ["input_click", "input_string"]:
                action_method(self.driver_handler, arg, dyn_choice, extra_time=2)
            elif isinstance(arg, str):
                action_method(self.driver_handler, arg, extra_time=2)
            elif isinstance(arg, dict):
                real_css_path = arg[dyn_choice]
                action_method(self.driver_handler, real_css_path, extra_time=2)

    def search_settings(self):
        # 初始化设定
        stat_search_settings = self.static_settings["搜索选项"]
        dyn_search_sequence = self.dynamic_sequence["搜索选项"]

        # 达到搜索页
        for sequence in dyn_search_sequence:
            meta_action_name = sequence[0]
            dyn_choice = sequence[1]
            actions = stat_search_settings[meta_action_name]
            self.deal_meta_action(dyn_choice, actions)

    def job_looking(self):
        stat_scrap_settings = self.static_settings["抓取内容"]
        father_page_url = self.driver_handler.current_url
        elements = self.driver_handler.find_elements_by_css_selector(
            stat_scrap_settings["table_path"])

        for element in elements:
            try:
                # 跳转至子页面，分析招聘信息
                self.action_handler.move_to_element(self.driver_handler, element)
                self.action_handler.click_new_tab(self.driver_handler, element)
                self.action_handler.to_child_page(self.driver_handler, father_page_url)

                try:
                    scraped_item = self.detail_page(item_fields=stat_scrap_settings["item_fields"])
                
                    if scraped_item.get("职位名称"):
                        self.bucket.append(scraped_item)
                        yield ("info", "小助手：发现职位：%s" % scraped_item["职位名称"])
                except Exception as e:
                    # yield ("info", "小助手：职位爬取失败了 555... %s" % str(e))
                    yield ("info", "小助手：职位爬取失败了 555...")

                self.action_handler.to_father_page(self.driver_handler, father_page_url)
            except Exception as e:
                # import traceback
                # print(traceback.format_exc())
                yield ("info", "小助手：职位爬取失败了 555...")

    def detail_page(self, item_fields):
        item = dict()
        item["职位唯一标识"] = self.driver_handler.current_url
        item["职位来源"] = self.mission_name
        item["是否投递"] = False
        for key, value in item_fields.items():
            item[key] = self.action_handler.text_scrap(self.driver_handler, value)
        return item

    def to_next_page(self):
        stat_pagination_settings = self.static_settings["翻页按钮"]
        self.action_handler.element_click(self.driver_handler,
                                          stat_pagination_settings["pagination_path"], extra_time=2)

    def get_eggs(self):
        eggs = self.bucket
        return eggs

    def run(self):
        try:
            self.auto_meta_on()
            self.search_settings()

            pagination_count = 0
            pagination_thresh = self.dynamic_sequence["翻页次数"]
            while pagination_count < pagination_thresh:
                for msg in self.job_looking():
                    yield msg
                pagination_count += 1
                self.to_next_page()

            yield ("info", "小助手：职位全部抓取成功！")
        except Exception as e:
            # import traceback
            # print(traceback.format_exc())
            # yield ("info", "小助手：职位爬取出现错误了 555... %s" % str(traceback.format_exc()))
            yield ("info", "小助手：职位抓取出错了......请确保浏览器运行期间不要操作或关闭浏览器哦~")

        # 尝试关闭浏览器
        try:
            self.action_handler.close_browser(self.driver_handler)
        except:
            pass


if __name__ == '__main__':
    chrome_webdriver_path = get_chrome_path(CHROME_WEBDRIVER_PATH_FILE)
    driver_handler = webdriver.Chrome(executable_path=chrome_webdriver_path)
    driver_handler.get("https://www.lagou.com/")
    time.sleep(2)
    element = driver_handler.find_element_by_css_selector("#changeCityBox > p.checkTips > a")
    element.click()
