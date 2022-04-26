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
    '''Set up the Database for use throughout the whole program'''
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
        cur.execute("INSERT OR IGNORE INTO voo (open,close,volume,date) VALUES (?,?,?,?)",(i['open'],i['close'],i['volume'],i['date']))
    conn.commit()
    



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
    
#EXTRACTING DATA FROM DATABASE

def wsbdata(cur, conn):
    cur.execute('SELECT wsbtoday.name, wsbmonthago.comments, wsbtoday.comments FROM wsbmonthago JOIN wsbtoday ON wsbmonthago.name = wsbtoday.name')
    comments = cur.fetchall()
    # print('wsb1')
    return comments

#getting the sentiment score of stocks today vs 1 month ago
def wsbdata2(cur, conn):
    cur.execute('SELECT name, sentimentscore FROM wsbtoday ORDER BY sentimentscore DESC')
    bullish_lastmonth = cur.fetchall()
    # print("Stocks that were bullish 1 month ago in WSB")
    return bullish_lastmonth



def hotstockdata(cur, conn):
    cur.execute("""SELECT hotstocks.rating, hotstocks.percentchangemonth FROM hotstocks WHERE rating LIKE '%Buy%'""")
    data_buy = cur.fetchall()
    # print("hotstocks")
    return data_buy

def voodata(cur, conn):
    cur.execute("""SELECT AVG(close) FROM voo""")
    avg_close = cur.fetchall()
    avg_close = avg_close[0][0]

    #Finds the volume for when price is below the average closing price
    cur.execute(f"""SELECT volume FROM voo WHERE close > {avg_close} """)
    volume_above2 = cur.fetchall()

    #Finds the volume for when price is above the average closing price 
    cur.execute(f"""SELECT volume FROM voo WHERE close < {avg_close} """)
    volume_below2 = cur.fetchall()
    
    combinedlist = []
    combinedlist.append(volume_above2)
    combinedlist.append(volume_below2)
    return combinedlist

#WRITING CSVs


def write_csv(datalist, file_name):
    path = os.path.dirname(os.path.abspath(__file__))
    f = open(path + "/" + file_name, "w")
    f.write("Number of comments for stocks a month ago and today")
    f.write('\n')
    f.write("Ticker, Comments a month ago, Comments today\n")
    for i in datalist:
        temp = i[0] + ", " +str(i[1]) + ", " + str(i[2])
        f.write(temp)
        f.write('\n')
    f.close()
    


def write_csv_hot_stocks(datalist, file_name):
    path = os.path.dirname(os.path.abspath(__file__))
    f = open(path + "/" + file_name, "w")
    f.write("""Average percent change of stocks over a month with 'buy' ratings""" )
    f.write('\n')
    f.write('Analyst Rating, Percent Change\n')
    total = 0
    for i in datalist:
        temp = i[0] + ", " + i[1]
        total += float(i[1])
        f.write(temp)
        f.write('\n')
    f.write("average: " + str(total/len(datalist)))
    f.close()

def wsb_sentimentchange(datalist, file_name):
    path = os.path.dirname(os.path.abspath(__file__))
    f = open(path + "/" + file_name, "w")
    # print(datalist)
    f.write("The sentiment of WSB stocks today")
    f.write('\n')
    f.write("Ticker, Sentiment\n")
    for i in datalist:
        temp = i[0] + ", " + str(i[1])
        f.write(temp)
        f.write('\n')
    f.close()

def voo_volume(datalist, file_name):
    path = os.path.dirname(os.path.abspath(__file__))
    f = open(path + "/" + file_name, "w")
    f.write("volumes when price is below and above average closing price\n")
    f.write('Volumes above average,Volumes below average\n')
    for i in range(len(datalist[1])): 
        temp = str(datalist[0][i][0]) + "," + str(datalist[1][i][0])
        f.write(temp)
        f.write('\n')
    f.close()



#VISUALIZATIONS

