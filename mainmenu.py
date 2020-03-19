import PySimpleGUI as sg
import masspost
import settings
import configparser

def configParsing():
    configs = []
    # 0 = theme, 1 = account number, 2 = member classes

    config = configparser.ConfigParser()
    try:
        config.read("haukiposticonfig.ini")
        configs.append(config["haukiposti"]["theme"])
        configs.append(config["haukiposti"]["accountnumber"])
        configs.append(config["haukiposti"]["memberclasses"])
    except:
        configs.append("reddit")
        configs.append("")
        configs.append("")

        sg.PopupOK("Ohjelma ei pystynyt löytämään asetustiedostoa.\nViemme sinut ensin asetuksiin, jotta voit laittaa ne kuntoon.")
        settings.settings(configs)

    return configs

def updateConfig(configs):
    config = configparser.ConfigParser()
    config.read("haukiposticonfig.ini")
    configs[1] = config["haukiposti"]["accountnumber"]
    configs[2] = config["haukiposti"]["memberclasses"]

    return configs


def main():

    configs = configParsing()

    # -- Theme --
    sg.theme(configs[0])

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Apua", ["a PU a"]]]

    # -- The layout --
    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti")],
                [sg.Button("Kirjaudu"), sg.Text("ei toiminnallisuutta")],
                [sg.Button("Massaposti")],
                [sg.Button("Laskutus"), sg.Text("ei toiminnallisuutta")],
                [sg.Button("Tarra-arkit"), sg.Text("ei toiminnallisuutta")],
                [sg.Button("Asetukset")],
                [sg.Button("Poistu")]]

    # -- Window creation --
    window1 = sg.Window("Haukiposti", layout)

    # -- Window functionality --
    while True:
        event, values = window1.read()

        if event == "Massaposti":
            window1.Hide()
            masspost.massPost(configs)
            window1.UnHide()
        elif event == "Asetukset":
            window1.Hide()
            settings.settings(configs)
            configs = updateConfig(configs)
            window1.UnHide()
        elif event in (None, "Poistu"):
            break

    window1.close()

main()