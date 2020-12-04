# -*- coding: utf-8 -*-

import time, hashlib, requests, base64, sys
from collections import OrderedDict

class RestClient(object):
    def __init__(self, key=None, secret=None, url=None):
        self.key = key
        self.secret = secret
        self.session = requests.Session()

        if url:
            self.url = url
        else:
            self.url = "https://www.deribit.com"

    def request(self, action, data):
        response = None

        if action.startswith("/api/v2/private/"):
            if self.key is None or self.secret is None:
                raise Exception("Key or secret empty")
            
            token = base64.b64encode(self.key + ":" + self.secret)
            response = self.session.get(self.url + action, params=data, headers={'Authorization': "Basic " + token}, verify=True)
        else:
            response = self.session.get(self.url + action, params=data, verify=True)
        
        if response.status_code != 200:
            raise Exception("Wrong response code: {0}".format(response.status_code))

        json = response.json()

        if json["success"] == False:
            raise Exception("Failed: " + json["message"])
        
        if "result" in json:
            return json["result"]
        elif "message" in json:
            return json["message"]
        else:
            return "Ok"

    def getorderbook(self, instrument):
        return self.request("/api/v2/public/get_order_book", {'instrument_name': instrument})

    def getinstruments(self, currency="BTC"):     #currency is required for this function
        return self.request("/api/v2/public/get_instruments", {"currency": currency})

    def getcurrencies(self):
        return self.request("/api/v2/public/get_currencies", {})

    def getlasttrades(self, instrument, count=None, since=None):
        options = {
            'instrument_name': instrument
        }

        if count:
            options['count'] = count

        if since is None:
            return self.request("/api/v2/public/get_last_trades_by_instrument", options)

        options['start_timestamp'] = since
        options['end_timestamp'] = int(time.time()* 1000)
        return self.request('/api/v2/public/get_last_trades_by_instrument_and_time', options)


    def getsummary(self, instrument):
        return self.request("/api/v2/public/get_book_summary_by_instrument", {"instrument_name": instrument})


    def index(self, currency="btc_usd"):    #currency is required for this function
        return self.request("/api/v2/public/get_index_price", {"index_name": currency})

    
    def stats(self):
        return self.request("/api/v2/public/get_trade_volumes", {})


    def account(self, currency="BTC"):      #currency is required for this function
        return self.request("/api/v2/private/get_account_summary", {"currency": currency})


    def buy(self, instrument, quantity, price, postOnly=None, label=None):
        options = {
            "instrument_name": instrument,
            "amount": quantity,
            "price": price
        }
  
        if label:
            options["label"] = label

        if postOnly:
            options["post_only"] = postOnly

        return self.request("/api/v2/private/buy", options)


    def sell(self, instrument, quantity, price, postOnly=None, label=None):
        options = {
            "instrument_name": instrument,
            "amount": quantity,
            "price": price
        }

        if label:
            options["label"] = label

        if postOnly:
            options["post_only"] = postOnly

        return self.request("/api/v2/private/sell", options)

    def buy_stop_market_order(self, instrument, quantity, price):
        options = {
            "instrument_name": instrument,
            "amount": quantity,
            "stop_price": price,
            "type": "stop_market",
            "trigger": "mark_price",
            "time_in_force": "good_til_cancelled",

        }

        return self.request("/api/v2/private/buy", options)

    def sell_stop_market_order(self, instrument, quantity, price):
        options = {
            "instrument_name": instrument,
            "amount": quantity,
            "stop_price": price,
            "type": "stop_market",
            "trigger": "mark_price",
            "time_in_force": "good_till_cancelled",
        }

        return self.request("/api/v2/private/sell", options)


    def cancel(self, orderId):
        return self.request("/api/v2/private/cancel", {"order_id": orderId})


    def cancelall(self, typeDef="all"):     #Doesn't take arguments. Argument typeDef should be removed 
        return self.request("/api/v2/private/cancelall", {})


    def edit(self, orderId, quantity, price):
        options = {
            "order_id": orderId,
            "amount": quantity,
            "price": price
        }

        return self.request("/api/v2/private/edit", options)


    def getopenorders(self, instrument=None, orderId=None, currency="BTC"):#currency argument is optionally added. orderId to be removed
        if instrument:
            self.request("/api/v2/private/get_open_orders_by_instrument", {"instrument_name": instrument})

        return self.request("/api/v2/private/get_open_orders_by_currency", {"currency": currency})

    def getorderstate(self, orderId=None):      #orderId is required not optional
        return self.request("/api/v2/private/get_order_state", {"order_id": orderId})  


    def positions(self, currency="BTC"):    #currency is required for this function
        return self.request("/api/v2/private/get_positions", {"currency": currency})


    def orderhistory(self, count=None, currency="BTC"):     #currency is required for this function
        options = {"currency": currency}
        if count:
            options["count"] = count

        return self.request("/api/v2/private/get_order_history_by_currency", options)

#tradehistory is deprecated
