import PySimpleGUI as sg
import masspost

def main():

    # -- Theme --
    theme = "DarkBlue14"

    sg.theme(theme)

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Apua", ["a PU a"]]]

    # -- The layout --
    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti")],
                [sg.Button("Kirjaudu")],
                [sg.Button("Massaposti")],
                [sg.Button("Laskutus")],
                [sg.Button("Tarra-arkit")],
                [sg.Button("Asetukset")],
                [sg.Button("Poistu")]]

    # -- Window creation --
    window1 = sg.Window("Haukiposti", layout)

    # -- Window functionality --
    while True:
        event, values = window1.read()

        if event == "Massaposti":
            window1.Hide()
            masspost.massPost()
            window1.UnHide()
        elif event in (None, "Poistu"):
            break

    window1.close()

main()