
import re
import urllib.request
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
from readability import Document
import os
import json
import urllib.parse
import time
import requests_html

HTTP_URL_PATTERN = r'^http[s]*://.+'

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
    r.html.render()
    return r.html

# Function to get the hyperlinks from a URL
def get_hyperlinks(r):
    try:       
        #r = get_websitecontent(url)
        urls = []
        items = r.find("a")
        for link in items:
            if "href" in link.attrs:
                urls.append(link.attrs["href"])
        return urls
    except Exception as ex:
        return []

# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(base_address, domain, r):
    clean_links = []
    pattern = re.compile(r'.*{}.*'.format(re.escape(base_address)))
    links = set(get_hyperlinks(r))
    for link in links:
        clean_link = None
        if link == None:
            continue
        print(link)
        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            if re.match(pattern,link):
                clean_link = link
                if clean_link.endswith(".pdf"):
                    continue

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
                link = "https://" + domain + "/" + link
                if re.match(pattern,link):
                    clean_link = link
            elif link.startswith("#") or link.startswith("mailto:") or link.startswith("tel:"):
                continue
            elif link.endswith(".pdf"):
                continue
          
        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))


def crawl(siteid, url):
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
    dataTosave = []
    # While the queue is not empty, continue crawling
    while queue:
        try:
        # Get the next URL from the queue
            url = queue.pop()
            response = get_websitecontent(url)
            doc = Document(response.html)
            title = doc.title()
            content = doc.summary()
            if not os.path.exists("htmlResult"):
                os.makedirs("htmlResult")
            if not os.path.exists("htmlResult/"+ str(siteid)):
                os.makedirs("htmlResult/"+ str(siteid))

            if title not in titles:
                title = title.replace("?", "_").replace("*", "").replace(":", "").replace("/", "_").replace('"', '').replace('<', '').replace('>', '').replace('|', '')
                filename = os.path.join("htmlResult/"+ str(siteid), f"{title}.html")

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            
                print(f"title:{title},url:{url},time:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}")
                dataTosave.append({"title": title, "url":url, "content": content })                
                titles.append(title)

            # Get the hyperlinks from the URL and add them to the queue
            for link in get_domain_hyperlinks(base_address,domain, response):
                if link not in seen:
                    queue.append(link)
                    seen.add(link)
        except Exception as ex:
            dataTosave.append({"title": "ERROR", "url":url, "content": "ERROR:" + str(ex) })                
             #print(f"url get failed: {url}")

    # Serializing json
    json_object = json.dumps(dataTosave, indent=4)
    
    # Writing to json file and upload to S3
    filename = str(siteid) + "_" + url.replace("?", "_").replace("*", "").replace(":", "").replace("/", "_").replace('"', '').replace('<', '').replace('>', '').replace('|', '') + ".json"
    with open(filename, "w") as outfile:
        outfile.write(json_object)
    return url


crawl(10000, "https://uh.edu/financial/")
