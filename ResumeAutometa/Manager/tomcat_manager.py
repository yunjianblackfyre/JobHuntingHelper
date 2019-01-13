#   AUTHOR: Sibyl System
#     DATE: 2019-01-13
#     DESC: 类信息增益过滤器

import time
from subprocess import Popen  # PIPE
from ResumeAutometa.Config.file_paths import TOMCAT_BIN_LOCATION


class TomcatManager(object):

    def __init__(self):
        self.start_up_command = [TOMCAT_BIN_LOCATION + "startup.sh"]
        self.shut_down_command = [TOMCAT_BIN_LOCATION + "shutdown.sh"]

    def run_proc(self):
        try:
            p = Popen(self.start_up_command)  # start up at 7:00am
            p.wait()
            time.sleep(3600*2)
            p = Popen(self.shut_down_command)  # shut down at 9:00am 
            p.wait()
            
            time.sleep(3600*10)
            
            p = Popen(self.start_up_command)  # start up at 7:00pm
            p.wait()
            time.sleep(3600*2)
            p = Popen(self.shut_down_command)  # shut down at 9:00pm
            p.wait()
            
        except Exception as e:
            print(e) 


if __name__ == '__main__':
    manager = TomcatManager()
    manager.run_proc()
