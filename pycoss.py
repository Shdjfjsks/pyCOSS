# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import requests


# If you have no API keys, you can generate them from the Account --> Services --> API Management page.
# API_SECRET _must_ be in byte format for SHA256 encoding.
# Ellipses (...) in a function's docstrings implies that this pattern continues for multiple symbols.

# One important thing to note is that pairs include _underscores_ (e.g. 'BTC_USDT') - ensure you're calling symbols
# like the example instead of 'ETH-BTC', 'ETHBTC', or 'ETH/BTC'.

# Initialise the client by instantiating the class and filling in the blanks with your API keys.
# client = PyCOSSClient(api_public="", api_secret="")


class PyCOSSClient(object):
    
    def __init__(self, api_public, api_secret):
        self.API_PUBLIC = api_public
        self.API_SECRET = bytearray(api_secret, encoding="utf8")
        self.TRADE_URL = "https://trade.coss.io/c/api/v1"
        self.EXCHANGE_URL = "https://exchange.coss.io/api"
        self.ENGINE_URL = "https://engine.coss.io/api/v1"
        self.order_headers = {"Content-Type": "application/json",
                              "X-Requested-With": "XMLHttpRequest",
                              "Authorization": self.API_PUBLIC, "Signature": None}
        self.s = requests.Session()

    def _sign(self, payload):
        """
        Authorises payload requests to the API.
        :param payload: JSON  str
        :return: hmac encoded string for API authorization
        """
        return hmac.new(self.API_SECRET, payload.encode("utf8"), hashlib.sha256).hexdigest()

    def get_balances(self):
        """
        Returns all of the coin balances in your account. 
        [
            {
            'currency_code': 'XYZ',
            'address': 'xyz',
            'total': '100',
            'available': '50',
            'in_order': '0',
            'memo': None
            },
        ...
        ]
        :return: JSON
        """
        payload = urlencode({"timestamp": int(time.time() * 1000)})
        self.order_headers["Signature"] = self._sign(payload=payload)
        return self.s.get(self.TRADE_URL + "/account/balances", headers=self.order_headers, params=payload).json()
    
    def get_account_details(self):
        """
        Returns all of your account details. 
        {
        'account_id': 'xyz123',
        'revenue_share_guid': 'zyx456',
        'email': 'hello_world@hello.coss',
        ...
        }
        :return: JSON
        """
        payload = urlencode({"timestamp": int(time.time() * 1000)})
        self.order_headers["Signature"] = self._sign(payload=payload)
        return self.s.get(self.TRADE_URL + "/account/details", headers=self.order_headers, params=payload).json()
    
    def get_exchange_info(self):
        """
        Returns exchange information. 
        {
        'timezone': 'UTC',
        'server_time': 123456789,
        'rate_limits':
            [
                {
                'type': 'REQUESTS',
                'interval': 'MINUTE',
                'limit': 1000
                }
            ],
        'base_currencies':
            [
                {
                'currency_code': 'BTC',
                'minimum_total_order': '0.0005'
                },
            ...
            ],
        'coins':
            [
                {
                'currency_code': 'ADI',
                'name': 'Aditus',
                'minimum_order_amount': '0.00000001'
                },
            ...
            ],
        'symbols': [
                    {
                    'symbol': 'ADI_BTC',
                    'amount_limit_decimal': 0,
                    'price_limit_decimal': 8,
                    'allow_trading': True
                    },
        ...
        ],
        }
        :return: JSON
        """
        return self.s.get(self.TRADE_URL + "/exchange-info").json()
    
    def get_market_summaries(self):
        """
        Gets summaries of all markets.
        {
        'success': True,
        'message': '',
        'result': [
            {
            'MarketName': 'BTC-USDT',
            'High': 123,
            'Low': 50,
            'BaseVolume': 999,
            'Last': 1234,
            'Timestamp': '2019-01-01T06:46:57.735Z',
            'Volume': None,
            'Ask': 123,
            'Bid': 123,
            'PrevDay': 123
             },
            ...
            ],
        't': 123456789
        }
        :return: JSON
        """
        return self.s.get(self.EXCHANGE_URL + "/getmarketsummaries").json()
    
    def get_market_price(self, symbol=None):
        """
        Gets the market price for all pairs by default. Otherwise, returns market prices for specific pair. 
        # Single #
        [
            {
            'symbol': 'BTC_USDT',
            'price': '0.03269',
            'updated_time': 123456789
            }
        ]
        # All #
        [
            {
            'symbol': 'BTC_USDT',
            'price': '0.03269',
            'updated_time': 123456789
            },
            ...
         ]
        :param symbol: str
        :return: JSON
        """
        if symbol:
            return self.s.get(self.TRADE_URL + "/market-price?symbol=%s" % symbol).json()
        return self.s.get(self.TRADE_URL + "/market-price").json()
    
    def get_order_book(self, symbol):
        """
        Gets order book for given pair. COSS currently has no capacity for limiting order book calls,
         so for now (COSS 1.2~) this gets the entire order book for the given pair. 
        {
        'symbol': 'BTC_USDT',
        'asks' [['0.03284000', '0.32100000'], ... ],
        'limit': 100,
        'bids': [['0.03252000', '0.05000000'], ... ],
        'time': 123456789
        }
        :param symbol: str
        :return: JSON
        """
        return self.s.get(self.ENGINE_URL + "/dp?symbol=%s" % symbol).json()
    
    def get_market_info(self, symbol):
        """
        Returns market information for symbol. 
        {
        'symbol': 'BTC_USDT',
        'limit': 100,
        'history':
            [
                {
                'id': 123,
                'price', '123',
                'qty': '12345',
                'isBuyerMarker': True,
                'time': 123456789
                },
                ...
            ]
        }
        :param symbol: str
        :return: JSON
        """
        return self.s.get(self.ENGINE_URL + "/ht?symbol=%s" % symbol).json()
    
    def create_order(self, symbol, side, order_type, size, price=None):
        """
        Creates a BUY/SELL, limit/market order of size for the specified symbol.
        Ensure that your order size is above the minimum order limit for the pair! E.g. ETH_BTC 0.02, USDT $2.00
        
        create_order('ETH_BTC', 'BUY', 'market', 0.025)
        create_order('ETH_BTC', 'SELL', 'limit', 0.025, 0.035)
    
        If COSS gets your request but something goes wrong, requests will return 400 (usually you've ordered something
        with too many decimals which COSS doesn't allow for your current pair).
        :param symbol: str
        :param side: str UPPER
        :param order_type: str
        :param size: int|float
        :param price: int|float
        :return: JSON
        """
        payload = json.dumps({"order_symbol": symbol,
                              "order_side": side,
                              "type": order_type,
                              "order_size": size,
                              "order_price": price,
                              "timestamp": int(time.time()) * 1000}, separators=(",", ":"))
        self.order_headers["Signature"] = self._sign(payload=payload)
        return self.s.post(self.TRADE_URL + "/order/add/", headers=self.order_headers, data=payload).json()
    
    def get_open_orders(self, symbol, limit=10, page=0):
        """
        Gets all current open orders up to limit.
        {
        'total': 1,
        'list':
            [
                {
                'hex_id': None,
                'order_id': '1234-1234-1234-1234-1234',
                'account_id': '1234-1234-1234-1234-1234',
                'order_symbol': 'BTC_USDT'
                'order_side': 'SELL'
                'status': 'open',
                'createTime': 123456789,
                'type': 'limit',
                'timeMatching': 0,
                'order_price': '0.00012800'
                'order_size': '0.123',
                'executed': '0.1',
                'stop_price': '0.00000000',
                'avg': '0.00012800'
                'total': '0.123 BTC'
                }
            ]
        }
        :param symbol: str
        :param limit: int
        :param page: int
        :return: JSON
        """
        payload = json.dumps({"symbol": symbol,
                              "limit": limit,
                              "page": page,
                              "timestamp": int(time.time() * 1000)}, separators=(",", ":"))
        self.order_headers["Signature"] = self._sign(payload=payload)
        return self.s.post(self.TRADE_URL + "/order/list/open", headers=self.order_headers, data=payload).json()
    
    def get_completed_orders(self, symbol, limit=10, page=0):
        """
        Gets all completed orders for the designated pair.
        :param symbol: str
        :param limit: int
        :param page: int
        :return: JSON
        """
        payload = json.dumps({"symbol": symbol,
                              "limit": limit,
                              "page": page,
                              "timestamp": int(time.time() * 1000)}, separators=(",", ":"))
        self.order_headers["Signature"] = self._sign(payload=payload)
        return self.s.post(self.TRADE_URL + "/order/list/completed", headers=self.order_headers, data=payload).json()
    
    def get_all_orders(self, symbol, from_id=None, limit=50):
        """
        Gets all orders up to max limit (50) for the specified symbol.
        [
            {
            'hex_id': '123456789',
            'order_id': '1234-1234-1234-1234-1234',
            'account_id': '1234-1234-1234-1234-1234',
            'order_symbol': 'BTC_USDT'
            'order_side': 'BUY'
            'status': 'filled',
            'createTime': 123456789
            'type': 'limit'
            'timeMatching': 0,
            'order_price': '0.01234000'
            'order_size': '0.1'
            'executed': '0.1',
            'stop_price': '0.00000000'
            'avg': '0.01234000'
            'total': '0.123 BTC'
            },
        ...
        ]
        :param symbol: str
        :param from_id: str
        :param limit: int
        :return: JSON
        """
        payload = json.dumps({"symbol": symbol,
                              "limit": limit,
                              "from_id": from_id,
                              "timestamp": int(time.time() * 1000)}, separators=(",", ":"))
        self.order_headers["Signature"] = self._sign(payload=payload)
        return self.s.post(self.TRADE_URL + "/order/list/all", headers=self.order_headers, data=payload).json()
    
    def cancel_order(self, order_id, order_symbol):
        """
        Cancels an order ID given the order symbol. 
        {
        'order_symbol': 'BTC_USDT',
        'order_id': '1234-1234-1234-1234-1234',
        'order_size': 0,
        'account_id': '1234-1234-1234-1234-1234',
        'timestamp': 123456789,
        'recvWindow': None
        }
        :param order_id: str
        :param order_symbol: str
        :return: JSON
        """
        payload = json.dumps({"order_id": order_id,
                              "order_symbol": order_symbol,
                              "timestamp": int(time.time() * 1000)}, separators=(",", ":"))
        self.order_headers["Signature"] = self._sign(payload=payload)
        return self.s.delete(self.TRADE_URL + "/order/cancel", headers=self.order_headers, data=payload).json()
    
    def get_order_details(self, order_id):
        """
        Gets details for specific order. 
        {
        'hex_id': None
        'order_id': '1234-1234-1234-1234-1234',
        'account_id': '1234abcd'
        'order_symbol': 'XRP_BTC',
        'order_side': 'SELL'
        'status': 'open',
        'createTime': 123456789
        'type': 'limit',
        'timeMatching': 0
        'order_price': '0.00009500',
        'order_size': '10.3'
        'executed': '0',
        'stop_price': '0.00000000'
        'avg': '0.00009500'
        'total': '0.0009000 BTC'
        }
        :param order_id: str
        :return: JSON
        """
        payload = json.dumps({"order_id": order_id,
                              "timestamp": int(time.time() * 1000)}, separators=(",", ":"))
        self.order_headers["Signature"] = self._sign(payload=payload)
        return self.s.post(self.TRADE_URL + "/order/details", headers=self.order_headers, data=payload).json()
    
    def get_trade_details(self, order_id):
        """
        Returns details for the specified trade. 
        [
            {
            'hex_id': None,
            'symbol': 'BTC_USDT',
            'order_id': '1234-5678-91011-121314-151617',
            'order_side': 'BUY',
            'price': '0.03308000',
            'quantity': '0.1',
            'fee': '0.012345 CFT',
            'additional_fee': None,
            'total': '0.00345 BTC',
            'is_taker': True,
            'timestamp': 123456789
            }
        ]
        :param order_id: str
        :return: JSON
        """
        payload = json.dumps({"order_id": order_id,
                              "timestamp": int(time.time() * 1000)}, separators=(",", ":"))
        self.order_headers["Signature"] = self._sign(payload=payload)
        return self.s.post(self.TRADE_URL + "/order/trade-detail", headers=self.order_headers, data=payload).json()
    
    def test_connection(self):
        """
        Checks connection to the server. 
        {
        'result': True
        }
        :return: JSON
        """
        return self.s.get(self.TRADE_URL + "/ping").json()
    
    def get_server_time(self):
        """
        Gets the current server time. 
        {
        'server_time': 123456789
        }
        :return: JSON
        """
        return self.s.get(self.TRADE_URL + "/time").json()
