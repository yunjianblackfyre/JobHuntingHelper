#   AUTHOR: Sibyl System
#     DATE: 2018-08-03
#     DESC: request shall be added with random user agent
import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

UserAgentList = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17'
]


# 兵不厌诈，BENDEJO
class MyUserAgentMiddleware(UserAgentMiddleware):
    """This middleware enables working with sites that change the user-agent"""
    def __init__(self, user_agent=''):
        super(MyUserAgentMiddleware, self).__init__()
        self.user_agent = user_agent

    def process_request(self, request, spider):
        agent = random.choice(list(UserAgentList))
        request.headers['User-Agent'] = agent