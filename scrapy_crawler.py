# https://stackoverflow.com/a/37250823/8094047
# https://stackoverflow.com/q/65226497/8094047
# https://github.com/scrapy-plugins/scrapy-playwright
# https://docs.scrapy.org/en/latest/topics/broad-crawls.html
# https://github.com/rafyzg/scrapy-requests
# https://docs.scrapy.org/en/latest/topics/extensions.html

import logging
import pickle

from requests_html import HTMLResponse
from scrapy import Spider
from scrapy.http import Response
from scrapy.signals import spider_closed
from scrapy_requests import HtmlRequest

from data_structure import Processed_Search_Engine_Index, Raw_Search_Engine_Index

MAX_PAGECOUNT = 100
# Quoting Scrapy docs:
# "When a certain closing condition is met,
# requests which are currently in the downloader queue
# (up to CONCURRENT_REQUESTS requests) are still processed."


class WebSpider(Spider):
    name = "webspider"

    custom_settings = {
        "SCHEDULER_PRIORITY_QUEUE": "scrapy.pqueues.DownloaderAwarePriorityQueue",
        "CONCURRENT_REQUESTS": 100,
        "REACTOR_THREADPOOL_MAXSIZE": 20,
        "LOG_LEVEL": "INFO",
        "COOKIES_ENABLED": False,
        "RETRY_ENABLED": False,
        "DOWNLOAD_TIMEOUT": 15,
        "AJAXCRAWL_ENABLED": True,
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_requests.RequestsMiddleware": 800,
        },
        "EXTENSIONS": {
            "scrapy.extensions.closespider.CloseSpider": 500,
        },
        "CLOSESPIDER_PAGECOUNT": MAX_PAGECOUNT,
        "DEFAULT_SCRAPY_REQUESTS_SETTINGS": {
            "browser_args": ["--no-sandbox"],
        },
    }

    def __init__(self):
        super().__init__()
        self.raw_search_engine_index = Raw_Search_Engine_Index()

    def start_requests(self):
        yield HtmlRequest(
            url="https://www.wikipedia.org", callback=self.parse, render=True
        )

    def parse(self, response: Response):
        page: HTMLResponse = response.request.meta["page"]
        self.log(f"Parsing {response.request.url}", level=logging.INFO)

        html = page.html

        self.raw_search_engine_index.add_website(html)

        for link in html.absolute_links:
            yield HtmlRequest(url=link, callback=self.parse, render=True)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(WebSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.closed, signal=spider_closed)
        return spider

    def closed(self, reason):
        processed_search_engine_index = Processed_Search_Engine_Index(
            self.raw_search_engine_index
        )
        with open("search_engine_index.pickle", "wb") as f:
            pickle.dump(processed_search_engine_index, f)
