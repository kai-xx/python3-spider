# -*- coding: utf-8 -*
__author__ = 'double k'

from os import path as osPath
from os import mkdir as osMkdir
import datetime
from PIL import Image
from urllib.request import urlretrieve
class DownLoadPicture:
    def __init__(self, url):
        self.url = url
        self.path = ""

    def destFile(self, path, thumb=""):
        if not osPath.exists(self.path):
            osMkdir(self.path)
        img = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + path.split('/')[-1]
        return osPath.join(self.path, thumb + img)

    def handleDown(self):
        filename = self.destFile(self.url)
        urlretrieve(self.url, filename)
        return filename

    def handleThumb(self, width=200, height=200):
        img = Image.open("/Users/carter/Documents/code/python3 object/20181030230515d333a20953.jpg", "r")
        img.thumbnail((width, height), Image.ANTIALIAS)
        thumb = str(width) + "*" + str(height) + "_"
        img.save(self.destFile(self.url, thumb))
        img.close()
        return