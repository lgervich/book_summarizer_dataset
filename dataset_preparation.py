import urllib

import pandas as pd
import requests
from joblib import Parallel, delayed
from tqdm import tqdm


def search_book(author, title):
    # Construct the search query
    query = urllib.parse.quote_plus(f"{author} {title}")

    # Make the API request
    response = requests.get(f"https://gutendex.com/books/?search={query}")

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Check if any results were found
        if data["count"] > 0:
            # Print information about each matching book
            try:
                results = list(filter(lambda x: x['media_type'] == 'Text', data["results"]))
                if len(results) > 0:
                    book = results[0]
                    gutenberg_id = book['id']
                    gutenberg_title = book['title']
                    gutenberg_authors = ";".join(map(lambda author: author["name"], book.get("authors", [])))
                    plain_text_url = book['formats'].get('text/plain; charset=us-ascii') or book['formats'].get('text/plain')
                    return {
                        "gutenberg_id": gutenberg_id,
                        "gutenberg_title": gutenberg_title,
                        "gutenberg_authors": gutenberg_authors,
                        "plain_text_url": plain_text_url,
                    }
            except KeyError:
                print(book)
        else:
            print("No results found.")
    else:
        print("Error: Failed to fetch data from the API.")
    return {
            "gutenberg_id": None,
            "gutenberg_title": None,
            "gutenberg_authors": None,
            "plain_text_url": None,
        }


# Example usage
if __name__ == "__main__":
    df = pd.read_csv("booksummaries/booksummaries.txt", sep='\t', header=None, names=[
        "wiki_id",
        "freebase_id",
        "title",
        "author",
        "publish_date",
        "genres",
        "plot_summary"

    ])
    df = df[(df['publish_date'] > '1800-01-01') & (df['publish_date'] < '1900-01-01')]
    # df = df.head(n=1)
    parallel = Parallel(n_jobs=4, backend="loky")
    output = parallel(delayed(search_book)(author=df.iloc[i]["author"], title=df.iloc[i]["title"]) for i in tqdm(range(len(df))))
    gutenberg_df = pd.DataFrame.from_dict(output)
    gutenberg_df.index = df.index
    target_df = pd.concat([df, gutenberg_df], axis=1)
    filtered_df = target_df[target_df['plain_text_url'].notnull()]
    filtered_df.to_csv('book_summaries.csv', index=False, sep='\t')
