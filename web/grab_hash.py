#!/usr/bin/python
#/*Copyright (c) 2013 Chris Knorowski <cknorow@gmail.com>
__author__ = 'cknorow@gmail.com (Chris knorowski)'

import os
import sys
import urllib2
import csv
import ast

pool_choices = [('""','None'),('dgc.miningpool.co','dgc.miningpool.co'),('arg.cryptopools','arg.cryptopools'),
                ('dgc.cryptopools','dgc.cryptopools'),('tag.cryptopools','tag.cryptopools'),('ltc.coinhuntr','ltc.coinhuntr'),
                ('doge.coinhuntr','doge.coinhuntr'),('liteguardian','liteguardian'),('suchcoins','suchcoins'),
                ('pool.karmacoin.info','pool.karmacoin.info')]

def miningco(token):
	#get hasrate from miningpool.co
    r = urllib2.urlopen('https://www.miningpool.co/api/balances?key=%s'%token)
    count = 0
    c = csv.reader(r,delimiter='}')
    for s in c.next():
        if "DigitalCoin" in s:
            tp = s.rfind('worker_count')
            workers =  int(s[tp:tp+20].split('"')[2])
            tp = s.rfind('hashrate')
            hashrate = float(s[tp:tp+20].split('"')[2])
    return workers, hashrate

# suchcoins.com
def suchcoins(token):
    #get hashrate from arg.cryptopools
    r = urllib2.urlopen("http://www.suchcoins.com/index.php?page=api&action=getuserstatus&api_key=%s"%(token))
    s = ast.literal_eval(r.readlines()[0])['getuserstatus']
    return 1, s['data']['hashrate']

# pool.karmacoin.info
def karmacoin_info(token):
    #get hashrate from arg.cryptopools
    r = urllib2.urlopen("http://pool.karmacoin.info/index.php?page=api&action=getuserstatus&api_key=%s"%(token))
    s = ast.literal_eval(r.readlines()[0])['getuserstatus']
    return 1, s['data']['hashrate']

# cryptopools.com
def cryptopools(coin,token):
	#get hashrate from arg.cryptopools
    r = urllib2.urlopen("http://%s.cryptopools.com/index.php?page=api&action=getuserstatus&api_key=%s"%(coin,token))
    s = ast.literal_eval(r.readlines()[0])['getuserstatus']
    return 1, s['data']['hashrate']

####### coinhuntr.com
def coinhuntr_ltc(token):
    r = urllib2.urlopen("https://www.coinhuntr.com/index.php?page=api&action=getuserstatus&api_key=%s"%token)
    s = ast.literal_eval(r.readlines()[0])['getuserstatus']
    return 1, s['data']['hashrate']

def coinhuntr_doge(token):
    r = urllib2.urlopen("https://doge.coinhuntr.com/index.php?page=api&action=getuserstatus&api_key=%s"%token)
    s = ast.literal_eval(r.readlines()[0])['getuserstatus']
    return 1, s['data']['hashrate']

####### liteguardian.com
def liteguardian(token):
    r = urllib2.urlopen("https://www.liteguardian.com/api/%s"%token)
    m = r.readlines()[0].replace('false','False')
    m = m.replace('null','None')
    m = m.replace('\/','.')
    m = m.replace('true','True')
    s = ast.literal_eval("%s"%m)
    return s['active_workers'], s['hashrate']

def get_stats(site, mining_token):
    if site == 'dgc.miningpool.co':
        return miningco(mining_token)
    if site == 'tag.cryptopools':
        return cryptopools('tag', mining_token)
    if site == 'arg.cryptopools':
        return cryptopools('arg', mining_token)
    if site == 'dgc.cryptopools':
        return cryptopools('dgc', mining_token)
    if site == 'ltc.coinhuntr':
        return coinhuntr_ltc(mining_token)
    if site == 'doge.coinhuntr':
        return coinhuntr_doge(mining_token)
    if site == 'liteguardian':
        return liteguardian(mining_token)
    if site == 'suchcoins':
        return suchcoins(mining_token)
    if site == 'pool.karmacoin.info':
        return karmacoin_info(mining_token)

