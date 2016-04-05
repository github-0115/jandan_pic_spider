#!/usr/bin/env python
# -*- coding:utf-8 -*-
from urllib2 import urlopen, Request, URLError, HTTPCookieProcessor, build_opener, install_opener
import re, os, time
from cookielib import CookieJar

__author__ = 'Naphy'

class Spider():

    def __init__(self):
        self.site_url = ''
        self.img_url_list = []
        self.count = 1
        self.headers = {
        'User-Agent':'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        }


    def start(self):
        print self.to_code('\n-----欢迎使用煎蛋图片爬虫-----\n\n')
        cookie = CookieJar()
        opener = build_opener(HTTPCookieProcessor(cookie))
        install_opener(opener)
        self.get_site()
        page = self.get_page()
        start_page = page[0]
        end_page = page[1]
        begin = time.time()
        while start_page <= end_page:
            img_page_url = self.get_img_url(str(start_page))
            self.log('log', start_page)
            self.save_img(img_page_url)
            start_page +=1
        end = time.time()
        total_time = self.total(end-begin)
        with open('log.txt', 'a') as f:
            f.write(self.to_code('\n花费时间：') + total_time + '\n\n\n')
        print self.to_code('\n花费时间：') + total_time


    def load_img_url_list(self):
        try:
            with open('img_url.txt', 'r') as f:
                for line in f.readlines():
                    url = re.split(r'\s', line)[0]
                    name = re.split(r'\s', line)[1]
                    page = re.split(r'\s', line)[2]
                    self.img_url_list.append([url, name, page])
        except Exception, e:
            print e


    def get_img_url(self, page):
        url = 'http://jandan.net/' + self.site_url % page
        img_page_url = []
        try:
            response = Request(url, headers=self.headers)
            content = urlopen(response).read()
            regex = re.compile(r'<div class="text">.*?<a.*?>(.*?)</a>.*?href="(.*?)"')
            items = regex.findall(content)
            for item in items:
                img_name = item[0]
                img_link = item[1]
                same = False
                for img_url in self.img_url_list:
                    if img_link in img_url:
                        same = True
                        break
                if not same:
                    self.img_url_list.append([img_link, img_name, page])
                    img_page_url.append([img_link, img_name, page])
                    with open('img_url.txt', 'a') as url_file:
                        url_file.write(img_link + ' ' + img_name + ' ' + page + '\n')
            return img_page_url
        except URLError, e:
            if hasattr(e, 'code'):
                print self.to_code('页面禁止访问：') + e.code
            elif hasattr(e, 'reason'):
                print e.reason
            else:
                print self.to_code('\n发生未知错误')


    def get_page(self):
        site = self.site_url.split('/')[0]
        start_page = None
        end_page = None
        if self.site_url == 'ooxx/page-%s#comments':
            min_page = 1500
        else: 
            min_page = 7500
        try:
            response = Request('http://jandan.net/' + site, headers=self.headers)
            content = urlopen(response).read()
            regex = re.compile(r'<span class="current-comment-page">\[(.*?)\]</span>')
            max_page = regex.search(content).group(1)
        except URLError, e:
            if hasattr(e, 'code'):
                print self.to_code('页面禁止访问：') + e.code
            elif hasattr(e, 'reason'):
                print e.reason
            else:
                print self.to_code('\n发生未知错误')
        while True :
            start_page = raw_input(self.to_code('\n请输入下载图片的起始页面:    （过旧的图片已被删除, 页面范围在 %s-%s)\n') % (min_page, max_page))
            end_page = raw_input(self.to_code('\n请输入终止页面:\n') ) 
            try:
                begin = int(start_page)
                end = int(end_page)
                limit = int(max_page)
            except:
                print self.to_code('\n输入错误，请重新输入\n\n')
                continue
            if min_page <= begin <= limit and begin <= end <=  limit:
                page = []
                page.append(begin)
                page.append(end)
                return page
            else:
                print self.to_code('\n输入错误，请重新输入\n\n')


    def get_site(self):
        site = None
        while True:
            site = raw_input(self.to_code('请选择需要下载的图片种类\n1：美女图\n2：无聊图\n'))
            if site == '1':
                self.site_url = 'ooxx/page-%s#comments'
                break;
            elif site == '2':
                self.site_url = 'pic/page-%s#comments'
                break;
            else:
                print self.to_code('\n输入错误，请重新输入\n\n')


    def save_img(self, img_page_url):
        if self.site_url == 'ooxx/page-%s#comments':
            dirname = 'beauty'
        else: 
            dirname = 'fun'
        DIR = dirname + str(self.count)
        try:
            os.mkdir(DIR)
        except Exception, e:
            pass
        for img in img_page_url:
            url = img[0]
            name = img[1]
            extention = re.search(r'\..*?/.*?(\..*?)$', img[0]).group(1)
            try:
                response = Request(url, headers = self.headers)
                content = urlopen(response).read()
                with open(DIR +'/' + name + extention, 'wb') as f:
                    f.write(content)
                print self.to_code('正在下载 ') + name + extention
            except URLError, e:
                if hasattr(e, 'code'):
                    print self.to_code('页面禁止访问：') + e.code
                elif hasattr(e, 'reason'):
                    print e.reason
                else:
                    print self.to_code('\n发生未知错误')
        if len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]) >=1000:
            self.count += 1


    def total(self, t):
        t = int(t)
        if t < 60:
            return self.to_code('%s秒') % t
        elif t < 3600:
            return self.to_code('%s分%s秒') % (t/60, t%60)
        else:
            return self.to_code('%s小时%s分%s秒') % (t/3600, (t%3600)/60, (t%3600)%60)


    def to_code(self, code):
        return code.decode('utf-8', 'ignore').encode('gbk', 'ignore')


    def log(self, name, data):
        with open( name + '.txt', 'a') as log_file:
            log_file.write(time.strftime('%Y-%m-%d %H:%M:%S') + self.to_code(' 下载 页面') + str(data) + '\n')
        print '\n' + time.strftime('%Y-%m-%d %H:%M:%S') + self.to_code(' 下载页面 ') + str(data)



jandan = Spider()
jandan.start()

