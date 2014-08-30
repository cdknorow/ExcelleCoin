config = {

# environment this app is running on: localhost, testing, production
'environment': "production",


# application name
'app_name': "ExcellCoin",

# webapp2 authentication
'webapp2_extras.auth': {'user_model': 'boilerplate.models.User',
                        'cookie_name': 'session_name'},

# jinja2 templates
'webapp2_extras.jinja2': {'template_path': ['templates', 'boilerplate/templates', 'admin/templates'],
                          'environment_args': {'extensions': ['jinja2.ext.i18n']}},

# the default language code for the application.
# should match whatever language the site uses when i18n is disabled
'app_lang': 'en',

# get your own recaptcha keys by registering at http://www.google.com/recaptcha/
'captcha_public_key': "6LdIyu0SAAAAALR_XcFO4elHFglK_RCDJ6vS3iBV",
'captcha_private_key': "6LdIyu0SAAAAAC813Uw-iJcqNPb17MxaZRtJuWe1",


# ----> ADD MORE CONFIGURATION OPTIONS HERE <----
# add status codes and templates used to catch and display errors
# if a status code is not listed here it will use the default app engine
# stacktrace error page or browser error page
'error_templates': {
    403: 'errors/default_error.html',
    404: 'errors/default_error.html',
    500: 'errors/default_error.html',
},


# Enable Federated login (OpenID and OAuth)
# Google App Engine Settings must be set to Authentication Options: Federated Login
'enable_federated_login': False,


# jinja2 base layout template
'base_layout': 'base.html',

# send error emails to developers
'send_mail_developer': False,

# fellas' list
'developers': (
    ('Chris Knorowswki', 'cknorow@gmail.com'),
),

# If true, it will write in datastore a log of every email sent
'log_email': True,

# If true, it will write in datastore a log of every visit
'log_visit': True,


}
