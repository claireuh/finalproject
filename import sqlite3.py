import sqlite3
import os
import matplotlib.pyplot as plt
import numpy as np
from itertools import count
import types
from unicodedata import name
import unittest
import json
import requests
import yfinance as yf
import numpy as np 



# https://dashboard.nbshare.io/api/v1/apps/reddit?date=2022-04-03

#Calculates percent Change between first and last item in list
#Takes in list of prices and number of stocks you are taking in {y}
def percent_change_over_entire_period(list_of_prices, number_of_stocks):
    #For if you are doing multiple stocks and taking the average of the percent change
    #Deletes nan values from list_of_prices
    list_of_prices = [x for x in list_of_prices if x == x]
    print(list_of_prices)
    #If there arent two or more values. Delete The stock and get stock number. 
    














    if "NewStock" in list_of_prices:
        count = 0
        skip = []
        num_skip = 0
        list_of_percent_changes = []
        for i in range(len(list_of_prices)):
            if list_of_prices[i] == "NewStock":
                count = 0
                end = list_of_prices[i-1]
                percent_change = (end - start) / start
                list_of_percent_changes.append(percent_change)
                continue
            if count == 0:
                start = list_of_prices[i]
                count += 1
        average_percent_change = sum(list_of_percent_changes) / len(list_of_percent_changes)
        return average_percent_change
    #For if you are doing a single stock and just getting the percent change     
    else:
        start = list_of_prices[0]
        end = list_of_prices[-1]
        percent_change = (end - start) / start
        return percent_change

##Gets Wall Street Bet data from API
def get_api_wallstreetbet(x):
    url = "https://tradestie.com/api/v1/apps/reddit"
    data = requests.get(url)
    data1 = data.text
    data_list = json.loads(data1)
    return data_list


#data = yf.download(tickers="MSFT", period="15m", interval="1m")

#Gets Stock Market Price Data and sees percent change for every 15 minutes
def get_stocks_with_good_setiment_15minute_change(ticker, number_of_stocks, period = "15m", interval = "1m"):
    # Get the data
    for i in ticker:
        data = yf.download(tickers=ticker, period=period, interval=interval)
        list_of_prices = []
        for i , y in data.tail().items():
            if i[1]:
                p = i[1]
                break
        for i , y in data.tail().items():
            for x in y:
                if 'Open' in i:
                    if i[1]:
                        if p == i[1]:
                            list_of_prices.append(x)
                        else:
                            p = i[1]
                            list_of_prices.append("NewStock")
                            list_of_prices.append(x)
    list_of_prices.append("NewStock")
    stock_percent_change = percent_change_over_entire_period(list_of_prices, number_of_stocks)
    return stock_percent_change


#Goes through Wall Street Bet data and gets the stocks with setiment scores above {SS} and returns top {y} (by number of comments) stocks
#Then puts it into get_stocks_with_good_setiment_15_change and returns the stocks percent change
def get_stocks_good_setiment(SS,number_of_stocks=2):

    data_list = get_api_wallstreetbet("cat")
    stocks_good_set = []
    stocks_good_set_ticker = []
    for dic in data_list:
        if dic["sentiment_score"] > SS:
            stocks_good_set.append(dic)
    stocks_good_set_sorted = sorted(stocks_good_set, key=lambda d: d['sentiment_score'], reverse=True) 
    counter = 0
    for i in stocks_good_set_sorted:
        if counter == number_of_stocks:
            break
        else:
            stocks_good_set_ticker.append(i['ticker'])
            counter += 1
    print(stocks_good_set_ticker)
    stock_percent_change = get_stocks_with_good_setiment_15minute_change(stocks_good_set_ticker, number_of_stocks)
    return stock_percent_change


#----------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------
#For stock in the past

# https://dashboard.nbshare.io/api/v1/apps/reddit?date=2022-04-03


#Getting most relevent stocks on different days
##Gets Wall Street Bet data from API
def wall_street_bet_different_days(x, date):
    url = "https://dashboard.nbshare.io/api/v1/apps/reddit?date={}"
    formated_url = url.format(date)
    data = requests.get(formated_url)
    data1 = data.text
    data_list = json.loads(data1)
    return data_list
   
