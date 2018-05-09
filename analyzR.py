# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 10:23:27 2018

@author: Navid.Bahmanyar
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

ORDER = 'sura_order.csv'

ldf = pd.read_csv('letterdf.csv')
sura_order = pd.read_csv(ORDER, sep=",", low_memory=False)
ldf = ldf.query('tgv > 0')
ldf = pd.merge(ldf, sura_order, how='inner', on=['sura'])

# create new order index
ldf.sort_values(['sura','verse'], inplace=True)
ldf['seq_l_index'] = np.arange(1, len(ldf)+1)
ldf.sort_values(['sura_order','verse'], inplace=True)
ldf['chron_l_index'] = np.arange(1, len(ldf)+1)
ldf.sort_values(['sura','verse'], inplace=True)

pltd = ldf.query('tgv==3')

plt.figure()
distchron = sns.distplot(pltd.chron_l_index, kde=False, bins=24)
distchron.set(ylabel='Count of Alef', title="Distribution of Alef's Across Quran by Chronological Index of Letter")
plt.xlabel('Chronological Index')
plt.savefig('assets/cronl.png')

plt.figure()
distseq = sns.distplot(pltd.seq_l_index, kde=False, bins=24)
distseq.set(ylabel='Count of Alef', title="Distribution of Alef's Across Quran by Sequential Index of Letter")
plt.xlabel('Sequential Index')
plt.savefig('assets/seql.png')