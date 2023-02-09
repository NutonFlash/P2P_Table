import requests
import json

# РАБОТА С BINANCE
BIN_ROOT_URL = 'https://api.binance.com'
AVG_PRICE_URL = '/api/v3/avgPrice'
P2P_BIN_URL = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'

currencies = ['USDT', 'BTC', 'BUSD', 'BNB', 'ETH', 'SHIB', 'RUB']

pay_type_russia = ['TinkoffNew', 'RosBankNew', 'RaiffeisenBank', 'QIWI', 'YandexMoneyNew', 'RUBfiatbalance',
            'PostBankNew', 'ABank', 'HomeCreditBank', 'MTSBank', 'Payeer', 'Advcash']

pay_type_ukraine = ['PrivatBank', 'Monobank', 'Sportbank', 'ABank', 'PUMBBank', 'izibank',
                    'OTPBank', 'ForwardBank', 'UAHfiatbalance', 'Wise', 'BANK', 'Revolut']

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "p2p.binance.com",
    "Origin": "https://p2p.binance.com",
    "Pragma": "no-cache",
    "TE": "Trailers",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
}


class Order:
    owner = ''
    asset = ''
    fiat = ''
    pay_method = []
    trade_type = ''
    min_limit = 0
    max_limit = 0
    price = 0

    def __init__(self, owner, asset, fiat, pay_method, trade_type, min_limit, max_limit, price):
        self.owner = owner
        self.asset = asset
        self.fiat = fiat
        self.pay_method = pay_method
        self.trade_type = trade_type
        self.min_limit = min_limit
        self.max_limit = max_limit
        self.price = price

    def toString(self):
        print(
            f'nickName: {self.owner}' + '\n'
            + f'asset: {self.asset}' + '\n'
            + f'fiat: {self.fiat}' + '\n'
            + f'pay_method: {self.pay_method}' + '\n'
            + f'trade_type: {self.trade_type}' + '\n'
            + f'min_limit: {self.min_limit}' + '\n'
            + f'max_limit: {self.max_limit}' + '\n'
            + f'price: {self.price}' + '\n')

# ВОЗВРАЩАЕТ СЛОВАРЬ {ВАЛЮТНАЯ ПАРА: ЦЕНА}
def get_avg_pair_price_dict(currencies):
    currencies_pair_spot = {}
    for cur1 in currencies:
        prices_arr = []
        for cur2 in currencies:
            pair = cur2 + cur1
            if cur2 in cur1:
                prices_arr.append('0')
            else:
                price = get_avg_pair_price(pair)
                if (price == '0'):
                    price = get_avg_pair_price(cur1 + cur2)
                price = round(float(price), 2)
                prices_arr.append(str(price))
        currencies_pair_spot[cur1] = prices_arr
    return currencies_pair_spot

# ВОЗВРАЩАЕТ СРЕДНЮЮ ЦЕНУ ВАЛЮТНОЙ ПАРЫ ЗА ПОСЛЕДНИЕ 5 МИНУТ
def get_avg_pair_price(pair):
    response = requests.get(BIN_ROOT_URL+AVG_PRICE_URL+'?symbol='+pair).text
    json_response = json.loads(response)
    try:
        result = json_response['price']
    except KeyError:
        result = '0'
    return result

# ВОЗВРАЩАЕТ ЛИСТ ОРДЕРОВ С BINANCE P2P
def get_orders(currency, fiat, pay_method, page, trade_type):
    data = {
        'asset': currency,
        'fiat': fiat,
        'page': page,
        'payTypes': pay_method,
        'publisherType': None,
        'rows': 20,
        'tradeType': trade_type
    }
    response = requests.post(P2P_BIN_URL, headers=headers, json=data).text
    orders = []
    for order in json.loads(response)['data']:
        obj = order['adv']
        owner = order['advertiser']['nickName']
        asset = obj['asset']
        fiat = obj['fiatUnit']
        pay_method = []
        for payment in obj['tradeMethods']:
            pay_method.append(payment['identifier'])
        trade_type = obj['tradeType']
        min_limit = float(obj['minSingleTransAmount'])
        max_limit = float(obj['dynamicMaxSingleTransAmount'])
        price = float(obj['price'])
        orders.append(Order(owner, asset, fiat, pay_method, trade_type, min_limit, max_limit, price))
    return orders

