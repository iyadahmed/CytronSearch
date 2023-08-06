import logging
import pickle

from bs4 import BeautifulSoup
from scrapy import Spider
from scrapy.http import Request, Response
from requests_html import HTML, HTMLSession

from data_structure import Processed_Search_Engine_Index, Raw_Search_Engine_Index

# The spider might crawl more pages than this because of concurrent requests
# and it might crawl less pages when requests fail
TARGET_PAGECOUNT = 100


class CytronSpider(Spider):
    name = "cytron"
    custom_settings = {
        "LOG_LEVEL": "INFO",
        "EXTENSIONS": {
            "scrapy.extensions.closespider.CloseSpider": 500,
        },
        "CLOSESPIDER_PAGECOUNT": TARGET_PAGECOUNT,
        # "DOWNLOADER_MIDDLEWARES": {
        #     "scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware": 500
        # },
        # "AJAXCRAWL_ENABLED": True,
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.raw_search_engine_index = Raw_Search_Engine_Index()
        self.visited_urls = set()
        # We use a session so that only one instance of requests_html.Browser is created
        # self.session = HTMLSession()

    def start_requests(self):
        yield Request(url="https://www.wikipedia.org", callback=self.parse)

    def parse(self, response: Response):
        if response.status != 200:
            return

        html = HTML(html=response.text)
        html.render(retries=1, wait=0)

        soup = BeautifulSoup(html.html, "lxml")
        self.raw_search_engine_index.index(response.url, soup.get_text())

        for link in html.absolute_links:
            if link in self.visited_urls:
                continue
            self.visited_urls.add(link)
            yield Request(url=link, callback=self.parse)

    def closed(self, reason):
        processed_search_engine_index = Processed_Search_Engine_Index(
            self.raw_search_engine_index
        )
        with open("search_engine_index.pickle", "wb") as f:
            pickle.dump(processed_search_engine_index, f)
