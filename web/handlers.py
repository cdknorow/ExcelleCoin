# -*- coding: utf-8 -*-
import datetime
import logging

# appengine specific libraries
from google.appengine.api import users
import httpagentparser

# boilerplate 
from boilerplate.models import User
from boilerplate.lib.basehandler import BaseHandler
from boilerplate.lib.decorators import user_required

# local application/library specific imports
import models 
from models import BTCurrency
from models import AltCurrency 
from models import SpreadSheetUser
from models import Graph
from google.appengine.api import memcache
import util


### Model Names
### Graph : price, volume
### AltCurrency : alt_btc, alt_ltc
### BTCurrency : btcoin
###
### Memcache Names
### get_alt_wparams: alt_btc_p, alt_ltc_p
### get_alt_data: alt_btc, alt_ltc
### get_btc: btcoin


#Currencies to scrape
Currency_Label = [ 'DGC','LTC','DOGE','BTB','QRK','ARG',
              'WDC','PTS','PPC','XPM',
              'LOT','ZET','CGB','DVC',
              'CAT','GLD','FTC','MOON','BCX','EAC',
              'GDC','KGC','FRK','STR','BTG','RPC',
              'TGC','NET','ANC','MEC','SRC','AMC','BQC','CAP','VTC',
              "UNO",
              ]

Currency_Label_LTC = [ 'TIPS','DGC','DOGE','QRK',
              'WDC','MEC','PPC','XPM',
              'ZET','CGB','GLD','MOON','IFC',
              'SXC','NET','TIX','MEC','DVC','MST','JKC',"ASC",
              "FLO","SBC","ELP"]


"""Renders the homepage with the chart.html"""
class HomeHandler(BaseHandler):
    ######################3

    def get(self):
        #get currency from datastore
        BT = util.get_btc()
        Vavg = util.get_alt_avg('volume')
        Pavg = util.get_alt_avg('price')
        Bdata, BtcAlt = util.get_alt_wparams('alt_btc_p', 'alt_btc', Pavg['btc_hml'])
        Ldata, LtcAlt = util.get_alt_wparams('alt_ltc_p', 'alt_ltc', Pavg['ltc_hml'])
        params = {
                'btc': BT,
                'alt': BtcAlt,
                'ltcalt': LtcAlt,
                'ltcindex':Ldata['Lindex'],
                'btcindex':Bdata['Bindex'],
                'bpercent':Bdata['time_Bpercent'],
                'lpercent':Ldata['time_Lpercent'],
                'lvchange':Ldata['time_Lvchange'],
                'bvchange':Bdata['time_Bvchange'],
                'LPchange':Ldata['Lpchange'],
                'LPpercent':Ldata['LPpercent'],
                'BPchange':Bdata['Bpchange'],
                'BPpercent':Bdata['BPpercent'],
                'BVhml':Vavg['btc_hml'],
                'LVhml':Vavg['ltc_hml'],
                 }
        return self.render_template('chart.html', **params)


"""Outputs all the coin info currently stored in database"""
class ChartsHandler(BaseHandler):
    def get(self, coin):
      Vavg = util.get_alt_avg('volume')
      Pavg = util.get_alt_avg('price')
      if coin[-3:] == 'BTC':
        try:
          index = Currency_Label.index(coin[:-3])
          params = {'price':Pavg['btc_avg'][index],
                      'pricex':Pavg['timestamp'],
                      'volume':Vavg['btc_avg'][index],
                      'volumex':Vavg['timestamp'],
                      'BTC':True,
                      }
        except:
          return self.redirect('/')
      elif coin[-3:] == 'LTC':
        try:
          index = Currency_Label_LTC.index(coin[:-3])
          params = {'price':Pavg['ltc_avg'][index],
                      'pricex':Pavg['timestamp'],
                      'volume':Vavg['ltc_avg'][index],
                      'volumex':Vavg['timestamp'],
                      'BTC':False,
                      }
        except:
          return self.redirect('/')
      else:
        return self.redirect('/')
      return self.render_template('coinchart.html',**params)


"""Outputs all the coin info currently stored in database"""
class CointTrackHandler(BaseHandler):
    def get(self):
        return self.render_template('cointrack.html')


"""Renders the about page"""
class AboutHandler(BaseHandler):
    def get(self):
        return self.render_template('about.html')


