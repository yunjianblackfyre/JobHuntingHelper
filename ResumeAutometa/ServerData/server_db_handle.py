#   AUTHOR: Sibyl System
#     DATE: 2018-01-02
#     DESC: 职位批量处理专用DB客户端

from ResumeAutometa.Config.interfaces import DB_INTERFACE_CFG
from ResumeAutometa.Foundations.mysql_client import MysqlClient


class CServerDbHandle(MysqlClient):

    def __init__(self):
        super(CServerDbHandle, self).__init__(**DB_INTERFACE_CFG)


if __name__ == '__main__':
    f = CServerDbHandle()
    f.destroy()
    print('What a fine day')