import  flet as ft


from datetime import date
from bunny_classes import Bunny, Farm
from helper_functions import create_rabbit_card, get_column_for_empty_box
from puthon_logic_func import search_process_date_for_rabbit

STATUS_FOR_NEST = dict([('install', 'встановлене порожнє'), ('close', 'встановлене з кролями'),
                        ('open', 'відкрите'), ('remove', 'без будки з кролями')])
STATUS_WORK = dict([('mate','запліднення'),('palpation','пальпація'),('kindling','окрол'),('install nest','монтаж гнізда'),
                    ('open nest',"відкривання гнізда"),('remove nest','демонтаж гнізда'),('resettle','переселення'),
                    ('vaccination nest','вакцинація гнізда'),('prepare nest','підготовка гнізда'),('swap box','переміщення'),
                    (None,'')])
STATUS_FOR_STR = {'mated': 'очікує на пальпацію', 'waiting_for_kindling': 'очікує на окріл', 'mother': 'матір',
          'mated mother': 'запліднена матір', 'mother*': 'матір без гнізда', 'culling': 'вибраківка', None:'немає'}
STATUS_FOR_VISUAL_BOX = {'очікує на пальпацію': ft.Colors.YELLOW_500, 'очікує на окріл': ft.Colors.BLUE_500,
                         'матір': ft.Colors.ORANGE_500, 'запліднена матір': ft.Colors.PINK_500,
                         'матір без гнізда': ft.Colors.WHITE_10, 'вибраківка': ft.Colors.RED_500,
                         'молодь': ft.Colors.GREEN_500}

BTN_SYNC = ft.IconButton(icon=ft.Icons.SYNC, tooltip='Синхронізувати з GoogleDisc')
BTN_CHANGE_THEME = ft.IconButton(icon=ft.Icons.SUNNY, tooltip='Поміняти тему')


def get_sort_menu(func_for_sort):
    return ft.PopupMenuButton(
            icon=ft.Icons.SORT,
            tooltip='Сортування',
            items=[ft.PopupMenuItem(content=ft.Text('По імені A-Z'), data=(lambda obj: obj.name, False), on_click=func_for_sort),
                   ft.PopupMenuItem(content=ft.Text('По імені Z-A'), data=(lambda obj: obj.name, True), on_click=func_for_sort),
                   ft.PopupMenuItem(content=ft.Text('По черзі додавання'), data=(None,False), on_click=func_for_sort),
                   ft.PopupMenuItem(content=ft.Text('По віку (зростання)'), data=(lambda obj: obj.age, False), on_click=func_for_sort),
                   ft.PopupMenuItem(content=ft.Text('По віку (спадання)'), data=(lambda obj: obj.age, True), on_click=func_for_sort),
                   ft.PopupMenuItem(content=ft.Text('По рейтингу (зростання)'), data=(lambda obj: obj.rating, False), on_click=func_for_sort),
                   ft.PopupMenuItem(content=ft.Text('По рейтингу (спадання)'), data=(lambda obj: obj.rating, True), on_click=func_for_sort)
                   ]
        )

def get_operations_by_rabbit(handle_operation):
    return ft.PopupMenuButton(icon=ft.Icon(ft.Icons.SETTINGS),
                              tooltip='Операції',
                              items=[ft.PopupMenuItem(content=ft.Text('Видалити кролицю (смерть)'), data='remove_by_death', on_click=handle_operation),
                                     ft.PopupMenuItem(content=ft.Text('Видалити кролицю (забій)'), data='remove_by_culling',on_click=handle_operation),
                                     ft.PopupMenuItem(content=ft.Text('Встановити як вибраківку'), data='set_culling', on_click=handle_operation),
                                     ft.PopupMenuItem(content=ft.Text('Втрата гнізда'), data='loose_nest', on_click=handle_operation),
                                     ft.PopupMenuItem(content=ft.Text('Переміщення'), data='swap_box', on_click=handle_operation)])

