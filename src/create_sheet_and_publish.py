import pandas as pd
import gspread

from datetime import date

DATE_FORMAT = '%d.%m.%Y'

def from_txt_file():
    with open('Mated_from_file.txt', 'r', encoding='utf-8') as file:
        data = file.read()

    list_of_data = data.split('\n')
    for_create = []
    dicts = []
    for el in list_of_data:
        for_create.append(el.split(' '))
    for x in for_create:
        x[0] = x[0][:-1]
    for i in for_create:
        num = i[0]
        box = i[1]
        name = i[2]
        status = i[3]

        raw = {'num':num, 'name': name,'box': box,'status': status,'father': '','result':'' }
        dicts.append(raw)

    return dicts

def prepare_data_to_fill_tab(data): # отримуємо словник для наповнення df
    final =[]
    for x in data:
        raw = {'номер':x[0], "ім'я": x[1],'клітка': x[2],'рейтинг': x[4],'вік':x[5], 'статус': x[3], 'батько': None, 'результат':None, "ім'я_": x[1], 'пальп.клітка': None }
        final.append(raw)

    return final

def create_and_publish(to_fill, sheet_name):
    df = pd.DataFrame(to_fill)  # наповнюємо
    data_to_upload = df.values.tolist()  # main tab
    data_to_upload.insert(0, df.columns.values.tolist())  # insert on top name columns

    gs = gspread.service_account(filename='meatberry_farm_for_gspread.json') # створюємо авторизацію
    sheet = gs.open_by_key('1Nu4JlbhGVOEW1UNg9mCtW-C4rhTmNj0HZkjIAlqlLqo')  # створюємо нову табл на гугл-диску
    worksheet = sheet.add_worksheet(sheet_name, 100, 25)
    worksheet = sheet.worksheet(sheet_name)  #open new start sheet
    worksheet.update(data_to_upload, 'A8') # fill data

def create_and_edit_kindling(sheet_name, data_to_fill, point_fill):
    df = pd.DataFrame(data_to_fill)
    data_to_upload = df.values.tolist()
    data_to_upload.insert(0, df.columns.values.tolist())

    gs = gspread.service_account(filename='meatberry_farm_for_gspread.json')
    sheet = gs.open_by_key('1bghOnHANyqLeAKUbVX-SRjHMw4mFTD8LpN0I4dqARI4')
    worksheet = sheet.worksheet(sheet_name)
    worksheet.update(data_to_fill, point_fill)

def create_and_publish_planned_work(to_fill, sheet_name):
    df = pd.DataFrame(to_fill)  # наповнюємо
    data_to_upload = df.values.tolist()  # main tab
    data_to_upload.insert(0, df.columns.values.tolist())  # insert on top name columns

    gs = gspread.service_account(filename='meatberry_farm_for_gspread.json') # створюємо авторизацію
    sheet = gs.open_by_key('1lfR0wtolQfcJ6DCKm_H3l3WPJPX_t3V_UeEPuTkcgAw')  # створюємо нову табл на гугл-диску
    worksheet = sheet.add_worksheet(sheet_name, 100, 20) #open new start sheet
    worksheet = sheet.worksheet(sheet_name)
    worksheet.update(data_to_upload, 'A2')
