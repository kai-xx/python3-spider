# -*- coding: utf-8 -*
__author__ = 'double k'

from re import compile
from re import sub
# 处理页面标签类
class Tool:
    # 删除超链接标签
    removeAddr = compile('<a.*?>|</a>')
    # 将换行符或双换行符替换为\n
    replaceBR = compile('\n|\t|\xa0')

    def __init__(self, x):
        self.x = x
    def replace(self):
        self.x = sub(self.removeAddr, "", self.x)
        self.x = sub(self.replaceBR, " ", self.x)
        # strip()将前后多余内容删除
        return self.x.strip()

def replace(x):
    tool = Tool(x)
    return tool.replace()