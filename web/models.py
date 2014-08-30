from google.appengine.ext import db
from google.appengine.ext import ndb
from webapp2_extras.appengine.auth.models import User
# local application/library specific imports
from oauth2client.appengine import CredentialsNDBProperty 




#Class that holds BTC/USD information
class BTCurrency(ndb.Model):
  key_name= ndb.StringProperty(required=True)
  currency = ndb.StringProperty(repeated=True)
  price = ndb.JsonProperty()
  timestamp = ndb.DateTimeProperty()
  @classmethod
  def get_by_key_name(cls, key_name):
    return cls.query(cls.key_name == key_name).get()


#Class which holds AltCoin/BTC information
class AltCurrency(ndb.Model):
  #currency : Currency Name
  #price : Last traded price
  #volume : 24 volume (cryptsy)
  #weighted_buy: Measure of the purchase support
  #weighted_sell: Meassure of available sellers
  #time_to_sell: Time to sell .25 bitcoins
  #volume_per_hour: Volume sold in the last 10 minutes on crypsty
  #timestampt: Timestamp for last update
  key_name = ndb.StringProperty(required=True)
  currency = ndb.StringProperty(repeated=True)
  marketname = ndb.StringProperty(repeated=True)
  price = ndb.JsonProperty()
  volume = ndb.JsonProperty()
  weighted_buy = ndb.JsonProperty()
  weighted_sell = ndb.JsonProperty()
  time_to_sell = ndb.JsonProperty()
  timestamp = ndb.DateTimeProperty()

  @classmethod
  def get_by_key_name(cls, key_name):
    return cls.query(cls.key_name == key_name).get()



#Holds data for currencies over time
class Graph(ndb.Model):
  key_name = ndb.StringProperty(required=True)
  btc_currency = ndb.StringProperty(repeated=True)
  ltc_currency = ndb.StringProperty(repeated=True)
  timestamp = ndb.DateTimeProperty(repeated=True)
  btc_avg = ndb.JsonProperty()
  ltc_avg = ndb.JsonProperty()
  btc_hml = ndb.JsonProperty()
  ltc_hml = ndb.JsonProperty()
  @classmethod
  def get_by_key_name(cls, key_name):
    return cls.query(cls.key_name == key_name).get()



class SpreadSheetUser(ndb.Model):
    user = ndb.KeyProperty(kind=User)
    username = ndb.StringProperty()
    provider = ndb.StringProperty()
    uid = ndb.StringProperty()
    # credential Property
    credentials = CredentialsNDBProperty()
    # stuatus of account
    status = ndb.StringProperty(default = '0')
    miners = ndb.StringProperty(repeated=True)


    @classmethod
    def get_by_user(cls, user):
        return cls.query(cls.user == user).fetch()

    @classmethod
    def get_by_user_id(cls, user):
        return cls.query(cls.user == user).get()

    @classmethod
    def get_by_username(cls, username):
        return cls.query(cls.username == username).get()

    @classmethod
    def get_by_uid(cls, uid):
        return cls.query( cls.uid == uid).get()

    @classmethod
    def get_by_status(cls, status):
        return cls.query( cls.status == status).fetch()

    @classmethod
    def check_unique_uid(cls, uid):
        # pair (provider, uid) should be unique
        test_unique = cls.get_by_uid( uid)
        if test_unique is not None:
            return False
        else:
            return True
    
    @classmethod
    def check_unique_user(cls, provider, user):
        # pair (user, provider) should be unique
        test_unique_user = cls.get_by_user_and_provider(user, provider)
        if test_unique_user is not None:
            return False
        else:
            return True

    @classmethod
    def check_unique(cls, user, provider, uid):
        # pair (provider, uid) should be unique and pair (user, provider) should be unique
        return cls.check_unique_uid(provider, uid) and cls.check_unique_user(provider, user)
