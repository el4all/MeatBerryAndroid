
import json
import  io
import os


import flet as ft
import requests

from datetime import datetime, timedelta, time, date

from flet import SnackBarBehavior
from loguru import logger
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from pathlib import Path

from bunny_classes import Farm, Bunny, Nest, Box, STATUS_WORK, STATUS_FOR_3_ROOM
from work_with_files import open_and_read_json, write_json
from puthon_logic_func import (looking_for_work, set_rabbit_culling, rewrite_block_and_box, remove_by_death, remove_by_culling,
                               vacant_index_for_rabbit, empty_boxes, create_and_add_new_bunny, search_process_date_for_rabbit,
                               cancel_culling, increase_quantity_in_third_room, decrease_quantity_in_third_room,
                               calculate_bunnies_in_block, calculate_age_and_quantity, add_box_in_third_room,
                               get_dates_for_processes, get_result_of_mates, get_info_of_one_mate,get_all_planning_for_process,
                               loose_nest,get_all_planning_for_today
                               )
from helper_functions import (create_rabbit_card, change_box_for_rabbit,open_alert_dialog,close_alert_dialog,open_picker,
                              quick_message,create_rabbit_tile, mass_kill_third_room,quantity_of_farm,average_age_of_farm,
                              farm_by_status,get_block)
from buttons_filters import (BTN_SYNC, get_sort_menu, get_operations_by_rabbit, get_nest_info_container,
                             get_text_fields_for_swap_boxes, BTN_CHANGE_THEME, get_info_by_rabbit,
                             get_operations_by_many_rabbits, get_main_container_for_trailing, get_operations_by_culling,
                             get_btn_for_operation_with_box, get_btns_for_box_str, get_btn_by_farm_info, get_btn_for_operation_in_third_room,
                             get_status_pop_menu, get_container_for_trailing_process,get_pop_menu_for_select_process,
                             get_trailing_for_rabbit_list,info_by_color)

URL = 'https://drive.google.com/uc?export=download&id=1459S6Uo3w-f5i5KnDhV5XG0RFCNBDLgW'
DATE_FORMAT = '%d.%m.%Y'
FILE_ID = '1459S6Uo3w-f5i5KnDhV5XG0RFCNBDLgW'
TEMP_FOR_CHECKBOX = 'temp_for_process_today.json'

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
    try:
        BASE_DIR = Path(__file__).resolve().parent
        KEY_PATH = str(BASE_DIR / 'meatberry_farm_for_gspread.json')

        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)
        creds.refresh(Request())
        access_token = creds.token

        json_string = json.dumps(meatberry.save_to_json(), ensure_ascii=False, indent=4)

        url = f'https://www.googleapis.com/upload/drive/v3/files/{FILE_ID}?uploadType=media'
        headers = {'Authorization': f'Bearer {access_token}', 'Content_Type': 'application/json'}

        response = requests.patch(url, headers=headers, data=json_string)

        if response.status_code == 200:
            logger.info('Синхронізовано')
            return True
        else:
            logger.error(f'Помилка {response.status_code} - {response.text}.')
            return False

    except Exception as e:
        print(e)
        return False

