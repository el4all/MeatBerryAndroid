import json
import  io

import flet as ft
import requests

from datetime import datetime, timedelta, time
from loguru import logger
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials

from bunny_classes import Farm, Bunny, Nest, Box, STATUS_WORK
from work_with_files import open_and_read_json, write_json
from puthon_logic_func import (looking_for_work, set_rabbit_culling, rewrite_block_and_box, remove_by_death, remove_by_culling,
                               vacant_index_for_rabbit, empty_boxes, create_and_add_new_bunny)
from helper_functions import create_rabbit_card, change_box_for_rabbit
from buttons_filters import (BTN_SYNC, get_sort_menu, get_operations_by_rabbit, get_nest_info_container, get_text_fields_for_swap_boxes,
                             get_operations_by_many_rabbits)

URL = 'https://drive.google.com/uc?export=download&id=1459S6Uo3w-f5i5KnDhV5XG0RFCNBDLgW'
DATE_FORMAT = '%d.%m.%Y'

def file_from_google():
    try:
        response = requests.get(URL, timeout=(5,30))
        response.raise_for_status()
        data = response.json()

        return data
    except Exception as e:
        print(f'Error download: {e}')
        return {'rabbits': {}}

def file_upload_google():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('meatberry_farm_for_gspread.json', scopes=SCOPES)
    drive_service = build('drive','v3', credentials=creds)

    FILE_ID = '1459S6Uo3w-f5i5KnDhV5XG0RFCNBDLgW'

    print(meatberry.save_to_json())
    json_string = json.dumps(meatberry.save_to_json(), ensure_ascii=False, indent=4)
    print(json_string)

    json_bytes = io.BytesIO(json_string.encode('utf-8'))
    media = MediaIoBaseUpload(json_bytes, mimetype='application/json', resumable=True)

    try:
        drive_service.files().update(fileId=FILE_ID, media_body=media).execute()
        print('Syncroo')
        return True

    except Exception as e:
        print(e)
        return False

farm_dict = file_from_google()
file_name = 'ACTUALLY_FARM.json'
meatberry = Farm('MeatBerry')
meatberry.load_from_network(farm_dict)


