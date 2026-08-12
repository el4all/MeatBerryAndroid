
import json
from datetime import datetime, date, timedelta
from loguru import logger

from work_with_files import open_and_read_json, write_json


STATUS_WORK = dict([('mate','запліднення'),('palpation','пальпація'),('kindling','окрол'),('install nest','монтаж гнізда'),
                    ('open nest',"відкривання гнізда"),('remove nest','демонтаж гнізда'),('resettle','переселення'),
                    ('vaccination nest','вакцинація гнізда'),('prepare nest','підготовка гнізда'),('swap box','перміщення')])
STATUS_FOR_STR = {'mated': 'очікує на пальпацію', 'waiting_for_kindling': 'очікує на окріл', 'mother': 'матір',
          'mated mother': 'запліднена матір', 'mother*': 'матір без гнізда', 'culling': 'вибраківка', None:'немає'}
DATE_FORMAT = '%d.%m.%Y'
DAYS = ['Понеділок',"Вівторок","Середа","Четвер","П'ятниця","Субота","Неділя"]


class Farm:
    def __init__(self, name='MeatBerry'):
        self.name = name
        self.rabbits: dict[str, Bunny] = {}
        self.third_room: dict[str, Box] = {}
        self.morgue = []
        self.defective = []

    @property
    def active(self):
        active_rabbits = []

        for bunny in self.rabbits.values():
            if bunny.birthday is not None and bunny.status != 'culling':
                active_rabbits.append(bunny.name)
        return active_rabbits

    @property
    def rating_list(self):
        return sorted(self.active, key=lambda x: self.rabbits[x].rating, reverse=True)

    def report_bunny(self, name):
        return (f'{self.rabbits[name]}\n'
                f'Місце в рейтингу {self.rating_list.index(name) + 1}')

    def add_bunny(self, bunny_obj):
        if isinstance(bunny_obj, Bunny):
            if bunny_obj.name not in self.rabbits:
                self.rabbits[bunny_obj.name] = bunny_obj
                bunny_obj.planing_mate()
                logger.info(f'{date.today().strftime(DATE_FORMAT)}: Bunny {bunny_obj.name} add in box {bunny_obj.block}.{bunny_obj.box}')
            else:
                logger.warning(f'Error. Bunny {bunny_obj.name} is already exist!!!')
        else:
            logger.error('Error. Wrong type object!!!')

    def set_defective(self, names):
        for name in names:
            self.rabbits[name].status = 'culling'
            self.defective.append(name)
            logger.info(f'{name} set as defective.')

    def remove_bunny_by_death(self, names: list):
        for name in names:
            if name in self.rabbits:
                old_box = self.rabbits[name].str_block_box
                self.morgue.append([name, self.rabbits[name].age, self.rabbits[name].history])
                del self.rabbits[name]
                if name in self.defective:
                    self.defective.remove(name)
                logger.info(f'{date.today().strftime(DATE_FORMAT)}: Bunny {name} deleted. Box {old_box} free.')
            else:
                if name in self.morgue:
                    logger.info(f'{name} is already died.')
                else:
                    logger.error(f'{name} not founded.')

    def remove_bunny_by_culling(self, name):
        if name in self.rabbits:
            old_box = self.rabbits[name].str_block_box
            del self.rabbits[name]
            if name in self.defective:
                self.defective.remove(name)
            logger.info(f'{date.today().strftime(DATE_FORMAT)}: Bunny {name} deleted. Box {old_box} free.')

    def mate(self,name_sheet, date_mate=None):
        if date_mate is None:
            date_mate = date.today()
        df = wwn.get_sheet_by_net(wwn.palpation_url, name_sheet)
        mate_tab = wwn.change_sheet_for_mate_and_palp(df)
        list_of_mated = [x for x in mate_tab.loc[:, "ім'я"]]
        for name in list_of_mated:
            father_tab = mate_tab.loc[mate_tab["ім'я"] == name, 'батько'].values[0]
            father = father_tab if father_tab in ['X', 'Y', 'Z','вибраковка'] else None
            if name in self.active:
                self.rabbits[name].get_mate(date_mate, father)
                if father is not None:
                    if father == 'вибраковка':
                        self.set_defective([name])
                    else:
                        logger.info(f'{date_mate.strftime(DATE_FORMAT)}: {name} was mated by {father}.' if father is not None else f'{date_mate.strftime(DATE_FORMAT)}: {name} not mated.')
                else:
                    next_try: date = self.find_next_dates('mate')
                    self.rabbits[name].all_planing_dates['mate'] = next_try
                    logger.info(f'{name} not mated. Next try {next_try.strftime(DATE_FORMAT)}.')

    def pre_palp_add_new_boxes(self, name_sheet):
        tab = wwn.get_sheet_by_net(wwn.palpation_url, name_sheet)
        final_tab = wwn.change_sheet_for_mate_and_palp(tab)
        need_list = []
        names = [x for x in final_tab.loc[:, "ім'я"]] # if final_tab.loc[final_tab["ім'я"] == x, 'батько'].values[0] in ['X', 'Y', 'Z']
        fathers = [x for x in final_tab.loc[:, "батько"]]
        for name, father in zip(names, fathers):
            need_list.append([self.rabbits[name].str_block_box] if father in ['X','Y','Z'] else [None])

        gs = gspread.service_account(filename='meatberry_farm_for_gspread.json')
        sheet = gs.open_by_key('1Nu4JlbhGVOEW1UNg9mCtW-C4rhTmNj0HZkjIAlqlLqo')
        worksheet = sheet.worksheet(name_sheet)
        worksheet.update(need_list, 'I9')

    def palpation(self, name_sheet, date_palp): # results = [(name, res)]
        if date_palp is None:
            date_palp = date.today()
        df = wwn.get_sheet_by_net(wwn.palpation_url, name_sheet)
        mate_tab = wwn.change_sheet_for_mate_and_palp(df)
        list_of_mated = [x for x in mate_tab.loc[:, "ім'я"] if mate_tab.loc[mate_tab["ім'я"] == x, 'батько'].values[0] in ['X', 'Y', 'Z']]
        print(len(list_of_mated), list_of_mated)
        for name in list_of_mated:
            res = mate_tab.loc[mate_tab["ім'я"] == name, 'результат'].values[0].strip()
            if name in self.active:
                self.rabbits[name].get_palpation(res, date_palp)

    def kindling(self, name_sheet, date_kindling):
        url = wwn.kindle_url
        sheet = wwn.get_sheet_by_net(url, name_sheet)
        df = wwn.change_sheet_for_kindle(sheet)
        all_names = [x for x in df.loc[:, 'name'] if x]
        for name in all_names:
            try:
                total = int(df.loc[df['name'] == name, 'total'].values[0])
                alive = int(df.loc[df['name'] == name, 'alive'].values[0])
                dead = int(df.loc[df['name'] == name, 'dead'].values[0])
                formed = int(df.loc[df['name'] == name, 'formed'].values[0])
                self.rabbits[name].get_kindling(total, alive, dead, formed, date_kindling)

                logger.info(f'{date_kindling.strftime(DATE_FORMAT)}: {name}: Birth {alive} + {dead}. Formed {formed}.')
            except KeyError:
                logger.error(f"{name} not found.")

    def move_to_3rd_room_meat(self, block, box, quantity, birth):
        cage = Box(block, box, quantity, birth)
        self.third_room[f'{block}.{box}'] = cage

        logger.info(f'{quantity} bunnies move to {block}.{box}')

    def change_box(self, name, to_box:str):
        old_block = self.rabbits[name].block
        old_box = self.rabbits[name].box
        new_block = int(to_box.split('.')[0])
        new_box = int(to_box.split('.')[1])
        name_in_new_box = ''
        for n, obj in self.rabbits.items():
            if obj.block == new_block and obj.box == new_box:
                name_in_new_box = n
                obj.block = old_block
                obj.box = old_box
                break
        self.rabbits[name].block = new_block
        self.rabbits[name].box = new_box

        logger.info(f'{name} stay in {to_box} box.') if name == name_in_new_box else logger.info(f'{name} move to {to_box} box.')

    def swap_box(self,from_box:str, to_box:str):
        name_in_from = None
        name_in_to = None
        old_block = int(from_box.split('.')[0])
        old_box = int(from_box.split('.')[1])
        new_block = int(to_box.split('.')[0])
        new_box = int(to_box.split('.')[1])
        for n, obj in self.rabbits.items():
            if obj.block == old_block and obj.box == old_box:
                name_in_from = n
            elif obj.block == new_block and obj.box == new_box:
                name_in_to = n
            if name_in_from and name_in_to :
                break
        if name_in_from and name_in_to:
            self.rabbits[name_in_from].block, self.rabbits[name_in_to].block = new_block, old_block
            self.rabbits[name_in_from].box, self.rabbits[name_in_to].box = new_box, old_box
            logger.info(f'{name_in_from} -> {to_box}  '
                f'{name_in_to} -> {from_box}  ')
        elif name_in_to is None:
            self.rabbits[name_in_from].box = new_box
            logger.info(f'{name_in_from} -> {to_box}  '
                  f'{from_box} is empty.')

    def who_in_box(self, block, box):
        for obj in self.rabbits.values():
            if obj.block == block and obj.box == box:
                return obj.name
        return 'порожньо'

    def get_wrote_rating(self):

        elements = []
        elements_per = []
        non_kindling = []
        for name, obj in self.rabbits.items():
            if len(self.rabbits[name].history) > 0 and name not in self.defective:
                id_bunny = name
                rating_per = self.rabbits[name].rating / len(self.rabbits[name].history)
                ratings = self.rabbits[name].rating
                elements.append([id_bunny, ratings])
                elements_per.append([id_bunny, rating_per])
            if len(self.rabbits[name].history) == 0 or self.rabbits[name].history is None:
                non_kindling.append([name, self.rabbits[name].age if self.rabbits[name].age else None,
                                     self.rabbits[name].history])

        rating_list = sorted(elements, key=lambda x: x[1], reverse=True)
        rating_per = sorted(elements_per, key=lambda x: x[1], reverse=True)
        final_report = []
        report_per_one = []
        for el in rating_list:
            rating = round(el[1], 3)
            report = (
                f'{rating_list.index(el) + 1}. {el[0]} {"+" + str(rating) if rating > 0 else rating} by {len(self.rabbits[el[0]].history)},'
                f' tried. Age {self.rabbits[el[0]].age_in_month}  {self.rabbits[el[0]].history[-7:]}. {'незадіяна' if self.rabbits[el[0]].status is None else STATUS_FOR_STR[self.rabbits[el[0]].status]}, '
                f'{str(self.rabbits[el[0]].nest.nest_age) + "дн." if self.rabbits[el[0]].status in ['mother', 'mated mother'] else ""}')
            final_report.append(report)
        for i in rating_per:
            rating = round(i[1], 3)
            report = (
                f'{rating_per.index(i) + 1}. {i[0]} {"+" + str(rating) if rating > 0 else rating} per try. Total try mate '
                f'{len(self.rabbits[i[0]].history)}. Age {self.rabbits[i[0]].age_in_month}. {self.rabbits[i[0]].history}')
            report_per_one.append(report)

        write_json('Ratings_by_sum.json', final_report)
        write_json('Ratings_per_kindling.json', report_per_one)
        write_json('RNon_mate.json', non_kindling)

    def mated_for_bunnies(self, need_date, sheet_name):
        c = 1
        rating_list = sorted(self.rabbits, key=lambda x: self.rabbits[x].rating, reverse=True)
        artificial = []
        none_status_x = []
        none_status_minus = []
        new = []

        for name, obj in self.rabbits.items():
            if obj.birthday is not None and name not in self.defective:
                if obj.status in ['mother', 'mother*'] and obj.all_planing_dates.get('mate') <= need_date:
                    artificial.append([name, obj.str_block_box, 'шт.', rating_list.index(name) + 1, obj.age_in_month])
                elif obj.status is None and obj.all_planing_dates.get('mate') <= need_date:
                    if not obj.history and obj.all_planing_dates.get('mate') <= need_date:
                        new.append([name, obj.str_block_box, 'new', 0, obj.age_in_month])
                    elif obj.history[-1] == 'X':
                        none_status_x.append([name, obj.str_block_box, obj.history[-1], rating_list.index(name) + 1, obj.age_in_month])
                    elif obj.history[-1] == '-':
                        none_status_minus.append([name, obj.str_block_box, obj.history[-1], rating_list.index(name) + 1, obj.age_in_month])

        list_1 = sorted(artificial, key=lambda x: (int(x[1].split('.')[0]), int(x[1].split('.')[1])))
        list_2 = sorted(none_status_x, key=lambda x: (int(x[1].split('.')[0]), int(x[1].split('.')[1])))
        list_3 = sorted(none_status_minus, key=lambda x: (int(x[1].split('.')[0]), int(x[1].split('.')[1])))
        list_4 = sorted(new, key=lambda x: (int(x[1].split('.')[0]), int(x[1].split('.')[1])))
        final = [*list_1, *list_2, *list_3, *list_4]
        for el in final:
            el.insert(0, c)
            c += 1

        to_fill = csap.prepare_data_to_fill_tab(final)
        csap.create_and_publish(to_fill, sheet_name)
        print('Done!!!')

    def find_min_max_dates(self, func, process):
        dates = []
        for obj in self.rabbits.values():
            day = obj.all_planing_dates.get(process)
            if day is not None and day not in dates:
                dates.append(day)

        return func(dates)

    def find_next_dates(self, process):
        dates = []
        for obj in self.rabbits.values():
            day = obj.all_planing_dates.get(process)
            if day is not None and day not in dates:
                dates.append(day)

        return sorted(dates)[1]

    def empty_boxes(self):
        len_block = {1:20, 2:20, 3:20, 4:20, 5:20, 6:25, 7:20, 8:20, 9:20, 10:20, 11:12, 12:12}
        all_blocks = {}
        free = []
        more_then_one =[]
        for obj in self.rabbits.values():
            all_blocks.setdefault(obj.block, []).append(obj.box)

        for block, box in all_blocks.items():
            empty = set(range(1, len_block[block] + 1)) - set(box)
            if empty:
                free.append(f'{block}.{[x for x in empty]}')
            once = []
            duplicates = []
            for el in box:
                if el in once:
                    duplicates.append(el)
                else:
                    once.append(el)
                if duplicates:
                    more_then_one.append(f'{block}.{[x for x in duplicates]}')

        return f'Free {free},\n More then one {more_then_one}'

    def vacant_indexes(self, line):
        indexes = []
        for x in self.rabbits.keys():
            if len(x) > 2:
                name = x[:2]
                num = int(x[2:])
                if name == line:
                    indexes.append(num)
        # if indexes:
        #     free = []
        #     for i in range(1, len(indexes)):
        #         if i not in indexes:
        #             free.append(i)
        #     return str(free[0]) if free else str(max(indexes) + 1)
        return indexes

    def planned_work(self, start_date_planed:date, end_date_planed:date):
        c = 1
        work = {}
        new = {}
        name_file = f'PLANNED_SORT {start_date_planed.day}.{start_date_planed.month} - {end_date_planed.day}.{end_date_planed.month}.{end_date_planed.year}.json'
        while start_date_planed < end_date_planed:
            for name, obj in self.rabbits.items():
                obj: Bunny
                if name in self.active:
                    for process, dates in obj.all_planing_dates.items():
                        if obj.all_planing_dates and dates == start_date_planed:
                            work.setdefault(f'{dates.strftime(DATE_FORMAT)}, {DAYS[dates.weekday()]}', []).append([name, obj.str_block_box, STATUS_WORK[process], self.rating_list.index(name) + 1])

            start_date_planed += timedelta(days=1)

        for k, v in work.items():
            new[k] = sorted(v, key=lambda x: (x[2], self.rabbits[x[0]].block, self.rabbits[x[0]].box))

        for el in new.values():
            for i in el:
                i.insert(0, c)
                c += 1

        write_json(name_file, new)

    def planned_work_sheet(self, start, end):
        pass

    def save_to_json(self, file_name='MeatBerryFarm.json'):
        export_data = {
            'farm_name': self.name,
            'rabbits': {},
            'third_room': {},
            'morgue': self.morgue,
            'defective': self.defective
        }
        for name, bunny_obj in self.rabbits.items():
            export_data['rabbits'][name] = bunny_obj.to_dict()
        for box_num, box_obj in self.third_room.items():
            export_data['third_room'][box_num] = box_obj.to_dict()

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=4)
            print('Data saved.')

    def load_from_json(self, file_name='MeatBerryFarm_for_tests.json'):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                farm_dict = json.load(f)
                self.name = farm_dict.get('farm_name', self.name)
                self.rabbits = {}
                self.third_room = {}
                self.morgue = farm_dict.get('morgue', [])
                self.defective = farm_dict.get('defective', [])
                raw_rabbits = farm_dict.get('rabbits', {})
                raw_boxes = farm_dict.get('third_room', {})

                for name, obj_dict in raw_rabbits.items():
                    new_bunny = Bunny(**obj_dict)
                    self.rabbits[name] = new_bunny
                print(f'{len(self.rabbits)} loaded.')
                for box_num, box_dict in raw_boxes.items():
                    new_box = Box(**box_dict)
                    self.third_room[box_num] = new_box
                print(f'{len(self.third_room)} loaded.')

        except FileNotFoundError:
            print('File not found. Stat new farm.')

    def load_from_network(self, farm_dict):
        if farm_dict:
            self.name = farm_dict.get('farm_name', self.name)
            self.rabbits = {}
            self.third_room = {}
            self.morgue = farm_dict.get('morgue', [])
            self.defective = farm_dict.get('defective', [])
            raw_rabbits = farm_dict.get('rabbits', {})
            raw_boxes = farm_dict.get('third_room', {})

            for name, obj_dict in raw_rabbits.items():
                new_bunny = Bunny(**obj_dict)
                self.rabbits[name] = new_bunny
            print(f'{len(self.rabbits)} loaded.')
            for box_num, box_dict in raw_boxes.items():
                new_box = Box(**box_dict)
                self.third_room[box_num] = new_box
            print(f'{len(self.third_room)} loaded.')
        else:
            print('Not founded')

