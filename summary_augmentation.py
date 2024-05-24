import urllib

import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm
from textattack.augmentation import WordNetAugmenter, EmbeddingAugmenter, CharSwapAugmenter, CheckListAugmenter, EasyDataAugmenter, CLAREAugmenter


if __name__ == "__main__":
    from textattack.augmentation import WordNetAugmenter
    # needs pip install scipy==1.10.1
    augmenters = {
        "wordnet": WordNetAugmenter(),
        "embedding": EmbeddingAugmenter(),
        "charswap": CharSwapAugmenter(),
        "checklist": CheckListAugmenter(),
        "easydata": EasyDataAugmenter(),
        "clare": CLAREAugmenter(),
    }

    df = pd.read_csv("book_summaries.csv", sep='\t')
    for augmenter_name, augmenter in augmenters.items():
        aug_df = df.copy()
        aug_df["plot_summary"] = aug_df["plot_summary"].apply(lambda x: augmenter.augment(x))
        aug_df.to_csv(f'book_summaries_{augmenter_name}_aug.csv', index=False, sep='\t')