#data 3 (comments) visualization
def data3vis(csvfile):
    f = open(os.path.abspath(os.path.join(os.path.dirname(__file__), csvfile)))
    lines = f.readlines()
    labels = []
    month = []
    today = []
    for row in lines[2:]:
        val = row.split(",")
        labels.append(val[0].strip())
        month.append(int(val[1].strip()))
        today.append(int(val[2].strip()))
    

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, month, width, label='1 Month ago')
    rects2 = ax.bar(x + width/2, today, width, label='Today')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Number of Comments')
    ax.set_title('Number of Comments on WSB for Stocks One Month Ago vs Today')
    ax.set_xticks(x, labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()


#data 2 visualization barchart:
def data2vis(csvfile):
    f = open(os.path.abspath(os.path.join(os.path.dirname(__file__), csvfile)))
    lines = f.readlines()

    tickers = [] #x axis
    sentiments = [] #y axis
    for row in lines[2:]:
        val = row.split(",")
        tickers.append(val[0])
        sentiments.append(float(val[1]))
    plt.ylabel("Stock Ticker")
    plt.xlabel("Stock Sentiment")
    plt.xticks([-0.4,-0.2,0,0.2,0.4,0.6,0.8,1])
    plt.title("Sentiment of Stocks on Wall Street Bets Today")
    plt.barh(tickers, sentiments)
    plt.tight_layout()
    plt.show()

#VOO boxplot
def visualizations_voo(cur,conn):
    #Finds the average Closing price for the voo
    cur.execute("""SELECT AVG(close) FROM voo""")
    avg_close = cur.fetchall()
    avg_close = avg_close[0][0]

    #Finds the volume for when price is below the average closing price
    cur.execute(f"""SELECT volume FROM voo WHERE close > {avg_close} """)
    volume_above2 = cur.fetchall()

    #Finds the volume for when price is above the average closing price 
    cur.execute(f"""SELECT volume FROM voo WHERE close < {avg_close} """)
    volume_below2 = cur.fetchall()

    volume_above = []
    volume_below = []
    for i in volume_above2:
        volume_above.append(i[0])
    for i in volume_below2:
        volume_below.append(i[0])
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
    labels = ['Volume when price is below average closing price', 'Volume when price is above average closing price']
    ax1.set_xticklabels(np.repeat(labels,1),
                    rotation=0, fontsize=8)
    # Creating plot
    plt.boxplot(data)
    plt.title("Boxplot of volumes when price is below and above average closing price")
    # show plot
    plt.show()



# Hot Stocks Visualizatoin
def hot_stock_vis(cur,conn):
    cur.execute("""SELECT hotstocks.rating, hotstocks.percentchangemonth FROM hotstocks WHERE rating LIKE '%Buy%'""")
    data_buy = cur.fetchall()
    data_buy_change = []
    for i in data_buy:
        data_buy_change.append(float(i[1]))
    cur.execute("""SELECT hotstocks.rating, hotstocks.percentchangemonth FROM hotstocks WHERE rating LIKE '%Hold%'""")
    data_hold = cur.fetchall()
    data_hold_change = []
    for i in data_hold:
        data_hold_change.append(float(i[1]))

     #Creates BoxPlot
    data = [data_buy_change,data_hold_change]
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
                alpha=0.5)
    ax1.set(
            axisbelow=True,  # Hide the grid behind plot objects
            xlabel='Analysis rating',
            ylabel='Percent Change',
        )
    labels = ['Percent change when analyst say to buy', 'Percent change when analysis say to hold']
    ax1.set_xticklabels(np.repeat(labels,1),
                        rotation=0, fontsize=8)
    # Creating plot
    plt.boxplot(data)
    plt.title("Boxplot of percent change in one month based off of analyst rating (penny stocks)")
    # show plot
    plt.show()

# Hot Stocks Visualizatoin2
def hot_stock_vis2(cur,conn):
    cur.execute("""SELECT hotstocks.rating, hotstocks.percentchangeday FROM hotstocks WHERE rating LIKE '%Buy%'""")
    data_buy = cur.fetchall()
    data_buy_change = []
    for i in data_buy:
        data_buy_change.append(float(i[1]))
    cur.execute("""SELECT hotstocks.rating, hotstocks.percentchangeday FROM hotstocks WHERE rating LIKE '%Hold%'""")
    data_hold = cur.fetchall()
    data_hold_change = []
    for i in data_hold:
        data_hold_change.append(float(i[1]))

     #Creates BoxPlot
    data = [data_buy_change,data_hold_change]
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
                alpha=0.5)
    ax1.set(
            axisbelow=True,  # Hide the grid behind plot objects
            xlabel='Analysis rating',
            ylabel='Percent Change',
        )
    labels = ['Percent change when analyst say to buy', 'Percent change when analysis say to hold']
    ax1.set_xticklabels(np.repeat(labels,1),
                        rotation=0, fontsize=8)
    # Creating plot
    plt.boxplot(data)
    plt.title("Boxplot of percent change in one day based off of analyst rating (penny stocks)")
    # show plot
    plt.show()

#MAIN
def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('stocks.db')
   
    #wsb data
    wsbtoday = get_reddit_stocks('2022-04-22')
    wsbmonthago = get_reddit_stocks('2022-03-22')
    wsb_into_db(cur, conn, wsbtoday, 'wsbtoday')
    wsb_into_db(cur, conn, wsbmonthago, 'wsbmonthago')
    
    
    # voo data
    data_list = get_sstock()
    get_data_to_databse(cur,conn,data_list)


    #hotstocks data
    response = hotstocks()
    put_data_in_database(cur, conn, response)


    #calling the data
    data1 = hotstockdata(cur,conn)
    data2 = wsbdata2(cur,conn)
    data3 = wsbdata(cur, conn)
    data4 = voodata(cur,conn)
    
    #writing data to a csv file
    write_csv(data3, 'wsbcomments.csv')
    wsb_sentimentchange(data2, 'wsbsentiment.csv')
    write_csv_hot_stocks(data1, 'hotstocks.csv')
    voo_volume(data4, 'voovolume.csv')

    #calling the visualizations
    data3vis('wsbcomments.csv')
    visualizations_voo(cur,conn)
    hot_stock_vis(cur,conn)
    data2vis('wsbsentiment.csv')
    hot_stock_vis2(cur,conn)


if __name__ == "__main__":
    main()