import PySimpleGUI as sg
from threading import Thread
import webbrowser
import os.path
import pandas as pd
import codes


def setup(theme='DarkAmber'):
    """
    define the theme and fonts of the PySimpleGUI windows.
    :param theme: string of a theme.
    :return: fonts (headline, regular, warning and button).
    """
    sg.theme(theme)

    headline_font = ('Arial bold', 20)
    font = ('Arial', 20)
    warning_font = ('Arial bold', 14)
    button_font = ('Arial', 14)

    return headline_font, font, warning_font, button_font


def read_registration_table():
    """
    The load registration table window. Asking from user to load the .xslx file
    :return: full_file_name, file_name, registered_number, registered_id_set, registered_name_set, df
    """
    layout = [[sg.Text('Enter the event registration table:')],
              [sg.Input(sg.user_settings_get_entry('-filename-', ''), key='-IN-'), sg.FileBrowse()],
              [sg.Text('.xlsx file with the header: Barcode #, First Name, Last Name, Job Title, Company')],
              [sg.B('Continue'), sg.B('Create QR codes'), sg.B('Exit', key='Exit')]]

    window = sg.Window("TAU Engineering Alumni Registering and Sticker Printing System", layout)

    file_name = ''
    registered_number = 0
    registered_id_set = set()
    registered_name_set = set()
    df = None

    # Create an event loop
    while True:
        event, values = window.read()
        full_file_name = values['-IN-']

        if event == 'Continue':
            if os.path.exists(full_file_name):
                df = pd.read_excel(full_file_name)
                registered_number = len(df)
                if not {'Barcode #', 'First Name', 'Last Name', 'Job Title', 'Company'}.issubset(set(df.columns)):
                    sg.popup('The following header of the excel file does not contain the following features:',
                             'Barcode #, First Name, Last Name, Job Title and Company',
                             'Please make sure the first row in the table containing these columns titles')
                    continue
                registered_id_set = set(df['Barcode #'])
                registered_name_set = set(df['First Name'] + ' ' + df['Last Name'])
                # file_path = os.path.dirname(full_file_name) + '/'
                file_name = os.path.splitext(full_file_name)[0] + ' '
            else:
                sg.popup('File does not exist!', 'No registration table')
                full_file_name = file_name = ''
                # file_path = ''
            break

        if event == 'Create QR codes':
            if os.path.exists(full_file_name):
                df = pd.read_excel(full_file_name)
                registered_number = len(df)
                try:
                    registered_id_set = set(df['Barcode #'])
                except ValueError:
                    sg.popup('The following header of the excel file does not contain the id feature!')
                    continue
                file_path = os.path.dirname(full_file_name) + '/'
                file_name = os.path.splitext(full_file_name)[0] + ' '
            else:
                sg.popup('File does not exist!', 'Can not create QR codes!')
                continue
            folder_path = file_path + 'codes/'
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
            sg.popup_timed('Creating QR codes...', button_type=5)
            for reg_id in registered_id_set:
                codes.create_qr(folder_path, str(reg_id))
            sg.popup_timed('Done!', button_type=5)

        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks Exit
            exit(0)

    window.close()

    return full_file_name, file_name, registered_number, registered_id_set, registered_name_set, df


def about():
    """
    The about (info) window. Showing the basic and development info with external links.
    """
    url = 'https://engineering.tau.ac.il/tauengalumni'
    source_url = 'https://github.com/EranPer/tauengalumni'

    layout = [[sg.Text('TAU Engineering Alumni Registering and Sticker Printing System.')],
              [sg.Text('Made by Eran Perelman. 2021')],
              [sg.Text('TAU Engineering Alumni Website',
                       enable_events=True, key='-LINK-', font=('Arial underline', 11))],
              [sg.Text('Source Code',
                       enable_events=True, key='-SOURCE_CODE-', font=('Arial underline', 11))],
              [sg.B('Ok')]]

    window = sg.Window("TAU Engineering Alumni Registering and Sticker Printing System", layout)

    while True:
        event, values = window.read()
        if event == '-LINK-':
            webbrowser.open(url)
        if event == '-SOURCE_CODE-':
            webbrowser.open(source_url)
        if event == 'Ok':
            break

    window.close()


def registered_guest(win_title, msg, font, button_font, n_current_find=1, n_names=1):
    """
    The registered guest window, showing the info of the current guest.
    :param win_title: the title of the window.
    :param msg: the text to display.
    :param font: the font of the text.
    :param button_font: the font of the button.
    :param n_current_find: the number of the current guest for multiple guests sharing the same name or the same string.
    :param n_names: the total number of guests sharing the same name or the same string.
    :return: the event.
    """
    if n_names > 1:
        title = [sg.Text(str(n_current_find) + '/' + str(n_names), font=font)]
        if n_current_find < n_names:
            last_button = 'Next'
        else:
            last_button = 'Cancel'
    else:
        title = ''
        last_button = 'Cancel'

    layout = [title,
              [sg.Text(msg, font=font)],
              [sg.Button('Confirm and Print', font=button_font),
               sg.Button('Confirm only', font=button_font),
               sg.Button(last_button, font=button_font)]]
    window = sg.Window(win_title, layout, modal=True, grab_anywhere=True, enable_close_attempted_event=True)
    event, value = window.read()
    if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == 'Next':
        event = "Cancel"
    window.close()
    return event