""" Scrapes the web and updates datastore with latest info """
class BTCWorkHorseHandler(BaseHandler):
  def get(self): 
    from web.workhorse import WorkHorse
    Label = []
    for i in Currency_Label:
        Label.append(i+'/BTC')
    counter = memcache.get('counter')
    if counter is None:
      memcache.set(key="counter", value=0)
      counter = 0
    if counter%20 == 0:
      write_database = True
    else:
      write_database = False
    speedy = WorkHorse(Label, 'alt_btc',write_database)
    try:
      speedy.update_prices()
    except:
      logging.error("Error: update prices failed") 
    try:
      speedy.update_btc_prices()  
    except:
      logging.error("Error: update btc prices failed") 
    memcache.incr("counter")


""" Scrapes the web and updates datastore with latest info """
class LTCWorkHorseHandler(BaseHandler):
  def get(self):
    from web.workhorse import WorkHorse
    Label = []
    for i in Currency_Label_LTC:
      Label.append(i+'/LTC')
    speedy = WorkHorse(Label, 'alt_ltc')
    try:
      speedy.update_prices()
    except:
      logging.error("Error: update prices failed")   

""" Keep Track of the volume over the last 14 days """
class FourteenDayVolumeHandler(BaseHandler):
  def get(self):
    LtcAlt = util.get_alt_data('alt_ltc')
    BtcAlt = util.get_alt_data('alt_btc')
    avg = Graph.get_by_key_name('volume')
    print BtcAlt.volume
    for i,v in enumerate(BtcAlt.volume):
        avg.btc_avg[i].append(v)
        avg.btc_hml[i] = [max(avg.btc_avg[i][-7:]),sum(avg.btc_avg[i][-7:])/7.,min(avg.btc_avg[i][-7:])]
    for i,v in enumerate(LtcAlt.volume):
        avg.ltc_avg[i].append(v)
        avg.ltc_hml[i] = [max(avg.ltc_avg[i][-7:]),sum(avg.ltc_avg[i][-7:])/7.,min(avg.ltc_avg[i][-7:])]
    avg.timestamp.append(LtcAlt.timestamp)
    avg.put()

""" Keep Track of the volume over the last 14 days"""
class FourteenDayPriceHandler(BaseHandler):
  def get(self): 
    LtcAlt = util.get_alt_data('alt_ltc')
    BtcAlt = util.get_alt_data('alt_btc')
    avg = Graph.get_by_key_name('price')
    for i,v in enumerate(BtcAlt.price):
        avg.btc_avg[i].append(v)
        avg.btc_hml[i] = [max(avg.btc_avg[i][-4:]),sum(avg.btc_avg[i][-4:])/4.,min(avg.btc_avg[i][-4:])]
    for i,v in enumerate(LtcAlt.price):
        avg.ltc_avg[i].append(v)
        avg.ltc_hml[i] = [max(avg.ltc_avg[i][-4:]),sum(avg.ltc_avg[i][-4:])/4.,min(avg.ltc_avg[i][-4:])]
    avg.timestamp.append(LtcAlt.timestamp)
    avg.put()


""" Update Spreadsheet for all users who have registerd"""
class UpdateSpreadsheetsFreeHandler(BaseHandler):
  def get(self):
    from web.spreadsheet import UserSpreadsheet
    #grab the currency from datastore
    BT = util.get_btc()
    BtcAlt = util.get_alt_data('alt_btc')
    for i in range(len(BtcAlt.currency)):
      BtcAlt.currency[i] = BtcAlt.currency[i][:-4]
    for user in SpreadSheetUser.get_by_status(status='1'):
      sheet_name = 'ExcellCoin'
      print "updating spreadsheet for", user.username
      try:
        spread = UserSpreadsheet(user.credentials,sheet_name,BtcAlt,BT,user.miners)
      except:
        logging.error("Refresh Token: "+str(user.credentials.refresh_token))
      try:
        spread.Run()
      except:
        logging.error("Error: UserSpreadsheet failed for %s"%user.username)
      print "Spreasheet Finished updating for", user.username