def get_info_by_rabbit(handle_operation):
    return ft.PopupMenuButton(icon=ft.Icon(ft.Icons.HELP),
                              tooltip='Інформація')

def get_operations_by_culling(handle_operation):
    return ft.PopupMenuButton(tooltip='Операції',
                              items=[ft.PopupMenuItem(content=ft.Text('Видалити кролицю (забій)'),
                                                   data='remove_by_culling', on_click=handle_operation),
                                     ft.PopupMenuItem(content=ft.Text('Скасувати вибраківку'),
                                                      data='cancel_culling', on_click=handle_operation)
                                     ])

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
    return ft.PopupMenuButton(content= ft.Row([ft.Icon(ft.Icons.BACK_HAND),
                                               ft.Icon(ft.Icons.ARROW_DROP_DOWN)],
                                              tight=True),
                              tooltip='Операції для декількох кролиць',
                              items=[ft.PopupMenuItem(content=ft.Text('Додати кролицю'), data='add_rabbit', on_click=handle_operation)])

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
        trailing_widget = ft.Container(width=80, height=70,
                                       content=ft.Column(controls=[get_little_containers_prework(data.get('tomorrow', None)),
                                                                   get_little_containers_today(data.get('today', None)),
                                                                   get_little_containers_afterwork(data.get('yesterday', None))],
                                                         spacing=2))

    return trailing_widget

def get_btn_for_operation_with_box(handle_operation):
    return ft.PopupMenuButton(items=[ft.PopupMenuItem(content=ft.Text('Змінити кількість мешканців'), data='change_quantity', on_click=handle_operation)])

def get_btns_for_box_str():
    quantity = ft.TextField(label='Кількість', keyboard_type=ft.KeyboardType.NUMBER)
    increase_btn = ft.Button('Додати')
    decrease_btn = ft.Button('Відняти')
    return quantity, increase_btn, decrease_btn

def get_btn_by_farm_info(farm: Farm, main_content, navigate_to):
    return ft.PopupMenuButton(content= ft.Row([ft.Text('Інформація', size=14, weight=ft.FontWeight.BOLD),
                                               ft.Icon(ft.Icons.ARROW_DROP_UP_SHARP)],
                                              tight=True),
                              tooltip='Інформація по фермі',
                              items=[ft.PopupMenuItem(content=ft.Text('Порожні клітки'), data='empty_boxes',
                                                      on_click=lambda e: (navigate_to(get_column_for_empty_box, farm, main_content), main_content.update())),
                                     ft.PopupMenuItem(content=ft.Text('Рейтинг'), data='rating')])

def get_btn_for_operation_in_third_room(handle_choice):
    return ft.PopupMenuButton(content= ft.Row([ft.Text('Операції', size=14, weight=ft.FontWeight.BOLD),
                                               ft.Icon(ft.Icons.ARROW_DROP_UP_SHARP)],
                                              tight=True),
                              tooltip='Операції',
                              items=[ft.PopupMenuItem(content=ft.Text('Додати клітку'),
                                                   data='add_box', on_click=lambda e: handle_choice(e)),
                                     ft.PopupMenuItem(content=ft.Text('Забій'), data='mass_kill',
                                                      on_click=lambda e: handle_choice(e))])

def get_status_pop_menu(handle_choice):
    return ft.PopupMenuButton(content=ft.Container(content=ft.Row([ft.Text('Статус'),
                                                                   ft.Icon(ft.Icons.ARROW_DROP_DOWN)])),
                              items=[ft.PopupMenuItem(content=ft.Text('Відгодівля'), data='meat', on_click=lambda e: handle_choice(e)),
                                     ft.PopupMenuItem(content=ft.Text('Ремонт'), data='repare', on_click=lambda e: handle_choice(e)),
                                     ft.PopupMenuItem(content=ft.Text('Догодівля'), data='feeding', on_click=lambda e: handle_choice(e))])

def get_little_containers_mate(res, color):
    return ft.Container(width=80,
                        content=ft.Text(res, size=10),
                        bgcolor= color,
                        padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                        border_radius=4)

