# import libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from time import sleep
from random import randint

###########################
# GET STARTING DATAFRAME
###########################

#Loop to go over all pages
pages = np.arange(1, 80, 1)
data=[]

for page in pages:
    page = requests.get("https://www.kijiji.ca/b-appartement-condo/ville-de-montreal/" + str(page) + "/c37l1700281?radius=10.0&ad=offering&address=Montr%C3%A9al%2C+QC+H2W+1S8&ll=45.503905,-73.570856")
    soup = BeautifulSoup(page.text, 'html.parser')
    my_table = soup.find_all(class_=['price', 'distance', 'details'])
    sleep(randint(2,10))

    for tag in my_table:
        data.append(tag.text.strip())

#Creating columns
location = data[1::3]
size = data[2::3]
price = data[0::3]


df=pd.DataFrame()
df['size'] = size
df['distance_center'] = location
df['price'] = price

df.to_csv(r'C:\Users\st-am\OneDrive\Documents\Data analytics\web_scrapping\apartments111.csv', index = False)

####################################
# DATA CLEANING
####################################

#Clean size
df['size']=pd.to_numeric(df['size'].str.extract('(\d+)', expand=False))
df['size']+=0.5

#Clean location
df['distance_center']=pd.to_numeric(df['distance_center'].str.extract('(\d+)', expand=False))
df['distance_center'] = df['distance_center'].fillna(1)

#Clean price
new=[]
for i in range(0,len(df)):
    strings = ''.join([i for i in df.price[i] if  i.isdigit()])
    strings = strings[:-2]
    new.append(pd.to_numeric(strings))

df['price'] = new
df['price'].replace('', np.nan, inplace=True)

#Clean all and remove outliers
df=df.dropna()
df = df[df['price'] < 10000]  

####################################
# DATA VIZ
####################################

import seaborn as sns

df['price'].mean()

#Distribution of the prices
sns.set(font_scale=1.2)
sns.distplot(df['price'], color="red", axlabel='Prices ($)').set(title='Distribution of Prices')

#Heatmap of prices
some_flats = df[(df['price']<3000) & (df['size']!= 7.5)]     
heat = some_flats.pivot_table("price", "size", "distance_center")
sns.heatmap(heat).set(title='Price Heatmap')

#Distance to center vs price
plots=sns.lineplot(x=df["distance_center"], y=df["price"], color='red').set(title='Price by Distance to Downtown')
plots.set(xlabel='Distance to Downtown', ylabel='Price ($)')

#Price per size
plot1 = df.groupby('size')['price'].mean().plot(kind='bar', figsize=(10,5), color='salmon',\
                                                title='Average Price by Size')
plot1.set_xlabel("Size",fontsize=14)
plot1.set_ylabel("Price ($)",fontsize=14)
plot1.title.set_size(16)

#Number of apartments by size
plot2=df['size'].value_counts().plot(kind='barh', color='salmon',figsize=(13,7),\
                                     title='Apartments available by size')
plot2.set_xlabel("Number of Apartments",fontsize=14)
plot2.set_ylabel("Size",fontsize=14)
plot2.title.set_size(16)

totals = []

for i in plot2.patches:
    totals.append(i.get_width())
    
total = sum(totals)
for i in plot2.patches:
    plot2.text(i.get_width()+-.7, i.get_y()+.3, \
            str(round((i.get_width()/total)*100, 1))+'%', fontsize=15,
color='black')
plot2.invert_yaxis()