def save_value_for_checkboxes(process_key: str, completed_ids: list):
    data = {}
    if os.path.exists(TEMP_FOR_CHECKBOX):
        try:
            with open(TEMP_FOR_CHECKBOX, 'r',encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}
    data[process_key] = completed_ids
    with open(TEMP_FOR_CHECKBOX, 'w',encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_value_for_checkboxes(process_key: str):
    if not os.path.exists(TEMP_FOR_CHECKBOX):
        return []
    try:
        with open(TEMP_FOR_CHECKBOX, 'r', encoding='utf-8') as f:
            data = json.load(f).get(process_key,[])
            return data
    except Exception:
        return []


farm_dict = file_from_google()
file_name = 'ACTUALLY_FARM.json'
meatberry = Farm('MeatBerry')
meatberry.load_from_network(farm_dict)



def main(page: ft.Page):
    main_content = ft.Container(expand=True)

    page.title = "Моя Ферма"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO  # Дозволяє гортати екран, якщо список великий
    dialog = ft.AlertDialog(title='eeee', modal=True)
    date_picker = ft.DatePicker()

    page.overlay.append(dialog)
    stack_views = []
    navigation = []
    current_scroll = getattr(page, 'rabbits_scroll_offset',0)

    def synchronization():
        if file_upload_google():
            quick_message('Синхронізовано успішно', False, page)
        else:
            quick_message('Не вдалося синхронізувати', True, page)

    BTN_SYNC.on_click = synchronization
    switch_mode_to_visual = ft.Row([ft.Container(ft.Icon(ft.Icons.GRID_VIEW),on_click=lambda e: show_blocks()),
                                    ft.Text('     ')])
    pop_for_visual = info_by_color()
    switch_mode_to_list = ft.Row([ft.Container(ft.Icon(ft.Icons.LIST), on_click=lambda e: show_list_of_blocks()),
                                  pop_for_visual])


    def navigate_to(func, *args):
        navigation.append((func, args))
        func(*args)

    def save_scroll_position(e: ft.OnScrollEvent):
        print(current_scroll)
        setattr(page,'rabbits_scroll_offset', e.pixels)
        print(getattr(page,'rabbits_scroll_offset'))
        print(e)

    def go_back():
        if len(navigation) > 1:
            navigation.pop()
            previous_func, args = navigation[-1]
            previous_func(*args)
        else:
            page.run_task(page.window.close)

    def returning_e_data(e):
        return e.control.data

    def change_theme():
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()

    BTN_CHANGE_THEME.on_click = change_theme

    def set_bottom_app_bar(left_button=None):
        page.bottom_appbar = ft.BottomAppBar(content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                            controls=[left_button if left_button else ft.Container(),
                                                            ft.Button('<-- Назад', on_click=lambda e: go_back())]))
        page.update()

    def set_appbar(title=None, left_actions=None, right_actions=None):
        page.appbar = ft.AppBar(toolbar_height=40, title=title,center_title=True, leading=left_actions if left_actions else ft.Container(),
                                               actions=right_actions if right_actions else ft.Container())

        page.update()

    def show_main_menu():
        main_content.content = ft.Column([ft.Text('Головне меню ферми', size=16, weight=ft.FontWeight.W_500),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.PETS), title=ft.Text('Кролиці'),
                                                      on_click=lambda e: navigate_to(alternate_show_rabbit_list, 'for_main')),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.GRID_VIEW), title=ft.Text('Блоки'),
                                                      on_click=lambda e: navigate_to(show_list_of_blocks)),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.MENU_BOOK), title=ft.Text('Відгодівля'),
                                                      on_click=lambda e: navigate_to(show_third_room_block_list)),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.DELETE_FOREVER), title=ft.Text('Вибраківка'),
                                                      on_click=lambda e: navigate_to(show_defective)),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.ADS_CLICK), title=ft.Text('Процеси'),
                                                      on_click=lambda e: navigate_to(show_processes)),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.INFO), title=ft.Text('Інформація'),
                                                      on_click=lambda e: navigate_to(show_info_on_farm))
                                          ])
        set_appbar(left_actions=BTN_CHANGE_THEME, right_actions=BTN_SYNC)
        btn_info = get_btn_by_farm_info(meatberry, main_content, navigate_to)
        set_bottom_app_bar(left_button=btn_info)
        main_content.update()

    page.appbar = ft.AppBar(title=ft.Text('MeatBerryFarm'),
                            actions=[BTN_SYNC])

    page.bottom_appbar = ft.BottomAppBar(padding=10,
                              content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                             controls=[ft.Button('<-- Назад', on_click= lambda  e: show_main_menu()), ft.Text('v1.0')]))

    page.add(main_content)
    page.update()

    def show_processes():
        def processing_pop_menu(e):
            mode = e.control.data
            match mode:
                case 'for_mate':
                    navigate_to(alternate_show_rabbit_list, mode)

        main_content.content = ft.Column([ft.Text('Процеси ферми', size=16, weight=ft.FontWeight.W_500),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.DONE_ALL), title=ft.Text('Проведені процеси'),
                                                      on_click=lambda e: navigate_to(show_past_processes)),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.ALARM),
                                                      title=ft.Text('Сьогоднішні процеси'),
                                                      on_click=lambda e: navigate_to(show_today_processes)),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.APP_REGISTRATION), title=ft.Text('Заплановані процеси'),
                                                      on_click=lambda e: navigate_to(show_future_processes))
                                          ])

        pop_menu_for_select_process = get_pop_menu_for_select_process(processing_pop_menu)
        set_appbar(title='Процеси ферми',right_actions=pop_menu_for_select_process)

        btn_info = get_btn_by_farm_info(meatberry, main_content, navigate_to)
        set_bottom_app_bar(left_button=btn_info)
        main_content.update()

    def dates_of_mates():

        dates = get_dates_for_processes(meatberry, 'mate')
        mates = ft.Column()

        for d in dates:

            results = get_result_of_mates(meatberry, d)
            trail = get_container_for_trailing_process(results)
            item = ft.ListTile(leading=ft.Icon(ft.Icons.CALENDAR_TODAY), data=d.strftime(DATE_FORMAT),title=ft.Text(d.strftime(DATE_FORMAT)),
                               trailing=trail, on_click=lambda e: navigate_to(show_info_about_mate, e))

            mates.controls.append(item)

        main_content.content = mates
        set_bottom_app_bar()
        page.update()

    def show_info_about_mate(e):
        date_ = datetime.strptime(e.control.data, DATE_FORMAT).date()
        info = get_info_of_one_mate(meatberry, date_)

        mates = ft.Column([ft.Text(e.control.data)])
        for el in info:
            name = el[0]
            obj = meatberry.rabbits[name]
            father = el[1]
            res = el[2]
            color = 'blue'
            if res == 'positive':
                res = '+'
                color = 'green'
            elif res == 'negative':
                res = '-'
                color = 'red'

            item = ft.Container(bgcolor=color, content=ft.Row(controls=[ft.Icon(ft.Icons.FEMALE), ft.Text(name),
                                                                       ft.Icon(ft.Icons.MALE), ft.Text(father),
                                                                       ft.Icon(ft.Icons.ARROW_FORWARD), ft.Text(res)]
                                                              ),
                                on_click=lambda e, x=obj: navigate_to(show_str_rabbit, x))
            mates.controls.append(item)

        main_content.content = mates
        main_content.update()

    def dates_of_kindling():
        dates = get_dates_for_processes(meatberry, 'kindling')
        mates = ft.Column()

        for d in dates:
            results = get_result_of_mates(meatberry, d)
            #trail = get_container_for_trailing_process(results)
            item = ft.ListTile(leading=ft.Icon(ft.Icons.CALENDAR_TODAY), data=d.strftime(DATE_FORMAT),
                               title=ft.Text(d.strftime(DATE_FORMAT)),
                                on_click=lambda e: navigate_to(show_info_about_mate, e))

            mates.controls.append(item)

        main_content.content = mates
        set_bottom_app_bar()
        page.update()

    def show_future_processes():
        icons = dict([('mate',ft.Icon(ft.Icons.NO_ADULT_CONTENT)),('palpation',ft.Icon(ft.Icons.SEARCH)),
                      ('kindling',ft.Icon(ft.Icons.CRUELTY_FREE)),('install nest',ft.Icon(ft.Icons.ADD_BOX)),
                    ('open nest',ft.Icon(ft.Icons.OUTPUT)),('remove nest',ft.Icon(ft.Icons.DISABLED_BY_DEFAULT)),
                      ('resettle',ft.Icon(ft.Icons.ARROW_RIGHT)),('vaccination nest',ft.Icon(ft.Icons.VACCINES_SHARP)),
                      ('prepare nest',ft.Icon(ft.Icons.SELECT_ALL)),('swap box',ft.Icon(ft.Icons.AUTORENEW))])
        processes = ft.Column([ft.Text('Заплановані процеси ферми')])

        for eng, ua in STATUS_WORK.items():
            item = ft.ListTile(leading=ft.Row([icons.get(eng, None),ft.Text(ua.capitalize())]),
                               on_click=lambda e, process=eng: navigate_to(show_need_process, process))
            processes.controls.append(item)

        main_content.content = processes
        main_content.update()

    def show_past_processes():
        main_content.content = ft.Column([ft.Text('Проведені процеси ферми', size=16, weight=ft.FontWeight.W_500),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.NO_ADULT_CONTENT), title=ft.Text('Запліднення'),
                                                      on_click=lambda e: navigate_to(dates_of_mates)),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.CRUELTY_FREE), title=ft.Text('Окроли'),
                                                      on_click=lambda e: navigate_to(dates_of_kindling)),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.VACCINES), title=ft.Text('Вакцинації'))
                                          ])
        set_appbar(right_actions=BTN_SYNC)
        btn_info = get_btn_by_farm_info(meatberry, main_content, navigate_to)
        set_bottom_app_bar(left_button=btn_info)
        main_content.update()

    def show_today_processes():
        process_key = 'show_today_process'
        values_for_checkboxes = set(get_value_for_checkboxes(process_key))

        def handle_check(e: ft.Event[ft.Checkbox]):
            id_of_list_tile = e.control.data
            checked = e.control.value

            if checked:
                values_for_checkboxes.add(id_of_list_tile)
            else:
                values_for_checkboxes.discard(id_of_list_tile)
            save_value_for_checkboxes(process_key, list(values_for_checkboxes))

        set_appbar(title='Операції на сьогодні')
        set_bottom_app_bar()
        data = get_all_planning_for_today(meatberry)

        today_process = ft.Column()

        if data:
            for process, list_of_names in data.items():
                item = ft.ExpansionTile(STATUS_WORK[process].capitalize(),
                                        controls=[ft.ListTile(ft.Row([ft.Text(el, size=20),ft.Text(meatberry.rabbits[el].str_block_box)]),
                                                              trailing=ft.Checkbox(value=el in values_for_checkboxes,
                                                                                       data=el, on_change=lambda e: handle_check(e)),
                                                              on_click=lambda e, obj=meatberry.rabbits[el]: navigate_to(show_str_rabbit, obj))
                                                  for el in list_of_names])
                today_process.controls.append(item)

        main_content.content = today_process
        main_content.update()

    def show_need_process(process):

        data = get_all_planning_for_process(meatberry, process)
        need_el = ft.Column()
        today = date.today()

        for x, names in reversed(sorted(data.items())):
            if x > today:
                item = ft.PopupMenuButton(content=ft.Row([ft.Text(x.strftime(DATE_FORMAT), size=14, weight=ft.FontWeight.BOLD),
                                                           ft.Icon(ft.Icons.ARROW_DROP_DOWN), ft.Text(f'{len(names)}')], tight=True),
                                          items=[ft.PopupMenuItem(content=ft.Text(name), data=name,
                                                                   on_click=lambda e, obj=meatberry.rabbits[name]: navigate_to(show_str_rabbit, obj)) for name in names])
                need_el.controls.append(item)

        main_content.content = need_el
        main_content.update()

    def show_rabbit_list(by_what=None):

        def handle_operation(e):
            operation = e.control.data
            if operation == 'add_rabbit':
                create_new_rabbit()
        if dialog and dialog.open:
            close_alert_dialog(page, dialog)
        left_button = get_operations_by_many_rabbits(handle_operation)
        set_bottom_app_bar(left_button)


        def handle_sort(e):
            select_sort = e.control.data
            show_rabbit_list(by_what=select_sort)

        sort_btn = get_sort_menu(func_for_sort=handle_sort)
        set_appbar(left_actions=BTN_SYNC, right_actions=sort_btn)
        bunnies = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, on_scroll=save_scroll_position)
        if current_scroll > 0:
            bunnies.scroll_to(offset=current_scroll, duration=0)
        text = ft.Text('Список кролиць', size=22, weight=ft.FontWeight.BOLD)

        names = []
        name_for_sort = [y for y in meatberry.rabbits if len(y) > 2]

        if by_what == 'by_name':
            names = sorted(name_for_sort, key=lambda x: (x[:2], int(x[2:])))
        elif by_what == 'by_time_add':
            names = name_for_sort
        elif by_what == 'by_age_up':
            names = sorted(name_for_sort, key=lambda x: meatberry.rabbits[x].age)
        elif by_what == 'by_age_down':
            names = sorted(name_for_sort, key=lambda x: meatberry.rabbits[x].age, reverse=True)
        elif by_what == 'by_rating_up':
            names = sorted(name_for_sort, key=lambda x: meatberry.rabbits[x].rating)
        elif by_what == 'by_rating_down':
            names = sorted(name_for_sort, key=lambda x: meatberry.rabbits[x].rating, reverse=True)
        else:
            names = sorted(name_for_sort, key=lambda x: (meatberry.rabbits[x].block, meatberry.rabbits[x].box))

        for name in names:
            rabbit = meatberry.rabbits[name]
            if rabbit is not None:

                pairs_work_color = search_process_date_for_rabbit(rabbit)
                main_container = get_main_container_for_trailing(pairs_work_color)

                process = looking_for_work(rabbit)
                color = create_rabbit_card(process)
                item = ft.ListTile(leading=ft.Icon(ft.Icons.PETS), title=ft.Text(name),
                                   subtitle=ft.Text(f"Клітка: {meatberry.rabbits[name].str_block_box}"),
                                   bgcolor=color,
                                   trailing=main_container,
                                   content_padding=ft.Padding.symmetric(horizontal=16, vertical=9),
                                   on_click=lambda e, b=meatberry.rabbits[name]: navigate_to(show_str_rabbit, b))
                bunnies.controls.append(item)
            else:
                print(f'{rabbit} not founded.')
        main_content.content = bunnies
        main_content.update()

    def alternate_show_rabbit_list(mode: str, block=None, rabbit_list=None):

        if not rabbit_list:
            rabbit_list = sorted(meatberry.rabbits.values(), key=lambda obj: ((obj.block, obj.box), False))

        def processing_pop_menu(e):
            operation = e.control.data
            match operation:
                case 'add_rabbit':
                    create_new_rabbit()

        def func_for_sort_list(e):
            sort_by, is_reverse = e.control.data
            if sort_by is None:
                sorted_rabbits = list(meatberry.rabbits.values())
            else:
                sorted_rabbits = sorted([x for x in meatberry.rabbits.values() if len(x.name) > 2], key=sort_by, reverse=is_reverse)
            alternate_show_rabbit_list(mode, block, sorted_rabbits)

        sort_btn = get_sort_menu(func_for_sort_list)
        operation_button = get_operations_by_many_rabbits(processing_pop_menu)
        set_appbar(title='Список кролиць', right_actions=ft.Row([operation_button, sort_btn]))
        set_bottom_app_bar()


        rabbits = ft.Column()
        for obj in rabbit_list:
            if block:
                if len(obj.name) > 2 and obj.block == block:
                    item = create_rabbit_tile(obj)
                    item.trailing = get_trailing_for_rabbit_list(mode, obj)
                    item.on_click = lambda e, r=obj: navigate_to(show_str_rabbit,r)
                    rabbits.controls.append(item)
            else:
                if len(obj.name) > 2:
                    item = create_rabbit_tile(obj)
                    item.trailing = get_trailing_for_rabbit_list(mode, obj)
                    item.on_click = lambda e, r=obj: navigate_to(show_str_rabbit,r)
                    rabbits.controls.append(item)

        main_content.content = rabbits
        main_content.update()

    def add_new_box_in_third_room():

        def handle_input():
            block_field.error = None
            box_field.error = None
            is_error = False

            if not block_field.value or not block_field.value.strip().isdigit():
                block_field.error = 'Введіть число'
                is_error = True
                block_field.update()

            if not box_field.value or not box_field.value.strip().isdigit():
                box_field.error = 'Введіть число'
                is_error = True
                box_field.update()

            if not is_error:
                yes_btn.disabled = False
                yes_btn.on_click = set_status_and_quantity_bunnies
            else:
                yes_btn.disabled = True

            dialog.update()

        def handle_quantity(pop_menu):
            pop_menu_text = pop_menu.content.content.controls[0].value
            quantity_field.error = None
            is_error = False

            if not quantity_field.value or not quantity_field.value.strip().isdigit():
                quantity_field.error = 'Введіть число'
                is_error = True
                quantity_field.update()

            if not is_error and pop_menu_text != 'Статус':
                yes_btn.disabled = False
                yes_btn.on_click = finally_create_box
            else:
                yes_btn.disabled = True

            print(is_error, pop_menu_text)
            dialog.update()

        def handle_choice(e):
            status_choise.content.content.controls[0].value = STATUS_FOR_3_ROOM[e.control.data]
            dialog.update()

        dict_to_create_box = {}
        cancel_btn = ft.Button('Скасувати додавання', on_click=lambda e: close_alert_dialog(page,dialog))
        block_field = ft.TextField(label='Блок', keyboard_type=ft.KeyboardType.NUMBER, on_change=handle_input, width=120)
        box_field = ft.TextField(label='Клітка', keyboard_type=ft.KeyboardType.NUMBER, on_change=handle_input, width=120)
        status_choise = get_status_pop_menu(handle_choice)
        quantity_field = ft.TextField(label='Кількість', keyboard_type=ft.KeyboardType.NUMBER,
                                      on_change=lambda e: handle_quantity(status_choise),
                                      max_length=3, width=100)
        yes_btn = ft.Button('Далі')
        no_btn = ft.Button('Назад')
        cancel_and_next_btns = ft.Row([cancel_btn, yes_btn])

        def add_date_birth_group():
            date_picker.on_change = contribution_date_birth
            open_calendar_btn = ft.Button('Відкрити календар', on_click=lambda e: open_picker(page,date_picker))
            open_alert_dialog(page,dialog)
            dialog.title = 'КРОК 1. Дата народження групи'
            dialog.content = ft.Column([ft.Text('Оберіть дату народження групи')], tight=True)
            dialog.actions = [cancel_btn, open_calendar_btn]
            dialog.update()

        def contribution_date_birth():
            yes_btn.on_click = set_address_group
            no_btn.on_click = add_date_birth_group

            if date_picker.value:
                birth = date_picker.value + timedelta(hours=3)
                dialog.title = 'КРОК 1. Дата народження групи'
                dialog.content = ft.Column([ft.Text(f'Народження групи {birth.strftime(DATE_FORMAT)}')], tight=True)
                dialog.actions = [no_btn, yes_btn]
                dialog.update()

        def set_address_group():
            date_birth = date_picker.value + timedelta(hours=3)
            dict_to_create_box['birth'] = date_birth.date()

            dialog.title = 'КРОК 2. Розміщення групи'
            dialog.content = ft.Column([ft.Text('Оберіть блок та клітку')], tight=True)
            yes_btn.disabled = True
            dialog.actions = [ft.Row([block_field, box_field]), cancel_and_next_btns]
            dialog.update()

        def set_status_and_quantity_bunnies():
            dict_to_create_box['block'] = int(block_field.value)
            dict_to_create_box['box'] = int(box_field.value)

            dialog.title = 'КРОК 3. Статус і кількість'
            dialog.content = ft.Column([ft.Text('Оберіть блок та клітку')], tight=True)
            yes_btn.disabled = True
            dialog.actions = [ft.Row([ status_choise,quantity_field]), cancel_and_next_btns]
            dialog.update()

        def finally_create_box():
            dict_to_create_box['quantity'] = int(quantity_field.value)
            dict_to_create_box['status'] = status_choise.content.content.controls[0].value

            try:
                add_box_in_third_room(meatberry, dict_to_create_box)
                close_alert_dialog(page,dialog)
                show_third_room_block_list()
                quick_message('Клітка додана', False,page)
            except Exception as e:
                close_alert_dialog(page,dialog)
                quick_message('Помилка додавання', True,page)
                show_third_room_block_list()


        add_date_birth_group()

    def show_third_room_block_list():

        def handle_choice(e):
            res = e.control.data
            match res:
                case 'add_box':
                    add_new_box_in_third_room()
                case 'mass_kill':
                    block = returning_e_data(e)
                    mass_kill_third_room(page, meatberry,block)

        set_appbar(title=ft.Text('Блоки'), right_actions=BTN_SYNC)
        left_btn = get_btn_for_operation_in_third_room(handle_choice)
        set_bottom_app_bar(left_button=left_btn)

        all_blocks = ft.Column([ft.Text('Відгодівля', size=16, weight=ft.FontWeight.W_500)])
        used_blocks = sorted([x for x in set(x.block for x in meatberry.third_room.values())])


        for el in used_blocks:
            quantity_bunnies = calculate_bunnies_in_block(meatberry, el)
            column_for_trailing = ft.Column(tight=True)
            data_for_block = calculate_age_and_quantity(meatberry, el)
            for d, q in data_for_block.items():
                item = ft.Text(f'{d} дн. -- {sum(q)} шт.')
                column_for_trailing.controls.append(item)
            item = ft.ListTile(leading=ft.Icon(ft.Icons.HOUSE), title=ft.Text(f'Блок {el}'),
                               trailing=column_for_trailing,
                               on_click=lambda e, block=el: navigate_to(show_third_room_boxes_in_block, block))
            all_blocks.controls.append(item)
            main_content.content = all_blocks
            main_content.update()

    def show_third_room_boxes_in_block(block: int):
        set_appbar(title=ft.Text('Клітки'))
        boxes = ft.Column()
        for box_obj in meatberry.third_room.values():
            if box_obj.block == block:
                item = ft.ListTile(leading=ft.Icon(ft.Icons.GRID_VIEW), title=ft.Text(f'{block}.{box_obj.box}'),
                                   subtitle=ft.Text(box_obj.birth.strftime(DATE_FORMAT)), trailing=ft.Text(f'{box_obj.box_age} дн.'),
                                   on_click=lambda e, box=box_obj: navigate_to(show_str_box, box))
                boxes.controls.append(item)

        main_content.content = boxes
        main_content.update()

    def show_str_rabbit(bunny: Bunny):

        def show_nest_info(rabbit):
            main_content.content = get_nest_info_container(rabbit)
            main_content.update()

        def handle_operation(e):
            operation = e.control.data

            if operation == 'set_culling':
                if set_rabbit_culling(meatberry, bunny):
                    report = f'{bunny.name} помічена як вибраковка'
                    quick_message(report, False,page)
                    show_str_rabbit(bunny)
                else:
                    report = f'{bunny.name} вже в списку вибраківки'
                    quick_message(report, True,page)
                    show_str_rabbit(bunny)
                logger.info(report)

            elif operation == 'swap_box':
                def handle_input(e):
                    change_box_for_rabbit(meatberry, block_input, box_input, result_field)
                    main_content.update()
                block_input, box_input, result_field = get_text_fields_for_swap_boxes(handle_input)
                def handle_save(e):
                    if change_box_for_rabbit(meatberry, block_input, box_input, result_field):
                        block, box = change_box_for_rabbit(meatberry, block_input, box_input, result_field)
                        old_address = bunny.str_block_box
                        rewrite_block_and_box(meatberry, bunny, block, box)
                        navigate_to(show_str_rabbit,bunny)
                        report = (f'{bunny.name} --> {block_input.value}.{box_input.value}  '
                                  f' {old_address} <-- {result_field.value.split()[-1]}')
                        quick_message(report, False,page)
                        logger.info(report)
                main_content.content = ft.Column(controls=[ft.Text(f'Картка: {bunny.name}', size=22, weight=ft.FontWeight.BOLD),
                                                           ft.Text(value=str(bunny), size=20),
                                                           ft.Divider(),
                                                           block_input, box_input, result_field,
                                                           ft.Button(content=ft.Text('Підтвердити'), on_click=handle_save)])
                main_content.update()

            elif operation == 'remove_by_death':
                remove_by_death(meatberry, bunny)
                report = f'Кролиця {bunny.name} видалена'
                quick_message(report, False,page)
                logger.info(f'{bunny.name} померла')
                show_blocks()

            elif operation == 'remove_by_culling':
                remove_by_culling(meatberry, bunny)
                report = f'Кролиця {bunny.name} видалена'
                quick_message(report, False,page)
                logger.info(f'{bunny.name} вибракована')
                navigation[-2][0](navigation[-2][1])

            elif operation == 'cancel_culling':
                cancel_culling(meatberry, bunny)
                report = f'Вибраківка {bunny.name} скасована'
                quick_message(report, False,page)
                logger.info(report)
                navigation[-2][0](navigation[-2][1])

            elif operation == 'loose_nest':
                loose_nest(bunny)
                logger.info(f'{bunny.name} loose nest.')
                show_str_rabbit(bunny)

        btn_info = get_info_by_rabbit(handle_operation)
        right_button = get_operations_by_culling(handle_operation) if navigation[-2][0] == show_defective else get_operations_by_rabbit(handle_operation)
        set_bottom_app_bar()
        info = ft.Text(value=str(bunny), size=20)

        main_content.content = ft.Column([ft.Divider(), ft.Text(f'Картка: {bunny.name}', size=22, weight=ft.FontWeight.BOLD), info])
        set_appbar(left_actions=btn_info, right_actions=right_button)
        main_content.update()

        page.update()

    def show_str_box(box: Box):

        def handle_operation(e):
            if e.control.data == 'change_quantity':
                quantity_field, plus_btn, minus_btn = get_btns_for_box_str()
                plus_btn.on_click = lambda e: (increase_quantity_in_third_room(box, quantity_field), show_str_box(box))
                minus_btn.on_click = lambda e: (decrease_quantity_in_third_room(box, quantity_field), show_str_box(box))
                main_content.content = ft.Column([ft.Divider(),
                                                  ft.Text(f'Картка: {box.block}.{box.box}', size=22, weight=ft.FontWeight.BOLD),
                                                  info, quantity_field, plus_btn, minus_btn])
                main_content.update()


        btn_op = get_btn_for_operation_with_box(handle_operation)
        set_appbar( right_actions=btn_op)
        info = ft.Text(value=str(box), size=20)

        main_content.content = ft.Column([ft.Divider(), ft.Text(f'Картка: {box.block}.{box.box}', size=22, weight=ft.FontWeight.BOLD), info])

        main_content.update()

    def show_defective(e=None):
        text = ft.Text(f'Вибраковані кролиці ({len(set(meatberry.defective))})', size=22, weight=ft.FontWeight.BOLD)
        culling = ft.Column([text])

        for num, name in enumerate(sorted([x for x in set(meatberry.defective)], key=lambda x: (meatberry.rabbits[x].block,meatberry.rabbits[x].box)), 1):
            obj_rabbit = meatberry.rabbits.get(name)
            subtitle_text = ft.Text(f'{meatberry.rabbits[name].str_block_box} . Вік {meatberry.rabbits[name].age_in_month}')
            item = ft.ListTile(leading=ft.Icon(ft.Icons.PETS),  title=ft.Text(name),  subtitle=subtitle_text,
                               on_click=lambda e, r=obj_rabbit: navigate_to(show_str_rabbit, r))
            culling.controls.append(item)

        set_appbar()
        set_bottom_app_bar()
        main_content.content = culling
        main_content.update()

    def create_new_rabbit():

        open_alert_dialog(page,dialog)

        cancel_btn = ft.Button('Скасувати додавання', on_click=lambda e:close_alert_dialog(page,dialog))

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
            dict_to_create_rabbit['block'] = int(block_field.value)
            dict_to_create_rabbit['box'] = int(box_field.value)
            obj = create_and_add_new_bunny(meatberry, dict_to_create_rabbit['birthday'], dict_to_create_rabbit['name'],
                                     dict_to_create_rabbit['block'], dict_to_create_rabbit['box'])

            if obj:
                dialog.title = ft.Text('Кролицю додано')
                dialog.content = ft.Text(f'')
                dialog.actions = [ft.Button('OK', on_click=lambda e:close_alert_dialog(page,dialog))]

                dialog.update()
                show_rabbit_list()
                logger.info(f'Кролиця {dict_to_create_rabbit['name']} ({dict_to_create_rabbit['birthday']}) додана в клітку {dict_to_create_rabbit['block']}.{dict_to_create_rabbit['box']}')

            else:
                dialog.title = ft.Text('Щось пішло не так')
                dialog.content = ft.Text('')
                dialog.actions = [ft.Button('Спробувати знову', on_click=lambda _: show_steps_for_add_new_rabbit(1))]

                dialog.update()

        picker = ft.DatePicker(on_change=handle_date)
        dict_to_create_rabbit = {}
        name_input = ft.TextField(label='Лінія', width=80, max_length=2, counter='')
        block_field, box_field, result_point = get_text_fields_for_swap_boxes(handle_input)
        to_create_bunny_obj_btn = ft.Button('Далі', on_click=final_create_bunny)

        def show_steps_for_add_new_rabbit(step):

            if step == 1:
                dialog.actions = [cancel_btn]
                dialog.title = ft.Text('КРОК 1. Дата народження')
                dialog.content = ft.Column([ft.Text('Оберіть дату народження кролиці')], tight=True)
                dialog.actions.append(ft.Button('Відкрити календар', on_click=lambda e: open_picker(page,picker)))

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

    def show_blocks():
        all_farm = ft.GridView(runs_count=2, spacing=10,
                                   run_spacing=50)
        blocks = [2,1,4,3,6,5,8,7,10,9,12,11]

        for num in blocks:
            first,second,third = get_block(meatberry, num)
            item = ft.Container(content=ft.Row([first,second,third],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                bgcolor=ft.Colors.GREY, padding=10)
            all_farm.controls.append(item)

        main_content.content = all_farm
        set_appbar(title="Оберіть блок", right_actions=switch_mode_to_list)
        set_bottom_app_bar()

    # def show_blocks():
    #     all_farm = ft.GridView(runs_count=2, spacing=10,
    #                            run_spacing=50,)
    #     blocks = sorted([x for x in set([y.block for y in meatberry.rabbits.values()])])
    #     for b in blocks:
    #         item = ft.Container(content=ft.Text(b,  size=20,
    #                                             color=ft.Colors.SURFACE),
    #                             width=50, height=50, border_radius=15,
    #                             bgcolor=ft.Colors.GREY_500 if page.theme_mode==ft.ThemeMode.LIGHT else ft.Colors.WHITE,
    #                             alignment=ft.Alignment.CENTER,
    #                             on_click=lambda _, block=b: navigate_to(alternate_show_rabbit_list, 'for_main', block))
    #         all_farm.controls.append(item)
    #
    #     main_content.content = all_farm
    #     set_appbar(title="Оберіть блок", right_actions=switch_mode_to_list)
    #     set_bottom_app_bar()

    def show_list_of_blocks():

        set_appbar(title='Блоки ферми', right_actions=switch_mode_to_visual)
        set_bottom_app_bar()
        blocks = sorted([x for x in set([x.block for x in meatberry.rabbits.values()])])
        all_blocks = ft.Column()

        for b in blocks:
            item = ft.ExpansionTile(f'Блок {b}',
                                     controls=[ft.ListTile(leading=ft.Row(controls=[ft.Icon(ft.Icons.PETS,
                                                                                            color=ft.Colors.RED_500 if x.status == 'culling' else ft.Colors.GREEN_500),
                                                                                    ft.Text(x.name, size=18),ft.Text(x.str_block_box, size=14)],
                                                                          alignment=ft.MainAxisAlignment.START,tight=True),
                                                           on_click=lambda e, obj=x: navigate_to(show_str_rabbit, obj))
                                               for x in sorted(meatberry.rabbits.values(), key=lambda x: int(x.box)) if x.block == b])
            all_blocks.controls.append(item)

        main_content.content = all_blocks
        main_content.update()

    def show_info_on_farm():
        set_appbar(title="Статистична інформація")
        set_bottom_app_bar()


        avg_age = average_age_of_farm(meatberry)
        quantity_farm = quantity_of_farm(meatberry)
        status_farm = farm_by_status(meatberry)

        info = ft.Column([avg_age, quantity_farm, status_farm])

        main_content.content = info
        main_content.update()

    # Стартова точка (функція)
    navigate_to(show_main_menu)
# Запуск додатка
ft.run(main=main, assets_dir='assets')


if __name__ == '__main__':
    pass