from webapp2_extras.routes import RedirectRoute
import users
from web import handlers

_routes = [
    RedirectRoute('/admin/logout/', users.AdminLogoutHandler, name='admin-logout', strict_slash=True),
    RedirectRoute('/admin/', users.AdminGeoChartHandler, name='geochart', strict_slash=True),
    RedirectRoute('/admin/tasks/spreadsheetfree',  handlers.UpdateSpreadsheetsFreeHandler, name='updatespreadsheetfree', strict_slash=True),
    RedirectRoute('/admin/tasks/spreadsheetpremium',  handlers.UpdateSpreadsheetsPremiumHandler, name='updatespreadsheetpremium', strict_slash=True),
    RedirectRoute('/admin/tasks/ltcworkhorse', handlers.LTCWorkHorseHandler, name='ltcworkhorse', strict_slash=True),
    RedirectRoute('/admin/tasks/btcworkhorse', handlers.BTCWorkHorseHandler, name='btcworkhorse', strict_slash=True),
    RedirectRoute('/admin/tasks/graphvolume', handlers.FourteenDayVolumeHandler, name='graphvolume', strict_slash=True),
    RedirectRoute('/admin/tasks/graphprice', handlers.FourteenDayPriceHandler, name='graphprice', strict_slash=True),
    RedirectRoute('/admin/tasks/populate', handlers.PopulateHandler, name='populate', strict_slash=True),
    #RedirectRoute('/admin/tasks/editgraph', handlers.EditGraphHandler, name='editgraph', strict_slash=True),
]

def get_routes():
    return _routes

def add_routes(app):
    for r in _routes:
        app.router.add(r)
