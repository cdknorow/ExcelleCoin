#!/usr/bin/python
#/*Copyright (c) 2013 Chris Knorowski <cknorow@gmail.com>
# *
__author__ = 'cknorow@gmail.com (Chris knorowski)'


import sys
import string
import datetime
import logging

import webapp2
from google.appengine.ext import db

from grab_rate import currency as cryptsy
from grab_rate import coinbasebtc
from grab_rate import mtgoxbtc


from models import BTCurrency
from models import AltCurrency
import util

#Workhorse class scrapes currency info and stores it into database
class WorkHorse:
  def __init__(self, Label, key_name, debug=False, write_database = False):
    #grab values from memcache
    self.write_database = write_database
    self.BTCurrency = util.get_btc()
    self.AltCurrency = util.get_alt_data(key_name, write_database)
    self.key_name=key_name
    if (self.BTCurrency is None):
      logging.error("BTCurrency does not exist")
    if len(list(set(self.AltCurrency.get_by_key_name(key_name).currency).symmetric_difference(set(Label)))) != 0:
      self.write_database = True
      self.adjust_database(Label)


   #check and see if the prices were actually update
  def adjust_database(self, Label):
    self.AltCurrency = util.get_alt_data(self.key_name, datastore=True)
    self.AltCurrency.currency = Label
    self.AltCurrency.put()

  #check and see if the prices were actually update
  def check(self, updated, last, s = False):
    for i,j in enumerate(updated):
      try:
        if j == "noupdate":
          updated[i] = last[i]
      except:
          updated[i] = 0.0
          if s:
            updated[i] = ''
    return updated

  #update mtgox and coinbase prices
  def update_btc_prices(self):
    # Get coinbase btc price
    self.BTCurrency.price = self.check([coinbasebtc(),mtgoxbtc()],[0.0,0.0])
    self.BTCurrency.timestamp = datetime.datetime.now()
    self.BTCurrency.put()

  #Scrape and update prices
  def update_prices(self):
    # Get the altcoin prices from cryptsy 
    pricealts = []
    marketalts = []
    volumealts = []
    time_to_sell = []
    weighted_buy = []
    weighted_sell = []

    for coin in self.AltCurrency.currency:
      market, price, volume, to_sell, ws, wb = cryptsy(coin)
      marketalts.append(market)
      pricealts.append(price)
      volumealts.append(volume)
      time_to_sell.append(to_sell)
      weighted_buy.append(wb)
      weighted_sell.append(ws)
    
    self.AltCurrency.marketname = self.check(marketalts,self.AltCurrency.marketname, s =True)
    self.AltCurrency.price = self.check(pricealts,self.AltCurrency.price)
    self.AltCurrency.volume = self.check(volumealts,self.AltCurrency.volume)
    self.AltCurrency.time_to_sell = self.check(time_to_sell,self.AltCurrency.time_to_sell)
    self.AltCurrency.weighted_buy = self.check(weighted_buy,self.AltCurrency.weighted_buy)
    self.AltCurrency.weighted_sell = self.check(weighted_sell,self.AltCurrency.weighted_sell)
    self.AltCurrency.timestamp = datetime.datetime.now()
    self.AltCurrency.put()
    #update the memcache after we write specifically to the database
    if self.write_database:
      AltCurrency = util.get_alt_data(self.key_name)
      AltCurrency = self.AltCurrency
      AltCurrency.put()


