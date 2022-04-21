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
    return data_list

def wsb_into_db(cur, conn, list):
    cur.execute("DROP TABLE IF EXISTS wsb")
    cur.execute("CREATE TABLE wsb (name TEXT, sentiment TEXT, sentimentscore INTEGER, comments INTEGER)")
    for s in list:
        cur.execute("INSERT INTO wsb (name,sentiment,sentimentscore,comments) VALUES (?,?,?,?)",(s['ticker'],s['sentiment'],s['sentiment_score'],s['no_of_comments']))
    conn.commit()


def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('stocks.db')
    data = get_reddit_stocks()
    wsb_into_db(cur, conn, data)

    
    
if __name__ == "__main__":
    main()
