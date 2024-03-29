
import re
import urllib.request
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
from readability import Document
import os
import shutil
import json
import urllib.parse
import time
import requests_html
from lxml.html import tostring
import lxml.html
import xml.etree.ElementTree as ET

re._pattern_type = re.Pattern
HTTP_URL_PATTERN = r'^http[s]*://.+'
utf8_parser = lxml.html.HTMLParser(encoding="utf-8")

debug_urls = []

def html_session():
    # 自动生成一个useragent
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=1',
        }
    # 设置代理 IP 和端口
    proxies = {
        'http': 'http://45.63.24.57:80',
        'http': 'http://47.88.62.42:80',
        'http': 'http://172.67.179.201:80',
        'http': 'http://172.64.94.136:80',
        'http': 'http://104.26.13.19:80',
        'http': 'http://172.67.70.62:80',
        'http': 'http://104.25.193.145:80',
        'http': 'http://172.67.31.55:80',
        'http': 'http://104.25.172.8:80',
        'http': 'http://104.21.72.241:80',
        'http': 'http://104.21.19.144:80',
        'http': 'http://104.18.16.111:80',
        'http': 'http://144.217.197.151:39399',
        'http': 'http://104.18.188.57:80'
        }
    # 创建session对象
    session = requests_html.HTMLSession()
    session.headers.update(headers)
    session.proxies.update(proxies)
    return session

session = html_session()

def clean_html(input):
    doc = lxml.html.document_fromstring(
        input.encode("utf-8", "replace"), parser=utf8_parser
    )
    #doc = html_cleaner.clean_html(doc)

    for elem in doc.findall(".//*"):
        if elem.tag in ["system-region", "noscript", "script", "iframe", "footer"]:            
            elem.drop_tree()
        elif 'style' in elem.attrib and ('display: none' in elem.attrib['style'] or 'display:none' in elem.attrib['style']) :
            elem.drop_tree()
    return tostring(doc)

# Function to get the hyperlinks from a URL
def get_hyperlinks(r):
    try:       
        urls = []
        items = r.find("a")
        for link in items:
            if "href" in link.attrs:
                urls.append(link.attrs["href"])
        return urls
    except Exception as ex:
        return []

# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(base_address, domain, r, url):
    clean_links = []
    pattern = re.compile(r'.*{}.*'.format(re.escape(base_address)))
    pathPattern = r"^[a-zA-Z]|^\.\./"
    links = set(get_hyperlinks(r))
    for link in links:
        clean_link = None
        if link == None:
            continue
        if link == "":
            continue
        if link.lower().endswith(".pdf"):
            continue
        if link.startswith("#") or link.lower().startswith("mailto:") or link.lower().startswith("tel:") or link.lower().startswith("javascript:"):
            continue
        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            if re.match(pattern,link):
                clean_link = link
                #print(link)
                debug_urls.append(link)

        # If the link is not a URL, check if it is a relative link
        else:
            #print(link)
            debug_urls.append(link)
            if link.startswith("/"):
                link = link[1:]
                link = "https://" + domain + "/" + link
                if re.match(pattern,link):
                    clean_link = link
            elif link.startswith("//"):
                link = "https:" + link
                if re.match(pattern,link):
                    clean_link = link
            elif re.search(pathPattern, link):
                if not url.endswith("/"):
                    url = url + "/"
                link = urllib.parse.urljoin(url,link)
                if re.match(pattern,link):
                    clean_link = link
          
        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))

def crawl(siteid, url, lang):
    url_obj = urlparse(url)
    domain = url_obj.netloc
    sitemapurl = "http://" + domain + "/sitemap.xml"
    response = urllib.request.urlopen(sitemapurl)
    if response.getcode() == 200:
        print(f"crawlbysitemap")
        crawlbysitemap(siteid, url, lang, response)
    else:
        print(f"crawlbyrecursion")
        crawlbyrecursion(siteid, url, lang)
        
def generatedirs(siteid, base_address):
    if not os.path.exists("htmlResult"):
        os.makedirs("htmlResult")
    if not os.path.exists("htmlResult/"+ str(siteid)):
        os.makedirs("htmlResult/"+ str(siteid))
    dirname = "htmlResult/"+ str(siteid)+ "/" + base_address.replace("?", "_").replace("*", "").replace(":", "").replace("/", "_").replace('"', '').replace('<', '').replace('>', '').replace('|', '')
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname) 

def resolvexml(response):
    xml_data = response.read()
    root = ET.fromstring(xml_data)
    urls = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")
    return [url.findtext("{http://www.sitemaps.org/schemas/sitemap/0.9}loc") for url in urls]

