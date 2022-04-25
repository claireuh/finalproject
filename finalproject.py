#final project
#Claire, Jack, Peter

import requests
import matplotlib.pyplot as plt
import os
import sqlite3
import unittest
import numpy as np
import json
from xml.sax import parseString




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
    cur.execute(f"CREATE TABLE IF NOT EXISTS {name} (name TEXT UNIQUE, sentiment TEXT, sentimentscore INTEGER, comments INTEGER)")
    for s in list:
        cur.execute(f"INSERT OR IGNORE INTO {name} (name,sentiment,sentimentscore,comments) VALUES (?,?,?,?)",(s['ticker'],s['sentiment'],s['sentiment_score'],s['no_of_comments']))
    conn.commit()


#S&P api

#5dbe879de68dbe57111390b991d08988

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
    cur.execute("CREATE TABLE IF NOT EXISTS voo (open REAL, close REAL, volume INTEGER, date TEXT)")
    for i in data_list['data']:
        cur.execute("INSERT OR IGNORE INTO voo (open,close,volume,date) VALUES (?,?,?,?)",(i['symbol'],i['open'],i['close'],i['volume'],i['date']))
    conn.commit()
    

#VOO Calculation
#SWITCH 410 TO THE {AVG_CLOSE} VARIABLE
def find_average_volume_from_high_price_low_price(cur,conn):
    #Finds the average Closing price for the voo
    cur.execute("""SELECT AVG(close) FROM voo""")
    avg_close = cur.fetchall()

    #Finds the average volume for when price is below the average closing price
    cur.execute("""SELECT AVG(volume) FROM voo WHERE close > '{avg_close}' """)
    avg_volume_above = cur.fetchall()
    print(avg_volume_above)

    #Finds the average volume for when price is above the average closing price 
    cur.execute("""SELECT AVG(volume) FROM voo WHERE close < '{avg_close}' """)
    avg_volume_below = cur.fetchall()
    print(avg_volume_below)
    
  
#VOO boxplot
def visualizations_voo(cur,conn):
    #Finds the average Closing price for the voo
    cur.execute("""SELECT AVG(close) FROM voo""")
    avg_close = cur.fetchall()

    #Finds the volume for when price is below the average closing price
    cur.execute("""SELECT volume FROM voo WHERE close > '{avg_close}' """)
    volume_above2 = cur.fetchall()

    #Finds the volume for when price is above the average closing price 
    cur.execute("""SELECT volume FROM voo WHERE close < '{avg_close}' """)
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




#analyst_rating
#price_change_percent_1d
#price_change_percent_1m
#symbol


def hotstocks():
    url = "https://hotstoks-sql-finance.p.rapidapi.com/query"
    
    payload = """SELECT * FROM stocks
                WHERE price <= 10 
                AND volume_avg_10d_percent_diff > 20
                ORDER BY market_cap DESC, volume_avg_10d_percent_diff DESC 
                LIMIT 25"""
    
    headers = {
        "content-type": "text/plain",
        "X-RapidAPI-Host": "hotstoks-sql-finance.p.rapidapi.com",
        "X-RapidAPI-Key": "15d6f5c74cmsh147566a8e4a1e04p138f5djsn688bfbde4bea"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    response = response.text
    response = json.loads(response)
    return response

def put_data_in_database(cur, conn, response):
    cur.execute("CREATE TABLE IF NOT EXISTS hotstocks (rating TEXT, percentchangeday TEXT, percentchangemonth TEXT, symbol TEXT UNIQUE)")
    for i in response['results']:
        cur.execute("INSERT OR IGNORE INTO hotstocks (rating,percentchangeday,percentchangemonth,symbol) VALUES (?,?,?,?)",(i['analyst_rating'], i['price_change_percent_1d'], i['price_change_percent_1m'], i['symbol']))
    conn.commit()
    


def wsbdata(cur, conn):
    cur.execute('SELECT wsbtoday.name, wsbmonthago.comments, wsbtoday.comments FROM wsbmonthago JOIN wsbtoday ON wsbmonthago.name = wsbtoday.name')
    sentimentscore = cur.fetchall()
    print('wsb1')
    print(sentimentscore)



#getting the names of stocks that were bullish 1 month ago
def wsbdata2(cur, conn):
    cur.execute('SELECT wsbmonthago.name FROM wsbmonthago WHERE sentimentscore > 0')
    data = cur.fetchall()
    print("Stocks that were bullish 1 month ago in WSB")
    print(data)
    print()



def hotstockdata(cur, conn):
    cur.execute("""SELECT hotstocks.rating, hotstocks.percentchangemonth FROM hotstocks WHERE rating LIKE '%Buy%'""")
    data_buy = cur.fetchall()
    print("hotstocks")
    print(data_buy)

def voodata(cur, conn):
    cur.execute("""SELECT AVG(close) FROM voo""")
    avg_close = cur.fetchall()
    avg_close = avg_close[0][0]
    print(avg_close)

    #Finds the volume for when price is below the average closing price
    cur.execute(f"""SELECT volume FROM voo WHERE close > {avg_close} """)
    volume_above2 = cur.fetchall()
    print(volume_above2)

    #Finds the volume for when price is above the average closing price 
    cur.execute(f"""SELECT volume, close FROM voo WHERE close < {avg_close} """)
    volume_below2 = cur.fetchall()
    print(volume_below2)


def write_csv(data_dict, file_name):
    path = os.path.dirname(os.path.abspath(__file__))
    f = open(path + "/" + file_name, "w")
    f.write("""We are able to use SQL select statements to calculate important indicators of VOO (Vanguard 500).The indicator we 
    where able to calculate was the volume traded when the price was below and above the average closing price. We were able to calculate the average volume for when the price was 
    below the average closing price, and calculate the average volume when the price was above the average closing price. When doing """)
    


def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('stocks.db')
   
    #wsb
    wsbtoday = get_reddit_stocks('2022-04-22')
    wsbmonthago = get_reddit_stocks('2022-03-22')
    wsb_into_db(cur, conn, wsbtoday, 'wsbtoday')
    wsb_into_db(cur, conn, wsbmonthago, 'wsbmonthago')
    
    
    # #s&p
    # data_list = get_sstock()
    # get_data_to_databse(cur,conn,data_list)
    # print(find_average_volume_from_high_price_low_price(cur,conn))
    # print(visualizations_voo(cur,conn))

    #hotstocks data

    #getting the data
    cur.execute("DROP TABLE IF EXISTS hotstocks")
    response = hotstocks()
    # print(response)
    put_data_in_database(cur, conn, response)


    #calling the data
    hotstockdata(cur,conn)
    wsbdata2(cur,conn)
    wsbdata(cur, conn)
    voodata(cur,conn)
if __name__ == "__main__":
    main()