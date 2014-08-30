from google.appengine.api import memcache
import models 
from models import BTCurrency
from models import AltCurrency 
from models import SpreadSheetUser
from models import Graph
import logging

#Check for new coins or coins removed coins in the avg database
def adjust_avg_database(avg, Currency_Label, Currency_Label_LTC):
    d = list(set(Currency_Label).symmetric_difference(set(avg.btc_currency)))
    if len(d) > 0:
      for i in d:
        #remove from avg
        if i in avg.btc_currency:
          index = avg.btc_currency.index(i)
          del avg.btc_currency[index]
          del avg.btc_avg[index]
          del avg.btc_hml[index]
      for i in d:
        #add to avg
        if i not in avg.btc_currency:
          index = Currency_Label.index(i)
          avg.btc_currency.insert(index,i)
          avg.btc_avg.insert(index, [0.0 for i in range(len(avg.btc_avg[0]))])
          avg.btc_hml.insert(index,[[0],[0],[0]])
    d = list(set(Currency_Label_LTC).symmetric_difference(set(avg.ltc_currency)))
    if len(d) > 0:
      for i in d:
        #remove from avg
        if i in avg.ltc_currency:
          index = avg.ltc_currency.index(i)
          del avg.ltc_currency[index]
          del avg.ltc_avg[index]
          del avg.ltc_hml[index]
      for i in d:
        #add to avg
        if i not in avg.ltc_currency:
          index = Currency_Label_LTC.index(i)
          avg.ltc_currency.insert(index,i)
          avg.ltc_avg.insert(index, [0.0 for i in range(len(avg.ltc_avg[0]))])
          avg.ltc_hml.insert(index,[[0],[0],[0]])
    avg.put()
    return avg


#calculate the change in volume
# time to btc
def time_volume_change(Alt, name):
    percent = []
    vchange = []
    #1/time_to_sell = btc/mins 
     #volume *last_price*(24*60) = AVG BTC per mintue
    scale = 1
    if name == 'ltc_alt':
        scale=5
    for i in range(len(Alt.volume)):
        if Alt.time_to_sell[i] == 0.0:
            Alt.time_to_sell[i] = .01
            percent.append(0)
            vchange.append('""')
        else:
            percent.append('%.2f'%(round(100*(scale*(1. / Alt.time_to_sell[i]) / (Alt.volume[i] / (24.* 60.))-1), 4)))
            if float(percent[-1]) > 0:
                vchange.append('"green"')
            elif float(percent[-1])<0:
                vchange.append('"red"')
            else:
                vchange.append('""')
    return vchange, percent

#reverse the index so that the highest volume is first
def reverse_index(Alt):
    index = []
    for i in sorted(Alt.volume, reverse=True):
       index.append(Alt.volume.index(i))
    return index

#conver to mBTC and mLTC
def convert(Alt):
    for i in range(len(Alt.price)):
        Alt.price[i] = '%.5f'%(Alt.price[i]*1000)
        Alt.volume[i] = '%.2f'%(Alt.volume[i])
        Alt.weighted_buy[i] = '%.2f'%(Alt.weighted_buy[i])
        Alt.time_to_sell[i] = '%.2f'%(Alt.time_to_sell[i])
        Alt.weighted_sell[i] = '%.2f'%(Alt.weighted_sell[i])

# determine the change in price in percentage
def price_change(Alt, hml):
    percent = []
    change = []
    for i in range(len(Alt.price)):
        try:
            percent.append(Alt.price[i]/hml[i][1]-1)
        except:
            logging.error("Error: Division by zero at price_change")
            percent.append(0)
        if percent[-1] > 0:
            change.append('"green"')
        elif percent[-1] < 0:
            change.append('"red"')
        else:
            change.append('""')
        percent[-1] = '%.2f'%(100*percent[-1])
    return change, percent


#get some parameters that we want to pass to chart.html from memcache
def get_params(Alt, name, hml=False):
    index = reverse_index(Alt)
    time_vchange, time_percent = time_volume_change(Alt,name)
    pchange, ppercent = price_change(Alt, hml)
    if name == 'alt_ltc':
        data = {'Lindex':index,'time_Lvchange':time_vchange,'time_Lpercent':time_percent, 
                'Lpchange':pchange, 'LPpercent':ppercent}
    if name == 'alt_btc':
        data = {'Bindex':index,'time_Bvchange':time_vchange,'time_Bpercent':time_percent,
                 'Bpchange':pchange, 'BPpercent':ppercent}
    return data


#get alt_coint prices from memcache
def get_alt_data(name, datastore=False):
    if datastore:
        return AltCurrency.get_by_key_name(name)
    data = memcache.get(name)
    if data is not None:
        return data
    else:
        data = AltCurrency.get_by_key_name(name)
        memcache.add(name, data, 300)
        return data


#get alt_coint prices from memcache
def get_alt_avg(name):
    data = memcache.get(name)
    if data is not None:
        return {'btc_avg': data.btc_avg,'ltc_avg':data.ltc_avg,'timestamp':data.timestamp,
                'btc_hml':data.btc_hml,'ltc_hml':data.ltc_hml}
    else:
        data = Graph.get_by_key_name(name)
        memcache.add(name, data, 60*60*6)
        return {'btc_avg': data.btc_avg,'ltc_avg':data.ltc_avg,'timestamp':data.timestamp,
                'btc_hml':data.btc_hml,'ltc_hml':data.ltc_hml}


#######################################################
# Memcache objects for faster page loads
#get btc prices from memcache
def get_btc(datastore=False):
        if datastore:
            return BTCurrency.get_by_key_name('btcoin')
        data = memcache.get('btcoin')
        if data is not None:
            return data
        else:
            data = BTCurrency.get_by_key_name('btcoin')
            memcache.add('btcoin', data, 300)
            return data
#################################################

#get alt_coint prices from memcache
def get_alt_wparams(memname, name, hml):
    params = memcache.get('params %s'%memname)
    data = memcache.get(memname)
    if data is not None and params is not None:
        return params, data
    else:
        data = get_alt_data(name)
        params = get_params(data, name, hml)
        convert(data)
        memcache.add('params %s'%memname, params,300)
        memcache.add(memname, data, 300)
        return params, data