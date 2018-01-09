# -*- coding: utf-8 -*-

import os

import ccxt
import requests

env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../env.py')
if os.path.exists(env_file):
    exec(open(env_file, 'rb').read())


def _create_crypto_exchange(exchange_id):
    api_key = None
    api_secret = None
    try:
        api_key = eval('{}_KEY'.format(exchange_id.upper()))
        api_secret = eval('{}_SECRET'.format(exchange_id.upper()))
    except NameError:
        pass

    if api_key and api_secret:
        ex = getattr(ccxt, exchange_id)({
            'apiKey': api_key,
            'secret': api_secret,
        })
    else:
        ex = getattr(ccxt, exchange_id)()

    return ex


def get_crypto_ticker(exchange_id, currency_pair):
    """
    :param exchange_id: id of exchange market
                        ex) 'coinmarketcap', 'bittrex'
                        cf) https://github.com/ccxt/ccxt#supported-cryptocurrency-exchange-markets
    :param currency_pair: ex) 'BTC/USD'
    :return:
    """
    ex = _create_crypto_exchange(exchange_id)

    # Get ticker from exchange
    ticker = ex.fetch_ticker(currency_pair)
    return ticker


def get_currency_exchange_rate(from_currency, to_currency):
    url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency}&to_currency={to_currency}&apikey={api_key}'.format(
        from_currency=from_currency,
        to_currency=to_currency,
        api_key=ALPHA_VANTAGE_API_KEY,
    )
    res_json = requests.get(url).json()
    print('res_json={}'.format(res_json))
    return float(res_json['Realtime Currency Exchange Rate']['5. Exchange Rate'])


def get_usdjpy():
    return get_currency_exchange_rate('USD', 'JPY')


def get_eurjpy():
    return get_currency_exchange_rate('EUR', 'JPY')