# ВРЗВРАЩАЕТ СПИСОК ВСЕХ ОТКРЫТЫХ ОРДЕРОВ
def get_all_orders(currency, fiat, pay_method, trade_type):
    all_orders = []
    page = 1
    while True:
        cur_order_page = get_orders(currency, fiat, pay_method, page, trade_type)
        if cur_order_page:
            all_orders += cur_order_page
            page = page + 1
        else:
            return all_orders

# ВОЗВРАЩАЕТ СЛОВАРЬ, В КОТОРОМ ВСЕ ОРДЕРА ОТСОРТИРОВАНЫ ПО ПЛАТЕЖКАМ В РОССИИ
def get_sorted_orders_dict_rub(orders):
    sorted_orders_dict = {
        'TinkoffNew': list(),
        'RosBankNew': list(),
        'RaiffeisenBank': list(),
        'QIWI': list(),
        'YandexMoneyNew': list(),
        'RUBfiatbalance': list(),
        'PostBankNew': list(),
        'ABank': list(),
        'HomeCreditBank': list(),
        'MTSBank': list(),
        'Payeer': list(),
        'Advcash': list()
    }
    for order in orders:
        for pay_type_in_order in order.pay_method:
            if pay_type_in_order in pay_type_russia:
                sorted_orders_dict.get(pay_type_in_order).append(order)
    return sorted_orders_dict

# ВОЗВРАЩАЕТ СЛОВАРЬ, В КОТОРОМ ВСЕ ОРДЕРА ОТСОРТИРОВАНЫ ПО ПЛАТЕЖКАМ В UKRAINE
def get_sorted_orders_dict_uah(orders):
    sorted_orders_dict = {
        'PrivatBank': list(),
        'Monobank': list(),
        'Sportbank': list(),
        'ABank': list(),
        'PUMBBank': list(),
        'izibank': list(),
        'OTPBank': list(),
        'UAHfiatbalance': list(),
        'Wise': list(),
        'BANK': list(),
        'Revolut': list(),
        'ForwardBank': list()
    }
    for order in orders:
        for pay_type_in_order in order.pay_method:
            if pay_type_in_order in pay_type_ukraine:
                sorted_orders_dict.get(pay_type_in_order).append(order)
    return sorted_orders_dict

# ВОЗВРАЩАЕТ ИЗ СПИСКА ОРДЕРОВ КОЛИЧЕСТВО КРИПТЫ, КОТОРЕ МОЖНО ПОЛУЧИТЬ С КОНКРЕТНЫМ ДЕПОМ
def calc_crypto_amount_from_buy(orders, deposit):
    crypto_amount = 0
    for order in orders:
        if order.min_limit <= deposit:
            if deposit <= order.max_limit:
                crypto_amount += deposit / order.price
                break
            else:
                crypto_amount += order.max_limit / order.price
                deposit -= order.max_limit
        else:
            continue
    return crypto_amount

# ВОЗВРАЩАЕТ ИЗ СПИСКА ОРДЕРОВ СУММУ В ФИАТЕ, КОТОРУЮ МОЖНО ПОЛУЧИТЬ С КОНКРЕТНОГО КОЛИЧЕСТВА КРИПТЫ
def calc_fiat_amount_from_sell(orders, crypto_amount):
    fiat_amount = 0
    for order in orders:
        deposit = crypto_amount * order.price
        if order.min_limit <= deposit:
            if deposit <= order.max_limit:
                fiat_amount += deposit
                break
            else:
                fiat_amount += order.max_limit
                crypto_amount -= order.max_limit / order.price
        else:
            continue
    return fiat_amount

# ВОЗВРАЩАЕТ СРЕДНЮЮ ЦЕНУ ТОП ДВУХ ОРЕДРОВ СТАКАНА
def calc_avg_price_in_limit(orders, limit):
    sum = 0
    counter = 0
    for order in orders:
        if limit < 1500:
            if float(order.min_limit) == limit:
                sum += float(order.price)
                counter += 1
        else:
            if limit >= float(order.min_limit) >= limit * 0.3:
                sum += order.price
                counter += 1
        if counter == 2:
            break
    return sum / 2

