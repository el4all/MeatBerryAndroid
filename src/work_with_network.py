import gspread
import pandas as pd
import numpy

kindle_url = 'https://docs.google.com/spreadsheets/d/1bghOnHANyqLeAKUbVX-SRjHMw4mFTD8LpN0I4dqARI4/edit?gid=0#gid=0'
palpation_url = 'https://docs.google.com/spreadsheets/d/1Nu4JlbhGVOEW1UNg9mCtW-C4rhTmNj0HZkjIAlqlLqo/edit?gid=0#gid=0'
planned_work_url = 'https://docs.google.com/spreadsheets/d/1lfR0wtolQfcJ6DCKm_H3l3WPJPX_t3V_UeEPuTkcgAw/edit?gid=2142952469#gid=2142952469'

def get_sheet_by_net(url, name_of_one_tab) -> pd.DataFrame:
    from_google = gspread.service_account('meatberry_farm_for_gspread.json')
    file = from_google.open_by_url(url)
    work_sheet = file.worksheet(name_of_one_tab)
    datas = work_sheet.get_all_values()
    df = pd.DataFrame(datas)

    return df

def change_sheet_for_kindle(df):
    df.columns = df.iloc[0]
    name_18 = ['N', 'cage', 'name', 'rating','total', 'alive', 'dead', 'formed',
                              'out_nest', 'to_3rd_room', 'repare']
    df = df.iloc[1:]
    df = df.reset_index(drop=True)
    df.columns = name_18
    df = df.replace("", numpy.nan)
    df = df.fillna(0)
    return df

def change_sheet_for_mate_and_palp(df):  # список імен - name_in_tab = [x for x in tab.loc[:, 'name']]

    df.columns = df.iloc[7]  # do raw 7 index (8 in nab) name columns
    df.columns.name = None
    df = df[8:]  # cut main tab that start from raw 8 index
    df = df.reset_index(drop=True)

    return df

if __name__ == "__main__":
    pass