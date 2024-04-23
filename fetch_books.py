import os
import time

import pandas as pd
import requests
from joblib import Parallel, delayed
from tqdm import tqdm
import re
from fake_useragent import UserAgent

output_path = "books/"
start_book_prefix = r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK [^*]+\*\*\*"
end_book_prefix = r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK [^*]+\*\*\*"


def download_book(gutenberg_id, url, title):
    ua = UserAgent()
    ua_chrome = ua.chrome
    response = requests.get(url, headers={"User-Agent": ua_chrome})
    time.sleep(0.3)
    data = response.text
    clean_data = re.split(start_book_prefix, data)
    clean_data = clean_data[1]
    clean_data = re.split(end_book_prefix, clean_data)[0].strip()
    with open(f'{output_path}/{gutenberg_id}.txt', 'w') as f:
        f.write(clean_data)


if __name__ == "__main__":
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    df = pd.read_csv("book_summaries.csv", sep='\t')
    parallel = Parallel(n_jobs=2, backend="loky")
    parallel(delayed(download_book)(gutenberg_id=df.iloc[i]["gutenberg_id"], url=df.iloc[i]["plain_text_url"],
                                    title=df.iloc[i]["gutenberg_title"]) for i in tqdm(range(len(df))))
