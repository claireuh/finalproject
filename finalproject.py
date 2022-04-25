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
def get_reddit_stocks(date):
    url = f'https://tradestie.com/api/v1/apps/reddit?date={date}'
    response = requests.get(url)
    data = response.text
    data_list = json.loads(data)
    return data_list[:25]

def wsb_into_db(cur, conn, list, name):
    cur.execute(f"DROP TABLE IF EXISTS {name}")
    cur.execute(f"CREATE TABLE {name} (name TEXT, sentiment TEXT, sentimentscore INTEGER, comments INTEGER)")
    for s in list:
        cur.execute(f"INSERT INTO {name} (name,sentiment,sentimentscore,comments) VALUES (?,?,?,?)",(s['ticker'],s['sentiment'],s['sentiment_score'],s['no_of_comments']))
    conn.commit()


#S&P api

#5dbe879de68dbe57111390b991d08988

def get_sstock():
    url = 'http://api.marketstack.com/v1/eod?access_key=5dbe879de68dbe57111390b991d08988&symbols=VOO&limit=25'
    response = requests.get(url)
    data = response.text
    data_list = json.loads(data)
    return data_list

def get_sstock():
    url = 'http://api.marketstack.com/v1/eod?access_key=5dbe879de68dbe57111390b991d08988&symbols=VOO&limit=25'
    response = requests.get(url)
    data = response.text
    data_list = json.loads(data)
    return data_list

#Open
#Close
#Volume
#Date


def get_data_to_databse(cur,conn,data_list):
    cur.execute("DROP TABLE IF EXISTS voo")
    cur.execute("CREATE TABLE voo (symbol TEXT, open REAL, close REAL, volume INTEGER, date TEXT)")
    for i in data_list['data']:
        cur.execute("INSERT INTO voo (symbol,open,close,volume,date) VALUES (?,?,?,?,?)",(i['symbol'],i['open'],i['close'],i['volume'],i['date']))
    conn.commit()


#VOO Calculation
#SWITCH 410 TO THE {AVG_CLOSE} VARIABLE
def find_average_volume_from_high_price_low_price(cur,conn):
    #Finds the average Closing price for the voo
    cur.execute("""SELECT AVG(close) FROM voo""")
    avg_close = cur.fetchall()

    #Finds the average volume for when price is below the average closing price
    cur.execute("""SELECT AVG(volume) FROM voo WHERE close > 410""")
    avg_volume_above = cur.fetchall()
    print(avg_volume_above)

    #Finds the average volume for when price is above the average closing price 
    cur.execute("""SELECT AVG(volume) FROM voo WHERE close < 410""")
    avg_volume_below = cur.fetchall()
    print(avg_volume_below)
    
  
#VOO boxplot
def visualizations_voo(cur,conn):
    #Finds the average Closing price for the voo
    cur.execute("""SELECT AVG(close) FROM voo""")
    avg_close = cur.fetchall()

    #Finds the volume for when price is below the average closing price
    cur.execute("""SELECT volume FROM voo WHERE close > 410""")
    volume_above2 = cur.fetchall()

    #Finds the volume for when price is above the average closing price 
    cur.execute("""SELECT volume FROM voo WHERE close < 410""")
    volume_below2 = cur.fetchall()

    volume_above = []
    volume_below = []
    for i in volume_above2:
        volume_above.append(i[0])
    for i in volume_below2:
        volume_below.append(i[0])
    print(volume_above)
    #Creates BoxPlot
    data = [volume_below,volume_above]
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
               alpha=0.5)
    ax1.set(
        axisbelow=True,  # Hide the grid behind plot objects
        xlabel='Volume Data',
        ylabel='Volume Traded (in millions)',
    )
    labels = ['Volume below average closing price', 'Volume above average closing price']
    ax1.set_xticklabels(np.repeat(labels,1),
                    rotation=0, fontsize=8)
    # Creating plot
    plt.boxplot(data)
    plt.title("Boxplot of volumes when price is below and above average closing price")
    # show plot
    plt.show()








def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('stocks.db')
   
    # #wsb
    wsbtoday = get_reddit_stocks('2022-04-22')
    wsbmonthago = get_reddit_stocks('2022-03-22')
    wsb_into_db(cur, conn, wsbtoday, 'wsbtoday')
    wsb_into_db(cur, conn, wsbmonthago, 'wsbmonthago')
    cur.execute(f"DROP TABLE IF EXISTS wsb")
    cur.execute(f"DROP TABLE IF EXISTS {wsbtoday}")
    cur.execute(f"DROP TABLE IF EXISTS {wsbmonthago}")
    
    # #s&p
    # data_list = get_sstock()
    # get_data_to_databse(cur,conn,data_list)
    print(find_average_volume_from_high_price_low_price(cur,conn))
    print(visualizations_voo(cur,conn))
    
if __name__ == "__main__":
    main()
