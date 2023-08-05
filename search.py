import sys
import pickle

from data_structure import Processed_Search_Engine_Index


processed_search_engine_index_filepath = sys.argv[1]
keyword = sys.argv[2]


with open(processed_search_engine_index_filepath, "rb") as f:
    processed_search_engine_index: Processed_Search_Engine_Index = pickle.load(f)


print(f"Number of websites indexed: {len(processed_search_engine_index.urls)}")
print(f"Top 10 results for keyword '{keyword}':")
for i in range(10):
    if processed_search_engine_index.keyword_index[keyword].empty():
        break
    url_index = processed_search_engine_index.keyword_index[keyword].get().url_index
    print(processed_search_engine_index.urls[url_index])
