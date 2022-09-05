# by Targosz Seweryn
# tseweryn@amazon.com

import PySimpleGUI as sg


class GrabWidget:
    @staticmethod
    def get_path():
        layout = [[sg.Text('Chose feedback source')],
                  [sg.Text('Chose excel file ', size=(15, 1)), sg.InputText(), sg.FileBrowse()],
                  [sg.Submit(), sg.Cancel()]]
        window = sg.Window('mm_feedback', layout)
        event, values = window.read()
        window.close()
        file_path = values[0]
        return file_path

    @staticmethod
    def get_driver():
        layout = [[sg.Text('Chose feedback source')],
                  [sg.Listbox(['Firefox', 'Chrome'], no_scrollbar=True,  s=(15, 2))],
                  [sg.Submit(), sg.Cancel()]]
        window = sg.Window('Driver picker', layout)
        event, values = window.read()
        window.close()
        tool_box = ''.join(values[0])
        return tool_box

    @staticmethod
    def get_progress_bar(current_v, max_v):
        check_cancel = sg.one_line_progress_meter('mm_feedback', current_v, max_v, 'key', 'Optional message')
        return check_cancel

    @staticmethod
    def get_date_picker():
        layout = [[sg.Text('Select date range', key='-TXT-')],
                  [sg.Input(key='-IN-', size=(20, 1)),
                   sg.CalendarButton('Start date', close_when_date_chosen=True, target='-IN-', format='%Y-%m-%d',
                   no_titlebar=False, )],
                  [sg.Input(key='-IN2-', size=(20, 1)),
                   sg.CalendarButton('End date', close_when_date_chosen=True, target='-IN2-', format='%Y-%m-%d',
                   no_titlebar=False, )],
                  [sg.Submit(), sg.Cancel()]]
        window = sg.Window('mm_feedback', layout)
        event, values = window.read()
        window.close()
        start_date = values['-IN-']
        end_date = values['-IN2-']
        return start_date, end_date

    @staticmethod
    def get_launcher():
        layout = [[sg.Text('Chose script to run')],
                  [sg.Listbox(['mm_feedback', 'bin_search', 'arrm_scraper', 'kibana_scraper'],
                              no_scrollbar=True, s=(60, 12))],
                  [sg.Submit(), sg.Cancel()]]
        window = sg.Window('py_tool_set launcher', layout, size=(400, 300))
        event, values = window.read()
        window.close()
        ch_driver = ''.join(values[0])
        return ch_driver

    @staticmethod
    def get_path_list():
        layout = [[sg.Text('Enter bins in text window, or chose excel file to get data from, or both')],
                  [sg.Text('Enter bins you \nwish to locate:'), sg.Multiline(s=(60, 20))],
                  [sg.Text('Chose excel file ', size=(15, 1)), sg.InputText(), sg.FileBrowse()],
                  [sg.Submit(), sg.Cancel()]]
        window = sg.Window('bin_search_app', layout)
        event, values = window.read()
        window.close()
        bin_list = values[0]
        file_path = values[1]
        out = []
        buff = []
        for c in bin_list:
            if c == '\n':
                out.append(''.join(buff))
                buff = []
            else:
                buff.append(c)
        else:
            if buff:
                out.append(''.join(buff))
        return out, file_path
