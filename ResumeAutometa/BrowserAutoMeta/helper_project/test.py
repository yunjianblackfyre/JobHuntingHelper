# -*- coding:utf-8 -*-
from ResumeAutometa.Foundations.utils import *
from selenium import webdriver
from ResumeAutometa.UserInterface.utils import get_chrome_path
from ResumeAutometa.Config.file_paths import CHROME_WEBDRIVER_PATH_FILE


if __name__ == '__main__':
    chrome_webdriver_path = get_chrome_path(CHROME_WEBDRIVER_PATH_FILE)
    driver_handler = webdriver.Chrome(executable_path=chrome_webdriver_path)

    # 打开百度
    print("正在打开百度......")
    driver_handler.get("https://www.baidu.com/")
    time.sleep(2)

    # 打开淘宝
    print("正在打开淘宝......")
    driver_handler.get("https://www.taobao.com/")
    time.sleep(2)

    # 打开京东
    print("正在打开京东......")
    driver_handler.get("https://www.jd.com/")
    time.sleep(2)

    # 打开腾讯视频
    print("正在打开腾讯视频......")
    driver_handler.get("https://v.qq.com/")
    time.sleep(5)

    driver_handler.close()