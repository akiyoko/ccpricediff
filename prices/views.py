from collections import namedtuple
from datetime import datetime
from pprint import pprint

from ccxt.base.errors import NetworkError
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from .utils import get_crypto_ticker, get_usdjpy, get_eurjpy

Target = namedtuple('Target', ('exchange_id', 'currency_pair', 'currency_pair2'))

BTC_TARGETS = [
    Target('kraken', 'BTC/USD', None),
    Target('kraken', 'BTC/EUR', None),
    Target('zaif', 'BTC/JPY', None),
    Target('coincheck', 'BTC/JPY', None),
]
BCH_TARGETS = [
    Target('kraken', 'BCH/USD', None),
    Target('kraken', 'BCH/EUR', None),
    Target('kraken', 'BCH/BTC', 'BTC/USD'),
    Target('kraken', 'BCH/BTC', 'BTC/EUR'),
    Target('zaif', 'BCH/JPY', None),
    Target('zaif', 'BCH/BTC', 'BTC/JPY'),
]
ETH_TARGETS = [
    Target('kraken', 'ETH/USD', None),
    Target('kraken', 'ETH/EUR', None),
    Target('kraken', 'ETH/BTC', 'BTC/USD'),
    Target('kraken', 'ETH/BTC', 'BTC/EUR'),
    Target('zaif', 'ETH/JPY', None),
    Target('zaif', 'ETH/BTC', 'BTC/JPY'),
]


class Currency:
    def __init__(self, exchange_id, ticker, fiat_rates=None):
        self.exchange_id = exchange_id
        self.symbol = ticker['symbol']
        self.base_currency = ticker['symbol'].split('/')[-1]
        last_price = ticker['last']
        self.price_usd = None
        self.price_eur = None
        self.price_jpy = None
        if self.base_currency == 'JPY':
            self.price_jpy = last_price
        elif self.base_currency == 'USD' or self.base_currency == 'USDT':
            self.price_usd = last_price
            self.price_jpy = last_price * fiat_rates['USD/JPY']
        elif self.base_currency == 'EUR':
            self.price_eur = last_price
            self.price_jpy = last_price * fiat_rates['EUR/JPY']

    def to_dict(self):
        return {
            'exchange_id': self.exchange_id,
            'symbol': self.symbol,
            'price_usd': self.price_usd,
            'price_eur': self.price_eur,
            'price_jpy': self.price_jpy,
        }

    def __repr__(self):
        return str(self.to_dict())


@method_decorator(login_required, name='dispatch')
class PricesIndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'prices/index.html')


@method_decorator(login_required, name='dispatch')
class CurrentPriceView(View):
    def get(self, request, *args, **kwargs):
        symbol = request.GET.get('symbol')
        now = datetime.now()
        print(now.strftime('%Y/%m/%d %H:%M:%S'))

        usd_jpy = get_usdjpy()
        eur_jpy = get_eurjpy()
        # TODO: Dummy
        # usd_jpy = 111.111
        # eur_jpy = 133.333
        print('USD/JPY={}'.format(usd_jpy))
        print('EUR/JPY={}'.format(eur_jpy))
        fiat_rates = {
            'USD/JPY': usd_jpy,
            'EUR/JPY': eur_jpy,
        }

        targets = []
        if symbol == 'btc':
            targets = BTC_TARGETS
        elif symbol == 'bch':
            targets = BCH_TARGETS
        elif symbol == 'eth':
            targets = ETH_TARGETS

        currencies = []
        max_price_jpy = 0
        min_price_jpy = float('inf')
        for target in targets:
            try:
                ticker = get_crypto_ticker(target.exchange_id, target.currency_pair)
                # print('--- {} {} ---'.format(target.exchange_id, target.currency_pair))
                # pprint(ticker)
                currency = Currency(target.exchange_id, ticker, fiat_rates)
                # NOTE: Overwrite currency if currency_pair2 is set
                if target.currency_pair2:
                    ticker2 = get_crypto_ticker(target.exchange_id, target.currency_pair2)
                    # NOTE: symbol is set to be like 'ETH/BTC/USD'
                    ticker['symbol'] = '{}/{}'.format(target.currency_pair, target.currency_pair2.split('/')[1])
                    ticker['last'] = ticker['last'] * ticker2['last']
                    currency = Currency(target.exchange_id, ticker, fiat_rates)
            except NetworkError as e:
                print(e)
                continue
            currencies.append(currency.to_dict())
            max_price_jpy = max(max_price_jpy, currency.price_jpy)
            min_price_jpy = min(min_price_jpy, currency.price_jpy)

        return JsonResponse({
            # 'currencies': currencies,
            'currencies': [dict(c, diff_jpy=c['price_jpy'] - min_price_jpy, diff_jpy_rate=(c['price_jpy'] - min_price_jpy) / c['price_jpy'] * 100) for c in currencies],
            'now': now.strftime('%Y/%m/%d %H:%M:%S'),
            'symbol': symbol,
            'usd_jpy': usd_jpy,
            'eur_jpy': eur_jpy,
        })
        # return JsonResponse({
        #     'status': False,
        #     'message': 'Timeout'
        # }, status=500)
