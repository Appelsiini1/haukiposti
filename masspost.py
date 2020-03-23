import PySimpleGUI as sg
import emailFunc as mail
import logging

def massPost(configs):

    # -- Theme --
    sg.theme(configs[0])

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Tietoa", ["Apua", "Tietoa"]]]

    # -- The layout --
    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti - massaposti")],
                [sg.Text("Vastaanottajat")],
                [sg.Input("", key="receivers"), sg.FileBrowse("Tuo vastaanottajat")],
                [sg.Text("Aihe")],
                [sg.InputText()],
                [sg.Text("Viesti")],
                [sg.Multiline(size=(60,10))],
                [sg.Text("Liite"), sg.Input("", key="attachment"), sg.FileBrowse("Selaa...")],
                [sg.Button("Lähetä"), sg.Button("Esikatsele"), sg.Button("Peruuta")]]

    window = sg.Window("Haukiposti - massaposti", layout)

    # -- Window functionality --
    while True:
        event, values = window.read()

        if event == "Peruuta":
            break
        elif event == "Apua":
            sg.PopupOK("Massaposti. Täältä voit lähettää massapostia.\nValitse vastaanottajat sisältävä CSV tiedosto, kirjoita heille viesti ja lähetä.")
        elif event == "Tietoa":
            sg.PopupOK("Rami Saarivuori\nAarne Savolainen\n2020")
        elif event in (None, "Poistu"):
            exit()

    window.close()