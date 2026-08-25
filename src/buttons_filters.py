import  flet as ft
from bunny_classes import Bunny
from helper_functions import create_rabbit_card

STATUS_FOR_NEST = dict([('install', 'встановлене порожнє'), ('close', 'встановлене з кролями'),
                        ('open', 'відкрите'), ('remove', 'без будки з кролями')])
STATUS_WORK = dict([('mate','запліднення'),('palpation','пальпація'),('kindling','окрол'),('install nest','монтаж гнізда'),
                    ('open nest',"відкривання гнізда"),('remove nest','демонтаж гнізда'),('resettle','переселення'),
                    ('vaccination nest','вакцинація гнізда'),('prepare nest','підготовка гнізда'),('swap box','перміщення'),
                    (None,'')])

BTN_SYNC = ft.IconButton(icon=ft.Icons.SYNC, tooltip='Синхронізувати з GoogleDisc')



def get_sort_menu(show_rabbits_list):
    return ft.PopupMenuButton(
            icon=ft.Icons.SORT,
            tooltip='Сортування',
            items=[ft.PopupMenuItem(content=ft.Text('По імені'), data='by_name', on_click=show_rabbits_list),
                   ft.PopupMenuItem(content=ft.Text('По черзі додавання'), data='by_time_add', on_click=show_rabbits_list),
                   ft.PopupMenuItem(content=ft.Text('По віку (зростання)'), data='by_age_up', on_click=show_rabbits_list),
                   ft.PopupMenuItem(content=ft.Text('По віку (спадання)'), data='by_age_down', on_click=show_rabbits_list),
                   ft.PopupMenuItem(content=ft.Text('По рейтингу (зростання)'), data='by_rating_up', on_click=show_rabbits_list),
                   ft.PopupMenuItem(content=ft.Text('По рейтингу (спадання)'), data='by_rating_down', on_click=show_rabbits_list)
                   ]
        )

def get_operations_by_rabbit(handle_operation):
    return ft.PopupMenuButton(tooltip='Операції',
                              items=[ft.PopupMenuItem(content=ft.Text('Видалити кролицю (смерть)'), data='remove_by_death', on_click=handle_operation),
                                     ft.PopupMenuItem(content=ft.Text('Видалити кролицю (вибраковка)'), data='remove_by_culling',on_click=handle_operation),
                                     ft.PopupMenuItem(content=ft.Text('Встановити як вибраківку'), data='set_culling', on_click=handle_operation),
                                     ft.PopupMenuItem(content=ft.Text('Переміщення'), data='swap_box', on_click=handle_operation)])

def get_nest_info_container(rabbit: Bunny):
    return ft.Container(content=ft.Column(controls=[ft.Text(f'Гніздо {rabbit.name}', weight=ft.FontWeight.BOLD, size=20),
                                                    ft.Text(f'Батько {rabbit.nest.father}', weight=ft.FontWeight.NORMAL, size=20),
                                                    ft.Text(f'Дата народження: {'' if rabbit.nest.date_birth is None else rabbit.nest.date_birth} ({"окрол ще не відбувся." if rabbit.nest.nest_age is None else f"{rabbit.nest.nest_age} дн."})', weight=ft.FontWeight.NORMAL, size=20),
                                                    ft.Text(f'Статус {STATUS_FOR_NEST.get(rabbit.nest.status)}', weight=ft.FontWeight.NORMAL, size=20),
                                                    ft.Text(f'Сформовано: {rabbit.nest.bunnies.get("formed", "(окрол ще не відбувся.)")}', weight=ft.FontWeight.NORMAL, size=20)]),

                        padding=10,
                        border_radius=8) if rabbit.nest is not None else ft.Container(content=ft.Column(controls=[ft.Text(f'Кролиця {rabbit.name} не має гнізда', weight=ft.FontWeight.BOLD)]),
                                                                                      bgcolor=ft.Colors.ON_SURFACE_VARIANT,
                                                                                      padding=10,
                                                                                      border_radius=8
                                                                                      )

def get_text_fields_for_swap_boxes(handle_input):
    block_num = ft.TextField(label='Блок', keyboard_type=ft.KeyboardType.NUMBER, on_change=handle_input)
    box_num = ft.TextField(label='Клітка', keyboard_type=ft.KeyboardType.NUMBER, on_change=handle_input)
    result_field = ft.Text(value='В клітці', size=18, weight=ft.FontWeight.BOLD)
    return block_num, box_num, result_field

def get_operations_by_many_rabbits(handle_operation):
    return ft.PopupMenuButton(content= ft.Row([ft.Text('Операції', size=14, weight=ft.FontWeight.BOLD),
                                               ft.Icon(ft.Icons.ARROW_DROP_UP_SHARP)],
                                              tight=True),
                              tooltip='Операції для декількох кролиць',
                              items=[ft.PopupMenuItem(content=ft.Text('Додати кролицю'), data='add_rabbit', on_click=handle_operation),
                                     ft.PopupMenuItem(content=ft.Text('Видалити кролиць (вибраковка)'), data='remove_by_culling',on_click=handle_operation)])

def get_little_containers_prework(text):
    return ft.Container(width=80,
                        content=ft.Text(STATUS_WORK[text], size=10, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.YELLOW_500 if text else create_rabbit_card(text),
                        padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                        border_radius=4)

def get_little_containers_today(text):
    return ft.Container(width=80,
                        content=ft.Text(STATUS_WORK[text], size=10, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREEN_500 if text else create_rabbit_card(text),
                        padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                        border_radius=4)

def get_little_containers_afterwork(text):
    return ft.Container(width=150,
                        content=ft.Text(STATUS_WORK[text], size=10, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.RED_500 if text else create_rabbit_card(text),
                        padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                        border_radius=4)

def get_main_container_for_trailing(data: dict):
    trailing_widget = None
    if data:
        trailing_widget = ft.Container(width=80, height=70, offset=ft.Offset(0, -0.35),
                                       content=ft.Column(controls=[get_little_containers_prework(data.get('tomorrow', None)),
                                                                   get_little_containers_today(data.get('today', None)),
                                                                   get_little_containers_afterwork(data.get('yesterday', None))],
                                                         spacing=2))

    return trailing_widget

# trailing for item in show_rabbits_list()
# ft.Row(controls=[ft.Text(STATUS_WORK.get(process, ''), size=14, weight=ft.FontWeight.BOLD),
#                  ft.Checkbox(value=False, on_change=lambda e: print('Flag worked'))] if check_box else [ft.Text(STATUS_WORK.get(process, ''),
#                                                                                                                 size=14, weight=ft.FontWeight.BOLD)],
#                                                 tight=True),