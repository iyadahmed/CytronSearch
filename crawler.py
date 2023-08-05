import pickle
from traceback import print_exc

from requests_html import HTMLSession
from tqdm import tqdm

from data_structure import Processed_Search_Engine_Index, Raw_Search_Engine_Index

MAX_ITERATIONS = 100


session = HTMLSession()
url_stack = ["https://www.wikipedia.org"]
raw_search_engine_index = Raw_Search_Engine_Index()
visited_urls = set()


def main():
    for _ in tqdm(range(MAX_ITERATIONS)):
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
            for link in html.absolute_links:
                url_stack.append(link)

        except Exception:
            print_exc()

    processed_search_engine_index = Processed_Search_Engine_Index(
        raw_search_engine_index
    )
    with open("search_engine_index.pickle", "wb") as f:
        pickle.dump(processed_search_engine_index, f)


if __name__ == "__main__":
    main()
