from pycoss import PyCOSSClient
from binance.client import Client
import datetime
import time

#                               [ READ THIS. SERIOUSLY. ]
# [  WARNING  ] [  WARNING  ] [  WARNING  ] [  WARNING  ] [  WARNING  ] [  WARNING  ]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# USE THIS SCRIPT AT YOUR OWN RISK.
# USAGE INSTRUCTIONS, A CHECKLIST, AND FURTHER WARNINGS ARE AT THE BOTTOM OF THE SCRIPT.
# YOU NEED PYTHON-BINANCE INSTALLED FOR THIS TO WORK: https://github.com/sammchardy/python-binance
# YOU CAN INSTALL IT VIA pip install python-binance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# !!! ALL ORDERS ARE LIVE. !!! COSS DOES NOT CURRENTLY HAVE TEST ORDERS.
# THIS SCRIPT IS INTENDED TO BE AN _EXAMPLE_ FOR BOT MAKERS.
# HOWEVER, IT WORKS. IT _CAN_ BE PROFITABLE. THIS DOES NOT MEAN YOU _SHOULD_ USE IT.
# THIS SCRIPT IS FOR EDUCATIONAL PURPOSES _ONLY_.
# !!! I AM NOT LIABLE IF YOU LOSE MONEY. !!!
# I WILL REFER YOU BACK TO THIS MESSAGE IF YOU LOSE MONEY.
# !!! DO NOT FORGET TO EDIT YOUR FEES. !!!
# LIMIT ORDERS ARE CURRENTLY _HARDCODED_.
# THIS CAN BE CHANGED, BUT REMEMBER: IT CHANGES THE FEE PERCENTAGES AND HOW THE BOT WORKS.
# !!! YOU HAVE BEEN WARNED !!!
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# [  WARNING  ] [  WARNING  ] [  WARNING  ] [  WARNING  ] [  WARNING  ] [  WARNING  ]

# Place your public and secret API keys for COSS and Binance here.
# Want to use a different exchange? This script should easily be adaptable to use CCXT or other exchange clients.
# The principles are the same.
binance_client = Client(api_key="",
                        api_secret="")
coss_client = PyCOSSClient(api_public="",
                           api_secret="")
# YOU WILL NEED TO EDIT THESE FEES TO MEET YOUR OWN FEE LIMITS!
# DO _NOT_ BEGIN TRADING UNTIL YOU ARE CERTAIN OF THESE VALUES!
# IT IS _HIGHLY RECOMMENDED_ TO USE [BNB] AND [CFT] FOR YOUR TRADING FEES TO GIVE YOU MORE TRADING OPPORTUNITIES.
# THE FEES ARE CURRENTLY SET TO INDICATE YOU OWN BOTH [BNB] AND [CFT] AND HAVE THEM ENABLED AS YOUR FEE PAYING TOKENS
# FOR BOTH EXCHANGES.
# You can find your COSS fees on the exchange page in the bottom right.
# Binance has a fee page but also includes your fee percentages on its exchange pages.
COSS_TAKER_FEE = 0.0015
COSS_MAKER_FEE = 0.00105
BIN_MAKER_FEE = 0.00075
BIN_TAKER_FEE = 0.00075
# Here you'll need to place the relevant PAIR and AMOUNT for what you would like to order.
# REMEMBER: The amount MUST exceed the minimum order limit for BOTH exchanges.
# What this means is that occasionally COSS has a lower minimum order threshold than Binance which can result
# in one or neither order being placed.
# Example of amount dictionary formatting:
# order_amounts = {"ETH_BTC": 0.03, "LTC/BTC": 0.15, ... }
order_amounts = {}


