import flet as ft


from datetime import date


from bunny_classes import Bunny, Farm
from puthon_logic_func import empty_box, average_age_rabbits


BOXES = dict([(1,20),(2,20),(3,20),(4,20),(5,20),(6,25),(7,20),(8,20),(9,20),(10,20),(11,12),(12,12)])


def open_alert_dialog(page: ft.Page, dialog):
    dialog.open = True
    page.update()

def close_alert_dialog(page: ft.Page, dialog):
    dialog.open = False
    page.update()

def quick_message(message: str, is_error: bool, page: ft.Page):
    snack = ft.SnackBar(content=ft.Text(message), duration=3000, behavior=ft.SnackBarBehavior.FLOATING,
                        bgcolor=ft.Colors.RED_100 if is_error else ft.Colors.BLUE_GREY_700, open=True)

    page.overlay.append(snack)
    page.update()

def open_picker(page: ft.Page, date_picker):
    if date_picker not in page.overlay:
        page.overlay.append(date_picker)
    date_picker.open = True
    page.update()

def first_step_enter_date_process(page, dialog, date_picker):
    cancel_btn = ft.Button('Скасувати операцію', on_click=lambda e: close_alert_dialog(page,dialog))
    open_calendar_btn = ft.Button('Відкрити календар', on_click=lambda e: open_picker(page,date_picker))

    open_alert_dialog(page,dialog)
    dialog.title = 'КРОК 1. Дата проведення запліднення'
    dialog.content = ft.Column([ft.Text('Оберіть дату запліднення групи')], tight=True)
    dialog.actions = [cancel_btn, open_calendar_btn]
    dialog.update()

def create_rabbit_card(work):
    color = None
    if work == 'resettle':
        color = ft.Colors.BLUE_100
    elif work == 'vaccination nest':
        color = ft.Colors.YELLOW_100
    elif work == 'install nest':
        color = ft.Colors.PINK_100
    elif work == 'prepare nest':
        color = ft.Colors.GREEN_100
    elif work == 'mate':
        color = ft.Colors.RED_100
    elif work == 'palpation':
        color = ft.Colors.AMBER_100
    elif work == 'kindling':
        color = ft.Colors.GREY_100
    elif work == 'open nest':
        color = ft.Colors.ORANGE_100
    elif work == 'remove nest':
        color = ft.Colors.TEAL_100
    elif work == 'swap box':
        color = ft.Colors.BROWN_100

    return color

def change_box_for_rabbit(farm: Farm, new_block: ft.TextField, new_box: ft.TextField, result_text: ft.Text):
    new_block.error = None
    new_box.error = None

    has_error = False

    block_val = new_block.value.strip() if new_block.value else ''
    if not block_val or not block_val.isdigit():
        new_block.error = 'Введіть блок'
        has_error = True
    new_block.update()

    box_val = new_box.value.strip() if new_box.value else ''
    if not box_val or not box_val.isdigit():
        new_box.error = 'Введіть клітку'
        has_error = True

    new_box.update()

    if has_error:
        return False

    name = ''
    if block_val.isdigit() and box_val.isdigit():
        name = who_in_box(farm, block_val, box_val)
    result_text.value = f"В клітці {block_val}.{box_val} - {name} "

    result_text.update()

    return int(block_val), int(box_val)

def who_in_box(farm: Farm, block, box):
    block = int(block)
    box = int(box)
    for obj in farm.rabbits.values():
        if obj.block == block and obj.box == box:
            return obj.name
    return 'порожньо'

def get_column_for_empty_box(farm: Farm, main_content):
    dict_of_empty_boxes = empty_box(farm)
    empty_boxes = ft.Column([ft.Text('Порожні клітки', size=16, weight=ft.FontWeight.W_500)])
    for block, list_boxes in dict_of_empty_boxes.items():
        if list_boxes:
            item = ft.ListTile(leading=ft.Icon(ft.Icons.SQUARE), title=ft.Text(f'Блок {block}'),
                               trailing=ft.Text(f'{",".join(map(str,list_boxes))}'))
            empty_boxes.controls.append(item)

    main_content.content = empty_boxes

    return main_content

def get_list_rabbits_with_checkbox(farm: Farm):
    pass

def add_mate(farm: Farm, page: ft.Page, dialog: ft.AlertDialog, date_picker, after_picker):
    date_picker.on_change = after_picker
    first_step_enter_date_process(page, dialog, date_picker)

def create_rabbit_tile(obj: Bunny):
    color = ft.Colors.RED_500 if obj.status == 'culling' else ft.Colors.GREEN_500
    return ft.ListTile(leading=ft.Icon(ft.Icons.PETS, color=color), title=ft.Text(obj.name),
                       subtitle=ft.Column(controls=[ft.Text(f"Клітка: {obj.str_block_box}"),
                                                     ft.Text(f"Вік: {obj.age_in_month}")]), data=obj.name,
                       content_padding=ft.Padding.symmetric(horizontal=16, vertical=9))

