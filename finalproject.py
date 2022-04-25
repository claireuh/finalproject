#final project
#Claire, Jack, Peter

import requests
import matplotlib.pyplot as plt
import os
import sqlite3
import unittest
import numpy as np
import json



def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


#wallstreetbets api
def get_reddit_stocks():
    url = 'https://tradestie.com/api/v1/apps/reddit'
    response = requests.get(url)
    data = response.text
    data_list = json.loads(data)
    return data_list[:25]

def wsb_into_db(cur, conn, list):
    cur.execute("DROP TABLE IF EXISTS wsb")
    cur.execute("CREATE TABLE wsb (name TEXT, sentiment TEXT, sentimentscore INTEGER, comments INTEGER)")
    for s in list:
        cur.execute("INSERT INTO wsb (name,sentiment,sentimentscore,comments) VALUES (?,?,?,?)",(s['ticker'],s['sentiment'],s['sentiment_score'],s['no_of_comments']))
    conn.commit()


#S&P api

#5dbe879de68dbe57111390b991d08988

def get_sstock():
    url = 'http://api.marketstack.com/v1/eod?access_key=5dbe879de68dbe57111390b991d08988&symbols=VOO&limit=25'
    response = requests.get(url)
    data = response.text
    data_list = json.loads(data)
    limited_data = {}
    i = 0
    for d in data_list:
        if i < 25:
            limited_data[d] = data_list[d]
            i += 1
    return limited_data


#Open
#Close
#Volume
#Date


def get_data_to_databse(cur,conn,data_list):
    cur.execute("DROP TABLE IF EXISTS voo")
    cur.execute("CREATE TABLE voo (open REAL, close REAL, volume INTEGER, date TEXT)")
    for i in data_list['data']:
        cur.execute("INSERT INTO voo (open,close,volume,date) VALUES (?,?,?,?)",(i['open'],i['close'],i['volume'],i['date']))
    conn.commit()










def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('stocks.db')
   
    #wsb
    wsbdata = get_reddit_stocks()
    wsb_into_db(cur, conn, wsbdata)

    #s&p
    data_list = get_sstock()
    get_data_to_databse(cur,conn,data_list)
    
if __name__ == "__main__":
    main()
