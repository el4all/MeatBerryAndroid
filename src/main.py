import flet as ft
import requests


from bunny_classes import Farm, Bunny, Nest, Box, STATUS_WORK
from work_with_files import open_and_read_json, write_json
from helper_functions import create_rabbit_card, looking_for_work
from buttons_filters import BTN_SYNC, BTN_SORT

URL = 'https://drive.google.com/uc?export=download&id=1459S6Uo3w-f5i5KnDhV5XG0RFCNBDLgW'

def file_from_google():
    try:
        response = requests.get(URL, timeout=(5,30))
        response.raise_for_status()
        data = response.json()

        return data
    except Exception as e:
        print(f'Error download: {e}')
        return {'rabbits': {}}

farm_dict = file_from_google()
file_name = 'ACTUALLY_FARM.json'
meatberry = Farm('MeatBerry')
meatberry.load_from_network(farm_dict)


def main(page: ft.Page):
    main_content = ft.Container(expand=True)

    page.title = "Моя Ферма"
    page.scroll = ft.ScrollMode.AUTO  # Дозволяє гортати екран, якщо список великий

    navigation = []

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

    def show_rabbit_list(by_what=None):

        left_button = ft.Button('Операції', on_click=lambda e: print('list of operations'))
        set_bottom_app_bar(left_button)

        set_appbar(left_actions=BTN_SYNC, right_actions=BTN_SORT)
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
                                   trailing=ft.Text(STATUS_WORK.get(process, ''), size=14, weight=ft.FontWeight.BOLD),
                                   on_click=lambda e, b=meatberry.rabbits[name]: navigate_to(show_str, b))
                bunnies.controls.append(item)
            else:
                print(f'{rabbit} not founded.')
        main_content.content = bunnies
        main_content.update()

    def show_str(bunny: Bunny):

        main_content.content = ft.Column()
        info = ft.Text(value=str(bunny), size=20)

        main_content.content = ft.Column([ft.Divider(), ft.Text(f'Картка: {bunny.name}', size=22, weight=ft.FontWeight.BOLD), info])
        set_appbar()
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


    # Стартова точка (функція)
    navigate_to(show_main_menu)
# Запуск додатка
ft.run(main)