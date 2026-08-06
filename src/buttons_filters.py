import  flet as ft

BTN_SYNC = ft.IconButton(icon=ft.Icons.SYNC, tooltip='Синхронізувати з GoogleDisc', on_click=lambda e: print('Синхронізація...'))

BTN_SORT = ft.PopupMenuButton(
            icon=ft.Icons.SORT,
            tooltip='Сортування',
            items=[ft.PopupMenuItem(content=ft.Text('По імені'), data='by_name'),
                   ft.PopupMenuItem(content=ft.Text('По кліткам'), data='by_box'),
                   ft.PopupMenuItem(content=ft.Text('По віку (зростання)'), data='by_age_up'),
                   ft.PopupMenuItem(content=ft.Text('По віку (спадання)'), data='by_age_down'),
                   ft.PopupMenuItem(content=ft.Text('По рейтингу (зростання)'), data='by_rating_up'),
                   ft.PopupMenuItem(content=ft.Text('По рейтингу (спадання)'), data='by_rating_down')
                   ]
        )