class Bunny:
    def __init__(self, name, birthday,  box, status=None, **kwargs):

        self.name = name   # ID bunny

        self.block = kwargs.get('block')

        self.box = box

        self.birthday = birthday

        self.status = status

        def parse_date(value):
            if isinstance(value, str):
                return datetime.strptime(value, DATE_FORMAT).date()
            return value

        self.last_mate = parse_date(kwargs.get('last_mate'))

        self.last_palpation = parse_date(kwargs.get('last_palpation'))

        self.last_kindling = parse_date(kwargs.get('last_kindling'))

        def restore_dict_all_dates(from_json_dict):
            if not from_json_dict:
                return {}
            return {k: datetime.strptime(v, DATE_FORMAT).date() if isinstance(v, str) else v for k, v in from_json_dict.items()}

        def restore_dict(from_json_dict):
            if not from_json_dict:
                return {}
            return {datetime.strptime(k, DATE_FORMAT).date() if isinstance(k, str) else k:v for k, v in from_json_dict.items()}

        self.all_planing_dates = restore_dict_all_dates(kwargs.get('all_planing_dates'))  # ['mate', 'palpation', 'kindling', 'install/open/remove nest', 'resettle']

        self.mate = restore_dict(kwargs.get('mate'))       # dict_structure {data_of_mate: {'line_father': line_father, 'result': result}}

        self.palpation = restore_dict(kwargs.get('palpation'))   # dict_structure {data_of_palpation: {result: status}} . status is 'waiting', 'positive' or 'negative'

        self.kindling = restore_dict(kwargs.get('kindling'))    # dict_structure {data_of_kindling: quantity: (total, alive, dead)}

        self.history = kwargs.get('history', [])

        self.nest_archive = kwargs.get('nest_archive')

        self.nest: Nest | None = None

        from_json_nest = kwargs.get('nest')
        if from_json_nest:
            self.nest = Nest(**from_json_nest)


    def __str__(self):
        kindling = len(self.kindling)
        alive = sum(v[1] for v in self.kindling.values())
        dead = sum(v[2] for v in self.kindling.values())
        formed = 0
        resettle = 0
        for x in self.history:
            if isinstance(x, list) and isinstance(x[-1], int):
                resettle += x[-1]
                formed += x[2]


        return (f'Кролиця {self.name}, клітка {self.str_block_box}:\n'
                f'Дата народження {self.birthday},\n'
                f'Вік - {self.age_in_month},\n'
                f'Статус - {STATUS_FOR_STR[self.status]},\n'
                f'Кількість окролів - {kindling},\n'
                f'Народжено {alive} живих, {dead} мертвих,\n'
                f'Переселено {round(resettle/formed if formed!=0 else 0, 3)*100} %\n'
                f'Історія - {self.history}')

    @property
    def age(self):         # age in 'days'
        today = date.today()

        return (today - datetime.strptime(self.birthday, DATE_FORMAT).date()).days if self.birthday is not None else None

    @property
    def age_in_month(self):
        birth = datetime.strptime(self.birthday, DATE_FORMAT).date()
        today = date.today()
        days = (today - birth).days
        years = days // 365
        month = round(days / 30.42) if not years else round(days % 365 / 30.42)

        return f'{years} p. {int(month)} м.'

    @property
    def str_block_box(self):
        return f'{self.block}.{self.box}'

    @property
    def rating(self):
        if not self.history:
            return 0
        diapason = self.history if len(self.history) <= 7 else self.history[-7:]
        quantity_birth = 0
        good_mother = 0
        for x in diapason:
            if isinstance(x, list) :
                quantity_birth += x[0] * 0.125
                good_mother += round(x[3] / x[2], 2) if x[2] != 0 and isinstance(x[3], int) else 0
        if len(diapason) == 1:
            fertility = 0
            if diapason == ['-']:
                fertility = -0.5
            elif diapason == ['X']:
                fertility = -0.3
            return quantity_birth + good_mother + fertility
        shifted = iter(diapason)
        next(shifted)
        count_minus = 0
        count_xx = 0
        count_plus = len([i for i in diapason if isinstance(i, list)])
        for el, next_el in zip(diapason, shifted):
            if el == '-' and next_el == '-':
                count_minus += 1
            elif el == "X" and next_el == 'X':
                count_xx += 1
            elif isinstance(el, list) and isinstance(next_el, list):
                count_plus += 1
        fertility = count_plus - count_minus * 0.5 - count_xx * 0.3

        return quantity_birth + good_mother + fertility

    def planing_mate(self)-> object:
        # if first time - (date = birthdate + 128 days), if not - (date = day_of_negative_palpation + 3 day) or (day_of_kindling + 19 days)
        mate_day = None        # Тут треба доробити логіку, якщо пальпація позитивна. Мабуть, треба дату з функції, котра буде відмічати окрол.
        if not self.mate:
            mate_day = datetime.strptime(self.birthday, DATE_FORMAT).date() + timedelta(days=128)
        else:
            if not self.palpation:

                return None
            else:
                if self.last_palpation is None:
                    pass
                else:
                    if self.palpation[self.last_palpation].get('result') == 'negative':
                        mate_day = self.last_palpation + timedelta(days=3)


                    elif self.palpation[self.last_palpation].get('result') == 'positive':
                        mate_day = self.last_kindling + timedelta(days=19)


        self.all_planing_dates['mate'] = mate_day
        return mate_day

    def get_mate(self, date_mate=None, father=None):
        today = date.today()
        if date_mate is None:
            date_mate = today
        if father is not None and father in ['X','Y','Z']:
            date_mate_obj = datetime.strptime(date_mate, DATE_FORMAT).date() if isinstance(date_mate, str) else date_mate
            self.mate.setdefault(date_mate_obj, {})['father_line'] = father
            self.mate.setdefault(date_mate_obj, {})['result'] = '?'
            self.status = 'mated mother' if self.status == 'mother' else 'mated'
            self.last_mate = date_mate_obj
            self.all_planing_dates.pop('mate', None)
            self.planing_palpation()
            return True
        else:
            self.history.append('X')
            self.status = None

            return False

    def planing_palpation(self)-> date:
        palpation_day = self.last_mate + timedelta(days=10)
        self.all_planing_dates['palpation'] = palpation_day

        return palpation_day

    def get_palpation(self, result, palp_date=None):
        if palp_date is None:
            palp_date = date.today()
        if result == '-':
            self.palpation.setdefault(palp_date, {})['result'] = 'negative'
            self.mate.setdefault(self.last_mate, {})['result'] = 'negative'
            self.history.append('-')
            self.last_palpation = datetime.strptime(palp_date, DATE_FORMAT).date() if isinstance(palp_date, str) else palp_date
            self.status = self.status if self.status in ['mother','mother*'] else None
            self.all_planing_dates.pop('palpation')
            self.planing_mate()
            logger.info(f'{palp_date}: {self.name} palpation result -')
            return False
        elif result == '+':
            self.palpation.setdefault(palp_date, {})['result'] = 'positive'
            self.mate.setdefault(self.last_mate, {})['result'] = 'positive'
            self.history.append('+')
            self.last_palpation = datetime.strptime(palp_date, DATE_FORMAT).date() if isinstance(palp_date, str) else palp_date
            self.status = 'waiting_for_kindling'
            self.all_planing_dates.pop('palpation')
            father = self.mate[[x for x in self.mate][-1]].get('father_line')
            self.nest = Nest(mother=self.name, father=father)
            self.planing_kindling()

            logger.info(f'{palp_date}: {self.name} palpation result +')
            return True
        else:
            print(f'{self.name} not palpated.')
            return None

    def planing_kindling(self)-> date:
        kindling_date = self.last_mate + timedelta(days=31)
        self.all_planing_dates['kindling'] = kindling_date
        self.all_planing_dates['swap box'] = kindling_date - timedelta(days=9)
        self.all_planing_dates['install nest'] = self.nest.planning_date_for_install_and_prepare_nest(kindling_date)[0]
        self.all_planing_dates['prepare nest'] = self.nest.planning_date_for_install_and_prepare_nest(kindling_date)[1]

        return kindling_date

    def get_kindling(self, total, alive, dead, formed, kind_date=None):
        if kind_date is None:
            kind_date = date.today()
        self.kindling[datetime.strptime(kind_date, DATE_FORMAT).date() if isinstance(kind_date, str) else kind_date] = (total, alive, dead)
        self.last_kindling = datetime.strptime(kind_date, DATE_FORMAT).date() if isinstance(kind_date, str) else kind_date
        self.history[-1] = [alive, dead, formed, '?'] if self.history[-1] == '+' else self.history.append([alive, dead, formed, '?'])
        self.status = 'mother' if formed else 'mother*'
        self.all_planing_dates.pop('kindling', None)
        self.all_planing_dates.pop('install nest', None)
        self.all_planing_dates.pop('prepare nest', None)
        if formed:
            father = self.mate[[x for x in self.mate][-1]].get('father_line')
            self.nest = Nest(mother=self.name, father=father)
            self.nest.date_birth = kind_date
            self.planning_resettle()
            dates = self.nest.planning_open_and_remove_nest_vaccination(datetime.strptime(kind_date, DATE_FORMAT).date() if isinstance(kind_date, str) else kind_date)
            self.all_planing_dates['open nest'] = dates[0]
            self.all_planing_dates['remove nest'] = dates[1]
            self.all_planing_dates['vaccination nest'] = dates[2]
            self.nest.formed_nest(formed)
            logger.info(f'{self.name}: kindling {total}, alive {alive}, dead {dead}. Formed {formed}.')
        else:
            self.nest = None
            logger.info(f'{self.name}: kindling {total}, alive {alive}, dead {dead}. Not formed..')
        self.planing_mate()


    def planning_resettle(self):
        resettle_day = self.last_kindling + timedelta(days=35)
        self.all_planing_dates['resettle'] = resettle_day

        return resettle_day

    def get_resettle_bunnies(self, resettle_date=None, bunnies=None, new_cage=None):
        date_resettle = resettle_date.strftime(DATE_FORMAT) if resettle_date is not None else date.today().strftime(DATE_FORMAT)
        quantity = bunnies if bunnies is not None else self.nest.get_resettle_nest(new_cage)
        self.history[-2][3] = quantity
        percent = quantity / self.nest.bunnies.get('formed') * 100 if quantity else 0

        report = {
            'date': date_resettle,
            'quantity': quantity,
            'percentage_of_nest': round(percent, 2),
            'move_to': new_cage
        }
        if self.nest_archive is None:
            self.nest_archive = []
        self.nest_archive.append(report)
        print(f'{quantity} bunnies moved to box {new_cage}.')
        self.all_planing_dates.pop('resettle', None)
        self.all_planing_dates.pop('open nest', None)
        self.all_planing_dates.pop('remove nest', None)
        self.nest = None
        self.status = None if self.status in ['mother', 'mother*'] else self.status

    def to_dict(self):
        data = self.__dict__.copy()

        data['birthday'] = self.birthday
        if self.last_mate:
            data['last_mate'] = self.last_mate.strftime(DATE_FORMAT)
        if self.last_palpation:
            data['last_palpation'] = self.last_palpation.strftime(DATE_FORMAT)
        if self.last_kindling:
            data['last_kindling'] = self.last_kindling.strftime(DATE_FORMAT)

        data['mate'] = {k.strftime(DATE_FORMAT) if isinstance(k, date) else k: v for k, v in self.mate.items()}
        data['palpation'] = {k.strftime(DATE_FORMAT) if isinstance(k, date) else k: v for k, v in self.palpation.items()}
        data['kindling'] = {k.strftime(DATE_FORMAT) if isinstance(k, date) else k: v for k, v in self.kindling.items()}
        data['all_planing_dates'] = {k: v.strftime(DATE_FORMAT) if isinstance(v, date) else v for k, v in self.all_planing_dates.items()}

        if self.nest is not None:
            data['nest'] = self.nest.to_dict()
        else:
            data['nest'] = None

        return data

