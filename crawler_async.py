import asyncio
import pickle
from time import perf_counter

import requests
import requests_html
from requests_html import HTML, AsyncHTMLSession
from tqdm.asyncio import tqdm

from data_structure import Processed_Search_Engine_Index, Raw_Search_Engine_Index

MAX_VISITS = 10
SEED_URL = "https://www.wikipedia.org"

session = AsyncHTMLSession()
raw_search_engine_index = Raw_Search_Engine_Index()
visited_urls = set()


async def crawl_async(progress_bar: tqdm, task_group: asyncio.TaskGroup, url: str):
    try:
        response = await session.get(url)
        if response.status_code != 200:
            return
    except requests.exceptions.ConnectionError:
        print("Failed to connect to", url)
        return

    html: HTML = response.html
    # TODO: render faster by using run_in_executor?
    try:
        await html.arender()
    except requests_html.MaxRetries:
        print("Failed to render", url)
        return

    for link in html.absolute_links:
        if len(visited_urls) >= MAX_VISITS:
            break
        if link in visited_urls:
            continue
        visited_urls.add(link)
        progress_bar.update(1)
        task_group.create_task(crawl_async(progress_bar, task_group, link))

    raw_search_engine_index.add_website(html)


async def main():
    t0 = perf_counter()

    with tqdm(total=MAX_VISITS) as pbar:
        async with asyncio.TaskGroup() as tg:
            visited_urls.add(SEED_URL)
            pbar.update(1)
            tg.create_task(crawl_async(pbar, tg, SEED_URL))

    t1 = perf_counter()
    print(f"Crawled {len(visited_urls)} websites in {t1 - t0} seconds")

    t0 = perf_counter()
    processed_search_engine_index = Processed_Search_Engine_Index(
        raw_search_engine_index
    )
    t1 = perf_counter()
    print(f"Processed search engine index in {t1 - t0} seconds")

    with open("search_engine_index.pickle", "wb") as f:
        pickle.dump(processed_search_engine_index, f)


if __name__ == "__main__":
    session.run(main)
