# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 19:02:18 2018

@author: Nav
"""

import pandas as pd
import seaborn as sns
from pandasql import sqldf
from funcs import calc_val, transString

# Read in datafiles
ldf = pd.read_csv('letter_df.csv')


# Create summary by letter
q = '''select sura, letters as letter, count(*) as letter_count
    from ldf 
    group by sura, letters 
    order by sura, letters;
    '''
pysqldf = lambda q: sqldf(q, globals())
ldfsum = pysqldf(q)
ldfsum['tgv'] = ldfsum['letter'].apply(lambda x: calc_val(transString(x), 'tgv'))
ldfsum = ldfsum.query('tgv > 0')


# Create TGV plotting dataset
q = '''select min(letter) as letter, tgv, sum(letter_count) as count
    from ldfsum
    group by tgv
    order by tgv;
    '''
tgv_plotting_df = pysqldf(q)
letters = [transString(l) for l in tgv_plotting_df['letter'].tolist()]

# Create plot
sns.lmplot( x="tgv", y="count", 
           data=tgv_plotting_df, fit_reg=False, hue='tgv', 
           legend=False )
            #, markers=letters)
