## Overview

pyCOSS clears up COSS.io's exchange API to make it easier and more intuitive for developers to develop trading bots on the exchange. It is also intended to allow for developers to use these functions as a template for their own implementations of the API in other languages.

To instantiate the client:
```
from pyCOSS import PyCOSSClient

client = PyCOSSClient(api_public='your_public_key', api_secret='your_secret_key')
```

You can then call all methods associated with the COSS web API.

For example:

```
balances = client.get_balances()
eth_btc = client.get_order_book('ETH_BTC')
order = client.create_order('ETH_BTC', 'BUY', 'limit', 0.5, 0.035)
```

All functions return the JSON response from the API call.


## The pyCOSS Arbitrage Bot

Firstly: __ALL trading is at your own risk when using this script__. _It is intended for educational purposes only_.
Secondly: to use this bot, you will need to have python-binance installed. You can get it here: https://github.com/sammchardy/python-binance . You can also install it directly via:
```
pip install python-binance
```

The bot file itself includes verbose and specific instructions on how to use it. Remember: not liable. Importantly: this bot is almost certainly easily exploitable by bad actors. Be careful.
