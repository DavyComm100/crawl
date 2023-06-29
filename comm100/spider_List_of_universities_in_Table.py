# -*- coding: utf-8 -*-
import pandas as pa
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


#1. get list university in Canada from wiki page: https://en.wikipedia.org/wiki/List_of_universities_in_Canada
#2. call google search to find qless with university name: https://www.google.com.hk/search?q=Acadia+University+qless
#3. forcus the first result, if the url or the description contains qless then retun true
#4. get list university in US from wiki page: https://en.wikipedia.org/wiki/List_of_universities_in_Canada  


def crawl():
    url = "https://en.wikipedia.org/wiki/List_of_colleges_and_universities_in_Texas"
    tables = pa.read_html(url)
    publicCaTable = tables[9]
    publicCaTable.to_csv('Texas.csv', index=False, encoding="utf-8-sig")
    # Parse the URL and get the domain
    
crawl()
