import PySimpleGUI as sg
import csv
import configparser
import os
from pathlib import Path

# (Re)writes the config file to /AppData/Roaming/Haukiposti (Haukiposti folder is created if needed)
def createSettingFile(theme, email, paymentreceiver, accnum, writeString):
    config = configparser.ConfigParser()
    config["haukiposti"] = {"theme": theme,
                            "email": email,
                            "paymentreceiver": paymentreceiver,
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
    memberList = [configs[4]]
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
                [sg.Text("Haukiposti - asetukset", font=("Verdana", 14, "bold"))],
                [sg.Text("Teema", font=("Verdana", 12)), sg.Radio("Vaalea", "THEME", key="themelight", font=("Verdana", 12), default=light), sg.Radio("Tumma", "THEME", key="themedark", font=("Verdana", 12), default=dark)],
                [sg.Text("Huom! Vaatii uudelleenkäynnistyksen", font=("Verdana", 12))],
                [sg.Text("")], # some space between stuff
                [sg.Text("Lähettäjän sähköposti", font=("Verdana", 12), size=(20,1)), sg.InputText(configs[1], key="senderemail")],
                [sg.Text("Maksunsaaja", font=("Verdana", 12), size=(20,1)), sg.InputText(configs[2], key="paymentreceiver")],
                [sg.Text("Tilinumero", font=("Verdana", 12), size=(20,1)), sg.InputText(configs[3], key="accnum")],
                [sg.Text("Jäsenlajit", font=("Verdana", 12))],
                [sg.Multiline(memberString, key="memberClasses", size=(60,6))],
                [sg.Text("Kirjoita jäsenlajit muodossa (jäsenlaji): (hinta)", font=("Verdana", 12))],
                [sg.Text("Erota jäsenlajit toisistaan rivin vaihdolla (enter)", font=("Verdana", 12))],
                [sg.Text("Esim", font=("Verdana", 12))],
                [sg.Text("Perusjäsen: 10", font=("Verdana", 12))],
                [sg.Text("Erikoisjäsen: 20", font=("Verdana", 12))],
                [sg.Button("Tallenna", font=("Verdana", 12)), sg.Button("Peruuta", font=("Verdana", 12))]]

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
                
                #Parses the member classes input field and creates a string to be writed to the configs file,
                #passing the string to createSettingFile
                writeString = ''
                string = values["memberClasses"].split("\n")
                i = 0
                while string[i] != "":
                    k = string[i].split(":")
                    writeString = writeString + '"' + k[0] + ',' + k[1].strip() + '"'
                    i = i + 1
                    if string[i] != "":
                        writeString = writeString + ','

                createSettingFile(theme, values["senderemail"], values["paymentreceiver"], values["accnum"], writeString)
                sg.PopupOK("Tallennettu", font=("Verdana", 12))
                break
            except:
                sg.PopupOK("Jokin meni pieleen tallennettaessa, todennäköisesti jäsenluokissa.\nTarkista, että ne ovat kirjoitettu oikeassa muodossa.", font=("Verdana", 10))

        elif event == "Apua":
            sg.PopupOK("Asetukset. Muokkaa sovelluksen asetuksia.\n\nKirjoita jäsenlajit muodossa (jäsenlaji): (hinta)\nErota jäsenlajit toisistaan rivin vaihdolla (enter)\nEsim\nPerusjäsen: 10\nErikoisjäsen: 20", font=("Verdana", 10))
        elif event == "Tietoa":
            sg.PopupOK("Haukiposti V0.5\n\nRami Saarivuori\nAarne Savolainen\n(c) 2020", font=("Verdana", 12))
        elif event in (None, "Poistu"):
            exit()

    window.close()