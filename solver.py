"""
Module for solving the alef count

Started 2/28/2018
"""

import pandas as pd
from pprint import pprint


infile = 'eng_quran_out.txt'


df = pd.read_csv(infile, sep="|", low_memory=False, header=None)
df.columns = ['sura', 'verse', 'arabic', 'english']
x = 'fox jumped over'

pprint(df.head())



def word_to_df(word, sura, verse):
    d = {'sura': sura,
         'verse': verse,
         'letters': list(word),
         'word': word,
        }
    df = pd.DataFrame(d)
    return df


def verse_to_df(verse_text, sura, verse):
    df_list = []
    # i = 1
    for word in verse_text.split():
        df = word_to_df(word, sura, verse)
        df_list.append(df)
    return pd.concat(df_list, ignore_index=True)