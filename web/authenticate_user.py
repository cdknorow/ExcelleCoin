#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Get Uer Oauth2 credentials and store them so 
they can access excell coin spreadsheet
"""

__author__ = 'cknorow@gmail.com (Chris Knorowski)'
# extended from'jcgregorio@google.com (Joe Gregorio)'


import os
import sys
import logging
import webapp2

try:
  import httplib2
except:
  try:
    import web.lib.httplib2 as httplib2
  except:
    pass
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db


#Wen 
try:
  from web.lib.apiclient import discovery
except:
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
  from web.lib.apiclient import discovery
from web.lib.oauth2client import appengine
from web.lib.oauth2client import client
from web.lib.oauth2client.appengine import CredentialsProperty
from web.models import SpreadSheetUser


#Boilerplate
try:
  from boilerplate.lib.basehandler import BaseHandler
except:
  sys.path.append(os.path.join(os.path.dirname(__file__), '../boilerplate/external'))
  sys.path.append('ExcellCoin/boilerplate/external')
  from boilerplate.lib.basehandler import BaseHandler
from boilerplate.models import User



#Certs for google oauth2
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secret.json')

SPREADSHEET_MIMETYPE = "application/vnd.google-apps.spreadsheet"

http = httplib2.Http(memcache)
service = discovery.build("drive", "v2", http=http)
decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope=['https://spreadsheets.google.com/feeds'], 
    )


#class to store oauth2 data
class oauth2Handler(BaseHandler):
  @decorator.oauth_aware
  def get(self):
    if not decorator.has_credentials():
      return self.redirect(decorator.authorize_url())
    else:
      credentials = decorator.get_credentials()
    try:
      decorator.http()
    except:
      logging.error("Error: Decorator Refresh Failed")
    if credentials.refresh_token is None:
      logging.error("Error: Refresh Token is None")
    current_user = users.get_current_user()
    if current_user:
      uid = current_user.user_id()
      email = current_user.email()
    else:
      message = _('No user authentication information received from %s. '
                'Please ensure you are logging in from an authorized OpenID Provider (OP).'
                % provider_display_name)
      self.add_message(message, 'error')
      return self.redirect_to('login', continue_url=continue_url) if continue_url else self.redirect_to(
                    'login')
    if self.user:
        # add social account to user
        user_info = User.get_by_id(long(self.user_id))
        if SpreadSheetUser.check_unique_uid( uid):
          credential_user = SpreadSheetUser(
                  user=user_info.key,
                  uid=uid,
                  username= user_info.username,
                  credentials = credentials,
                  status = '1',
                  miners=['none']
              )
          credential_user.put() 
    return self.redirect('/settings/profile')

#class to test refresh token
class oauth2RefreshHandler(BaseHandler):
  @decorator.oauth_required
  def get(self):
    user_info = User.get_by_id(long(self.user_id))
    credentials =SpreadSheetUser.get_by_username(user_info.username)
    if credentials.credentials.refresh_token is None:
      logging.error("Error: Refresh Token is None")
    return self.redirect('/settings/profile')



#routes for authentication
from webapp2_extras.routes import RedirectRoute

_routes =   [
    RedirectRoute('/authenticate', oauth2Handler, name='oauth2request', strict_slash=True),
    RedirectRoute('/refreshoauth2', oauth2RefreshHandler, name='oauth2request', strict_slash=True),
    RedirectRoute(decorator.callback_path, decorator.callback_handler(), name='callback', strict_slash=True),
    ]


def get_routes():
    return _routes

def add_routes(app):
    if app.debug:
        secure_scheme = 'http'
    for r in _routes:
        app.router.add(r)
