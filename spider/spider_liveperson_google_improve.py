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

ssl._create_default_https_context = ssl._create_unverified_context
HTTP_URL_PATTERN = r'^http[s]*://.+'

#1. get list university in Canada from wiki page: https://en.wikipedia.org/wiki/List_of_universities_in_Canada
#2. call google search to find qless with university name: https://www.google.com.hk/search?q=Acadia+University+qless
#3. forcus the first result, if the url or the description contains qless then retun true
#4. get list university in US from wiki page: https://en.wikipedia.org/wiki/List_of_universities_in_Canada  
def get_websitecontent(url):
    try:
        # 自动生成一个useragent
        user_agent = requests_html.user_agent()
        # 创建session对象
        session = requests_html.HTMLSession()
        HEADERS = {
            "User-Agent":user_agent,
            'Accept-Language': 'en-US, en;q=1'
        }
        # 请求Url
        r = session.get(url,headers=HEADERS, timeout=15)
        # 渲染Javasc内容，模拟滚动条翻页5次，每次滚动停止1秒
        r.html.render(scrolldown=6, sleep=1, timeout=300)
        return r.html
    except Exception as ex:
        print(f"url get failed: {url}")
        return ""

def crawl():
    df_init= {'Name':[], 'LivePerson':[], 'Website':[]}
    googleUrl = "https://www.google.com/search?hl=en&q="
    HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
            'Accept-Language': 'en-US, en;q=1',\
            'referer':'https://www.google.com/'})
    names = extract_xls(os.path.join(os.getcwd(),'spider/data/CACompanies.xls'))
    names = ["godaddy"]
    print(len(names))
    count=0
    index=0
    for name in names:
        time.sleep(3)
        url = googleUrl + name + ' live chat'
        try:
            webpage = get_websitecontent(url)
            #soup = BeautifulSoup(webpage, "html.parser")
            dom = etree.HTML(webpage.html)

            searchData = dom.xpath('//div[@id="main"]//div[contains(@class, "fP1Qef")]//a')
            if len(searchData) >0 :
                link = ""
                for aLink in searchData:
                    link = aLink.attrib["href"]
                    if re.search(HTTP_URL_PATTERN, link) and not link.startswith('https://www.google.com'):
                        break  
                # Parse the URL and check if the domain is the same
                    if link.startswith("/"):
                        parse_url = urlparse(link)
                        urlPara = parse_qs(parse_url.query).get('url')
                        qPara = parse_qs(parse_url.query).get('q')
                        if urlPara != None:
                            link = urlPara[0]
                        if qPara != None:
                            link = qPara[0]
                        break 
                print(link)
                if link.startswith('https://free-apply.com'):
                    print('no match')
                    df_init['Name'].append(name)
                    df_init['LivePerson'].append('')
                    df_init['Website'].append('')
                else:
                    #df_init['Name'].append(name)
                    #df_init['Website'].append(link)
                    webpagecontent = requests.get(link, timeout=10)
                    if webpagecontent.status_code == 302:
                        link = webpagecontent.headers["Location"]                    
                    
                    print(link)
                    webpagecontent = get_websitecontent(link)
                    
                    df_init['Name'].append(name)            
                    df_init['Website'].append(link)
                    
                    if 'liveperson.net' in webpagecontent.html:
                        df_init['LivePerson'].append('Yes')
                    else:
                        df_init['LivePerson'].append('')
            else:
                print('no match')
                df_init['Name'].append(name)
                df_init['LivePerson'].append('')
                df_init['Website'].append('')
        except:
            df_init['Name'].append(name)
            df_init['LivePerson'].append('ERROR')
            df_init['Website'].append('')
        count = count +1
        if count == 60:
            count = 0
            index=index+1
            print(len(df_init['Name']))
            df = pd.DataFrame(df_init)
            filename = 'USGoogle'+str(index)+'.csv'
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            time.sleep(3)

    print(len(df_init['Name']))
    df = pd.DataFrame(df_init)
    filename = 'USGoogle.csv'
    df.to_csv(filename, index=False, encoding="utf-8-sig")
          

def extract_xls(data_path):
    workbook = xlrd.open_workbook(data_path)
    table = workbook.sheets()[0]
    names = []
    for i in range(table.nrows):
        if i == 0:
            continue
        name = str(table.cell(i, 0).value)
        #province = str(table.cell(i, 1).value)
        #print(name)
        names.append(name)
    return names

crawl()
