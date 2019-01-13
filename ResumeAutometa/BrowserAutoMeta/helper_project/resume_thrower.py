# -*- coding:utf-8 -*-
#   AUTHOR: Sibyl System
#     DATE: 2018-04-24
#     DESC: 浏览器投递简历

import traceback
from ResumeAutometa.Foundations.utils import *
from selenium import webdriver
from ResumeAutometa.UserInterface.utils import get_chrome_path
from ResumeAutometa.BrowserAutoMeta.foundations.human_actions import HumanActions
from ResumeAutometa.Config.file_paths import CHROME_WEBDRIVER_PATH_FILE


class ResumeThrower(object):

    def __init__(self, mission, orig_settings, switchboard):
        self.mission = mission
        self.orig_settings = orig_settings
        self.switchboard = switchboard
        self.main_page_title = ""
        self.action_handler = HumanActions()
        self.driver_handler = None

    def auto_meta_on(self):
        chrome_webdriver_path = get_chrome_path(CHROME_WEBDRIVER_PATH_FILE)
        self.driver_handler = webdriver.Chrome(chrome_webdriver_path)

    def deal_meta_action(self, actions):
        for action in actions:
            action_name = action["action"]
            arg = action["arg"]
            action_method = getattr(self.action_handler, action_name)
            action_method(self.driver_handler, arg)

    def throw_resume(self, job_info):
        try:
            job_name = job_info[0]
            job_url = job_info[1]
            job_source = job_info[2]

            self.action_handler.to_website(self.driver_handler, job_url)
            action_sequence = self.orig_settings[job_source]["投简历"]
            self.deal_meta_action(action_sequence)
            detail_msg = {
                "url": job_url
            }
            msg = ("progress", "小助手：您要申请的职位：" + job_name + "投递成功了！", detail_msg)
        except:
            print(traceback.format_exc())
            msg = ("progress", "小助手：简历投递失败了，555~")
        return msg

    def login_wait(self):
        self.switchboard["confirm_permission"] = True
        self.switchboard["wait_login"] = True

        while self.switchboard["wait_login"]:
            time.sleep(0.5)

    def run(self):
        try:
            self.auto_meta_on()
            for job_source, login_url in self.mission["login_info"].items():
                self.action_handler.to_website(self.driver_handler, login_url)
                yield ("info", "小助手：麻烦主人登陆一下" + job_source + "嘛")
                self.login_wait()

            for job_info in self.mission["mission_detail"]:
                yield self.throw_resume(job_info)
            yield ("info", "小助手：简历全部投递成功！")
        except Exception as e:
            yield ("info", "小助手：职位投递出错了......请确保浏览器运行期间不要操作或关闭浏览器哦~")

        # 尝试关闭浏览器
        try:
            self.action_handler.close_browser(self.driver_handler)
        except:
            pass


if __name__ == '__main__':
    mission = {
        "智联招聘": [
          "https://jobs.zhaopin.com/134220573253568.htm"
        ],
        "前程无忧": [
          "https://jobs.51job.com/hangzhou-bjq/106725054.html?s=01&t=0"
        ]
    }
    task_executor = ResumeThrower(mission, orig_settings=dict(), switchboard=dict())
    for msg in task_executor.run():
        print(msg)