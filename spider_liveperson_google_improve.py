# -*- coding: utf-8 -*-
import os.path
import xlrd
import requests
import requests_html
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
import re
import time
from urllib.parse import urlparse
from urllib.parse import parse_qs
import urllib.parse

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
    r = session.get(url,headers=HEADERS)
    if 'text/html' not in r.headers['Content-Type']:
        return ''
    if r.status_code != 200:
        print(f"{str(r.status_code)}: {url}")
        return ''
    # 渲染Javascript内容，模拟滚动条翻页3次，每次滚动停止1秒
    r.html.render(scrolldown=3, sleep=1, timeout=300)
    return r.html.html

def crawl():
    df_init= {'Name':[], 'LivePerson':[], 'Website':[]}
    googleUrl = "https://www.google.com/search?hl=en&q="
    if not os.path.exists("liveperson"):
        os.makedirs("liveperson")
    names = extract_xls(os.path.join(os.getcwd(),'spider/data/CACompanies.xls'))
    #names = ["godaddy"]
    print(len(names))
    count=0
    index=0
    for name in names:
        param = urllib.parse.quote_plus(name + ' live chat')
        #time.sleep(2)
        url = googleUrl + param
        #url = googleUrl + urllib.parse.urlencode(name + ' live chat')
        try:
            webpage = get_websitecontent(url)
            if webpage != "":
            #soup = BeautifulSoup(webpage, "html.parser")
                dom = etree.HTML(webpage)

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
                        try:                                              
                            webpagecontent = get_websitecontent(link)        
                            #print(link)
                            df_init['Name'].append(name)            
                            df_init['Website'].append(link)
                            
                            if 'liveperson.net' in webpagecontent or 'liveperson' in webpagecontent or 'liveper.sn' in webpagecontent:
                                print('Yes')
                                df_init['LivePerson'].append('Yes')
                            else:
                                print('No')
                                df_init['LivePerson'].append('')
                        except Exception as ex:
                            print(f"url get failed: {link}, {str(ex)}")
                            df_init['Name'].append(name)            
                            df_init['Website'].append(link)
                            df_init['LivePerson'].append('ERROR:' + str(ex))
                else:
                    print('no match')
                    df_init['Name'].append(name)
                    df_init['LivePerson'].append('')
                    df_init['Website'].append('')
            else:
                df_init['Name'].append(name)
                df_init['LivePerson'].append('ERROR')
                df_init['Website'].append(url)
        except Exception as e:
            print(f"url get failed: {url}, {str(e)}")
            df_init['Name'].append(name)
            df_init['LivePerson'].append('ERROR:' + str(e))
            df_init['Website'].append(url)
        count = count +1
        if count == 100:
            count = 0
            index=index+1
            print(len(df_init['Name']))
            df = pd.DataFrame(df_init)
            #filename = 'CAGoogle'+str(index)+'.csv'
            filename = os.path.join("liveperson",'CAGoogle'+str(index)+'.csv')
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            time.sleep(10)

    print(len(df_init['Name']))
    df = pd.DataFrame(df_init)    
    #filename = 'CAGoogle.csv'
    filename = os.path.join("liveperson", 'CAGoogle.csv')
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