class Nest:
    def __init__(self, **kwargs):
        self.mother = kwargs.get('mother')
        self.father = kwargs.get('father')
        self.status = kwargs.get('status')
        self.bunnies = kwargs.get('bunnies', {})
        self.output_cage = kwargs.get('output_cage')
        def parse_date(value):
            if isinstance(value, str):
                return datetime.strptime(value, DATE_FORMAT).date()
            return value
        self.date_birth = parse_date(kwargs.get('date_birth'))
        self.date_install = parse_date(kwargs.get('date_install'))
        self.date_open = parse_date(kwargs.get('date_open'))
        self.date_remove = parse_date(kwargs.get('date_remove'))

    def __str__(self):
        return (f'Mother {self.mother}, father {self.father}.'
                f' {self.nest_age}. Status - {self.status}'
                f'{self.bunnies}.')

    @property
    def nest_age(self):
        return (date.today() - self.date_birth).days if self.date_birth is not None else None

    def planning_date_for_install_and_prepare_nest(self, date_of_kindling):
        date_install = date_of_kindling - timedelta(days=7)
        date_prepare = date_of_kindling - timedelta(days=1)
        return date_install, date_prepare

    def planning_open_and_remove_nest_vaccination(self, date_kind):
        open_date = date_kind + timedelta(days=10)
        remove_date = date_kind + timedelta(days=20)
        vaccination_date = date_kind + timedelta(days=28)

        return open_date, remove_date, vaccination_date

    def clear_dates_for_nest(self):
        self.date_install = None
        self.date_open = None
        self.date_remove = None

    def install_nest(self, install=None):
        if install is None:
            install = date.today()
        self.status = 'install'
        self.bunnies = dict([('formed', 0), ('alive', 0)])
        self.date_install = install

    def formed_nest(self, formed):

        self.status = 'close'
        self.bunnies['formed'] = formed
        self.bunnies['alive'] = formed

    def fill_nest(self, alive=0, dead=0):
         if self.bunnies.get('alive') is not None:
             self.bunnies['alive'] += alive
         if self.bunnies.get('dead') is not None:
             self.bunnies['dead'] += dead
             self.bunnies['alive'] -= dead

         self.bunnies['alive'] = alive

    def open_nest(self, opened=None):
        if opened is None:
            opened = date.today()
        self.status = 'open'

    def remove_nest(self, remove=None):
        if remove is None:
            remove = date.today()
        self.status = 'remove'
        self.clear_dates_for_nest()
        self.date_remove = remove

    def get_resettle_nest(self, block=None, box=None):
        quantity = self.bunnies.get('alive', 0)
        self.output_cage = f'{block}.{box}'

        return quantity

    def to_dict(self):
        export_data = {
            'mother': self.mother,
            'father': self.father,
            'status': self.status,
            'bunnies': self.bunnies,
            'date_birth': self.date_birth.strftime(DATE_FORMAT) if isinstance(self.date_birth,date) else self.date_birth,
            'date_install': self.date_install.strftime(DATE_FORMAT) if isinstance(self.date_install, date) else self.date_install,
            'date_open': self.date_open.strftime(DATE_FORMAT) if isinstance(self.date_open, date) else self.date_open,
            'date_remove': self.date_remove.strftime(DATE_FORMAT) if isinstance(self.date_remove, date) else self.date_remove,
            'output_cage': self.output_cage
        }

        return export_data


