#   AUTHOR: Sibyl System
#     DATE: 2018-01-03
#     DESC: 数据批处理基类

import traceback
from ResumeAutometa.LogHandle.Log import Log
from ResumeAutometa.ServerData.server_db_handle import CServerDbHandle
from ResumeAutometa.Foundations.exception import NotImplementedException
RETRY_TIMES = 0


class BatchProc:

    def __init__(self, proc_name):
        self.firelinker = {         # 当前函数为下一个函数提供的数据
            "result": "Usurvive"    # 初始化为“成功”
        }    
        self.abyss = {              # 异常、缺陷信息统计器
            "Usurvive": 0,
            "URdead": 0,
            "UPoison": 0,
            "UPlay": 0
        }
        self.log_handler = Log(proc_name, "async")
        self._db = CServerDbHandle()

    # 每次跑完一批数据，重置监视器（点燃篝火）
    def _bonfire(self):
        self.firelinker = {         # 当前函数为下一个函数提供的数据
            "result":"Usurvive"     # 初始化为“成功”
        }    
        self.abyss = {              # 异常、缺陷信息统计器
            "Usurvive": 0,
            "URdead": 0,
            "UPoison": 0,
            "UPlay": 0
        }

    # 成功处理完单个数据（完成击杀）
    def _extract_soul(self):
        result = self.firelinker["result"]
        self.abyss[result] += 1
        self.abyss["UPlay"] += 1
        self.firelinker = {
            "result": "Usurvive"
        }

    # 处理单个数据失败（落命）
    def _you_are_dead(self, item):
        self.firelinker["result"] = "URdead"
        self.log_handler.log.info(str(item))
        self.log_handler.log.info(traceback.format_exc())
        
    def close(self):
        if self._db:
            self._db.destroy()
        self._db = None
    
    def run(self):
        raise NotImplementedException
        
    def main(self):
        try:
            print("Lover Fucker")
            self.run()
            self.close()
        except:
            self.log_handler.log.info("Critical failure detected")
            self.log_handler.log.info(traceback.format_exc())