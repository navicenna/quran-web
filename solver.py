"""
Module for solving the alef count

Started 2/28/2018
"""

import pandas as pd
from pprint import pprint
import seaborn as sns, numpy as np


infile = 'eng_quran_out.txt'


qdf = pd.read_csv(infile, sep="|", low_memory=False, header=None)
qdf.columns = ['sura', 'verse', 'arabic', 'english']
x = 'fox jumped over'

#pprint(df.head())



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


def sura_to_df(qdf, sura):
    sura_df = qdf.query('sura == {}'.format(sura))
    df_list = []
    for df_row in sura_df.itertuples():
        df_list.append(verse_to_df(df_row.arabic, df_row.sura, df_row.verse))
    return pd.concat(df_list, ignore_index=True)


def quran_to_df():
    pass
    

#ldf = verse_to_df(qdf.iloc[0,2], 1, 1)
ldf = sura_to_df(qdf, 1)