#{Date} = The day you want to look at for the WSB stocks data (format: yyyy-mm-dd). The following day then 7 days after will be the one we take stock price from
#{NOC} = Number of comments (returns over that amount)
#{Sentiment} = Bearish or Bullish
#{SS} = sentiment score (returns over that amount)
#{number_of_stocks} = The amount of stocks you want to return


#Gets the tickers for the stocks you want given the restrictions, for stocks on previous days. Sorted by sentiment score.
def wall_street_bet_get_stock_from_previous_days(date, NOC = 0, Sentiment = "Bullish", SS = 0, number_of_stocks = 2):
    data_list = wall_street_bet_different_days("dog", date)
    print(data_list)
    stocks_good_set = []
    stocks_good_set_ticker = []
    for dic in data_list:
        if dic['no_of_comments'] > NOC:
            if dic['sentiment'] == Sentiment:
                if dic['sentiment_score'] > SS:
                    stocks_good_set.append(dic)
    print(stocks_good_set)
    stocks_good_set_sorted = sorted(stocks_good_set, key=lambda d: d['sentiment_score'], reverse=True) 
    counter = 0
    for i in stocks_good_set_sorted:
        if counter == number_of_stocks:
            break
        else:
            stocks_good_set_ticker.append(i['ticker'])
            counter += 1
    print(stocks_good_set_ticker)
    c = get_stocks_change_in_value_from_WSB_previous_days(stocks_good_set_ticker, date)
    return c


#Takes the stocks from the certain criteria and then gets average change in stock price from a day after criterea was recieved to 7 days later. 
def get_stocks_change_in_value_from_WSB_previous_days(stocks_good_set_ticker, date):
    list_of_prices = []
    ns = 0
    for i in stocks_good_set_ticker:
        data = yf.download(i, start= '2016-06-18', end='2016-06-25')
        for i , y in data.tail().items():
            if i[1]:
                p = i[1]
                break
        for i , y in data.tail().items():
            for x in y:
                if 'Open' in i:
                    if i[1]:
                        if p == i[1]:
                            list_of_prices.append(x)
                            ns = 0
            if ns == 0:
                list_of_prices.append("NewStock")
                ns = 1
    average_percent_change = percent_change_for_stocks_previous_date(list_of_prices)
    return average_percent_change


def percent_change_for_stocks_previous_date(list_of_prices):
    #For if you are doing multiple stocks and taking the average of the percent change

    #Deletes nan values from list_of_prices
    list_of_prices = [x for x in list_of_prices if x == x]

    if "NewStock" in list_of_prices:
        count = 0
        list_of_percent_changes = []
        for i in range(len(list_of_prices)):
            if list_of_prices[i] == "NewStock":
                count = 0
                end = list_of_prices[i-1]
                percent_change = (end - start) / start
                list_of_percent_changes.append(percent_change)
                continue
            if count == 0:
                start = list_of_prices[i]
                count += 1
        average_percent_change = sum(list_of_percent_changes) / len(list_of_percent_changes)
        return average_percent_change
    #For if you are doing a single stock and just getting the percent change     
    else:
        start = list_of_prices[0]
        end = list_of_prices[-1]
        percent_change = (end - start) / start
        return percent_change


#--------------------------------------------------------------
#Databases SQLITE
#--------------------------------------------------------------


#Getting the database ready
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


#Creating Table with Percent Change
def create_table(percent_change,cur,conn):
    cur.execute("""CREATE TABLE IF NOT EXISTS Stocks_Percent_Change(
        id INTEGER PRIMARY KEY,
        Percent_Change INTEGER,
    )""")
    cur.execute("INSERT OR IGNORE INTO Pokemon VALUES(?)",(percent_change))






def main():
    #Test not past stock
    # print(get_stocks_good_setiment(.5, 'no'))

    #Test past stock
    print(wall_street_bet_get_stock_from_previous_days('2016-05-18',10,"Bullish",0,5))
    



if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)