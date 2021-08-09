import PySimpleGUI as sg
from win32com.client import Dispatch


def setup(selectPrinter='DYMO LabelWriter 450'):
    """
    DYMO Printer setup.
    :param selectPrinter: The printer type
    :return: labelCom, labelText
    """
    layout = [[sg.Text(selectPrinter)], [sg.Text('Preparing printer. Please wait...')]]
    window = sg.Window('Setup', layout)
    window.Read(timeout=1000)

    try:
        labelCom = Dispatch('Dymo.DymoAddIn')
        labelText = Dispatch('Dymo.DymoLabels')
        isOpen = labelCom.Open('sticker.label')
        labelCom.SelectPrinter(selectPrinter)
    except:
        sg.popup('No drivers for DYMO printer were found. Unable to print!')
        labelCom, labelText = None, None

    window.close()

    return labelCom, labelText


def print(labelCom, labelText, str):
    """
    Printing a text on a sticker with a label template.
    :param labelCom: the type of sticker label.
    :param labelText: the label text.
    :param str: the string to print.
    """
    labelText.SetField('TEXT', str)

    labelCom.StartPrintJob()
    labelCom.Print(1, False)
    labelCom.EndPrintJob()
