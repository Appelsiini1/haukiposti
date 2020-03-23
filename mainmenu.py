import PySimpleGUI as sg
import masspost
import settings
import configparser
import os

# Reads the config file from /AppData/Roaming/Haukiposti and saves the information to a configs list
def configParsing():
    configs = []
    # 0 = theme, 1 = sender email, 2 = payment receiver, 3 = account number, 4 = member classes
    save_path = os.getenv("APPDATA") + "\\Haukiposti"
    completeName = os.path.join(save_path, "haukiposticonfig.ini")

    config = configparser.ConfigParser()
    try:
        config.read(completeName)
        configs.append(config["haukiposti"]["theme"])
        configs.append(config["haukiposti"]["email"])
        configs.append(config["haukiposti"]["paymentreceiver"])
        configs.append(config["haukiposti"]["accountnumber"])
        configs.append(config["haukiposti"]["memberclasses"])
    except:
        configs.append("reddit")
        configs.append("")
        configs.append("")
        configs.append("")
        configs.append("")

        sg.PopupOK("Ohjelma ei pystynyt löytämään asetustiedostoa.\nViemme sinut ensin asetuksiin, jotta voit laittaa ne kuntoon.")
        settings.settings(configs)

    return configs

# Updates the configs list's accountnumber and memberclasses info by reading the configs file after quitting the settings
def updateConfig(configs):
    try:
        save_path = os.getenv("APPDATA") + "\\Haukiposti"
        completeName = os.path.join(save_path, "haukiposticonfig.ini")
        config = configparser.ConfigParser()
        config.read(completeName)
        configs[1] = config["haukiposti"]["email"]
        configs[2] = config["haukiposti"]["paymentreceiver"]
        configs[3] = config["haukiposti"]["accountnumber"]
        configs[4] = config["haukiposti"]["memberclasses"]

        return configs

    except:
        sg.PopupOK("Virhe asetustiedoston päivittämisessä.")



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