def mass_kill_third_room(page: ft.Page, farm: Farm, block):

    boxes = ft.Column()
    for el in farm.third_room.values():
        if el.block == block:
            item = ft.Row(controls=[ft.Text(f'{el.block}.{el.box}     '),
                                    ft.Checkbox(label='Догодівля', label_position=ft.LabelPosition.LEFT,
                                                on_change=lambda e: print('III')),
                                    ft.TextField(width=100),
                                    ft.Text('Кількість')])
            boxes.controls.append(item)
    page.clean()
    page.add(boxes)
    page.update()

def quantity_of_farm(farm: Farm):
    quantity_female = len([x for x in farm.rabbits.values() if x.sex == 'female'])
    quantity_male = len([x for x in farm.rabbits.values() if x.sex == 'male'])
    quantity_bunnies = sum([x.quantity for x in farm.third_room.values()])
    quantity_rabbits_vidget = ft.ExpansionTile('Кількість ферми',
                                               controls=[ft.ListTile(ft.Row([ft.Text('     '),
                                                                             ft.Icon(ft.Icons.FEMALE,
                                                                                     color=ft.Colors.PINK_100),
                                                                             ft.Text(f'Cамиці - {quantity_female}')])),
                                                         ft.ListTile(ft.Row([ft.Text('     '),
                                                                             ft.Icon(ft.Icons.FEMALE,
                                                                                     color=ft.Colors.BLUE_100),
                                                                             ft.Text(f'Cамці - {quantity_male}')])),
                                                         ft.ListTile(ft.Row([ft.Text('     '),
                                                                             ft.Icon(ft.Icons.CRUELTY_FREE,
                                                                                     color=ft.Colors.GREY_500),
                                                                             ft.Text(
                                                                                 f'Відгодівля - {quantity_bunnies}')]))
                                                         ])
    return quantity_rabbits_vidget

def average_age_of_farm(farm:Farm):
    avg_age_female = average_age_rabbits(farm, 'female')
    #avg_age_male = average_age_rabbits(farm, 'male')
    avg_age_vidget = ft.ExpansionTile("Середній вік ферми",
                                      controls=[ft.ListTile(ft.Row([ft.Text('     '),
                                                                    ft.Icon(ft.Icons.FEMALE, color=ft.Colors.PINK_100),
                                                                    ft.Text(f"Самиці - {avg_age_female} днів")])),
                                                # ft.ListTile(ft.Row([ft.Text('     '),
                                                #                     ft.Icon(ft.Icons.MALE, color=ft.Colors.BLUE_100),
                                                #                     ft.Text(f"Самці - {avg_age_male} днів")]))
                                                ])
    return avg_age_vidget

def farm_by_status(farm: Farm):
    all_rabbits = len([x for x in farm.rabbits.values() if x.sex == 'female'])
    worked = len([x for x in farm.rabbits.values() if x.sex == 'female' and x.status != 'culling'])
    culling = len([x for x in farm.rabbits.values() if x.sex == 'female' and x.status == 'culling'])
    mother = len([x for x in farm.rabbits.values() if x.sex == 'female' and x.status == 'mother'])
    new = len([x for x in farm.rabbits.values() if x.sex == 'female' and not x.history])

    status_ui = ft.ExpansionTile('Статус',
                                 controls=[ft.ExpansionTile(f'{5*' '}Робоче стадо - {worked} шт. ({(worked / all_rabbits*100):.2f} %)',
                                                            controls=[ft.ListTile(ft.Text(f'{10*' '}Матері - {mother} шт. ({(mother / worked*100):.2f} %)'),
                                                                      ft.ListTile(ft.Text(f'{10*''}Молодь - {new} шт. ({(new / worked*100):.2f} %)')))]),
                                           ft.ListTile(f'{5*' '}Вибраківка - {culling} шт. ({(culling / all_rabbits*100):.2f} %)')])
    return status_ui

STATUS_FOR_STR = {'mated': 'очікує на пальпацію', 'waiting_for_kindling': 'очікує на окріл', 'mother': 'матір',
          'mated mother': 'запліднена матір', 'mother*': 'матір без гнізда', 'culling': 'вибраківка', None:'немає',
                  'new': 'молодь', 'man': 'самець'}
STATUS_FOR_VISUAL_BOX = {'очікує на пальпацію': ft.Colors.YELLOW_300, 'очікує на окріл': ft.Colors.BLUE_300,
                         'матір': ft.Colors.ORANGE_100, 'запліднена матір': ft.Colors.PINK_100,
                         'матір без гнізда': ft.Colors.WHITE_10, 'вибраківка': ft.Colors.RED_300,
                         'молодь': ft.Colors.GREEN_200, 'cамець': ft.Colors.TEAL_100, 'немає': ft.Colors.GREY_500}

