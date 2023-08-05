import pickle
from time import perf_counter

from requests_html import HTMLSession
from tqdm import tqdm

from data_structure import Processed_Search_Engine_Index, Raw_Search_Engine_Index

MAX_INDEXES = 100


session = HTMLSession()
url_stack = ["https://www.wikipedia.org"]
raw_search_engine_index = Raw_Search_Engine_Index()
visited_urls = set()
num_indexes = 0


def crawl():
    with tqdm(total=MAX_INDEXES) as pbar:
        global num_indexes
        while num_indexes < MAX_INDEXES:
            if len(url_stack) == 0:
                break

            url = url_stack.pop()
            if url in visited_urls:
                continue
            visited_urls.add(url)
            try:
                response = session.get(url)
                if response.status_code != 200:
                    continue

                html = response.html
                html.render()
                raw_search_engine_index.add_website(html)
                num_indexes += 1
                pbar.update(1)

                for link in html.absolute_links:
                    url_stack.append(link)

            except Exception:
                # We print new line because tqdm doesn't print new line after printing progress bar
                print(f"\nFailed URL {url}")


def main():
    t0 = perf_counter()
    crawl()
    t1 = perf_counter()
    print(f"Crawled {num_indexes} websites in {t1 - t0} seconds")

    t0 = perf_counter()
    processed_search_engine_index = Processed_Search_Engine_Index(
        raw_search_engine_index
    )
    t1 = perf_counter()
    print(f"Processed search engine index in {t1 - t0} seconds")

    with open("search_engine_index.pickle", "wb") as f:
        pickle.dump(processed_search_engine_index, f)


if __name__ == "__main__":
    main()
