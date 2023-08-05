from dataclasses import dataclass, field
from collections import defaultdict
from typing import List, DefaultDict

from heapq import heappush, heappop

from requests_html import HTML


class Priority_Queue:
    def __init__(self):
        self._queue = []

    def empty(self):
        return self.size() == 0

    def size(self):
        return len(self._queue)

    def put(self, item):
        heappush(self._queue, item)

    def get(self):
        return heappop(self._queue)


@dataclass
class Raw_Search_Engine_Index:
    urls: List[str] = field(default_factory=list)
    # Maps keyword to a map of url_index to number of times the keyword appears in the website at url
    keyword_index: DefaultDict[str, DefaultDict[int, int]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(lambda: 0))
    )

    def add_website(self, html: HTML):
        # This assumes the html is already rendered (i.e. html.render() has been called)
        url_index = len(self.urls)
        self.urls.append(html.url)

        for keyword in html.text.split():
            self.keyword_index[keyword.lower()][url_index] += 1


@dataclass(order=True)
class Processed_Search_Engine_Index_Priority_Queue_Item:
    url_priority: int
    url_index: int = field(compare=False)


class Processed_Search_Engine_Index:
    def __init__(self, raw_search_engine_index: Raw_Search_Engine_Index):
        self.urls = raw_search_engine_index.urls

        # Maps keyword to a priority queue of (url_priority, url_index) pairs
        # where url_priority is the -1 * number of times the keyword appears in the website at url
        # we negated the priority so that we get the website with most occurrences of the keyword
        # when we pop from the priority queue (because Python's PriorityQueue is a min heap, we want a max heap)
        self.keyword_index: defaultdict[str, Priority_Queue] = defaultdict(
            Priority_Queue
        )

        for keyword, keyword_count_map in raw_search_engine_index.keyword_index.items():
            for url_index, keyword_count in keyword_count_map.items():
                self.keyword_index[keyword].put(
                    Processed_Search_Engine_Index_Priority_Queue_Item(
                        -keyword_count, url_index
                    )
                )
