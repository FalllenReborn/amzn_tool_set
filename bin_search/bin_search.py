#by Targosz Seweryn
#tseweryn@amazon.com
#
#place driver in same path as script file

import os
import PySimpleGUI as sg
import pandas as pd
from selenium.webdriver.common.keys import Keys
from main_tools.widget_grabers import GrabWidget
from main_tools.df_tools import GrabDataframe
from main_tools.selenium_scrap import GrabWeb


out, file_path = GrabWidget.get_path_list()
if file_path != '':
    df = GrabDataframe.get_df_excel(ex_path=file_path)
else:
    data = {'bin_id': []}
    df = pd.DataFrame.from_dict(data)
for bin_id in out:
    df.loc[len(df)] = bin_id
driver = GrabWeb.open_driver(GrabWidget.get_driver())

test_dict = {
    'floor': [],
    'pod_id': [],
    'target_bin_id': [],
    'pod_face': []
}


# get element with result table
is_rdy = driver.find_element('id', 'content_inner_container')

# get element with text area to which 'df' dataframe will be extracted
text_w = driver.find_element('id', 'adjacent_bins_textarea_input')

# get element with 'submit entries' button
btn = driver.find_element('id', 'btnGetInfo')

# variable to check if 100 rows is entered
i = 0

# create window to display progress bar
layout = [[sg.Text(f'Downloading {df.size} rows...')],
          [sg.ProgressBar(df.size, orientation='h', size=(20, 20), key='progressbar')],
          [sg.Cancel()]]
window = sg.Window(f'bin_search', layout)
progress_bar = window['progressbar']

for row in df['bin_id']:
    text_w.send_keys(row)
    text_w.send_keys(Keys.RETURN)
    event, values = window.read(timeout=10)

    # to fix
    if event == 'Cancel' or event == sg.WIN_CLOSED:
        break

    progress_bar.UpdateBar(i)

    i += 1
    if i % 100 == 0 or i == df.size:
        btn.click()
        while True:
            try:
                is_rdyy = is_rdy.find_elements('css selector', 'p')[1]
            except IndexError:
                continue
            break
        mytable = is_rdy.find_element('tag name', 'table')
        for row in mytable.find_elements('tag name', 'tr')[1:]:
            test_dict['floor'].append(row.find_elements('tag name', 'td')[1].text)
            test_dict['pod_id'].append(row.find_elements('tag name', 'td')[2].text)
            test_dict['target_bin_id'].append(row.find_elements('tag name', 'td')[3].text)
            test_dict['pod_face'].append(row.find_elements('tag name', 'td')[4].text)
        driver.find_element('id', 'adjacent_bins_textarea_input').clear()

df_result = pd.DataFrame.from_dict(test_dict)
df_result.to_excel('bin_search_result.xlsx', sheet_name='result', index=False)