def arbitrage_bot(symbol, slippage_protection=True, threshold=0.1):
    """
    This is a DEMONSTRATION bot for arbitrage between COSS and Binance using python-binance and pyCOSS.
    DEFAULT BEHAVIOR:
        1. Calculates the ROI minus fees of buying and selling on either exchange for selected symbol.
           Note that both exchanges must have the market you intend to trade on (e.g. not COSS_ETH).
        2. Checks for slippage on orders (i.e. buying or selling beyond the best ROI price).
        3. If there is no slippage and the ROI is higher than your threshold, the bot executes your orders.

    You can change slippage_protection to False if you want specific behavior on certain symbols or make it default.
    Slippage protection is explained in more detail below.

    The threshold has been intentionally set to a conservative value.
    In theory, the bot will return a profit when ROI is > 0. However, it can also result in a small loss.
    This is due to differences in how the exchanges and the bot calculate profitability.

    :param symbol: str
    :param slippage_protection: Boolean
    :param threshold: float
    :return: str
    """
    symbol_dict = dict()
    symbol_dict[symbol] = {}
    bin_ob = binance_client.get_order_book(symbol=symbol.replace("_", ""), limit=5)
    coss_ob = coss_client.get_order_book(symbol="ETH_BTC")
    symbol_dict[symbol]["bin_ask"] = float(bin_ob["asks"][0][0])
    symbol_dict[symbol]["bin_bid"] = float(bin_ob["bids"][0][0])
    symbol_dict[symbol]["coss_ask"] = float(coss_ob["asks"][0][0])
    symbol_dict[symbol]["coss_bid"] = float(coss_ob["bids"][0][0])

    symbol_dict[symbol]["bin_ask_amount"] = float(bin_ob["asks"][0][1])
    symbol_dict[symbol]["coss_bid_amount"] = float(coss_ob["bids"][0][1])
    symbol_dict[symbol]["coss_ask_amount"] = float(coss_ob["asks"][0][1])
    symbol_dict[symbol]["bin_bid_amount"] = float(bin_ob["bids"][0][1])

    symbol_dict[symbol]["buy_bin_sell_coss_roi_pct"] = (symbol_dict[symbol]["coss_bid"] *
                                                        (1 - COSS_MAKER_FEE) /
                                                        (symbol_dict[symbol]["bin_ask"] *
                                                         (1 + BIN_MAKER_FEE) - 1) * 100)
    symbol_dict[symbol]["buy_coss_sell_bin_roi_pct"] = (symbol_dict[symbol]["bin_bid"] *
                                                        (1 - BIN_MAKER_FEE) /
                                                        (symbol_dict[symbol]["coss_ask"] *
                                                         (1 + COSS_MAKER_FEE) - 1) * 100)
    # Fail early if the current trading pair isn't profitable.
    if symbol_dict[symbol]["buy_bin_sell_coss_roi_pct"] and symbol_dict[symbol]["buy_coss_sell_bin_roi_pct"] <= 0:
        return "{0} | {1} UNPROFITABLE | COSS ROI {2} | BINANCE ROI {3}".format(datetime.datetime.now().time(),
                                                                                symbol,
                                                                                symbol_dict[symbol][
                                                                                    "buy_coss_sell_bin_roi_pct"],
                                                                                symbol_dict[symbol][
                                                                                    "buy_bin_sell_coss_roi_pct"])

    # ~~~ How slippage protection (ENABLED BY DEFAULT) works ~~~
    # IF: the ROI is profitable for at least one of the exchanges ABOVE USER-SET THRESHOLD (KEEP IT ABOVE 0 ;) )
    # AND: neither amount is smaller than your order amount...
    # THEN: place your orders!
    # BUY at Exchange A's ASK price
    # SELL at Exchange B's BID price
    # Resulting in a profit of the DIFFERENCE between the two prices.
    # If slippage protection IS NOT ENABLED, it allows you to place orders at a price that may only be
    # PARTIALLY FILLED (i.e., you buy or sell more than the top order can fulfil).
    # The order will stay on the books UNTIL IT IS FILLED.
    if symbol_dict[symbol]["buy_bin_sell_coss_roi_pct"] > threshold and slippage_protection and (
            symbol_dict[symbol]["bin_ask_amount"] and symbol_dict[symbol]["coss_bid_amount"]) >= order_amounts[symbol]:
        binance_client.create_order(symbol=symbol.replace("_", ""),
                                    side="BUY",
                                    type="limit",
                                    amount=order_amounts[symbol],
                                    price=symbol_dict[symbol]["bin_ask"])
        coss_client.create_order(symbol=symbol,
                                 side="SELL",
                                 order_type="limit",
                                 size=order_amounts[symbol],
                                 price=symbol_dict[symbol]["coss_bid"])
        return "{0} | {1} | BOUGHT BINANCE | SOLD COSS | {2}% PROFIT".format(datetime.datetime.now().time(),
                                                                             symbol,
                                                                             symbol_dict[symbol][
                                                                                 "buy_bin_sell_coss_roi_pct"])
    elif symbol_dict[symbol]["buy_coss_sell_bin_roi_pct"] > threshold and slippage_protection:
        coss_client.create_order(symbol=symbol,
                                 side="BUY",
                                 order_type="limit",
                                 size=order_amounts[symbol],
                                 price=symbol_dict[symbol]["coss_ask"])
        binance_client.create_order(symbol=symbol.replace("_", ""),
                                    side="SELL",
                                    type="limit",
                                    amount=order_amounts[symbol],
                                    price=symbol_dict[symbol]["bin_bid"])
        return "{0} | {1} | BOUGHT COSS | SOLD BINANCE | {2}% PROFIT".format(datetime.datetime.now().time(),
                                                                             symbol,
                                                                             symbol_dict[symbol][
                                                                                 "buy_coss_sell_bin_roi_pct"])
    elif symbol_dict[symbol]["buy_bin_sell_coss_roi_pct"] > threshold and not slippage_protection:
        binance_client.create_order(symbol=symbol.replace("_", ""),
                                    side="BUY",
                                    type="limit",
                                    amount=order_amounts[symbol],
                                    price=symbol_dict[symbol]["bin_ask"])
        coss_client.create_order(symbol=symbol,
                                 side="SELL",
                                 order_type="limit",
                                 size=order_amounts[symbol],
                                 price=symbol_dict[symbol]["coss_bid"])
        return "{0} | {1} | BOUGHT BINANCE | SOLD COSS | {2}% PROFIT".format(datetime.datetime.now().time(),
                                                                             symbol,
                                                                             symbol_dict[symbol][
                                                                                 "buy_bin_sell_coss_roi_pct"])
    elif symbol_dict[symbol]["buy_coss_sell_bin_roi_pct"] > threshold and not slippage_protection:
        coss_client.create_order(symbol=symbol,
                                 side="BUY",
                                 order_type="limit",
                                 size=order_amounts[symbol],
                                 price=symbol_dict[symbol]["coss_ask"])
        binance_client.create_order(symbol=symbol.replace("_", ""),
                                    side="SELL",
                                    type="limit",
                                    amount=order_amounts[symbol],
                                    price=symbol_dict[symbol]["bin_bid"])
        return "{0} | {1} | BOUGHT COSS | SOLD BINANCE | {2}% PROFIT".format(datetime.datetime.now().time(),
                                                                             symbol,
                                                                             symbol_dict[symbol][
                                                                                 "buy_coss_sell_bin_roi_pct"])


