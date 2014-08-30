#!/usr/bin/python
#/*Copyright (c) 2013 Chris Knorowski <cknorow@gmail.com>
__author__ = 'cknorow@gmail.com (Chris knorowski)'

import os
import sys
import urllib2
from datetime import datetime, timedelta
import ast
import math

marketid ={
    "VTC/BTC": 151,
    "42/BTC": 141,
    "ALF/BTC": 57,
    "AMC/BTC": 43,
    "ANC/BTC": 66,
    "ANC/LTC": 121,
    "ARG/BTC": 48,
    "ASC/LTC": 111,
    "ASC/XPM": 112,
    "BCX/BTC": 142,
    "BET/BTC": 129,
    "BQC/BTC": 10,
    "BTB/BTC": 23,
    "BTE/BTC": 49,
    "BTG/BTC": 50,
    "BUK/BTC": 102,
    "CAP/BTC": 53,
    "CAT/BTC": 136,
    "CENT/XPM": 118,
    "CGB/BTC": 70,
    "CGB/LTC": 123,
    "CLR/BTC": 95,
    "CMC/BTC": 74,
    "CNC/BTC": 8,
    "CNC/LTC": 17,
    "COL/LTC": 109,
    "COL/XPM": 110,
    "CPR/LTC": 91,
    "CRC/BTC": 58,
    "CSC/BTC": 68,
    "DBL/LTC": 46,
    "DEM/BTC": 131,
    "DGC/BTC": 26,
    "DGC/LTC": 96,
    "DMD/BTC": 72,
    "DOGE/BTC": 132,
    "DOGE/LTC": 135,
    "DVC/BTC": 40,
    "DVC/LTC": 52,
    "DVC/XPM": 122,
    "EAC/BTC": 139,
    "ELC/BTC": 12,
    "ELP/LTC": 93,
    "EMD/BTC": 69,
    "EZC/LTC": 55,
    "FFC/BTC": 138,
    "FLO/LTC": 61,
    "FRC/BTC": 39,
    "FRK/BTC": 33,
    "FST/BTC": 44,
    "FST/LTC": 124,
    "FTC/BTC": 5,
    "GDC/BTC": 82,
    "GLC/BTC": 76,
    "GLD/BTC": 30,
    "GLD/LTC": 36,
    "GLX/BTC": 78,
    "GME/LTC": 84,
    "HBN/BTC": 80,
    "IFC/LTC": 60,
    "IFC/XPM": 105,
    "IXC/BTC": 38,
    "JKC/LTC": 35,
    "KGC/BTC": 65,
    "LK7/BTC": 116,
    "LKY/BTC": 34,
    "LOT/BTC": 137,
    "LTC/BTC": 3,
    "MEC/BTC": 45,
    "MEC/LTC": 100,
    "MEM/LTC": 56,
    "MNC/BTC": 7,
    "MOON/BTC": 146,
    "MOON/LTC": 145,
    "MST/LTC": 62,
    "NAN/BTC": 64,
    "NBL/BTC": 32,
    "NEC/BTC": 90,
    "NET/BTC": 134,
    "NET/LTC": 108,
    "NET/XPM": 104,
    "NMC/BTC": 29,
    "NRB/BTC": 54,
    "NVC/BTC": 13,
    "ORB/BTC": 75,
    "OSC/BTC": 144,
    "PHS/BTC": 86,
    "PPC/BTC": 28,
    "PPC/LTC": 125,
    "PTS/BTC": 119,
    "PXC/BTC": 31,
    "PXC/LTC": 101,
    "PYC/BTC": 92,
    "Points/BTC": 120,
    "QRK/BTC": 71,
    "QRK/LTC": 126,
    "RED/LTC": 87,
    "RPC/BTC": 143,
    "RYC/LTC": 37,
    "SBC/BTC": 51,
    "SBC/LTC": 128,
    "SPT/BTC": 81,
    "SRC/BTC": 88,
    "STR/BTC": 83,
    "SXC/LTC": 98,
    "TAG/BTC": 117,
    "TEK/BTC": 114,
    "TGC/BTC": 130,
    "TIPS/LTC": 147,
    "TIX/LTC": 107,
    "TIX/XPM": 103,
    "TRC/BTC": 27,
    "UNO/BTC": 133,
    "WDC/BTC": 14,
    "WDC/LTC": 21,
    "XJO/BTC": 115,
    "XNC/LTC": 67,
    "XPM/BTC": 63,
    "XPM/LTC": 106,
    "YBC/BTC": 73,
    "ZET/BTC": 85,
    "ZET/LTC": 127
}



def _get_time_to_sell(s,last_time,scale=1):
    #get the time to sell last bitcoin
    total = 0
    for x in s['recenttrades']:
        total += float(x['total'])
        if total >= scale*1:
            sell_time = datetime.strptime(x['time'],"%Y-%m-%d %H:%M:%S")
            time_to_sell = (last_time - sell_time).seconds/60.
            if time_to_sell == 0:
                return 0.1
            return time_to_sell
    sell_time = datetime.strptime(s['recenttrades'][-1]['time'],"%Y-%m-%d %H:%M:%S")
    return (last_time - sell_time).seconds/60.

