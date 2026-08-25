from datetime import date, datetime, timedelta

from bunny_classes import  Farm, Bunny

BOXES = dict([(1,[x for x in range(1,21)]),(2,[x for x in range(1,21)]),(3,[x for x in range(1,21)]),(4,[x for x in range(1,21)]),
              (5,[x for x in range(1,21)]),(6,[x for x in range(1,26)]),(7,[x for x in range(1,21)]),(8,[x for x in range(1,21)]),
              (9,[x for x in range(1,21)]),(10,[x for x in range(1,21)]),(11,[x for x in range(1,13)]),(12,[x for x in range(1,13)])])

def looking_for_work(rabbit: Bunny):
    today = date.today()
    if rabbit.all_planing_dates is not None:
        for work, dates in rabbit.all_planing_dates.items():
            if dates == today:
                return work
    return None

def set_rabbit_culling(farm: Farm, rabbit: Bunny):
    rabbit.status = 'culling'
    farm.defective.append(rabbit.name)

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