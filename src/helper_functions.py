import flet as ft


from datetime import date
from bunny_classes import Bunny


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

def looking_for_work(rabbit: Bunny):
    today = date.today()
    if rabbit.all_planing_dates is not None:
        for work, dates in rabbit.all_planing_dates.items():
            if dates == today:
                return work
    return None

