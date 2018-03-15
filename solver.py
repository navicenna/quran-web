"""
Module for solving the alef count

Started 2/28/2018
"""

import pandas as pd
from pprint import pprint
import seaborn as sns, numpy as np


infile = 'eng_quran_out.txt'
sura_order_csv = 'sura_order.csv'




def quran_as_df(infile, sura_order_table):
    qdf = pd.read_csv(infile, sep="|", header=None, quoting=3)
    sura_order = pd.read_csv(sura_order_csv, sep=",", low_memory=False)
    qdf.columns = ['sura', 'verse', 'arabic', 'english']
    qdf = pd.merge(qdf, sura_order, how='inner', on=['sura'])
    qdf['seq_index'] = np.arange(1, len(qdf)+1)
    qdf.sort_values(['sura_order','verse'], inplace=True)
    qdf['chron_index'] = np.arange(1, len(qdf)+1)
    return qdf


def word_to_letter_df(word, sura, verse):
    d = {'sura': sura,
         'verse': verse,
         'letters': list(word),
         'word': word,
        }
    df = pd.DataFrame(d)
    return df


def verse_to_letter_df(verse_text, sura, verse):
    df_list = []
    # i = 1
    for word in verse_text.split():
        df = word_to_letter_df(word, sura, verse)
        df_list.append(df)
    return pd.concat(df_list, ignore_index=True)


def sura_to_letter_df(qdf, sura):
    sura_df = qdf.query('sura == {}'.format(sura))
    df_list = []
    for df_row in sura_df.itertuples():
        df_list.append(verse_to_letter_df(df_row.arabic, df_row.sura, df_row.verse))
    return pd.concat(df_list, ignore_index=True)


def quran_to_letter_df(qdf):
    df_list = []
    for i in range(1,115):
        try:
            df_list.append(sura_to_letter_df(qdf, i))
        except:
            pass
    return pd.concat(df_list, ignore_index=True)

    
if __name__=='__main__':
    df = quran_as_df(infile, sura_order_csv)
#ldf = verse_to_letter_df(qdf.iloc[0,2], 1, 1)
#ldf = quran_to_letter_df(qdf)



