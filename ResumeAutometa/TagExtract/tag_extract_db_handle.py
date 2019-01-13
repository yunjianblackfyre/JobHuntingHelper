#   AUTHOR: Sibyl System
#     DATE: 2018-01-02
#     DESC: 标签过滤器专用DB客户端

from ResumeAutometa.Config.interfaces import DB_INTERFACE_CFG
from ResumeAutometa.Foundations.mysql_client import MysqlClient


class CTagExtractDbHandle(MysqlClient):

    def __init__(self):
        super(CTagExtractDbHandle, self).__init__(**DB_INTERFACE_CFG)


if __name__ == '__main__':
    f = CTagExtractDbHandle()
    f.destroy()
    print('All word and no play makes Jack a dull boy')
