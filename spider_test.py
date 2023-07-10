# -*- coding: utf-8 -*-
import os.path
import xlrd
import requests
import requests_html
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
import ssl
import re
import time
from urllib.parse import urlparse
from urllib.parse import parse_qs
import urllib.parse

ssl._create_default_https_context = ssl._create_unverified_context
HTTP_URL_PATTERN = r'^http[s]*://.+'

#1. get list university in Canada from wiki page: https://en.wikipedia.org/wiki/List_of_universities_in_Canada
#2. call google search to find qless with university name: https://www.google.com.hk/search?q=Acadia+University+qless
#3. forcus the first result, if the url or the description contains qless then retun true
#4. get list university in US from wiki page: https://en.wikipedia.org/wiki/List_of_universities_in_Canada  
def get_websitecontent(url):
    # 自动生成一个useragent
    user_agent = requests_html.user_agent()
    # 创建session对象
    session = requests_html.HTMLSession()
    HEADERS = {
        "User-Agent":user_agent
    }
    # 请求Url
    r = session.get(url,headers=HEADERS, timeout=15)
    if len(r.history) > 0:
        his = r.history[len(r.history)-1]
        if his.status_code == 302:
            link = his.headers["Location"]                
            r = session.get(link,headers=HEADERS, timeout=15)        
    # 渲染Javasc内容，模拟滚动条翻页5次，每次滚动停止1秒
    r.html.render(scrolldown=6, sleep=1, timeout=300)
    return r.html

get_websitecontent('https://www.5nplus.com/contact-us.html')
