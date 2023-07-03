# -*- coding: utf-8 -*-
import os.path
import xlrd
import requests
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

def crawl():
    df_init= {'Name':[], 'LivePerson':[], 'Website':[]}
    googleUrl = "https://www.google.com/search?hl=en&q="
    HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
            'Accept-Language': 'en-US, en;q=1',\
            'referer':'https://www.google.com/'})
    names = extract_xls(os.path.join(os.getcwd(),'spider/data/CAUniversities.xls'))
    #names = ["godaddy"]
    print(len(names))
    count=0
    index=0
    for name in names:
        time.sleep(3)
        url = googleUrl + name + " live chat"
        try:
            webpage = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(webpage.content, "html.parser")
            dom = etree.HTML(str(soup))

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
                #df_init['Name'].append(name)
                #df_init['Website'].append(link)
                webpagecontent = requests.get(link)
                if webpagecontent.status_code == 302:
                    link = webpagecontent.headers["Location"]                    
                    webpagecontent = requests.get(link)
                
                df_init['Name'].append(name)            
                df_init['Website'].append(link)
                if webpagecontent.status_code != 200:
                    df_init['LivePerson'].append(str(webpagecontent.status_code))
                else:
                    if 'liveperson.net' in webpagecontent.text:
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
            filename = 'listcollegeslivepersonca'+str(index)+'.csv'
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            time.sleep(30)

    print(len(df_init['Name']))
    df = pd.DataFrame(df_init)
    filename = 'listcollegeslivepersonca.csv'
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
