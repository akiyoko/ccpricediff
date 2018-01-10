# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta, timezone

import ccxt
import requests
from pymongo import MongoClient, DESCENDING
import pymongo.errors

env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../env.py')
if os.path.exists(env_file):
    exec(open(env_file, 'rb').read())


def create_crypto_exchange(exchange_id):
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
    Get ticker from exchange

    :param exchange_id: id of exchange market
                        ex) 'coinmarketcap', 'bittrex'
                        cf) https://github.com/ccxt/ccxt#supported-cryptocurrency-exchange-markets
    :param currency_pair: ex) 'BTC/USD'
    :return:
    """
    ex = create_crypto_exchange(exchange_id)
    ticker = ex.fetch_ticker(currency_pair)
    return ticker


def get_fiat_rate(currency_pair):
    """
    :param currency_pair: ex) 'USD/JPY', 'EUR/JPY'
    :return:
    """
    url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency}&to_currency={to_currency}&apikey={api_key}'.format(
        from_currency=currency_pair.split('/')[0],
        to_currency=currency_pair.split('/')[1],
        api_key=ALPHA_VANTAGE_API_KEY,
    )
    res_json = requests.get(url).json()
    print('res_json={}'.format(res_json))
    rate_dict = res_json['Realtime Currency Exchange Rate']
    return {
        'currency_pair': currency_pair,
        'rate': float(rate_dict['5. Exchange Rate']),
        'datetime': datetime.strptime(rate_dict['6. Last Refreshed'], '%Y-%m-%d %H:%M:%S'),
    }


def get_fiat_rate_from_mongo(currency_pair):
    # Find one which was saved on MongoDB within 30(+α) mins
    collection = MongoClient(serverSelectionTimeoutMS=1000)['fiats']['alphavantage']
    try:
        return collection.find_one(
            {'currency_pair': currency_pair, 'datetime': {'$gte': datetime.now(timezone.utc) - timedelta(minutes=40)}},
            {'_id': False},
            sort=[('datetime', DESCENDING)]
        )
    except pymongo.errors.ConnectionFailure:
        return None


def get_usdjpy():
    fiat_rate = get_fiat_rate_from_mongo('USD/JPY') or get_fiat_rate('USD/JPY')
    return fiat_rate['rate']


def get_eurjpy():
    fiat_rate = get_fiat_rate_from_mongo('EUR/JPY') or get_fiat_rate('EUR/JPY')
    return fiat_rate['rate']
