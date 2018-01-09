from collections import namedtuple
from datetime import datetime
from pprint import pprint

from django.shortcuts import render
from django.views.generic import View
import plotly.offline as opy
import plotly.graph_objs as go

from .utils import get_crypto_ticker, get_usdjpy, get_eurjpy

Target = namedtuple('Target', ('exchange_id', 'currency_pair'))

TARGETS = [
    # Kraken
    Target('kraken', 'BTC/EUR'),
    # Target('kraken', 'BCH/EUR'),
    # Target('kraken', 'ETH/EUR'),

    # Zaif
    Target('zaif', 'BTC/JPY'),
    # Target('zaif', 'BCH/JPY'),
    # Target('zaif', 'ETH/JPY'),

    # Coincheck
    Target('coincheck', 'BTC/JPY'),
    Target('poloniex', 'BCH/USDT'),
    Target('poloniex', 'ETH/USDT'),
]


class Currency:
    def __init__(self, exchange_id, ticker, currency_exchange_rates=None):
        self.exchange_id = exchange_id
        self.symbol = ticker['symbol'].split('/')[0]
        self.base_currency = ticker['symbol'].split('/')[1]
        self.currency_exchange_rates = currency_exchange_rates
        self.price = ticker['last']
        if self.base_currency == 'JPY':
            self.price_jpy = self.price
        elif self.base_currency == 'USD':
            self.price_jpy = self.price * currency_exchange_rates['USD/JPY']
        elif self.base_currency == 'EUR':
            self.price_jpy = self.price * currency_exchange_rates['EUR/JPY']
        else:
            self.price_jpy = None

    def __repr__(self):
        return str({
            'exchange_id': self.exchange_id,
            'symbol': self.symbol,
            'base_currency': self.base_currency,
            'price': self.price,
            'price_jpy': self.price_jpy,
        })


class PricesIndexView(View):
    def get(self, request, *args, **kwargs):
        now = datetime.now()
        print(now.strftime('%Y/%m/%d %H:%M:%S'))

        usd_jpy = get_usdjpy()
        eur_jpy = get_eurjpy()
        print('USD/JPY={}'.format(usd_jpy))
        print('EUR/JPY={}'.format(eur_jpy))
        currency_exchange_rates = {
            'USD/JPY': usd_jpy,
            'EUR/JPY': eur_jpy,
        }

        currencies = []
        for target in TARGETS:
            ticker = get_crypto_ticker(target.exchange_id, target.currency_pair)
            print('--- {} {}--------'.format(target.exchange_id, target.currency_pair))
            pprint(ticker)
            currencies.append(Currency(target.exchange_id, ticker, currency_exchange_rates))

        # print('--- currencies ' + '-' * 50)
        # pprint(currencies)

        trace = go.Table(
            header=dict(values=['A Scores', 'B Scores'],
                        line=dict(color='#7D7F80'),
                        fill=dict(color='#a1c3d1'),
                        align=['left'] * 5),
            cells=dict(values=[[100, 90, 80, 90],
                               [95, 85, 75, 95]],
                       line=dict(color='#7D7F80'),
                       fill=dict(color='#EDFAFF'),
                       align=['left'] * 5))

        layout = dict(width=500, height=300)
        data = [trace]
        fig = dict(data=data, layout=layout)
        div = opy.plot(fig, auto_open=False, output_type='div')

        return render(request, 'prices/index.html', {
            'currencies': currencies,
            'usd_jpy': usd_jpy,
            'eur_jpy': eur_jpy,
            'graph': div,
        })
