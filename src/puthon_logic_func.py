from datetime import date

from bunny_classes import  Farm, Bunny


def looking_for_work(rabbit: Bunny):
    today = date.today()
    if rabbit.all_planing_dates is not None:
        for work, dates in rabbit.all_planing_dates.items():
            if dates == today:
                return work
    return None

def set_rabbit_culling(rabbit: Bunny):
    rabbit.status = 'culling'

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
