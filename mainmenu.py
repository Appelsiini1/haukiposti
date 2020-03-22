import PySimpleGUI as sg
import masspost
import settings
import configparser
import os

def configParsing():
    configs = []
    # 0 = theme, 1 = account number, 2 = member classes
    save_path = os.getenv("APPDATA") + "\\Haukiposti"
    completeName = os.path.join(save_path, "haukiposticonfig.ini")

    config = configparser.ConfigParser()
    try:
        config.read(completeName)
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
    save_path = os.getenv("APPDATA") + "\\Haukiposti"
    completeName = os.path.join(save_path, "haukiposticonfig.ini")
    config = configparser.ConfigParser()
    config.read(completeName)
    configs[1] = config["haukiposti"]["accountnumber"]
    configs[2] = config["haukiposti"]["memberclasses"]

    return configs


def main():

    configs = configParsing()

    # -- Theme --
    sg.theme(configs[0])

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Tietoa", ["Apua", "Tietoa"]]]

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
        elif event == "Apua":
            sg.PopupOK("Tämä on päänäkymä. Valitse mitä haluat tehdä painamalla nappia.")
        elif event == "Tietoa":
            sg.PopupOK("Rami Saarivuori\nAarne Savolainen\n2020")
        elif event in (None, "Poistu"):
            break

    window1.close()

main()
