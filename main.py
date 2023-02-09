from spreadsheets import spreadsheet_tools
from binance import binance_parser
import time

SPREADSHEET_ID = '1RHEkv9TJYh2R7QZxUlOHTBkLtpghSekden_WKQkhaoI'
CREDENTIALS_FILE = 'p2p-table-377308-5ec048826254.json'
SHEETS = ['Binance', 'RUB - SELL (Binance)']

httpAuth = spreadsheet_tools.authorize(CREDENTIALS_FILE)
service = spreadsheet_tools.create_service(httpAuth)

crypto_spot_values = {}
sorted_buy_orders_dict = {}
sorted_sell_orders_dict = {}

# ПАРСИТ ВАЛЮТНЫЕ ПАРЫ С BINANCE И ОБНОВЛЯЕТ EXCEL SHEET
def update_spot_values():
    range = SHEETS[0] + '!L5:R11'
    values = []
    crypto_spot_values = binance_parser.get_avg_pair_price_dict(binance_parser.currencies)
    for key, val in crypto_spot_values.items():
        values += [val]
    major_dimension = 'ROWS'
    value_input_option = 'USER_ENTERED'
    table = spreadsheet_tools.Table(range, values, major_dimension, value_input_option)
    spreadsheet_tools.create_table(service, SPREADSHEET_ID, table)

# ПАРСИТ ВСЕ RUB - BUY ОРДЕРА ПО КАЖДОЙ ИЗ ВАЛЮТ,
# СЧИТАЕТ ОПТИМАЛЬНОЕ КОЛ-ВО КРПИТЫ, КОТОРОЕ МОЖНО КУПИТЬ ПО ЗАДАННОМУ ДЕПУ ПО КАЖДОЙ ПЛАТЕЖКЕ
def update_buy_orders(deposit, currency, pay_type):
    values = []
    for crypto in binance_parser.currencies:
        orders = binance_parser.get_all_orders(crypto, currency, pay_type, 'BUY')
        sorted_orders = binance_parser.get_sorted_orders_dict_rub(orders)
        sorted_buy_orders_dict[crypto] = sorted_orders
        crypto_amount_arr = []
        for key, val in sorted_orders.items():
            amount = binance_parser.calc_crypto_amount_from_buy(val, deposit)
            crypto_amount_arr.append(str(amount))
        values.append(crypto_amount_arr)
    table_range = SHEETS[0] + '!B5:H16'
    major_dimension = 'COLUMNS'
    value_input_option = 'USER_ENTERED'
    table = spreadsheet_tools.Table(table_range, values, major_dimension, value_input_option)
    spreadsheet_tools.create_table(service, SPREADSHEET_ID, table)

# ПАРСИТ ВСЕ RUB - SELL ОРДЕРА ПО КАЖДОЙ ИЗ ВАЛЮТ,
# СЧИТАЕТ ОПТИМАЛЬНОЕ КОЛ-ВО КРПИТЫ, КОТОРОЕ МОЖНО КУПИТЬ ПО ЗАДАННОМУ ДЕПУ ПО КАЖДОЙ ПЛАТЕЖКЕ
def update_rub_sell_orders(crypto_amount):
    values = []
    for crypto in binance_parser.currencies:
        orders = binance_parser.get_all_orders(crypto, 'RUB', binance_parser.pay_type_russia, 'SELL')
        sorted_orders = binance_parser.get_sorted_orders_dict_rub(orders)
        sorted_sell_orders_dict[crypto] = sorted_orders
        fiat_amount_arr = []
        for key, val in sorted_orders.items():
            amount = binance_parser.calc_fiat_amount_from_sell(val, crypto_amount)
            fiat_amount_arr.append(str(amount))
        values.append(fiat_amount_arr)
    table_range = SHEETS[1] + '!B5:H16'
    major_dimension = 'COLUMNS'
    value_input_option = 'USER_ENTERED'
    table = spreadsheet_tools.Table(table_range, values, major_dimension, value_input_option)
    spreadsheet_tools.create_table(service, SPREADSHEET_ID, table)

# ОБНОВЛЯЕТ ТАБЛИЦУ ТОПОВОЙ ЦЕНЫ В СТАКАНЕ
def update_top_price_by_limit_table(table_range, limit):
    values = []
    for crypto, val_dict in sorted_buy_orders_dict.items():
        avg_price_by_crypto = []
        for pay_method, val in val_dict.items():
            avg_price = binance_parser.calc_avg_price_in_limit(val, limit)
            avg_price_by_crypto.append(str(avg_price))
        values.append(avg_price_by_crypto)
    major_dimension = 'COLUMNS'
    value_input_option = 'USER_ENTERED'
    table = spreadsheet_tools.Table(table_range, values, major_dimension, value_input_option)
    spreadsheet_tools.create_table(service, SPREADSHEET_ID, table)

# binance_parser.get_all_orders('SHIB', 'RUB', [], 'BUY')

deposit = 100000
while True:
    update_spot_values()
    update_buy_orders(deposit, 'RUB', binance_parser.pay_type_russia)
    print('Обновилась таблица c количеством крипты по депу ' + str(deposit))
    update_top_price_by_limit_table(SHEETS[0] + '!B20:H31', 500)
    print('Обновилась таблица по лимиту ордеров от 500')
    update_top_price_by_limit_table(SHEETS[0] + '!B34:H45', 5000)
    print('Обновилась таблица по лимиту ордеров от 5000')
    update_top_price_by_limit_table(SHEETS[0] + '!B48:H59', 50000)
    print('Обновилась таблица по лимиту ордеров от 50000')
    str_time = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())
    print('Время обновления: ' + str_time)
    table = spreadsheet_tools.Table(SHEETS[0] + '!B2:C2', [[str_time]], 'ROWS', 'USER_ENTERED')
    spreadsheet_tools.create_table(service, SPREADSHEET_ID, table)
    time.sleep(90)
