# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 10:23:27 2018

@author: Navid.Bahmanyar
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

ldf = pd.read_csv('letterdf.csv')
pltd = ldf.query('tgv==3')

plt.figure()
distchron = sns.distplot(pltd.chron_index, kde=False, bins=24)
distchron.set(ylabel='Count of Alef', title="Distribution of Alef's Across Quran by Chronological Index of Verse")
plt.xlabel('Chronological Index (1 through 6234)')
plt.savefig('cron.png')

plt.figure()
distseq = sns.distplot(pltd.seq_index, kde=False, bins=24)
distseq.set(ylabel='Count of Alef', title="Distribution of Alef's Across Quran by Sequential Index of Verse")
plt.xlabel('Sequential Index (1 through 6234)')
plt.savefig('seq.png')