# -*- coding:utf-8 -*-

from ResumeAutometa.Foundations.utils import *
from selenium import webdriver
from ResumeAutometa.BrowserAutoMeta.foundations.human_actions import HumanActions
from ResumeAutometa.Config.file_paths import CHROME_WEBDRIVER_PATH
from ResumeAutometa.Config.login_profile import TENCENT_LOGIN


class TencentAutoMeta(object):

    def __init__(self):
        self.login_info = TENCENT_LOGIN
        self.main_page_title = ""
        self.action_handler = HumanActions()
        self.driver_handler = None

    def auto_meta_on(self):
        self.driver_handler = webdriver.Chrome(CHROME_WEBDRIVER_PATH)

    def front_page(self):
        self.action_handler.to_website(self.driver_handler, "https://hr.tencent.com/social.php")

        self.action_handler.set_combo_box(self.driver_handler,
                                          ["#socia_search > div:nth-child(1) > div.show",
                                           "#socia_search > div:nth-child(1) > div.options > div:nth-child(2)"])

        self.action_handler.set_combo_box(self.driver_handler,
                                          ["#socia_search > div.select.ml9 > div.show",
                                           "#socia_search > div.select.ml9 > div.options > div:nth-child(2)"])

        self.action_handler.input_click(self.driver_handler, "#hsearch", "数据")

        # self.father_page_name = self.driver_handler.title

    def search_result_page(self):
        father_page_name = self.driver_handler.title
        elements = self.driver_handler.find_elements_by_css_selector(
            "#position > div.left.wcont_b.box > table > tbody > tr > td.l.square > a")

        for element in elements:
            # 跳转至子页面，分析招聘信息
            element.click()
            time.sleep(1)
            self.action_handler.to_child_page(self.driver_handler, father_page_name)

            self.detail_page()

            self.action_handler.to_father_page(self.driver_handler, father_page_name)

    def detail_page(self):
        self.action_handler.text_scrap(self.driver_handler, "#position_detail > div > table")

    def start(self):
        self.front_page()

        pagination_count = 0
        pagination_thresh = 9
        while pagination_count < pagination_thresh:
            self.search_result_page()
            pagination_count += 1
            self.action_handler.element_click(self.driver_handler, "#next")

    def run(self):
        try:
            self.auto_meta_on()
            self.start()
            time.sleep(5)   # 等待5秒后关闭整个浏览器
        except Exception as e:
            print(e)
        finally:
            self.action_handler.close_browser(self.driver_handler)


if __name__ == '__main__':
    task_executor = TencentAutoMeta()
    task_executor.run()