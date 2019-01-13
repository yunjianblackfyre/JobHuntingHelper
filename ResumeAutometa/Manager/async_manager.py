#   AUTHOR: Sibyl System
#     DATE: 2019-01-13
#     DESC: 类信息增益过滤器

from subprocess import Popen  # PIPE
from ResumeAutometa.Config.file_paths import ASYNC_LOCATION


class AsyncManager(object):

    def __init__(self):
        self.start_up_command = ["python3", ASYNC_LOCATION + "job_preproc.py"]

    def run_proc(self):
        try:
            p = Popen(self.start_up_command)  # start up at 7:00am
            p.wait()
        except Exception as e:
            print(e) 


if __name__ == '__main__':
    manager = AsyncManager()
    manager.run_proc()
