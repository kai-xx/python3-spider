# -*- coding: utf-8 -*
__author__ = 'double k'
import re
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq
import threading
from urllib.request import urlretrieve
import os
from PIL import Image
from bs4 import BeautifulSoup
from ownModule import tool

class DownLoadPicture:
    def __init__(self, url):
        self.url = url
        self.path = ""

    def destFile(self, path, thumb=""):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        img = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + path.split('/')[-1]
        return os.path.join(self.path, thumb + img)

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




class GetNav:
    def __init__(self, baseUrl):
        self.baseUrl = baseUrl
        self.brower = None
        self.count = 0
        self.html = None

    def getHtml(self):
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--headless")
        self.brower = webdriver.Chrome(chrome_options=chromeOptions)
        self.brower.get(self.baseUrl)
        self.html = pq(self.brower.page_source)
        items = self.html(".more").items()
        print("--------", "开始获取更多图文信息导航", "--------")
        moreUrls = []
        for item in items:
            url = item.attr.href
            moreUrls.append(url)
            print("获取到的图文更多链接为：", url)
            self.count += 1
        self.brower.quit()
        print("共获取", self.count, "条图文信息导航")
        print("--------", "结束获取更多图文信息导航", "--------")
        return moreUrls

class GetTextList:
    def __init__(self, baseUrl):
        self.baseUrl = baseUrl
        self.brower = None
        self.wait = None
        self.count = 0
        self.html = None
        self.isPaging = False

    def getData(self, url):
        self.isPaging = True
        self.brower.get(url)
        self.html = pq(self.brower.page_source)
        items = self.html(".listlbc_cont_l .Clbc_Game_l_a .gxnew-kc").items()
        for item in items:
            soup = BeautifulSoup(str(item), 'lxml')
            titleList = soup.select(".gxnew-bt > a")[0]
            title = titleList.string
            detailHref = titleList.attrs['href']
            thumbImg = soup.select("#imgshow img")[0].attrs['original']
            list = {
               "title": title,
               "detail-href": detailHref,
               "thumb-img": thumbImg
            }
            self.count += 1
            print("当前第", self.count, "获取的图文信息为：", list)
            detail = GetTextDetail(detailHref)
            detail.main()
    def waitForGetAllData(self):
        page = 2
        if self.html == None:
            return
        items = self.html("#pageNum").children()
        pageInfo = items.eq(len(items)-1)
        href = pageInfo.attr.href
        pageNum = re.search(re.compile(".{0,}_\d+_(\d+).{0,}",re.DOTALL), href).group(1)
        wait = WebDriverWait(self.brower, 5)
        while self.isPaging == True :
            if page > int(pageNum):
                return
            try:
                # text_to_be_present_in_element
                wait.until(
                    EC.text_to_be_present_in_element(
                        (By.CSS_SELECTOR, '#pageNum a:nth-last-child(2)'), '下一页'
                    )
                )
                url = re.sub(re.compile("(?<=_)(\d+)(?=\.)"), str(page), href)
                baseUrl = self.baseUrl + url
                self.getData(baseUrl)
                page += 1
            except TimeoutException:
                self.isPaging = False
                print("所有数据已经全部抓完，共抓取", self.count, "条数据")

    def getHtml(self):
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument('--headless')
        self.brower = webdriver.Chrome(chrome_options=chromeOptions)
        print("--------", "开始获取图文列表信息", "--------")
        self.getData(self.baseUrl)
        self.waitForGetAllData()
        self.brower.quit()
        print("--------", "结束获取图文列表信息，共获取到", self.count, "条数据--------")

class GetTextDetail:
    def __init__(self, baseUrl):
        self.baseUrl = baseUrl
        self.browes = None
        self.html = None
        self.detailhtml = None
        self.count = 0
    def getCategorys(self):
        soup = BeautifulSoup(self.detailhtml, 'lxml')
        catItems = soup.select(".show-gps a")
        categorys = []
        for item in catItems:
            category = item.string
            if category == "唯一图库":
                continue
            if category:
                categorys.append(category)
        return categorys

    def handleContent(self, tool):
        html = tool.replace(self.html(".imgcont").html())
        soap = BeautifulSoup(html, "lxml")
        for i in range(0,len(soap.find_all('img'))):
            if soap.find_all('img')[i].get('src') == None:
                soap.find_all('img')[i]['src'] = soap.find_all('img')[i].get('original')

        return str(soap)

    def main(self):
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--headLess")
        self.browes = webdriver.Chrome(chrome_options=chromeOptions)
        self.browes.get(self.baseUrl)
        self.detailhtml = self.browes.page_source
        self.html = pq(self.detailhtml)
        title = tool.replace(self.html(".show-cont-title").text())
        dateOrigin = re.findall(
            re.compile("更新时间：(.*?)\Z"),
            self.html(".show-cont-xxlist .updateTime").text()
        )
        if len(dateOrigin) > 0:
            date = dateOrigin[0]
        else:
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        viws = re.search(re.compile("(\d+)次"), self.html("#hits").text()).group(1)
        intro = tool.replace(self.html(".Arc_description").text())
        content = self.handleContent(tool)
        categorys = self.getCategorys()
        detail = {
            "title": title,
            "date": date,
            "viws": viws,
            "intro": intro,
            "content": content,
            "categorys": categorys
        }
        print("获取到的信息信息为：", detail)
        self.browes.quit()

url = "http://www.mmonly.cc/tstx/"
navbar = GetNav(url)
navs = navbar.getHtml()
def worke(nav):
    listItem = GetTextList(nav)
    listItem.getHtml()
#  开启线程
thres = [threading.Thread(target=worke, args=(nav,))
            for nav in navs]
# 开始执行线程
[thr.start() for thr in thres]
# 等待线程执行结束
[thr.join() for thr in thres]

# 获取列表调试代码
# url = "http://www.mmonly.cc/tstx/ylxw/"
# listObj = GetTextList(url)
# listObj.getHtml()

# 获取详情信息调试代码
# url = "http://www.mmonly.cc/tstx/ylxw/192333.html"
# detailObj = GetTextDetail(url)
# detailObj.main()