def _get_volume_hour(s,last_time, trade_end):
    #get the volume per half hour
    total = 0
    sell_time = 0
    for x in s['recenttrades']:
        total += float(x['total'])
        sell_time = datetime.strptime(x['time'],"%Y-%m-%d %H:%M:%S")
        if  (last_time - sell_time).seconds >= 30*60:
            return 30.*total/((last_time - sell_time).seconds/(60.))          
    return  total * 30. / trade_end

def _get_liquidity(s, scale=1):
    #get the buy order distribution
    average_buy = 0
    count = 0
    total = 0
    buy_top = float(s['buyorders'][0]['price'])
    weighted_buy = 0
    for x in s['buyorders']:
        total += float(x['total'])
        average_buy += float(x['price'])*float(x['total'])
        count += 1
        if total >= 1*scale:
            return abs((average_buy/count - buy_top))/buy_top
        else: 
            weighted_buy = abs((average_buy/count - buy_top))/buy_top
    return weighted_buy

def _get_purchase(s, scale=1):
    #get the sell order distribution              
    count = 0
    average_sell = 0
    total = 0
    sell_top = float(s['sellorders'][0]['price'])
    weighted_sell = 0
    for x in s['sellorders']:
        total += float(x['total'])
        average_sell += float(x['price'])*float(x['total'])
        count+=1
        if total >= 1*scale:
            return abs((sell_top - average_sell/count))/sell_top
        else:
            weighted_sell = abs((sell_top - average_sell/count))/sell_top
    return weighted_sell

def currency(label):
    try_counter = 0
    while try_counter < 10:
        try:
            r = urllib2.urlopen('http://pubapi.cryptsy.com/api.php?method=singlemarketdata&marketid=%i'%marketid[label])
            s = ast.literal_eval(r.readlines()[0])['return']['markets'][label[:-4]]
            try_counter = 15
        except:
            try_counter += 1
    if try_counter <15:
        print "No update to ",label
        return "noupdate","noupdate","noupdate","noupdate","noupdate","noupdate"

    #get volume, last sell price, and last time of sale
    volume = float(s['volume'])
    last_price =  float(s['lasttradeprice'])
    last_time =  datetime.strptime(s['lasttradetime'],"%Y-%m-%d %H:%M:%S")
    trade_end = (datetime.strptime(s['recenttrades'][-1]['time'],"%Y-%m-%d %H:%M:%S")-last_time).seconds
    market = s['primaryname']
    #for btc
    scale=1
    #for ltc
    if label[-3:] == "LTC":
        scale=5
    time_to_sell = _get_time_to_sell(s,last_time,scale)
    weighted_sell = _get_purchase(s, scale)
    weighted_buy = _get_liquidity(s, scale)
  
    #sanity check
    if time_to_sell > 1000:
        return (market, last_price, round(volume*last_price, 2), 'noupdate',
             round(weighted_sell,4), round(math.log(volume*last_price)*weighted_buy,4))
    else:
        return (market,last_price, round(volume*last_price,2), round(time_to_sell,3),
             round(math.log(volume*last_price)*weighted_sell,4), round(math.log(volume*last_price)*weighted_buy,4))
#        return (market,last_price, round(volume*last_price,2), round(time_to_sell,2),
#            round(math.log(volume*last_price)*weighted_sell,4), round(math.log(volume*last_price)*weighted_buy,4),
#            volume_change)
        

def currency_all(label):
    try_counter = 0
    while try_counter < 10:
        try:
            r = urllib2.urlopen('http://pubapi.cryptsy.com/api.php?method=marketdatav2')
            s = ast.literal_eval(r.readlines()[0])['return']['markets'][label[:-4]]
            try_counter = 10
        except:
            try_counter += 1
    try:
        #get volume, last sell price, and last time of sale
        volume = float(s['volume'])
        last_price =  float(s['lasttradeprice'])
        last_time =  datetime.strptime(s['lasttradetime'],"%Y-%m-%d %H:%M:%S")
        trade_end = (datetime.strptime(s['recenttrades'][-1]['time'],"%Y-%m-%d %H:%M:%S")-last_time).seconds

        time_to_sell = _get_time_to_sell(s,last_time)
        weighted_sell = _get_purchase(s)
        weighted_buy = _get_liquidity(s)
        volume_per_hour = _get_volume_hour(s,last_time,trade_end)
        
        if time_to_sell > 1000:
            return ('mk', last_price, round(volume*last_price,2), 'noupdate',
                 round(weighted_sell,4), 'noupdate')
        else:
            return ('mk', last_price, round(volume*last_price,2), round(time_to_sell,2),
                 round(math.log(volume*last_price)*weighted_sell,4), round(math.log(volume*last_price)*weighted_buy,4),
                  )
    except:
        return "noupdate", "noupdate","noupdate","noupdate","noupdate","noupdate","noupdate"



def coinbasebtc():
	#get btc to usd price at coinbase
    try:
        r = urllib2.urlopen('https://coinbase.com/api/v1/currencies/exchange_rates')
        s = r.readlines()[0]
        tp = s.rfind('btc_to_usd')
        BtcUsd =  float(s[tp:tp+35].split('"')[2])
        return BtcUsd
    except:
        return "noupdate"


def mtgoxbtc():
	#get btc to usd price at mtgox
    try:
        r = urllib2.urlopen('https://data.mtgox.com/api/2/BTCUSD/money/ticker')
        s = r.readlines()[0]
        tp = s.rfind('"last"')
        BtcUsd =  float(s[tp:tp+35].split('"')[5])
        return BtcUsd
    except:
        return "noupdate"
