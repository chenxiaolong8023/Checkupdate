# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Time    : 2019/5/5 19:42
# Author  : Amd794
# Email   : 2952277346@qq.com
# Github  : https://github.com/Amd794

import sys, os
import requests
import re

BASEDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASEDIR)
from pyquery import PyQuery
from checkupdate import Response


# ComicList = {
#     '武动乾坤': 'wudongqiankun',
#     '斗破苍穹': 'doupocangqiong',
#     '斗罗大陆': 'douluodalu',
#     '妖神记': 'yaoshenji',
# }
#
# datas = dict()
#
# for key, value in ComicList.items():
#     old_data = datas.get(key, 'None')
#     print(old_data)

class TencentVedio():
    """腾讯视频"""

    def __init__(self, url):
        self.comicUrl = url

    def detailHtml(self, html):
        pq = PyQuery(html)
        content = pq('.mod_episode span:last-child a').text()
        url = pq('.mod_episode span:last-child a').attr('href')
        url = 'https://v.qq.com' + url
        return content, url

    def run(self):
        r = Response.getResponse(self.comicUrl)
        if r:
            text, url = self.detailHtml(r.text)
            print(text, url)


t = TencentComic('https://v.qq.com/x/cover/y0jueuihog64xhb/j0030ajsgq9.html')
i = t.run()
if i:
    print('lsjdfl')

# print(Response.getResponse('http://www.tutubar2019.com').text[:1000])

# url = 'a'
# old_data = 's'
# new_data = 'c'
#
# with open('template.html', encoding='utf-8') as f:
#     tx = f.read().format(url=url, new_data=new_data, old_data=old_data)