def main(page: ft.Page):
    main_content = ft.Container(expand=True)

    page.title = "Моя Ферма"
    page.scroll = ft.ScrollMode.AUTO  # Дозволяє гортати екран, якщо список великий
    dialog = ft.AlertDialog(title='eeee', modal=True)
    page.overlay.append(dialog)

    navigation = []
    BTN_SYNC.on_click = file_upload_google

    def open_alert_dialog():
        dialog.open = True
        page.update()

    def close_alert_dialog():
        dialog.open = False
        page.update()

    def navigate_to(func, *args):
        navigation.append((func, args))
        func(*args)

    def go_back():
        if len(navigation) > 1:
            navigation.pop()
            previous_func, args = navigation[-1]
            previous_func(*args)
        else:
            page.run_task(page.window.close)

    def set_bottom_app_bar(left_button=None):
        page.bottom_appbar = ft.BottomAppBar(content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                            controls=[left_button if left_button else ft.Container(),
                                                            ft.Button('<-- Назад', on_click=lambda e: go_back())]))
        page.update()

    def set_appbar(left_actions=None, right_actions=None):
        page.appbar = ft.AppBar(leading=left_actions if left_actions else ft.Container(),
                                               actions=right_actions if right_actions else ft.Container())

        page.update()

    def show_main_menu():

        main_content.content = ft.Column([ft.Text('Головне меню ферми', size=16, weight=ft.FontWeight.W_500),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.PETS), title=ft.Text('Кролиці'), on_click=lambda e: navigate_to(show_rabbit_list)),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.PETS), title=ft.Text('Третя кімната')),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.CASINO), title=ft.Text('Кладовище')),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.NIGHTLIFE), title=ft.Text('Вибраківка'), on_click= lambda e: navigate_to(show_defective))
                                          ])
        set_appbar(right_actions=BTN_SYNC)
        set_bottom_app_bar()
        main_content.update()

    page.appbar = ft.AppBar(title=ft.Text('MeatBerryFarm'),
                            actions=[BTN_SYNC])

    page.bottom_appbar = ft.BottomAppBar(padding=10,
                              content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                              controls=[ft.Button('<-- Назад', on_click= lambda  e: show_main_menu()), ft.Text('v1.0')]))

    page.add(main_content)
    page.update()

    def show_rabbit_list(by_what=None, check_box=None):
        def handle_operation(e):
            operation = e.control.data
            if operation == 'add_rabbit':
                create_new_rabbit()

        left_button = get_operations_by_many_rabbits(handle_operation)
        set_bottom_app_bar(left_button)


        def handle_sort(e):
            select_sort = e.control.data
            show_rabbit_list(by_what=select_sort)
        sort_btn = get_sort_menu(show_rabbits_list=handle_sort)
        set_appbar(left_actions=BTN_SYNC, right_actions=sort_btn)
        bunnies = ft.Column()
        text = ft.Text('Список кролиць', size=22, weight=ft.FontWeight.BOLD)

        names = []
        name_for_sort = [y for y in meatberry.rabbits if len(y) > 2]

        if by_what == 'by_name':
            names = sorted(name_for_sort, key=lambda x: (x[:2], int(x[2:])))
        elif by_what == 'by_box':
            names = sorted(name_for_sort, key=lambda x: (meatberry.rabbits[x].block, meatberry.rabbits[x].box))
        elif by_what == 'by_age_up':
            names = sorted(name_for_sort, key=lambda x: meatberry.rabbits[x].age)
        elif by_what == 'by_age_down':
            names = sorted(name_for_sort, key=lambda x: meatberry.rabbits[x].age, reverse=True)
        elif by_what == 'by_rating_up':
            names = sorted(name_for_sort, key=lambda x: meatberry.rabbits[x].rating)
        elif by_what == 'by_rating_down':
            names = sorted(name_for_sort, key=lambda x: meatberry.rabbits[x].rating, reverse=True)
        else:
            names = name_for_sort

        for name in names:
            rabbit = meatberry.rabbits[name]
            if rabbit is not None:
                process = looking_for_work(rabbit)
                color = create_rabbit_card(process)
                item = ft.ListTile(leading=ft.Icon(ft.Icons.PETS), title=ft.Text(name),
                                   subtitle=ft.Text(f"Клітка: {meatberry.rabbits[name].str_block_box}"),
                                   bgcolor=color,
                                   trailing=ft.Row(controls=[ft.Text(STATUS_WORK.get(process, ''), size=14, weight=ft.FontWeight.BOLD),
                                                             ft.Checkbox(value=False, on_change=lambda e: print('Flag worked'))] if check_box else [ft.Text(STATUS_WORK.get(process, ''), size=14, weight=ft.FontWeight.BOLD)],
                                                tight=True),
                                   on_click=lambda e, b=meatberry.rabbits[name]: navigate_to(show_str, b))
                bunnies.controls.append(item)
            else:
                print(f'{rabbit} not founded.')
        main_content.content = bunnies
        main_content.update()

    def show_str(bunny: Bunny):
        def show_nest_info(rabbit):
            main_content.content = get_nest_info_container(rabbit)
            main_content.update()
        def handle_operation(e):
            operation = e.control.data

            if operation == 'set_culling':
                set_rabbit_culling(bunny)
                show_str(bunny)
                logger.info(f'{bunny.name} помічена як вибраковка')

            elif operation == 'swap_box':
                def handle_input(e):
                    change_box_for_rabbit(meatberry, block_input, box_input, result_field)
                    main_content.update()
                block_input, box_input, result_field = get_text_fields_for_swap_boxes(handle_input)
                def handle_save(e):
                    if change_box_for_rabbit(meatberry, block_input, box_input, result_field):
                        block, box = change_box_for_rabbit(meatberry, block_input, box_input, result_field)
                        rewrite_block_and_box(meatberry, bunny, block, box)
                        navigate_to(show_str,bunny)
                main_content.content = ft.Column(controls=[ft.Text(f'Картка: {bunny.name}', size=22, weight=ft.FontWeight.BOLD),
                                                           ft.Text(value=str(bunny), size=20),
                                                           ft.Divider(),
                                                           block_input, box_input, result_field,
                                                           ft.Button(content=ft.Text('Підтвердити'), on_click=handle_save)])
                main_content.update()
                logger.info(f'{bunny.name} --> {block_input}.{box_input}')

            elif operation == 'remove_by_death':
                remove_by_death(meatberry, bunny)
                show_rabbit_list()
                logger.info(f'{bunny.name} померла')

            elif operation == 'remove_by_culling':
                remove_by_culling(meatberry, bunny)
                show_rabbit_list()
                logger.info(f'{bunny.name} вибракована')

        right_button = get_operations_by_rabbit(handle_operation)
        set_bottom_app_bar()
        info = ft.Text(value=str(bunny), size=20)

        main_content.content = ft.Column([ft.Divider(), ft.Text(f'Картка: {bunny.name}', size=22, weight=ft.FontWeight.BOLD), info])
        set_appbar(right_actions=right_button)
        main_content.update()

        page.update()

    def show_defective(e=None):
        text = ft.Text(f'Вибраковані кролиці ({len(meatberry.defective)})', size=22, weight=ft.FontWeight.BOLD)
        culling = ft.Column([text])

        for num, name in enumerate(meatberry.defective, 1):
            item = ft.ListTile(leading=ft.Icon(ft.Icons.PETS),  title=ft.Text(name),  subtitle=ft.Text(f'{meatberry.rabbits[name].str_block_box if name in meatberry.rabbits else 'Вже померла'}'), on_click=lambda e:navigate_to(show_str, meatberry.rabbits[name]))
            culling.controls.append(item)

        set_bottom_app_bar()
        main_content.content = culling
        main_content.update()

    def create_new_rabbit():
        open_alert_dialog()

        cancel_btn = ft.Button('Скасувати додавання', on_click=close_alert_dialog)

        dialog.actions = [cancel_btn]

        def handle_date(e):
            if e.control.value:
                selected_date = e.control.value + timedelta(hours=3)
                dict_to_create_rabbit['birthday'] = selected_date.date().strftime(DATE_FORMAT)
                dialog.content = ft.Text(f"Дата народження кролиці - "
                                         f"{selected_date.strftime('%d.%m.%Y')}")
                dialog.actions = [ft.Button('Так', on_click=lambda _: show_steps_for_add_new_rabbit(2)),
                                  ft.Button('Ні', on_click=lambda _: show_steps_for_add_new_rabbit(1))]
                dialog.update()

        def handle_input(e):

            if change_box_for_rabbit(meatberry, block_field, box_field, result_point):
                block, box = change_box_for_rabbit(meatberry, block_field, box_field, result_point)
                if to_create_bunny_obj_btn not in dialog.actions:
                    dialog.actions.append(to_create_bunny_obj_btn)
            else:
                dialog.actions = [block_field, box_field, result_point, cancel_btn]
            dialog.update()

        def final_create_bunny():
            dict_to_create_rabbit['block'] = block_field.value
            dict_to_create_rabbit['box'] = box_field.value

            if create_and_add_new_bunny(meatberry, dict_to_create_rabbit['birthday'], dict_to_create_rabbit['name'],
                                     dict_to_create_rabbit['block'], dict_to_create_rabbit['box']):
                dialog.title = ft.Text('Кролицю додано')
                dialog.content = ft.Text(f'')
                dialog.actions = [ft.Button('OK', on_click=close_alert_dialog)]

                dialog.update()
                show_rabbit_list()
                logger.info(f'Кролиця {dict_to_create_rabbit['name']} додана в клітку {dict_to_create_rabbit['block']}.{dict_to_create_rabbit['box']}')

            else:
                dialog.title = ft.Text('Щось пішло не так')
                dialog.content = ft.Text('')
                dialog.actions = [ft.Button('Спробувати знову', on_click=lambda _: show_steps_for_add_new_rabbit(1))]

                dialog.update()

        date_picker = ft.DatePicker(on_change=handle_date)
        dict_to_create_rabbit = {}
        name_input = ft.TextField(label='Лінія', width=80, max_length=2, counter='')
        block_field, box_field, result_point = get_text_fields_for_swap_boxes(handle_input)
        to_create_bunny_obj_btn = ft.Button('Далі', on_click=final_create_bunny)

        def show_steps_for_add_new_rabbit(step):
            def open_picker():
                if date_picker not in page.overlay:
                    page.overlay.append(date_picker)
                date_picker.open = True
                page.update()

            if step == 1:
                dialog.actions = [cancel_btn]
                dialog.title = ft.Text('КРОК 1. Дата народження')
                dialog.content = ft.Column([ft.Text('Оберіть дату народження кролиці')], tight=True)
                dialog.actions.append(ft.Button('Відкрити календар', on_click=open_picker))

                dialog.update()

            elif step == 2:

                def handle_input(e):

                    if len(dialog.actions) > 2:
                        need_elements = [dialog.actions[0], dialog.actions[-1]]
                        dialog.actions = need_elements
                        dialog.content = None
                        dialog.update()

                    if e.control.value:
                        rabbit_line = e.control.value
                        if len(rabbit_line) == 2:
                            vacant_index = vacant_index_for_rabbit(meatberry, rabbit_line)
                            dialog.content = ft.Text(f"Кролиця {rabbit_line}{vacant_index}")
                            dialog.actions.remove(cancel_btn)
                            dialog.actions.extend([ft.Text(vacant_index, size=20),
                                                   ft.Button('Далі', on_click=lambda _: show_steps_for_add_new_rabbit(3)),
                                                   ft.Button('Назад', on_click=lambda _: show_steps_for_add_new_rabbit(2)),
                                                   cancel_btn])
                            dialog.update()

                if dict_to_create_rabbit.get('birthday'):
                    name_input.on_change = handle_input
                dialog.title = ft.Text('КРОК 2. Введіть імя')
                dialog.content = None
                dialog.actions = [name_input, cancel_btn]
                dialog.update()

            elif step == 3:
                dict_to_create_rabbit['name'] = name_input.value + str(vacant_index_for_rabbit(meatberry, name_input.value))
                print(dict_to_create_rabbit)

                dialog.title = 'КРОК 3. Розміщення кролиці'
                dialog.content = ft.Text('Введіть номера блоку та клітки')
                dialog.actions = [block_field, box_field, result_point, cancel_btn]
                dialog.update()

        show_steps_for_add_new_rabbit(1)

    # Стартова точка (функція)
    navigate_to(show_main_menu)
# Запуск додатка
ft.run(main=main, assets_dir='assets')


if __name__ == '__main__':
    pass