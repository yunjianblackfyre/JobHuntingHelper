# -*- coding:utf-8 -*-

from ResumeAutometa.Foundations.utils import *
from selenium import webdriver
from ResumeAutometa.BrowserAutoMeta.foundations.human_actions import HumanActions
from ResumeAutometa.Config.file_paths import CHROME_WEBDRIVER_PATH
from ResumeAutometa.Config.login_profile import TENCENT_LOGIN


class ZhilianAutoMeta(object):

    def __init__(self):
        self.login_info = TENCENT_LOGIN
        self.main_page_title = ""
        self.action_handler = HumanActions()
        self.driver_handler = None

    def auto_meta_on(self):
        self.driver_handler = webdriver.Chrome(CHROME_WEBDRIVER_PATH)

    def front_page(self):
        self.action_handler.to_website(self.driver_handler, "https://sou.zhaopin.com")

        self.action_handler.set_combo_box(self.driver_handler,
                                          ["#queryTitleUls > li.currentCity.query-city__uls__li.current-city",
                                           "#queryCityBox > div > ul > li:nth-child(2)"])

        self.action_handler.element_click(self.driver_handler,
                                          "div.query-search__border__content > div > ul > li:nth-child(3) > div > a")

        self.action_handler.element_click(self.driver_handler,
                                          "div.query-search__border__content > div > ul > li:nth-child(4) > a")

        self.action_handler.input_click(self.driver_handler, "div.fl.sf-search-box.zp-searchs__sf > div > div > input", "前端")

        # self.father_page_name = self.driver_handler.title

    def search_result_page(self):
        father_page_name = self.driver_handler.title
        elements = self.driver_handler.find_elements_by_css_selector(
            "#listContent > div > div > div > div.itemBox.nameBox > div.jobName")

        for element in elements:
            # 跳转至子页面，分析招聘信息
            element.click()
            time.sleep(1)
            self.action_handler.to_child_page(self.driver_handler, father_page_name)

            self.detail_page()

            self.action_handler.to_father_page(self.driver_handler, father_page_name)

    def detail_page(self):
        scraped_text = self.action_handler.text_scrap(self.driver_handler, "div.responsibility.pos-common > div.pos-ul")
        print(scraped_text)

    def start(self):
        self.front_page()

        pagination_count = 0
        pagination_thresh = 9
        while pagination_count < pagination_thresh:
            self.search_result_page()
            pagination_count += 1
            self.action_handler.element_click(self.driver_handler, "#pagination_content > div > button:nth-last-child(2)")

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
    task_executor = ZhilianAutoMeta()
    task_executor.run()