def color_for_box(farm: Farm, block, box):
    status = None
    for obj in farm.rabbits.values():
        if obj.block == block and obj.box == box:
            if obj.sex == 'female' and not obj.history:
                status = 'new'
            elif obj.sex == 'male':
                status = 'man'
            else:
                status = obj.status
            break

    return STATUS_FOR_VISUAL_BOX.get(STATUS_FOR_STR[status])

def get_block(farm: Farm, block):
    location_block = 'left' if block % 2 == 1 else 'right'

    first_container = ft.Column(alignment=ft.MainAxisAlignment.CENTER)
    second_container = ft.Container(content=ft.Text(str(block), size=25, weight=ft.FontWeight.BOLD))
    third_container = ft.Column(alignment=ft.MainAxisAlignment.CENTER)

    if block == 6:
        near_low_boxes = [5,4,3,2,1]
        near_high_near_boxes = [14,12,10,8,6]
        near_high_far_boxes = [15,13,11,9,7]
        far_low_boxes = [16,17,18,19,20]
        far_high_boxes = [21,22,23,24,25]

        for n_l_b, n_h_n_b, n_h_f_b, f_l_b, f_h_b in zip(near_low_boxes,near_high_near_boxes,near_high_far_boxes,
                                                         far_low_boxes,far_high_boxes):
            first_cont_row = (
                ft.Row(controls=[ft.Container(content=ft.Text(str(f_l_b) if len(str(f_l_b)) == 2 else f' {f_l_b} '),
                                              bgcolor=color_for_box(farm,block,f_l_b)),
                                 ft.Container(content=ft.Text(str(f_h_b) if len(str(f_h_b)) == 2 else f' {f_h_b} '),
                                              bgcolor=color_for_box(farm,block,f_h_b))]))
            first_container.controls.append(first_cont_row)

            third_cont_row = (
                ft.Row(controls=[ft.Container(content=ft.Text(str(n_h_f_b) if len(str(n_h_f_b)) == 2 else f' {n_h_f_b} '),
                                              bgcolor=color_for_box(farm,block,n_h_f_b)),
                                 ft.Container(content=ft.Text(str(n_h_n_b) if len(str(n_h_n_b)) == 2 else f' {n_h_n_b} '),
                                              bgcolor=color_for_box(farm,block,n_h_n_b)),
                                 ft.Container(content=ft.Text(str(n_l_b) if len(str(n_l_b)) == 2 else f' {n_l_b} '),
                                              bgcolor=color_for_box(farm,block,n_l_b))]))
            third_container.controls.append(third_cont_row)

        return first_container,second_container,third_container

    near_boxes = [x for x in range(1, int(BOXES[block]/4)+1)]\
        if location_block == 'left' else reversed([x for x in range(int(BOXES[block]/4+1), int(BOXES[block]/2+1))])
    far_boxes = reversed([x for x in range(int(BOXES[block]/4*3+1),BOXES[block]+1)])\
        if location_block == 'left' else [x for x in range(int(BOXES[block]/2+1), BOXES[block]-int(BOXES[block]/4)+1)]
    neighbour_near_box = [x for x in range(int(BOXES[block]/4+1), int(BOXES[block]/2+1))]\
        if location_block == 'left' else reversed([x for x in range(1, int(BOXES[block]/4)+1)])
    neighbour_far_box = reversed([x for x in range(int(BOXES[block]/2+1), BOXES[block]-int(BOXES[block]/4)+1)]) \
        if location_block == 'left' else [x for x in range(int(BOXES[block]/4*3+1),BOXES[block]+1)]


    for n_b, n_n_b, f_b, f_n_b in zip(near_boxes, neighbour_near_box, far_boxes, neighbour_far_box):
        first_cont_row = (ft.Row(controls=[ft.Container(content=ft.Text(str(n_b) if len(str(n_b)) == 2 else f' {n_b} '),
                                                        bgcolor=color_for_box(farm,block,n_b)),
                                           ft.Container(content=ft.Text(str(n_n_b) if len(str(n_n_b)) == 2 else f' {n_n_b} '),
                                                        bgcolor=color_for_box(farm,block,n_n_b))]))
        first_container.controls.append(first_cont_row) if location_block == 'left' else third_container.controls.append(first_cont_row)

        third_cont_row = (ft.Row(controls=[ft.Container(content=ft.Text(str(f_b) if len(str(f_b)) == 2 else f' {f_b} '),
                                                        bgcolor=color_for_box(farm,block,f_b)),
                                           ft.Container(content=ft.Text(str(f_n_b) if len(str(f_n_b)) == 2 else f' {f_n_b} '),
                                                        bgcolor=color_for_box(farm,block,f_n_b))]))
        third_container.controls.append(third_cont_row) if location_block == 'left' else first_container.controls.append(third_cont_row)

    return first_container,second_container,third_container