""" Update Spreadsheet for all users who have registerd"""
class UpdateSpreadsheetsPremiumHandler(BaseHandler):
  def get(self):
    from web.spreadsheet import UserSpreadsheet
    #grab the currency from datastore
    BT = util.get_btc()
    BtcAlt = util.get_alt_data('alt_btc')
    for i in range(len(BtcAlt.currency)):
      BtcAlt.currency[i] = BtcAlt.currency[i][:-4]
    for user in SpreadSheetUser.get_by_status(status='2'):
      sheet_name = 'ExcellCoin'
      try:
        spread = UserSpreadsheet(user.credentials,sheet_name,BtcAlt,BT,user.miners)
      except:
        logging.error("Refresh Token: "+str(user.credentials.refresh_token))
      try:
        spread.Run()
      except:
        logging.error("Error: UserSpreadsheet failed for %s"%user.username)

#Initial the databases for the first time
class PopulateHandler(BaseHandler):
    #initialize the AltCurrency datastore
    def generate_data(self, Label, key_name,add):
      currency = []
      for i in Label:
        currency .append(i+add)
      AltCurrency(key_name = key_name, currency = currency).put()
    #initialize the graph datastore for price and volume
    def generate_graph(self, key_name):
      avg = Graph(key_name = key_name, 
                     btc_currency = Currency_Label,
                     btc_avg = [[0] for i in range(len(Currency_Label))],
                     btc_hml = [[] for i in range(len(Currency_Label))],                    
                     ltc_currency = Currency_Label_LTC,
                     ltc_avg = [[0] for i in range(len(Currency_Label_LTC))],
                     ltc_hml = [[] for i in range(len(Currency_Label_LTC))],
                     timestamp = [datetime.datetime.now()])
      avg.put()
    #class to initialize graph, altcurrency, btcurrency and upate graph if we 
    # change the coins to serve
    def get(self):
      if BTCurrency.get_by_key_name('btcoin') is None:
        BTCurrency(key_name = 'btcoin', currency = ['Coinbase','MtGox'], 
                  price = [0.0,0.0], timestamp = datetime.datetime.now()).put()
      if AltCurrency.get_by_key_name('alt_btc') is None:
        self.generate_data(Currency_Label, 'alt_btc','/BTC')
        self.generate_data(Currency_Label_LTC, 'alt_ltc','/LTC')
      if Graph.get_by_key_name('price') is None:
        self.generate_graph('price')    
      if Graph.get_by_key_name('volume') is None:
        self.generate_graph('volume')
      #check if we ened to update the graphs
      ### TODO CHECK IF THIS WORKS
      Pavg = util.adjust_avg_database(Graph.get_by_key_name('price'),Currency_Label,Currency_Label_LTC)
      Vavg = util.adjust_avg_database(Graph.get_by_key_name('volume'),Currency_Label,Currency_Label_LTC)
      params = {'price':Pavg.btc_avg,
                'volume':Vavg.btc_avg,
               }
      memcache.set(key="counter", value=0)
      return self.render_template('about.html', **params)

#Initial the databases for the first time
class EditGraphHandler(BaseHandler):
      #initialize the graph datastore for price and volume
    def get(self):
      Pavg = Graph.get_by_key_name('price')
      for i in range(len(Pavg.btc_avg)):
        del Pavg.btc_avg[i][0]
      for i in range(len(Pavg.ltc_avg)):
        del Pavg.ltc_avg[i][0]
      Vavg = Graph.get_by_key_name('volume')
      for i in range(len(Vavg.btc_avg)):
        del Vavg.btc_avg[i][0]
      for i in range(len(Vavg.ltc_avg)):
        del Vavg.ltc_avg[i][0]
      Pavg.put()
      Vavg.put()


"""
    A real simple app for using webapp2 with auth and session.

    It just covers the basics. Creating a user, login, logout
    and a decorator for protecting certain handlers.

    Routes are setup in routes.py and added in main.py
"""
class SecureRequestHandler(BaseHandler):
    """
    Only accessible to users that are logged in
    """
    @user_required
    def get(self, **kwargs):
        user_session = self.user
        user_session_object = self.auth.store.get_session(self.request)

        user_info = models.User.get_by_id(long(self.user_id))
        user_info_object = self.auth.store.user_model.get_by_auth_token(
            user_session['user_id'], user_session['token'])

        try:
            params = {
                "user_session": user_session,
                "user_session_object": user_session_object,
                "user_info": user_info,
                "user_info_object": user_info_object,
                "userinfo_logout-url": self.auth_config['logout_url'],
            }
            return self.render_template('secure_zone.html', **params)
        except (AttributeError, KeyError), e:
            return "Secure zone error:" + " %s." % e

