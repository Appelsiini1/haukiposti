import PySimpleGUI as sg
import csv
import configparser
import os
from pathlib import Path

def createSettingFile(theme, accnum, writeString):
    config = configparser.ConfigParser()
    config["haukiposti"] = {"theme": theme,
                            "accountnumber": accnum,
                            "memberclasses": writeString}
    
    save_path = os.getenv("APPDATA") + "\\Haukiposti"
    Path(save_path).mkdir(exist_ok=True)
    completeName = os.path.join(save_path, "haukiposticonfig.ini")
    
    with open(completeName, "w") as configfile:
        config.write(configfile)
    configfile.close()

def settings(configs):

    # -- Theme --
    sg.theme(configs[0])

    if configs[0] == "reddit":
        light = True
        dark = False
    else:
        light = False
        dark = True

    # -- List of member classes converted to a string --
    memberList = [configs[2]]
    parser = csv.reader(memberList)
    memberString = ""
    for fields in parser:
        for field in fields:
            string = field.split(",")
            memberString = memberString + string[0] + ": " + string[1] + "\n"

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Tietoa", ["Apua", "Tietoa"]]]

    # -- The layout --
    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti - asetukset")],
                [sg.Text("Teema"), sg.Radio("Vaalea", "THEME", key="themelight", default=light), sg.Radio("Tumma", "THEME", key="themedark", default=dark)],
                [sg.Text("Huom! Vaatii uudelleenkäynnistyksen")],
                [sg.Text("")], # some space between stuff
                [sg.Text("Tilinumero"), sg.InputText(configs[1], key="accnum")],
                [sg.Text("Jäsenlajit")],
                [sg.Multiline(memberString, key="memberClasses", size=(60,6))],
                [sg.Text("Kirjoita jäsenlajit muodossa (jäsenlaji): (hinta)")],
                [sg.Text("Esim")],
                [sg.Text("Perusjäsen: 10")],
                [sg.Text("Erikoisjäsen: 20")],
                [sg.Button("Tallenna"), sg.Button("Peruuta")]]

    window = sg.Window("Haukiposti - massaposti", layout)

    # -- Window functionality --
    while True:
        event, values = window.read()

        if event == "Peruuta":
            break

        elif event == "Tallenna":
            try:
                if values["themelight"]:
                    theme = "reddit"
                else:
                    theme = "darkblue14"
                
                writeString = ''
                string = values["memberClasses"].split("\n")
                i = 0
                while string[i] != "":
                    k = string[i].split(":")
                    writeString = writeString + '"' + k[0] + ',' + k[1].strip() + '"'
                    i = i + 1
                    if string[i] != "":
                        writeString = writeString + ','

                createSettingFile(theme, values["accnum"], writeString)
                sg.PopupOK("Tallennettu")
                break
            except:
                sg.PopupOK("Jokin meni pieleen tallennettaessa, todennäköisesti jäsenluokissa.\nTarkista, että ne ovat kirjoitettu oikeassa muodossa.")

        elif event == "Apua":
            sg.PopupOK("Asetukset. Muokkaa sovelluksen asetuksia.\n\nKirjoita jäsenlajit muodossa (jäsenlaji): (hinta)\nEsim\nPerusjäsen: 10\nErikoisjäsen: 20")
        elif event == "Tietoa":
            sg.PopupOK("Rami Saarivuori\nAarne Savolainen\n2020")
        elif event in (None, "Poistu"):
            exit()

    window.close()