def get_container_for_trailing_process(data: dict):
    trailing_widget = None
    if data:
        control_two_color = [get_little_containers_mate(data.get('positive', None),'green'),
                             get_little_containers_mate(data.get('negative', None), 'red')]
        control_unknown = [get_little_containers_mate(data.get('?', None),'blue')]
        trailing_widget = ft.Container(width=80, height=70,
                                       content=ft.Column(controls=control_two_color if len(data) > 1 else control_unknown,
                                                         spacing=2))

    return trailing_widget

def get_trailing_for_rabbits_list_for_mates():
        return ft.PopupMenuButton(content= ft.Row([ft.Text('Лінія самця', size=10, weight=ft.FontWeight.BOLD),
                                                            ft.Icon(ft.Icons.ARROW_DROP_DOWN_SHARP)], tight=True),
                                           items=[ft.PopupMenuItem(content='X'),
                                                  ft.PopupMenuItem(content='Y'),
                                                  ft.PopupMenuItem(content='Z'),
                                                  ft.PopupMenuItem(content='вибраківка'),
                                                  ft.PopupMenuItem(content='*')])

def get_pop_menu_for_select_process(processing_pop_menu):
    return ft.PopupMenuButton(content= ft.Row([ft.Icon(ft.Icons.FRONT_HAND),
                                               ft.Icon(ft.Icons.ARROW_DROP_DOWN_SHARP)],
                                              tight=True),
                              tooltip='Обрати операцію',
                              items=[ft.PopupMenuItem(content=ft.Text('Запліднення'), data='for_mate', on_click=processing_pop_menu),
                                     ft.PopupMenuItem(content=ft.Text('Пальпація'), data='for_palpation', on_click=processing_pop_menu),
                                     ft.PopupMenuItem(content=ft.Text('Окрол'), data='for_kindling', on_click=processing_pop_menu),
                                     ft.PopupMenuItem(content=ft.Text('Монтаж гнізда'), data='for_install_nest', on_click=processing_pop_menu),
                                     ft.PopupMenuItem(content=ft.Text('Підготовка гнізда'), data='for_prepare_nest', on_click=processing_pop_menu),
                                     ft.PopupMenuItem(content=ft.Text('Відкриття гнізда'), data='for_open_nest', on_click=processing_pop_menu),
                                     ft.PopupMenuItem(content=ft.Text('Демонтаж гнізда'), data='for_uninstall_nest', on_click=processing_pop_menu),
                                     ft.PopupMenuItem(content=ft.Text('Переселення'), data='for_resettle', on_click=processing_pop_menu),
                                     ft.PopupMenuItem(content=ft.Text('Вакцинація'), data='for_vaccination', on_click=processing_pop_menu)]
                              )

def get_trailing_for_rabbit_list(mode: str, rabbit: Bunny):
    match mode:
        case 'for_main':
            pairs_work_color = search_process_date_for_rabbit(rabbit)
            return get_main_container_for_trailing(pairs_work_color)
        case 'for_mate':
            return  get_trailing_for_rabbits_list_for_mates()
        case _:
            return None

def get_pop_menu_for_choose_block(farm: Farm, returning_e_data):
    items = []
    for el in sorted([x for x in set([x.block for x in farm.third_room.values()])]):
        item = ft.PopupMenuItem(content=ft.Text(el), data=el, on_click=returning_e_data)
        items.append(item)

    return ft.PopupMenuButton(content=ft.Text('Оберіть блок'), items=items)

def info_by_color():
    pop_menu = ft.PopupMenuButton(icon=ft.Icon(ft.Icons.INFO))
    for description, color in STATUS_FOR_VISUAL_BOX.items():
        item=ft.PopupMenuItem(content=ft.Row([ft.Icon(ft.Icons.SQUARE, color=color), ft.Divider(), ft.Text(description)]))
        pop_menu.items.append(item)

    return pop_menu