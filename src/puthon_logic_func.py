from datetime import date, datetime, timedelta

import loguru

from datetime import  date
from bunny_classes import  Farm, Bunny, Box


BOXES = dict([(1,[x for x in range(1,21)]),(2,[x for x in range(1,21)]),(3,[x for x in range(1,21)]),(4,[x for x in range(1,21)]),
              (5,[x for x in range(1,21)]),(6,[x for x in range(1,26)]),(7,[x for x in range(1,21)]),(8,[x for x in range(1,21)]),
              (9,[x for x in range(1,21)]),(10,[x for x in range(1,21)]),(11,[x for x in range(1,13)]),(12,[x for x in range(1,13)])])

STATUS_WORK = dict([('mate','запліднення'),('palpation','пальпація'),('kindling','окрол'),('install nest','монтаж гнізда'),
                    ('open nest',"відкривання гнізда"),('remove nest','демонтаж гнізда'),('resettle','переселення'),
                    ('vaccination nest','вакцинація гнізда'),('prepare nest','підготовка гнізда'),('swap box','перміщення')])

def looking_for_work(rabbit: Bunny):
    today = date.today()
    if rabbit.all_planing_dates is not None:
        for work, dates in rabbit.all_planing_dates.items():
            if dates == today:
                return work
    return None

def set_rabbit_culling(farm: Farm, rabbit: Bunny):
    rabbit.status = 'culling'
    if rabbit.name not in farm.defective:
        farm.defective.append(rabbit.name)
        return True
    return False

def cancel_culling(farm: Farm, rabbit: Bunny):
    rabbit.status = None
    if rabbit.name in farm.defective:
        farm.defective.remove(rabbit.name)

def rewrite_block_and_box(farm: Farm, bunny, block, box):
    print(bunny.name, block, box)
    rabbit_in_new_box = ''
    moved_rabbit_block = bunny.block
    moved_rabbit_box = bunny.box
    for obj in farm.rabbits.values():
        if obj.block == block and obj.box == box:
            rabbit_in_new_box = obj
            break
    if rabbit_in_new_box:
        rabbit_in_new_box.block = moved_rabbit_block
        rabbit_in_new_box.box = moved_rabbit_box
        bunny.block = block
        bunny.box = box
    else:
        bunny.block = block
        bunny.box = box

def remove_by_death(farm: Farm, bunny):
    farm.morgue.append([bunny.name, bunny.age, bunny.history])

    if bunny.name in farm.defective:
        farm.defective.remove(bunny.name)

    for rabbit in farm.rabbits.copy():
        if rabbit == bunny.name:
            farm.rabbits.pop(rabbit)

def remove_by_culling(farm: Farm, bunny):
    if bunny.name in farm.defective:
        farm.defective.remove(bunny.name)

    for rabbit in farm.rabbits.copy():
        if rabbit == bunny.name:
            farm.rabbits.pop(rabbit)

def vacant_index_for_rabbit(farm: Farm, line: str):
    indexes = []
    for name in farm.rabbits:
        if line in name:
            index = int(name[2:])
            print(index)
            indexes.append(index)
    if not indexes:
        return 1

    free_indexes = [x for x in set(range(1, len(indexes)+1)) - set(indexes)]

    return free_indexes[0] if free_indexes else len(indexes)+1

def empty_boxes(farm: Farm):
    all_boxes = BOXES.copy()
    more_then_one = {}

    for obj in farm.rabbits.values():
        if obj.block in BOXES and obj.box in all_boxes[obj.block]:
            all_boxes[obj.block].remove(obj.box)
        else:
            more_then_one.setdefault(obj.block, []).append(obj.box)

    print(all_boxes)
    print(more_then_one)

def create_and_add_new_bunny(farm: Farm, birthday: str, name, block, box):
    if name not in farm.rabbits:
        bunny_obj = Bunny(name, birthday, block, box)
        farm.rabbits[name] = bunny_obj
        return True
    else:
        return False

