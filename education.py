import pandas as pd
import matplotlib.pyplot as plt
from pandas.tools.plotting import scatter_matrix
from scipy import stats
import numpy as np
import statsmodels.api as sm
import math
import requests
from pandas.io.json import json_normalize
import sqlite3 as lite
import time  # a package with datetime objects
from dateutil.parser import parse  # a package for parsing a string into a Python datetime object
import collections
import datetime
import pandas.io.sql as psql
from bs4 import BeautifulSoup
import os
import re
import csv

url = "http://web.archive.org/web/20110514112442/http://unstats.un.org/unsd/demographic/products/socind/education.htm"
r = requests.get(url)
soup = BeautifulSoup(r.content)

#for row in soup('table'):
#    print row
#print(soup.prettify())
#print soup('table')[6]

#A = soup('table')[6].findall('tr',{'class': 'tcont'})
A = soup('table')[6].findAll('tr')
#A = soup('table')[6].findall('tr')
#print 'Length of A[6]: ' + str(len(A[6]))
#print 'Length of A: ' + str(len(A)) 

B = [x for x in A if len(x)==25] #removing records without value
records = []

for rows in B:
    col = rows.findAll('td')
    country = col[0].string
    year = col[1].string
    total = col[4].string
    men = col[7].string
    women = col[10].string
    record = (country, year, total, men, women)
    records.append(record)

column_name = ['country', 'year', 'total', 'men', 'women']

table = pd.DataFrame(records, columns = column_name)
#table['year'] = table['year'].map(lambda x: int(x))
table['total'] = table['total'].map(lambda x: int(x))
table['men'] = table['men'].map(lambda x: int(x))
table['women'] = table['women'].map(lambda x: int(x))
print table.describe()
print 'Men Median: ' + str(table['men'].median())
print 'Women Median: ' + str(table['women'].median())

table.hist(column='men')
plt.show()
table.hist(column='women')
plt.show()

columns = ['Country Name','Country Code','Indicator Name','Indicator Code',
           '1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010']
df1999to2010 = pd.read_csv('ny.gdp.mktp.cd_Indicator_en_csv_v2.csv', skiprows=4, usecols=columns)
#print df1999to2010

df1999to2010.set_index('Country Name', inplace=True)
table.set_index('country', inplace=True)
merged = pd.merge(table, df1999to2010, how='inner', left_index=True, right_index=True)
merged['CommonGDP'] = merged.apply(lambda x: x[x['year']], axis=1)
merged.dropna(how='any', axis=0, inplace=True)  #drops rows with nothing in them
#print merged
merged['logGDP'] = np.log(merged['CommonGDP'])

x = np.matrix(merged['logGDP']).transpose()
y = np.matrix(merged['total']).transpose()
X = sm.add_constant(x)
model = sm.OLS(y,X)
f = model.fit()
m = f.params[1]
b = f.params[0]
print m
print b

logGDP = merged['logGDP']
total = merged['total']
merged.plot(kind='scatter', x='logGDP', y='total')
plt.plot(logGDP, b + m*logGDP, '-')
plt.show()
print f.summary()

print 'There is a weak positive correlation between nominal GDP and education life expectancy.'
print 'Generally we can expect that wealthier nations have established education systems.'

