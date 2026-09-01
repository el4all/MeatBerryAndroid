import json
import  io
import os


import flet as ft
import requests

from datetime import datetime, timedelta, time

from flet import SnackBarBehavior
from loguru import logger
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from pathlib import Path

from bunny_classes import Farm, Bunny, Nest, Box, STATUS_WORK
from work_with_files import open_and_read_json, write_json
from puthon_logic_func import (looking_for_work, set_rabbit_culling, rewrite_block_and_box, remove_by_death, remove_by_culling,
                               vacant_index_for_rabbit, empty_boxes, create_and_add_new_bunny, search_process_date_for_rabbit,
                               cancel_culling, increase_quantity_in_third_room, decrease_quantity_in_third_room,
                               calculate_bunnies_in_block, calculate_age_and_quantity)
from helper_functions import create_rabbit_card, change_box_for_rabbit
from buttons_filters import (BTN_SYNC, get_sort_menu, get_operations_by_rabbit, get_nest_info_container,
                             get_text_fields_for_swap_boxes,
                             get_operations_by_many_rabbits, get_main_container_for_trailing, get_operations_by_culling,
                             get_btn_for_operation_with_box, get_btns_for_box_str, get_btn_by_farm_info, get_btn_for_operation_in_third_room)

URL = 'https://drive.google.com/uc?export=download&id=1459S6Uo3w-f5i5KnDhV5XG0RFCNBDLgW'
DATE_FORMAT = '%d.%m.%Y'
FILE_ID = '1459S6Uo3w-f5i5KnDhV5XG0RFCNBDLgW'

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

farm_dict = file_from_google()
file_name = 'ACTUALLY_FARM.json'
meatberry = Farm('MeatBerry')
meatberry.load_from_network(farm_dict)


def main(page: ft.Page):
    main_content = ft.Container(expand=True)

    page.title = "Моя Ферма"
    page.bgcolor = '#FFFFFF'
    page.scroll = ft.ScrollMode.AUTO  # Дозволяє гортати екран, якщо список великий
    dialog = ft.AlertDialog(title='eeee', modal=True)

    page.overlay.append(dialog)

    navigation = []
    current_scroll = getattr(page, 'rabbits_scroll_offset',0)

    def open_alert_dialog():
        dialog.open = True
        page.update()

    def close_alert_dialog():
        dialog.open = False
        page.update()

    def quick_message(message: str, is_error: bool):
        snack = ft.SnackBar(content=ft.Text(message), duration=3000, behavior=SnackBarBehavior.FLOATING,
                            bgcolor=ft.Colors.RED_100 if is_error else ft.Colors.BLUE_GREY_700, open=True)
        page.overlay.clear()
        page.overlay.append(snack)
        page.update()

    def synchronization():
        if file_upload_google():
            quick_message('Синхронізовано успішно', False)
        else:
            quick_message('Не вдалося синхронізувати', True)

    BTN_SYNC.on_click = synchronization

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
                                          ft.ListTile(leading=ft.Icon(ft.Icons.PETS), title=ft.Text('Третя кімната'), on_click=lambda e: navigate_to(show_third_room_block_list)),
                                          ft.ListTile(leading=ft.Icon(ft.Icons.NIGHTLIFE), title=ft.Text('Вибраківка'), on_click= lambda e: navigate_to(show_defective))
                                          ])
        set_appbar(right_actions=BTN_SYNC)
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

    def show_rabbit_list(by_what=None, check_box=None):

        def handle_operation(e):
            operation = e.control.data
            if operation == 'add_rabbit':
                create_new_rabbit()
        if dialog and dialog.open:
            close_alert_dialog()
        left_button = get_operations_by_many_rabbits(handle_operation)
        set_bottom_app_bar(left_button)


        def handle_sort(e):
            select_sort = e.control.data
            show_rabbit_list(by_what=select_sort)
        sort_btn = get_sort_menu(show_rabbits_list=handle_sort)
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

    def show_third_room_block_list():
        set_appbar()
        left_btn = get_btn_for_operation_in_third_room()
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
                set_rabbit_culling(meatberry, bunny)
                report = f'{bunny.name} помічена як вибраковка'
                quick_message(report, False)
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
                        quick_message(report, False)
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
                quick_message(report, False)
                logger.info(f'{bunny.name} померла')
                show_rabbit_list()

            elif operation == 'remove_by_culling':
                remove_by_culling(meatberry, bunny)
                report = f'Кролиця {bunny.name} видалена'
                quick_message(report, False)
                logger.info(f'{bunny.name} вибракована')
                navigation[-2][0](navigation[-2][1])

            elif operation == 'cancel_culling':
                cancel_culling(meatberry, bunny)
                report = f'Вибраківка {bunny.name} скасована'
                quick_message(report, False)
                logger.info(report)
                navigation[-2][0](navigation[-2][1])

        right_button = get_operations_by_rabbit(handle_operation) if navigation[-2][0] == show_rabbit_list else get_operations_by_culling(handle_operation)
        set_bottom_app_bar()
        info = ft.Text(value=str(bunny), size=20)

        main_content.content = ft.Column([ft.Divider(), ft.Text(f'Картка: {bunny.name}', size=22, weight=ft.FontWeight.BOLD), info])
        set_appbar(right_actions=right_button)
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
        set_appbar(right_actions=btn_op)
        info = ft.Text(value=str(box), size=20)

        main_content.content = ft.Column([ft.Divider(), ft.Text(f'Картка: {box.block}.{box.box}', size=22, weight=ft.FontWeight.BOLD), info])

        main_content.update()

    def show_defective(e=None):
        text = ft.Text(f'Вибраковані кролиці ({len(meatberry.defective)})', size=22, weight=ft.FontWeight.BOLD)
        culling = ft.Column([text])

        for num, name in enumerate(meatberry.defective, 1):
            obj_rabbit = meatberry.rabbits.get(name)
            subtitle_text = ft.Text(f'{meatberry.rabbits[name].str_block_box if name in meatberry.rabbits else 'Вже померла'}')
            item = ft.ListTile(leading=ft.Icon(ft.Icons.PETS),  title=ft.Text(name),  subtitle=subtitle_text,
                               on_click=lambda e, r=obj_rabbit: navigate_to(show_str_rabbit, r))
            culling.controls.append(item)

        set_appbar()
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
            dict_to_create_rabbit['block'] = int(block_field.value)
            dict_to_create_rabbit['box'] = int(box_field.value)
            obj = create_and_add_new_bunny(meatberry, dict_to_create_rabbit['birthday'], dict_to_create_rabbit['name'],
                                     dict_to_create_rabbit['block'], dict_to_create_rabbit['box'])

            if obj:
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