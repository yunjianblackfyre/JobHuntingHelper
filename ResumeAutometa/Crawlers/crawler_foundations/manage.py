# -*- coding:utf-8 -*-
#   AUTHOR: Sibyl System
#     DATE: 2018-01-02
#     DESC: 爬虫调度器，伪装成人类访问

import time
import traceback
from subprocess import Popen  # PIPE
from datetime import datetime, timedelta
from random import randint
from ResumeAutometa.LogHandle.Log import Log
from ResumeAutometa.Config.executable_paths import SPIDER_SHELL
from ResumeAutometa.Crawlers.zhilian_project.zhilian_spider import city_id_list, job_type_list
from ResumeAutometa.Crawlers.tencent_project.tencent_spider import LID_LIST, TID_LIST

MISSION_CHOPS = 5

TASK_NAMES = [
    "zhilian_task",
    "tencent_task"
]

DETAIL_NAMES = [
    "zhilian_detail",
    "tencent_detail"
]


def gen_human_work_time():
    time_now = datetime.now()
    # time_now = datetime(year=2018, month=9, day=1, hour=11, minute=00, second=20)
    if time_now.hour < 9:
        time_then = time_now.replace(hour=9, minute=randint(0, 30))
        return (time_then - time_now).seconds
    elif 9 <= time_now.hour < 14:
        time_then = time_now.replace(hour=14, minute=randint(0, 30))
        return (time_then - time_now).seconds
    elif 14 <= time_now.hour < 19:
        time_then = time_now.replace(hour=19, minute=randint(0, 30))
        return (time_then - time_now).seconds
    else:
        time_then = time_now.replace(hour=9, minute=randint(0, 30))
        time_then = time_then + timedelta(hours=23, minutes=59, seconds=59)
        return (time_then - time_now).seconds


def wait_process2stop(processes):
    process_num = len(processes)
    while process_num > 0:
        for proc in processes:
            if proc.poll() is not None:
                proc.wait()
                process_num -= 1
            else:
                time.sleep(0.5)


class CMissAdler(object):

    def __init__(self, is_task=True):
        self.task_intervals = dict()
        self.prepare_intervals()
        manager_name = "task" if is_task else "detail"
        self.log_handler = Log("%s_manager" % manager_name, "crawler")

    def prepare_intervals(self):
        for task_name in TASK_NAMES:
            self.task_intervals[task_name] = self.get_task_interval(task_name)

    @staticmethod
    def get_task_interval(name):
        if name == "zhilian_task":
            task_length = len(city_id_list)*len(job_type_list)
        elif name == "tencent_task":
            task_length = len(TID_LIST)*len(LID_LIST)
        else:
            task_length = 0
        step = task_length//MISSION_CHOPS + 1
        begin = 0
        end = step
        return begin, end, step, task_length

    def run_task(self):
        job_info_dict = dict()
        for task_name in TASK_NAMES:
            begin, end, step, task_length = self.task_intervals[task_name]
            job_info_dict[task_name] = {
                "job_category": "task",
                "job_task_begin": begin,
                "job_task_end": end,
                "job_task_step": step,
                "job_task_length": task_length
            }

        # 闹铃响了，先让我睡会儿
        sleep_time = gen_human_work_time()
        self.log_handler.log.info("Let me sleep for a while, wake me up after %s hours" % str(sleep_time / 3600.0))
        time.sleep(sleep_time)

        self.log_handler.log.info("All task crawlers begin")
        while True:
            finished_task = []
            running_task = []
            for job_name, job_info in job_info_dict.items():
                try:
                    interval = (job_info["job_task_begin"], job_info["job_task_end"])
                    p = Popen(["python3", SPIDER_SHELL, job_name, str(interval[0]), str(interval[1])])
                    running_task.append(p)
                    self.log_handler.log.info("Crawler %s with interval %s started" % (job_name, str(interval)))
                    job_info["job_task_begin"] += job_info["job_task_step"]
                    job_info["job_task_end"] += job_info["job_task_step"]
                    if job_info["job_task_begin"] > job_info["job_task_length"]:
                        finished_task.append(job_name)
                except:
                    err_msg = str(traceback.format_exc())
                    self.log_handler.log.info("signal task critical error")
                    self.log_handler.log.info(err_msg)

            self.log_handler.log.info("Waiting for crawlers to stop")
            wait_process2stop(running_task)
            self.log_handler.log.info("All crawlers stopped")
            # 若所有task_spider运行完毕，则
            for task_name in finished_task:
                job_info_dict.pop(task_name)
                self.log_handler.log.info("Crawler %s is totally finished" % task_name)
            if not job_info_dict.keys():
                self.log_handler.log.info("All task crawlers finished")
                break

            sleep_time = gen_human_work_time()
            self.log_handler.log.info("Assume crawlers stopped. wake crawler after %s hours" % str(sleep_time / 3600.0))
            time.sleep(sleep_time)

    def run_detail(self):
        job_info_dict = dict()

        for detail_name in DETAIL_NAMES:
            job_info_dict[detail_name] = {
                "job_category": "detail",
                "job_run_time": 0
            }

        # 闹铃响了，先让我睡会儿
        sleep_time = gen_human_work_time()
        self.log_handler.log.info("Let me sleep for a while, wake me up after %s hours" % str(sleep_time / 3600.0))
        time.sleep(sleep_time)

        self.log_handler.log.info("All detail crawlers begin")
        while True:
            finished_detail = []
            running_task = []
            for job_name, job_info in job_info_dict.items():
                try:
                    p = Popen(["python3", SPIDER_SHELL, job_name])  # stdout=PIPE, stderr=PIPE
                    running_task.append(p)
                    self.log_handler.log.info("Crawler %s started" % job_name)
                    job_info["job_run_time"] += 1
                    if job_info["job_run_time"] > 9:
                        finished_detail.append(job_name)
                except:
                    err_msg = str(traceback.format_exc())
                    self.log_handler.log.info("signal task critical error")
                    self.log_handler.log.info(err_msg)

            # 若所有detail_spider运行完毕，则
            self.log_handler.log.info("Waiting for crawlers to stop")
            wait_process2stop(running_task)
            self.log_handler.log.info("All crawlers stopped")

            for detail_name in finished_detail:
                job_info_dict.pop(detail_name)
                self.log_handler.log.info("Crawler %s is totally finished" % detail_name)
            if not job_info_dict.keys():
                self.log_handler.log.info("All detail crawlers finished")
                break

            sleep_time = gen_human_work_time()
            self.log_handler.log.info("Assume crawlers stopped. wake crawler after %s hours" % str(sleep_time / 3600.0))
            time.sleep(sleep_time)


if __name__ == '__main__':
    manager = CMissAdler(is_task=False)
    manager.run_detail()
