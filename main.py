import PySimpleGUI as sg
import csv
import os.path
import pandas as pd
import datetime
import window
import codes
import printer


def create_or_read_attendees_table(file_name):
    """
    Creating or reading the attendees table based on the registration table file
    :param file_name: the registration table filename (with path)
    :return: n_guests, counter_id_for_non_registered_attendees, counter_id_for_registered_attendees,
    df_attendees, attendees_id_set
    """
    if not os.path.exists(file_name + 'attendees.csv'):
        with open(file_name + 'attendees.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            header = ['time', 'name', 'job title', 'company', 'is registered', 'registration id']
            writer.writerow(header)
            counter_id_for_non_registered_attendees = 0
            counter_id_for_registered_attendees = 0
            n_guests = 0
        f.close()
        df_attendees = pd.read_csv(file_name + 'attendees.csv')
        attendees_id_set = set()

    else:
        df_attendees = pd.read_csv(file_name + 'attendees.csv', encoding='ISO-8859-1')
        n_guests = len(df_attendees)
        attendees_id_set = set(df_attendees['registration id'])
        if n_guests > 0:
            if min(df_attendees['registration id']) < 0:
                counter_id_for_non_registered_attendees = min(df_attendees['registration id'])
            else:
                counter_id_for_non_registered_attendees = 0
            counter_id_for_registered_attendees = n_guests - abs(counter_id_for_non_registered_attendees)
        else:
            counter_id_for_non_registered_attendees = 0
            counter_id_for_registered_attendees = 0

    return n_guests, \
    counter_id_for_non_registered_attendees, counter_id_for_registered_attendees, df_attendees, attendees_id_set


def registered_window_answer(row, reservation_number, attendees_id_set, font, warning_font, button_font):
    """
    Showing the info window for a registered guest.
    :param row: the row of dataframe (guest's info).
    :param reservation_number: the reservation number.
    :param attendees_id_set: the set of attendees ids.
    :param font: the text font.
    :param warning_font: the warning font.
    :param button_font: the button font.
    :return: the answer (choice) chosen by the user.
    """
    name = row['name'].iloc[0]
    job_title = row['job title'].iloc[0]
    company = row['company'].iloc[0]
    msg = name + '\n' + job_title + '\n' + company

    # Showing the registered guest window, for a guest who hasn't signed in yet
    if int(reservation_number) not in attendees_id_set:
        answer = window.registered_guest(reservation_number,
                                         msg,
                                         font,
                                         button_font)
    # Showing the double registration attempt window, for a guest who already signed in
    else:
        answer = window.double_registered_guest(reservation_number,
                                                msg,
                                                '*already signed in',
                                                font,
                                                warning_font,
                                                button_font)
    return answer, name, job_title, company


def main():
    """
    The main function creates the registration system which uses the GUI methods, the loading and writing to files,
    the camera setup and qr/bar codes creating and scanning methods, the printer setup and the printing method.
    """
    # Create the pre-defined fonts and theme
    headline_font, font, warning_font, button_font = window.setup()

    # Reading the registration table
    full_file_name, file_name, \
    registered_number, registered_id_set, registered_name_set, df = window.read_registration_table()

    # Creating or reading the attendees table
    n_guests, counter_id_for_non_registered_attendees, counter_id_for_registered_attendees, \
    df_attendees, attendees_id_set = create_or_read_attendees_table(file_name)

    # Printer setup
    labelCom, labelText = printer.setup()

    # The main window setup
    win = window.main(full_file_name, headline_font, font, button_font, registered_number,
                      n_guests, counter_id_for_non_registered_attendees, counter_id_for_registered_attendees)

    # The 3 counter threads for:
    # number of attendees (guests), number of non registered attendees, number of registered attendees
    # for the main window display
    window.start_threads(win, n_guests, counter_id_for_non_registered_attendees, counter_id_for_registered_attendees)

    # Initialize variables
    event = qrcode_info = None
    values = None
    # answer = None
    registered = 'no'
    registration_id = 0

    # Create an event loop
    while True:
        # Read events and values from user,
        # unless the event is scan or scanned QR code,
        # which we want to disable in this case
        if event != 'Scan QR code' or qrcode_info is None:
            event, values = win.read()

        # If user closes window or clicks Exit
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        # If user clicks About, open About window
        if event == 'About':
            window.about()
            continue

        # Read values into variables
        name = values['name']
        job_title = values['job title']
        company = values['company']
        reservation_number = values['reservation number']

        answer = None

        # Assign a non registered guest info into variables
        if event == 'Confirm and Print' or event == 'Confirm only':
            if name == '':
                sg.popup('Please insert a name!')
                continue
            else:
                registered = 'no'
                counter_id_for_non_registered_attendees -= 1
                registration_id = counter_id_for_non_registered_attendees

        # Search for a name (or a string) in the names column
        if event == 'Search':
            if name == '':
                sg.popup('Please insert a name!')
                continue
            else:
                # n_names = len(df[df['name'] == name])
                n_names = len(df[df['name'].str.contains(name)])

                # No found
                if n_names == 0:
                    sg.popup('There is no ' + name + ' in database!')
                    continue

                # found more than one
                if n_names > 1:
                    sg.popup('There are ' + str(n_names) + ' ' + name + ' in database!')
                # reservation_numbers = df[df['name'] == name]['id'].to_list()
                reservation_numbers = df[df['name'].str.contains(name)]['id'].to_list()

                # Showing a window for each guest found
                for i, res_number in enumerate(reservation_numbers):
                    row = df[df['id'] == res_number]
                    name = row['name'].iloc[0]
                    job_title = row['job title'].iloc[0]
                    company = row['company'].iloc[0]
                    msg = name + '\n' + job_title + '\n' + company

                    # Showing the registered guest window, for a guest who hasn't signed in yet
                    if res_number not in attendees_id_set:
                        answer = window.registered_guest(res_number,
                                                         msg,
                                                         font,
                                                         button_font,
                                                         i + 1,
                                                         n_names)
                    # Showing the double registration attempt window, for a guest who already signed in
                    else:
                        answer = window.double_registered_guest(res_number,
                                                                msg,
                                                                '*already signed in',
                                                                font,
                                                                warning_font,
                                                                button_font,
                                                                i + 1,
                                                                n_names)
                    # Exit loop for a cancel answer
                    if answer == 'Cancel':
                        continue

                    # Assign a non registered guest info into variables
                    if answer != 'Print':
                        registered = 'yes'
                        counter_id_for_registered_attendees += 1
                        registration_id = str(res_number)
                        break

                    # Break for printing the info for a guest who already signed in
                    if answer == 'Print':
                        break

                # Return to the main window if the user clicked cancel and wait for the input from user
                if answer == 'Cancel':
                    continue

        # In case of reservation number input
        if event == 'OK':
            if reservation_number != '':
                if not reservation_number.isnumeric():
                    sg.popup('Type only numbers!')
                    continue

                # In case of reservation number input
                if int(reservation_number) in registered_id_set:
                    row = df[df['id'] == int(reservation_number)]

                    answer, name, job_title, company = registered_window_answer(row, reservation_number,
                                                                                attendees_id_set,
                                                                                font, warning_font, button_font)
                    # Exit loop for a cancel answer
                    if answer == 'Cancel':
                        continue

                    # Assign a non registered guest info into variables
                    if answer != 'Print':
                        registered = 'yes'
                        counter_id_for_registered_attendees += 1
                        registration_id = reservation_number
                else:
                    sg.popup('Reservation number is invalid')
                    continue
            else:
                sg.popup('Reservation number is invalid')
                continue

        # In case of scanning QR codes
        if event == 'Scan QR code':
            try:
                # Open Camera and start scanning
                qrcode_info = codes.camera_scan()
            except:
                sg.popup('Check camera!')
                continue

            if qrcode_info is None:
                continue

            # The decoded QR code is the reservation number
            reservation_number = qrcode_info

            if int(reservation_number) in registered_id_set:
                row = df[df['id'] == int(reservation_number)]

                answer, name, job_title, company = registered_window_answer(row, reservation_number, attendees_id_set,
                                                                            font, warning_font, button_font)
                # Exit loop for a cancel answer
                if answer == 'Cancel':
                    continue

                # Assign a non registered guest info into variables
                if answer != 'Print':
                    registered = 'yes'
                    counter_id_for_registered_attendees += 1
                    registration_id = reservation_number
            else:
                # answer = None
                sg.popup('QR code is invalid')
                continue

        # Print a sticker for guests
        if event == 'Confirm and Print' or answer == 'Confirm and Print' or answer == 'Print':
            print('Printing a sticker...')
            sg.popup_timed('Printing a sticker...', button_type=5)
            printer.print(labelCom, labelText, name + '\n' + job_title + '\n' + company)
            print('Done!')

            # Return to the main window without registration (for guests who already signed in)
            if answer == 'Print':
                continue

        # Info, for guests who just signed in, that will be written in the attendees file
        data = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                name, job_title, company,
                registered, int(registration_id)]

        # Printing info on console
        print('Name:', name)
        print('job title:', job_title)
        print('company:', company)
        print('reservation number:', registration_id)

        # Update the attendees id set: add the new registration id to the set of already signed guests
        attendees_id_set.add(int(registration_id))

        # Append the new row (info) to the attendees file
        with open(file_name + 'attendees.csv', 'a', newline='') as f:
            writer = csv.writer(f)

            # write the data
            writer.writerow(data)
        f.close()

        # clear window's inputs
        win['name']('')
        win['job title']('')
        win['company']('')
        win['reservation number']('')

        # update number of attendees
        n_guests = counter_id_for_registered_attendees - counter_id_for_non_registered_attendees
        win['guests counter'].update(str(n_guests))
        win['non registered counter'].update(str(-1 * counter_id_for_non_registered_attendees))
        win['registered counter'].update(str(counter_id_for_registered_attendees))

    # close main window
    win.close()


if __name__ == "__main__":
    main()
