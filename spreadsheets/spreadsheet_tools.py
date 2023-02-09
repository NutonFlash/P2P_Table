import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials

class Table:
    range = ''
    values = []
    major_dimension = ''
    value_input_option = ''

    def __init__(self, range, values, major_dimension, value_input_option):
        self.range = range
        self.values = values
        self.major_dimension = major_dimension
        self.value_input_option = value_input_option


# АВТОРИЗИРУЕТ В СИСТЕМЕ ПО КЛЮЧАМ ИЗ JSON ФАЙЛА
def authorize(CREDENTIALS_FILE):
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    # Авторизуемся в системе
    return credentials.authorize(httplib2.Http())

# ДОБАВЛЯЕТ ПРАВА НА РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯМ
def add_access(httpAuth, spreadsheetId, mail):
    # Выбираем работу с Google Drive и 3 версию API
    driveService = apiclient.discovery.build('drive', 'v3', http=httpAuth)
    # Открываем доступ на редактирование
    driveService.permissions().create(
        fileId=spreadsheetId,
        body={'type': 'user', 'role': 'writer', 'emailAddress': mail},
        fields='id'
    ).execute()

# СОЗДАЕТ ОБЪЕКТ ДЛЯ РАБОТЫ С СЕРВИСАМИ SPREADSHEET
def create_service(httpAuth):
    # Выбираем работу с таблицами и 4 версию API
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
    return service

# СОЗДАЕТ НОВЫЙ ФАЙЛ С ТАБЛИЦАМИ И ВОЗВРАЩАЕТ ЕГО ID
def create_spreadsheet(service, properties, sheets):
    spreadsheet = service.spreadsheets().create(body={
        'properties': properties,
        'sheets': sheets
    }).execute()
    return spreadsheet['spreadsheetId']

# СОЗДАЕТ ТАБЛИЦУ ПО ДАННЫМ ОБЪЕКТА table
def create_table(service, spreadsheetId, table):
    data = [
        {
            'range': table.range,
            'values': table.values,
            'majorDimension': table.major_dimension
        }
    ]
    body = {
        'valueInputOption': table.value_input_option,
        'data': data
    }
    service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheetId, body = body).execute()