# !!! AGAIN: ALL TRADING IS _AT YOUR OWN RISK_. I AM NOT LIABLE FOR ANY PROFITS OR LOSSES YOU INCUR BY USING THIS. !!!
# SCRIPT CHECKLIST:
# 1. Do you have a SUFFICIENT BALANCE of each coin you wish to trade on BOTH exchanges?
#    What you might find is that you tend to sell a lot more on one exchange than the other.
#    You will need to periodically balance your portfolio via deposits and withdrawals to allow you to trade.
#    Therefore, ensure that your market is NOT disabled on both exchanges AND that it is accepting
#    deposits and withdrawals before you begin.
# 2. Have you got your API KEYS in the relevant places?
# 3. Have you ensured your FEE PERCENTAGES are correct?
# 4. Have you put "symbol":amount pairs for each symbol you intend to trade in order_amounts?
# 5. Have you set an APPROPRIATE PROFITABILITY THRESHOLD?

# If you can answer yes to all of those questions, here are examples below of you can use the bot.
# NOTE: If you are finding yourself timing out due to a rate limit or running out of funds quickly,
# you can add a sleep function underneath each call to help ensure you do not inadvertently buy or sell
# into your own partial orders. It is highly recommended you do so.
# The above should only really be a problem if you are trading a low liquidity pair OR you are trading VERY fast.
# This is not necessarily A Bad Thing. But it can often result in confusion.
# Examples below.

# Single pair with default settings.
# while True:
#    print(arbitrage_bot("ETH_BTC"))
#    time.sleep(10)

# Multiple pairs with default settings.
# You'll need to ensure that you have "symbol":amount pairs for ALL traded symbols in order_amounts.
# while True:
#   print(arbitrage_bot("ETH_BTC"))
#   time.sleep(10)
#   print(arbitrage_bot("LTC_BTC"))
#   time.sleep(10)

# Multiple pairs with and without slippage protection.
# while True:
#   print(arbitrage_bot("ETH_BTC"))
#   time.sleep(30)
#   print(arbitrage_bot("LTC_BTC", slippage_protection=False, threshold=0))
#   time.sleep(30)
#   print(arbitrage_bot("LTC_ETH", slippage_protection=False, threshold=0.15))

# Alternative
# l = ["ETH_BTC", "LTC_BTC", "LTC_ETH"]
# while True:
#   for symbol in l:
#       print(arbitrage_bot(symbol))
#       time.sleep(60)