def double_registered_guest(win_title, msg, warning, font, warning_font, button_font, n_current_find=1, n_names=1):
    """
    The double registration attempt window, showing the info of the current guest who signed into the system before.
    :param win_title: the title of the window.
    :param msg: the text to display.
    :param warning: the warning text to display (already signed warning).
    :param font: the font of the text.
    :param warning_font: the font of the warning.
    :param button_font: the font of the button.
    :param n_current_find: the number of the current guest for multiple guests sharing the same name or the same string.
    :param n_names: the total number of guests sharing the same name or the same string.
    :return: the event.
    """
    if n_names > 1:
        title = [sg.Text(str(n_current_find) + '/' + str(n_names), font=font)]
        if n_current_find < n_names:
            last_button = 'Next'
        else:
            last_button = 'Cancel'
    else:
        title = ''
        last_button = 'Cancel'

    layout = [title,
              [sg.Text(msg, font=font)],
              [sg.Text(warning, font=warning_font, text_color='red')],
              [sg.Button('Print', font=button_font),
               sg.Button(last_button, font=button_font)]]
    win = sg.Window(win_title, layout, modal=True, grab_anywhere=True, enable_close_attempted_event=True)
    event, value = win.read()
    if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == 'Next':
        event = "Cancel"
    win.close()
    return event


def guests_counter(window, n_guests):
    """
    The write event value function for the counter of total number of guests (attendees) to be shown on the main window.
    :param window: the window.
    :param n_guests: the number of guests.
    """
    window.write_event_value('-COUNT-', n_guests)


def non_registered_guests_counter(window, counter_id_for_non_registered_attendees):
    """
    The write event value function for the counter of non registered attendees to be shown on the main window.
    :param window: the window.
    :param counter_id_for_non_registered_attendees: the counter for non registered attendees.
    """
    window.write_event_value('-COUNT2-', counter_id_for_non_registered_attendees)


def registered_guests_counter(window, counter_id_for_registered_attendees):
    """
    The write event value function for the counter of registered attendees to be shown on the main window.
    :param window: the window.
    :param counter_id_for_registered_attendees: the counter for registered attendees.
    """
    window.write_event_value('-COUNT3-', counter_id_for_registered_attendees)


def start_threads(window, n_guests, counter_id_for_non_registered_attendees, counter_id_for_registered_attendees):
    """
    The threads of the counters for registered and non registered attendees and the total number of attendees.
    :param window: the window.
    :param n_guests: the number of guests.
    :param counter_id_for_non_registered_attendees: the counter for non registered attendees.
    :param counter_id_for_registered_attendees: the counter for registered attendees.
    """
    Thread(target=guests_counter(window, n_guests), daemon=True).start()
    Thread(target=non_registered_guests_counter(window, counter_id_for_non_registered_attendees), daemon=True).start()
    Thread(target=registered_guests_counter(window, counter_id_for_registered_attendees), daemon=True).start()


def main(full_file_name, headline_font, font, button_font, registered_number,
         n_guests, counter_id_for_non_registered_attendees, counter_id_for_registered_attendees):
    """
    The main program window. Managing input, button options and showing the information about the ongoing event
    :param full_file_name: the full file name, including the path.
    :param headline_font: the headline font.
    :param font: the text font.
    :param button_font: the button font.
    :param registered_number: the total number of people who registered.
    :param n_guests: the total number of attendees.
    :param counter_id_for_non_registered_attendees: the number of non registered attendees.
    :param counter_id_for_registered_attendees: the number of registered attendees.
    :return: the window.
    """
    layout_title = [
                    [sg.Text('מערכת רישום והדפסה לאירועים של ארגון בוגרי.ות הנדסה באוניברסיטת תל אביב',
                             justification='center', size=(70, 1), font=headline_font)]]

    if full_file_name == '':
        sg_text_registered_number = sg.Text('')
    else:
        sg_text_registered_number = sg.Text('/   ' + str(registered_number) + '  total number of people who registered',
                                            font=font)

    layout = [[sg.Text('Enter Name:', font=font), sg.InputText(key='name', font=font)],
              [sg.Text('Enter Job Title:', font=font), sg.InputText(key='job title', font=font)],
              [sg.Text('Enter Company:', font=font), sg.InputText(key='company', font=font)],
              [sg.Button('Confirm and Print', font=button_font), sg.Button('Confirm only', font=button_font),
               sg.Button('Search', font=button_font)],
              [sg.Text('Number of non registered attendees:', font=font),
               sg.Text(str(-1 * counter_id_for_non_registered_attendees), key='non registered counter', font=font)],
              [sg.Button('Scan QR code', font=button_font),
               sg.Text('Or enter a reservation number:', font=font),
               sg.InputText(key='reservation number', font=font),
               sg.Button('OK', font=button_font)],
              [sg.Text('Number of registered attendees:', font=font),
               sg.Text(str(counter_id_for_registered_attendees), key='registered counter', font=font),
               sg_text_registered_number],
              [sg.Text('Total number of attendees:', font=font),
               sg.Text(str(n_guests), key='guests counter', font=font)],
              [sg.Button('Exit', font=button_font), sg.Button('About', font=button_font)]]

    layout = [[sg.Column(layout_title, element_justification='center')], [layout]]

    # Create the window
    window = sg.Window("TAU Engineering Alumni Registering and Sticker Printing System", layout)

    return window
