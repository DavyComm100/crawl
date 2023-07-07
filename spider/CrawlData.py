
import requests
import re
import urllib.request
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
from readability import Document
import os
import openpyxl
import urllib.parse
import time
import requests_html

HTTP_URL_PATTERN = r'^http[s]*://.+'

# Function to get the hyperlinks from a URL
def get_hyperlinks(url):
    try:
        # 自动生成一个useragent
        user_agent = requests_html.user_agent()
        # 创建session对象
        session = requests_html.HTMLSession()
        headers = {
            "User-Agent":user_agent
        }
        # 请求Url
        r = session.get(url,headers=headers)
        # 渲染Javasc内容，模拟滚动条翻页5次，每次滚动停止1秒
        r.html.render(scrolldown=5, sleep=1, timeout=200)

    except Exception as ex:
        text=""
        return []

    urls = []
    items = r.html.find("a")
    # 获取href值
    for link in items:
       urls.append(link.attrs["href"])
    return urls

# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(base_address, domain, url):
    clean_links = []
    pattern = re.compile(r'.*{}.*'.format(re.escape(base_address)))
    links = set(get_hyperlinks(url))
    for link in links:
        clean_link = None
        if link == None:
            continue

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            if re.match(pattern,link):
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
                link = "https://" + domain + "/" + link
                if re.match(pattern,link):
                    clean_link = link
            elif link.startswith("#") or link.startswith("mailto:"):
                continue
            elif link.endswith(".pdf"):
                continue
          
        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))


def crawl(url):
    # Parse the URL and get the domain
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
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Title","URL","Content"])
    # While the queue is not empty, continue crawling
    while queue:
        try:
        # Get the next URL from the queue
            url = queue.pop()
            response = requests.get(url)
            doc = Document(response.content)
            doc.title()
            content = doc.summary()
            if not os.path.exists("Output"):
                os.makedirs("Output")

            # Get the text from the URL using BeautifulSoup
            soup = BeautifulSoup(requests.get(url).text, "html.parser")
            title = soup.title.string
            if title not in titles:
                filename = os.path.join("Output", f"{title}.html")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            
                data = [title, url, content]
                print(f"title:{title},url:{url},time:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}")
                sheet.append(data)
                titles.append(title)

            # Get the hyperlinks from the URL and add them to the queue
            for link in get_domain_hyperlinks(base_address,domain, url):
                if link not in seen:
                    queue.append(link)
                    seen.add(link)
        except Exception as ex:
            text=""
             #print(f"url get failed: {url}")

    # 保存Excel文件
    workbook.save('data.xlsx')
    return url


crawl("https://uh.edu/financial/")
