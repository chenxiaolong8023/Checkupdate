# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Time    : 2019/5/4 22:41
# Author  : Amd794
# Email   : 2952277346@qq.com
# Github  : https://github.com/Amd794


import sys
from pathlib import Path

BASEDIR = Path().absolute()
sys.path.append(BASEDIR)

import time
import requests
from pyquery import PyQuery
from fake_useragent import UserAgent
import json
import traceback
from SendEmail import SendEmail
from settings import ComecDict


class Response():
    ua = UserAgent()
    max_count = 3  # 最大尝试连接次数
    timeout = 5  # 超时设置
    ua_type = 'random'

    @classmethod
    def getResponse(self, url, ):
        header = {
            'User-Agent': getattr(self.ua, self.ua_type)
        }
        count = 0
        while count < self.max_count:
            try:
                response = requests.get(url=url, headers=header, verify=True, timeout=self.timeout)
                response.raise_for_status()
                response.encoding = requests.utils.get_encodings_from_content(response.text)[
                                        0] or response.apparent_encoding
                return response
            except requests.exceptions.RequestException:
                print('连接超时, 正在重试...')
                count += 1
        else:
            print('%s 连接失败, 正在放弃连接...' % url)
            return None


class Manhuatai():
    """漫画台下的漫画"""

    def detailHtml(self, html):
        p = PyQuery(html)
        text = p('#topic1 li:nth-of-type(1)').text()  # 获取最新章节漫画标题
        url = p('#topic1 li:nth-of-type(1) a').attr('href')  # 获取最新章节漫画观看地址
        url = "https://www.manhuatai.com/" + url
        return text, url

    def run(self, comicUrl):
        r = Response.getResponse(comicUrl)
        if r:
            text, url = self.detailHtml(r.text)
            return text, url
        return None


class TencentVedio(Manhuatai):
    """腾讯视频"""

    def detailHtml(self, html):
        pq = PyQuery(html)
        content = pq('.mod_episode span:last-child a').text()
        url = pq('.mod_episode span:last-child a').attr('href')
        url = 'https://v.qq.com' + url
        return content, url


class TencentComic(Manhuatai):
    """腾讯动漫下的漫画"""

    def detailHtml(self, html):
        pq = PyQuery(html)
        content = pq('ol[data-ping="ac_comicInfo.about.chapter"] li p:last-child span:last-child').text()
        url = pq('ol[data-ping="ac_comicInfo.about.chapter"] li p:last-child span:last-child a').attr('href')
        url = 'https://ac.qq.com' + url
        return content, url


class Tohomh123(Manhuatai):
    """土豪漫画下的平台"""

    def detailHtml(self, html):
        pq = PyQuery(html)
        content = ''.join(pq('#detail-list-select-1 li:first-child a').text().split()[:2])
        url = pq('ul[id="detail-list-select-1"] li:first-child a').attr('href')
        url = 'https://www.tohomh123.com/' + url
        return content, url


def main():
    # 支持的平台
    paltfromList = {
        'Manhuatai': Manhuatai,  # 漫画台
        'TencentComic': TencentComic,  # 腾讯动漫平台
        'Tohomh123': Tohomh123,  # 土豪漫画平台
        'TencentVedio': TencentVedio,  #  腾讯视频
    }
    with open('datas.json', encoding='utf-8') as fr:  # 读取本地漫画状态
        datas = json.load(fr)
    for key, value in ComecDict.items():
        try:
            paltfrom, key = key.split('-')
            obj = paltfromList.get(paltfrom)().run(value)  # 获取漫画最新更新状态
            if obj:
                content, url = obj
                new_data = content  # 最新章节数据
                old_data = datas.get(key, None)  # 本地章节数据
                if old_data != new_data:  # 判断是否有更新
                    datas[key] = content  # 更新本地章节

                    with open('template.html', encoding='utf-8') as f:
                        tx = f.read().format(url=url, new_data=new_data, old_data=old_data)  # 构造邮件内容

                    SendEmail(content=tx, title='{key} 更新通知'.format(key=key),
                              emtype='htmlcontent').sendEmail()  # 发送邮件, 推送更新

                    with open('datas.json', 'w', encoding='utf-8') as fw:  # 存储更新后的状态
                        json.dump(datas, fw, ensure_ascii=False, indent=4, separators=(', ', ': '))
                else:
                    print('\033[22;35;m {} \033[m 暂无更新, 当前章节: \033[22;35;m {} \033[m'.format(key, old_data))
        except TypeError:
            print('检测{key}失败, 该平台没有{key}, 或者平台配置有误'.format(key=key))
        except Exception:
            SendEmail(content=traceback.format_exc(),
                      title='获取 {key} 时脚本异常通知'.format(key=key)).sendEmail()  # 发送邮件, 脚本异常

    tm = time.localtime()
    print(time.strftime('%Y-%m-%d %H:%M:%S', tm).center(65, '-'))
    print()


if __name__ == '__main__':
    while True:
        main()
        time.sleep(60 * 60)  # 运行周期为1小时
