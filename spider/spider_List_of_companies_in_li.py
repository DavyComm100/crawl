# -*- coding: utf-8 -*-
import os.path

import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
HTTP_URL_PATTERN = r'^http[s]*://.+'

#1. get list university in Canada from wiki page: https://en.wikipedia.org/wiki/List_of_universities_in_Canada
#2. call google search to find qless with university name: https://www.google.com.hk/search?q=Acadia+University+qless
#3. forcus the first result, if the url or the description contains qless then retun true
#4. get list university in US from wiki page: https://en.wikipedia.org/wiki/List_of_universities_in_Canada  


def crawl(url):
    HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
            'Accept-Language': 'en-US, en;q=0.5'})
  
    webpage = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "html.parser")
    dom = etree.HTML(str(soup))
    df_init= {'Name':[]}
   
    for li in dom.xpath('//main[@id="content"]//ul/li'):
        aEles = li.xpath('./a')
        if len(aEles) > 0:
            df_init['Name'].append(aEles[0].text)

    print(len(df_init['Name']))
    df = pd.DataFrame(df_init)
    df.to_csv('US.csv', index=False, encoding="utf-8-sig")


    
crawl("https://en.wikipedia.org/wiki/List_of_companies_of_the_United_States_by_state")
