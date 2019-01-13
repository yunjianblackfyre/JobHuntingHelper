# -*- coding:utf-8 -*-
#   AUTHOR: Sibyl System
#     DATE: 2018-04-24
#     DESC: 浏览器模拟人类行为合集

from ResumeAutometa.UserInterface.utils import sleep_random
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from ResumeAutometa.Foundations.utils import is_xpath

time_floor = 0.5

time_ceiling = 1.5


class HumanActions(object):

    # 完全关闭浏览器
    @staticmethod
    def close_browser(auto_meta):
        if auto_meta is not None:
            nums = len(auto_meta.window_handles)
            for idx in range(nums):
                this_window = auto_meta.window_handles[0]
                auto_meta.switch_to.window(this_window)
                auto_meta.close()

    # 输入文本后点击按钮
    @staticmethod
    def input_click(auto_meta, location, input_str, extra_time=0):
        search_slot = auto_meta.find_element_by_css_selector(location)
        search_slot.send_keys(input_str)
        search_slot.send_keys(Keys.RETURN)
        sleep_random(time_floor + extra_time, time_ceiling + extra_time)

    # 输入文本
    @staticmethod
    def input_string(auto_meta, location, input_str, extra_time=0):
        search_slot = auto_meta.find_element_by_css_selector(location)
        search_slot.send_keys(input_str)
        sleep_random(time_floor + extra_time, time_ceiling + extra_time)

    # 点击元素
    @staticmethod
    def element_click(auto_meta, location, extra_time=0):
        if is_xpath(location):
            element = auto_meta.find_element_by_xpath(location)
        else:
            element = auto_meta.find_element_by_css_selector(location)
        element.click()
        sleep_random(time_floor+extra_time, time_ceiling+extra_time)  # 等待按键结果的反应

    @staticmethod
    def text_scrap(auto_meta, location):
        text_element = auto_meta.find_element_by_css_selector(location)
        return text_element.text

    # 返回父级页面
    @staticmethod
    def to_father_page(auto_meta, father_page_url):
        switch_result = False
        if father_page_url != auto_meta.current_url:
            auto_meta.close()
            windows = auto_meta.window_handles
            nums = len(windows)
            for idx in range(nums):
                auto_meta.switch_to.window(windows[idx])
                if father_page_url == auto_meta.current_url:
                    switch_result = True
                    break
        return switch_result

    # 跳转子级页面
    @staticmethod
    def to_child_page(auto_meta, father_page_url):
        switch_result = False
        if father_page_url == auto_meta.current_url:
            nums = len(auto_meta.window_handles)
            windows = auto_meta.window_handles
            for idx in range(nums):
                auto_meta.switch_to.window(windows[idx])
                if father_page_url != auto_meta.current_url:
                    switch_result = True
                    break
        return switch_result

    # 滚动到此元素
    @staticmethod
    def move_to_element(auto_meta, element):
        current_window_shape = auto_meta.get_window_size(auto_meta.current_window_handle)
        current_window_height = current_window_shape["height"]
        view_offset = current_window_height//2
        element_height = element.location["y"]-view_offset
        script = "window.scrollTo(0," + str(element_height) + ")"
        auto_meta.execute_script(script)
        sleep_random(time_floor, time_ceiling)

    # 快捷键点开一个新CHROME窗口
    @staticmethod
    def click_new_tab(auto_meta, element, extra_time=0):
        ActionChains(auto_meta).key_down(Keys.CONTROL).click(element) \
            .key_up(Keys.CONTROL).perform()
        sleep_random(time_floor + extra_time, time_ceiling + extra_time)

    # 跳转至某个网页
    @staticmethod
    def to_website(auto_meta, url, extra_time=0):
        auto_meta.get(url)
        sleep_random(time_floor+extra_time, time_ceiling+extra_time)