class Box:
    def __init__(self, block, box, quantity, birth, mother=None, father=None,  kill_date=None):
        self.block = block
        self.box = box
        self.quantity = quantity
        self.birth: date = birth if isinstance(birth, date) else datetime.strptime(birth, DATE_FORMAT).date()
        self.mother = mother
        self.father = father
        self.kill_date: date = kill_date

    def __str__(self):
        return ''

    @classmethod
    def from_dict_box(cls, data: dict):
        block = data['block']
        box = data['box']
        mother = data['mother']
        father = data['father']
        quantity = data['quantity']
        birth = datetime.strptime(data['birth'], DATE_FORMAT).date()
        kill_date = datetime.strptime(data['kill_date'], DATE_FORMAT).date()

        cage = cls(block=block, box=box, quantity=quantity, birth=birth, mother=mother, father=father, kill_date=kill_date)

        return cage

    def to_dict(self):
        data = self.__dict__.copy()

        data['birth'] = self.birth.strftime(DATE_FORMAT) if isinstance(data['birth'], date) else data['birth']
        data['kill_date'] = self.kill_date.strftime(DATE_FORMAT) if isinstance(data['kill_date'], date) else data['kill_date']
        return data

    def set_kill_date(self):
        date_of_kill = self.birth + timedelta(days=100)
        self.kill_date = date_of_kill