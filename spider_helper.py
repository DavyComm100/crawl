# -*- coding: utf-8 -*-

# import time

import trafilatura
import sys
from urllib.parse import urlparse

from trafilatura.spider import focused_crawler
from utils import *


def crawl(homepage, save_path):
    all_contents = []

    to_visit, known_urls = focused_crawler(homepage, max_seen_urls=sys.maxsize, max_known_urls=sys.maxsize)
    logger.info("to spider cnt: {}".format(len(known_urls)))

    for url in known_urls:
        if not url.startswith(homepage):
            continue
        logger.info("start fetching: {}".format(url))

        downloaded = trafilatura.fetch_url(url)
        result = trafilatura.extract(downloaded)

        if result is not None and result.strip() != "":
            local_domain = urlparse(url).netloc
            file_name_text = url[url.index(local_domain) + len(local_domain) + 1:].replace("/", "_").replace('-', ' ').replace('_', ' ').replace('#update', '').replace("#", " ").strip()

            text = file_name_text + "\n" + result
            all_contents.append(text.strip())

    if len(all_contents) > 0:
        with open(save_path, 'w') as file:
            file.write("\n\n".join(all_contents).strip())
    return save_path

# start_t = time.time()
# print(crawl("https://uh.edu/financial/", "test/test_spi.txt"))
# print("cost: {}".format(time.time() - start_t))
