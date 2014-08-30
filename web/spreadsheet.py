#!/usr/bin/python
#/*Copyright (c) 2013 Chris Knorowski <cknorow@gmail.com>
__author__ = 'cknorow@gmail.com (Chris knorowski)'
#motiated by google data sample spreadsheetsample.py 
#__author__ = 'api.laurabeth@gmail.com (Laura Beth Lincoln)'

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.service
import atom.service
import atom
import getopt
import sys
import string
import time
import logging
from datetime import datetime

import httplib2

from google.appengine.ext import db
from gdata.oauth2client_gdata_bridge import OAuth2BearerToken
from gdata.spreadsheets.client import SpreadsheetsClient
from gdata.spreadsheets.client import SpreadsheetQuery
from gdata.spreadsheets.client import CellQuery

import grab_hash  as gb
import gdata.gauth as gauth
import gdata.spreadsheets.data

class UserSpreadsheet:
  def __init__(self, credentials, sheet_name, Alt, BT, Miners):
    self.credentials = credentials
    self.gd_client = SpreadsheetsClient()
    self.spreadsheet_name = sheet_name
    self.Alt = Alt
    self.BT = BT
    self.Miners=Miners
    auth2token = gauth.OAuth2TokenFromCredentials(self.credentials)
    auth2token.authorize(self.gd_client)

  def create_spreadsheet(self):
    from apiclient.discovery import build
    service = build('drive', 'v2')
    http = self.credentials.authorize(httplib2.Http())
    body = {
          'mimeType': 'application/vnd.google-apps.spreadsheet',
          'title': self.spreadsheet_name,
              }
    file = service.files().insert(body=body).execute(http=http)


  def Run(self):
    num_coins = len(self.Alt.currency)
    #query for spreadsheet
    q = SpreadsheetQuery(title= self.spreadsheet_name,title_exact=True)
    try:
      self.gd_client.get_spreadsheets(query = q).entry[0].get_spreadsheet_key()
    except:
      return logging.error("Error: No ExcellCoin SpreadSheet")
    self.spreadsheet_key = self.gd_client.get_spreadsheets(query = q).entry[0].get_spreadsheet_key()
    #get the first row data to figure out what coins to update.
    #if blank update all
    cq = CellQuery(range='A1',return_empty=True)
    cs = self.gd_client.GetCells(self.spreadsheet_key,'od6',q=cq)
    coins =  cs.entry[0].cell.input_value
    if coins != '':
      num_coins = len(coins.split())

    cq = CellQuery(range=('R1C1:R%iC3'%(num_coins+13)),return_empty=True)
    cs = self.gd_client.GetCells(self.spreadsheet_key,'od6',q=cq)
    count = 1
    cs.entry[count*3].cell.input_value='%s'%str(datetime.now())
    cs.entry[count*3+1].cell.input_value='USD/BTC'
    #update the bitcoin to usd rates
    count+=1
    for i,coin in enumerate(self.BT.currency):
      cs.entry[3*count].cell.input_value=self.BT.currency[i]
      cs.entry[3*count+1].cell.input_value='%.2f'%self.BT.price[i]
      count+=1
    #update the Altcoin to BTC rates
    count+=1
    cs.entry[3*count].cell.input_value='Altcoins'
    cs.entry[3*count+1].cell.input_value='Exchange Rate'
    cs.entry[3*count+2].cell.input_value='Volume in BTC'
    count+=1

    if coins == '':
      for i,coin in enumerate(self.Alt.currency):
        cs.entry[3*count].cell.input_value='%s'%coin
        cs.entry[3*count+1].cell.input_value='%.8f'%self.Alt.price[i]
        cs.entry[3*count+2].cell.input_value='%.2f'%self.Alt.volume[i]
        count+=1
    else:
      for i,coin in enumerate(coins.split()):
        try:
          if coin in self.Alt.currency:
            index = self.Alt.currency.index(coin)
            cs.entry[3*count].cell.input_value=self.Alt.currency[index]
            cs.entry[3*count+1].cell.input_value='%.8f'%self.Alt.price[index]
            cs.entry[3*count+2].cell.input_value='%.2f'%self.Alt.volume[index]
            count+=1
        except:
          logging.error("Error: unable to update coins%s"%coin)

    count+=2
    cs.entry[3*count].cell.input_value='MiningPool'
    cs.entry[3*count+1].cell.input_value='Workers'
    cs.entry[3*count+2].cell.input_value='HashRate'
    count+=1
    for Miners in self.Miners:
      ############ Hash Rate ###################
      try:
        if Miners != 'none':
          site = Miners.split(',')[0]
          nickname = Miners.split(',')[1]
          mining_token = Miners.split(',')[2]
          workers, hash_rate = gb.get_stats(site,mining_token)
          cs.entry[3*count].cell.input_value=nickname
          cs.entry[3*count+1].cell.input_value='%i'%int(workers)
          cs.entry[3*count+2].cell.input_value='%i'%int(hash_rate)
          count+=1
      except:
        logging.error("Error: unable to update hashrate %s"%Miners.split(',')[0])
        count+=1

    #send a batch job to update everything in spreadsheet at once
    try:
      objData = gdata.spreadsheets.data
      batch = objData.BuildBatchCellsUpdate(self.spreadsheet_key, 'od6')
      for cell in cs.entry:
        batch.add_batch_entry(cell, cell.id.text, batch_id_string=cell.title.text, operation_string='update')
      self.gd_client.batch(batch, force=True)
    except:
      return logging.error("Error: Unable to send batch operation")


