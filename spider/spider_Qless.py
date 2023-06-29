# -*- coding: utf-8 -*-
import os.path
import xlrd
import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
import ssl
import re
from urllib.parse import urlparse
from urllib.parse import parse_qs

ssl._create_default_https_context = ssl._create_unverified_context
HTTP_URL_PATTERN = r'^http[s]*://.+'

#1. get list university in Canada from wiki page: https://en.wikipedia.org/wiki/List_of_universities_in_Canada
#2. call google search to find qless with university name: https://www.google.com.hk/search?q=Acadia+University+qless
#3. forcus the first result, if the url or the description contains qless then retun true
#4. get list university in US from wiki page: https://en.wikipedia.org/wiki/List_of_universities_in_Canada  



def crawl():
    df_init= {'Name':[], 'Qless':[], 'Url':[]}
    googleUrl = "https://www.google.com.hk/search?q="
    names = extract_xls('datainus.xls')
    print(len(names))
    count=0
    index=0
    for name in names:
        query = name + " QLess"
        url = googleUrl + query
        try:
            webpage = requests.get(url)
            soup = BeautifulSoup(webpage.content, "html.parser")
            dom = etree.HTML(str(soup))

            province = []
            searchData = dom.xpath('//div[@id="main"]//div[contains(@class, "fP1Qef")]')
            if len(searchData) >0 :
                alist = searchData[0].xpath('.//a')
                #get a herf url or q
                if len(alist) >0 :
                    link = alist[0].attrib["href"]
                    if re.search(HTTP_URL_PATTERN, link):
                        print(link)
                    else:
                    # Parse the URL and check if the domain is the same
                        if link.startswith("/"):
                            parse_url = urlparse(link)
                            urlPara = parse_qs(parse_url.query).get('url')
                            qPara = parse_qs(parse_url.query).get('q')
                            if urlPara != None:
                                link = urlPara[0]
                            if qPara != None:
                                link = qPara[0]
                    #print(link)
                title = searchData[0].xpath('string(.//a//h3)')
                #print(title)
                description = searchData[0].xpath('string(.//div[@class="kCrYT"]/div/div[@class="BNeawe s3v9rd AP7Wnd"]/div/div)')
                #print(description)
                #check qless keyword
                if ('qless' in link.lower() or 'qless' in title.lower() or 'qless' in description.lower()) and 'qless.com' not in link.lower() and 'youtube.com' not in link.lower() and 'instagram.com' not in link.lower() and 'linkedin.com' not in link.lower() and 'google.com' not in link.lower():                    
                    #print('match:' + link)
                    df_init['Name'].append(name)
                    df_init['Qless'].append('Yes')
                    df_init['Url'].append(link)
                else:
                    #print('no match')
                    df_init['Name'].append(name)
                    df_init['Qless'].append('')
                    df_init['Url'].append(link)
            else:
                #print('no match')
                df_init['Name'].append(name)
                df_init['Qless'].append('')
                df_init['Url'].append('')
        except:
            df_init['Name'].append(name)
            df_init['Qless'].append('ERROR')
            df_init['Url'].append('')
        count = count +1
        if count == 50:
            count = 0
            index=index+1
            print(len(df_init['Name']))
            df = pd.DataFrame(df_init)
            filename = 'listcollegesqlessinUS'+str(index)+'.csv'
            df.to_csv(filename, index=False, encoding="utf-8-sig")

    print(len(df_init['Name']))
    df = pd.DataFrame(df_init)
    filename = 'listcollegesqlessinUS.csv'
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