def search_process_date_for_rabbit(rabbit: Bunny):
    today = date.today()
    if rabbit.all_planing_dates is not None:
        pair_process_color = {}
        for process, day in rabbit.all_planing_dates.items():
            if day == today:
                pair_process_color['today'] = process
            elif day - today == timedelta(days=1):
                pair_process_color['tomorrow'] = process
            elif day - today == timedelta(days=-1):
                pair_process_color['yesterday'] = process
        return pair_process_color
    return {}

def increase_quantity_in_third_room(obj:Box, quantity_field):
    current = int(quantity_field.value) if quantity_field.value and quantity_field.value.isdigit() else 0

    obj.quantity += current
    loguru.logger.info(f'In box {obj.block}.{obj.box} + {current} bunnies')

def decrease_quantity_in_third_room(obj: Box, quantity_field):
    current = int(quantity_field.value) if quantity_field.value and quantity_field.value.isdigit() else 0
    if current <= obj.quantity:
        obj.quantity -= current
        loguru.logger.info(f'In box {obj.block}.{obj.box} - {current} bunnies')

def calculate_bunnies_in_block(farm: Farm, block):
    return sum([x.quantity for x in farm.third_room.values() if x.block == block])

def calculate_age_and_quantity(farm: Farm, block):
    data = {}
    for obj in farm.third_room.values():
        if obj.block == block:
            data.setdefault(obj.box_age, []).append(obj.quantity)

    return data

def empty_box(farm: Farm):
    empty = {}
    all_boxes = {}
    for obj in farm.rabbits.values():
        all_boxes.setdefault(obj.block, []).append(obj.box)

    for block, box in BOXES.items():
        e_b = set(box) - set(all_boxes.get(block))
        empty.setdefault(block, []).extend(sorted([x for x in e_b]))

    return empty

def add_box_in_third_room(farm: Farm, dict_attr):
    box_obj = Box(dict_attr['block'], dict_attr['box'],dict_attr['quantity'], dict_attr['birth'], dict_attr['status'])
    farm.third_room[f'{box_obj.block}.{box_obj.box}'] = box_obj
    box_obj.set_kill_date()

def get_dates_for_processes(farm: Farm, process):

    dates = []
    for obj in farm.rabbits.values():
        attr = getattr(obj, process)
        for el in attr:
            if not el in dates:
                dates.append(el)

    return sorted(dates, reverse=True)

def get_result_of_mates(farm: Farm, date_of_mate: date):

    results = {}

    for obj in farm.rabbits.values():
        for day, info in obj.mate.items():
            if day == date_of_mate:
                result = info.get('result')
                results[result] = results.get(result, 0) + 1

    return results

def get_info_of_one_mate(farm: Farm, day: date):
    res = []
    for obj in farm.rabbits.values():
        for d, info in obj.mate.items():
            if d == day:
                res.append([obj.name, info.get('father_line'), info.get('result')])

    return res

def get_info_of_one_kindling(farm: Farm, day: date):
    res = []
    for obj in farm.rabbits.values():
        for d, info in obj.kindling.items():
            if d == day:
                res.append([obj.name, info.get('father_line'), info.get('result')])

    return res

def get_all_planning_for_process(farm: Farm, process):
    need = {}
    for obj in farm.rabbits.values():
        for p, d in obj.all_planing_dates.items():
            if p == process:
                need.setdefault(d, []).append(obj.name)

    return need

def get_all_planning_for_today(farm: Farm):
    today = date.today()
    need = {}
    for obj in farm.rabbits.values():
        for p, d in obj.all_planing_dates.items():
            if d == today:
                need.setdefault(p, []).append(obj.name)

    if need:
        for p, l in need.items():
            need[p] = sorted(l, key=lambda x: (farm.rabbits[x].block, farm.rabbits[x].box))

    return need

def average_age_rabbits(farm: Farm, sex):
    avg_age = 0

    for obj in farm.rabbits.values():
        if obj.sex == sex:
            avg_age += obj.age

    return round(avg_age / len([x for x in farm.rabbits.values() if x.sex == sex]))

def loose_nest(obj):
        obj.nest = None
        obj.status = 'mother*'
        for i in range(len(obj.history)-1, -1, -1):
            if isinstance(obj.history[i], list):
                obj.history[i] = 'LN'
                break