def savedata(url, lang, dirname, titles, dataTosave):
    r = session.get(url)
    if r.status_code == 200:
        # try to filter english page.
        content_language = r.headers.get('Content-Language')
        if content_language and lang not in content_language:
            return
        if 'text/html' not in r.headers['Content-Type']:
            return
        # 渲染Javascript内容，模拟滚动条翻页3次，每次滚动停止1秒
        r.html.render(scrolldown=2, sleep=1, timeout=300)
        response = r.html
        lang_attribute = response.find('html[lang]')
        if lang_attribute and lang not in lang_attribute[0].attrs['lang']:
            return
        doc = Document(clean_html(response.html))
        title = doc.title()
        content = doc.summary(True)
        content = re.sub(r'\n+\s+', '\n', content.replace('\t', ''))            
        if content == '' or content == '<div></div>':
            dataTosave.append({"title": "ERROR", "url":url, "content": "ERROR: Empty Body"})
            return
        if title not in titles:
            name_windows = title.replace("?", "_").replace("*", "").replace(":", "").replace("/", "_").replace('"', '').replace('<', '').replace('>', '').replace('|', '')
            filename = os.path.join(dirname, f"{name_windows}.html")

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        
            print(f"title:{title},url:{url},time:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}")
            dataTosave.append({"title": title, "url":url, "content": content })                
            if title != "" and title != "[no-title]":
                titles.append(title)
        return response
    elif r.status_code == 403:
        session.close()
        session = html_session()
        savedata(url, lang, dirname, titles, dataTosave)
    else:
        print(f"url get failed: {url} ,ERROR: {str(r.status_code)}")
        dataTosave.append({"title": "ERROR", "url":url, "content": "ERROR:" + str(r.status_code) })
            
def crawlbysitemap(siteid, url, lang, response):
    url_obj = urlparse(url)
    domain = url_obj.netloc
    path = url_obj.path
    base_address = domain + path
    # get the base host to filter link.
    base_address = base_address.replace('www.','')
    titles = []
    dataTosave = []
     #create dir to store html files
    dirname = generatedirs(siteid, base_address)
    page_urls = resolvexml(response)
    pattern = re.compile(r'.*{}.*'.format(re.escape(base_address)))
    for url in page_urls:
        if re.match(pattern, url):
            try:
                time.sleep(60)
                # 请求Url
                savedata(url, lang, dirname, titles, dataTosave)
            except Exception as ex:
                dataTosave.append({"title": "ERROR", "url":url, "content": "ERROR:" + str(ex) })                
                print(f"url get failed: {url},ERROR: {str(ex)}")
        else:
            debug_urls.append(url)
    # Serializing json
    json_object = json.dumps(dataTosave, indent=4)
    
    # Writing to json file and upload to S3
    filename = str(siteid) + "_" + base_address.replace("?", "_").replace("*", "").replace(":", "").replace("/", "_").replace('"', '').replace('<', '').replace('>', '').replace('|', '') + ".json"
    with open(filename, "w") as outfile:
        outfile.write(json_object)
        
    filename_debug_urls = str(siteid) + "_" + base_address.replace("?", "_").replace("*", "").replace(":", "").replace("/", "_").replace('"', '').replace('<', '').replace('>', '').replace('|', '') + "_debug_urls.json"
    json_object = json.dumps(debug_urls)
    with open(filename_debug_urls, "w") as outfile:
        outfile.write(json_object)

def crawlbyrecursion(siteid, url, lang):
    # get the base host to filter link.
    url_obj = urlparse(url)
    domain = url_obj.netloc
    path = url_obj.path
    base_address = domain + path
    # get the base host to filter link.
    base_address = base_address.replace('www.','')
    # Create a queue to store the URLs to crawl
    queue = deque([url])

    # Create a set to store the URLs that have already been seen (no duplicates)
    seen = {url}
    titles = []
    dataTosave = []

    #create dir to store html files
    dirname = generatedirs(siteid, base_address)
    # While the queue is not empty, continue crawling
    while queue:
        try:
            # Get the next URL from the queue
            url = queue.pop()
            time.sleep(60)
            # 请求Url
            response = savedata(url, lang, dirname, titles, dataTosave)
            # Get the hyperlinks from the URL and add them to the queue
            for link in get_domain_hyperlinks(base_address,domain, response, url):
                if link not in seen:
                    queue.append(link)
                    seen.add(link)
        except Exception as ex:
            dataTosave.append({"title": "ERROR", "url":url, "content": "ERROR:" + str(ex) })                
            print(f"url get failed: {url},ERROR: {str(ex)}")

    # Serializing json
    json_object = json.dumps(dataTosave, indent=4)
    
    # Writing to json file and upload to S3
    filename = str(siteid) + "_" + base_address.replace("?", "_").replace("*", "").replace(":", "").replace("/", "_").replace('"', '').replace('<', '').replace('>', '').replace('|', '') + ".json"
    with open(filename, "w") as outfile:
        outfile.write(json_object)
    
    filename_debug_urls = str(siteid) + "_" + base_address.replace("?", "_").replace("*", "").replace(":", "").replace("/", "_").replace('"', '').replace('<', '').replace('>', '').replace('|', '') + "_debug_urls.json"
    json_object = json.dumps(debug_urls)
    with open(filename_debug_urls, "w") as outfile:
        outfile.write(json_object)
    return len(dataTosave)

crawl(10000, "https://help.dropbox.com/","en")