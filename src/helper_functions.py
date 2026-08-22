import flet as ft


from datetime import date
from bunny_classes import Bunny, Farm


BOXES = dict([(1,20),(2,20),(3,20),(4,20),(5,20),(6,25),(7,20),(8,20),(9,20),(10,20),(11,12),(12,12)])


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



