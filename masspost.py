import PySimpleGUI as sg

def massPost():

    # -- Theme --
    theme = "DarkBlue14"

    sg.theme(theme)

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Apua", ["a PU a"]]]

    # -- The layout --
    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti - massaposti")],
                [sg.Button("Tuo vastaanottajat")],
                [sg.Text("Aihe")],
                [sg.InputText()],
                [sg.Text("Viesti")],
                [sg.Multiline(size=(60,10))],
                [sg.Text("Liite"), sg.Button("Selaa...")],
                [sg.Button("Lähetä"), sg.Button("Esikatsele"), sg.Button("Peruuta")]]

    window = sg.Window("Haukiposti - massaposti", layout)

    # -- Window functionality --
    while True:
        event, values = window.read()

        if event == "Peruuta":
            break
        elif event in (None, "Poistu"):
            exit()

    window.close()