import PySimpleGUI as sg
import csv, os, configparser, common
from pathlib import Path

# (Re)writes the config file to /AppData/Roaming/Haukiposti (Haukiposti folder is created if needed)
def createSettingFile(theme, paymentreceiver, accnum, writeString, bankBIC):
    config = configparser.ConfigParser()
    config["haukiposti"] = {"theme": theme,
                            "email": "",
                            "paymentreceiver": paymentreceiver,
                            "accountnumber": accnum,
                            "memberclasses": writeString,
                            "bank": bankBIC}
    
    save_path = os.getenv("APPDATA") + "\\Haukiposti"
    Path(save_path).mkdir(exist_ok=True)
    completeName = os.path.join(save_path, "haukiposticonfig.ini")
    
    with open(completeName, "w") as configfile:
        config.write(configfile)
    configfile.close()

def deleteLogin():
    path = os.getenv("APPDATA") + "\\Haukiposti"

    if os.path.exists(path + "\\token.pickle"):
        os.remove(path + "\\token.pickle")
        sg.PopupOK("Kirjautumistiedot poistettu.")
    else:
        sg.PopupOK("Kirjautumistietoja ei ole olemassa")

def bankToBIC(bank):
    if bank == "Aktia":
        return "HELSFIHH"
    elif bank == "POP":
        return "POPFFI22"
    elif bank == "Danske Bank":
        return "DABAFIHH"
    elif bank == "Handelsbanken":
        return "HANDFIHH"
    elif bank == "Nordea":
        return "NDEAFIHH"
    elif bank == "OP":
        return "OKOYFIHH"
    elif bank == "SEB":
        return "ESSEFIHX"
    elif bank == "S-Pankki":
        return "SBANFIHH"
    elif bank == "Säästöpankki":
        return "ITELFIHH"
    elif bank == "Ålandsbanken":
        return "AABAFI22"
    else:
        return "Tuntematon"

def BICToBank(BIC):
    if BIC == "HELSFIHH":
        return "Aktia"
    elif BIC == "POPFFI22":
        return "POP"
    elif BIC == "DABAFIHH":
        return "Danske Bank"
    elif BIC == "HANDFIHH":
        return "Handelsbanken"
    elif BIC == "NDEAFIHH":
        return "Nordea"
    elif BIC == "OKOYFIHH":
        return "OP"
    elif BIC == "ESSEFIHX":
        return "SEB"
    elif BIC == "SBANFIHH":
        return "S-Pankki"
    elif BIC == "ITELFIHH":
        return "Säästöpankki"
    elif BIC == "AABAFI22":
        return "Ålandsbanken"
    else:
        return "Tuntematon"

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
                ["Tietoa", ["Apua", "Tietoa", "Lisenssit"]]]

    # -- The layout --
    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti - asetukset", font=("Verdana", 14, "bold"))],
                [sg.Text("Teema", font=("Verdana", 12)), sg.Radio("Vaalea", "THEME", key="themelight", font=("Verdana", 12), default=light), sg.Radio("Tumma", "THEME", key="themedark", font=("Verdana", 12), default=dark)],
                [sg.Text("Huom! Vaatii uudelleenkäynnistyksen", font=("Verdana", 12))],
                [sg.Button("Poista kirjautumistiedot", font=("Verdana", 12), pad=(0, 20))],
                [sg.Text("Maksunsaaja", font=("Verdana", 12), size=(20,1)), sg.InputText(configs[2], key="paymentreceiver")],
                [sg.Text("Pankki", font=("Verdana", 12), size=(20,1)), sg.Combo(["Aktia", "POP", "Danske Bank", "Handelsbanken", "Nordea", "OP", "SEB", "S-Pankki", "Säästöpankki", "Ålandsbanken"], key="bank", default_value=BICToBank(configs[5]))],
                [sg.Text("Tilinumero", font=("Verdana", 12), size=(20,1)), sg.InputText(configs[3], key="accnum")],
                [sg.Text("Jäsenlajit", font=("Verdana", 12))],
                [sg.Multiline(memberString, key="memberClasses", size=(60,6))],
                [sg.Text("Kirjoita jäsenlajit muodossa (jäsenlaji): (hinta)", font=("Verdana", 12))],
                [sg.Text("Erota jäsenlajit toisistaan rivin vaihdolla (enter)", font=("Verdana", 12))],
                [sg.Text("Esim.", font=("Verdana", 12))],
                [sg.Text("Perusjäsen: 10.00", font=("Verdana", 12))],
                [sg.Text("Erikoisjäsen: 20", font=("Verdana", 12))],
                [sg.Text("Käytä senttierottimena pistettä! Senttejä ei ole kuitenkaan pakko merkitä.", font=("Verdana", 12))],
                [sg.Button("Tallenna", font=("Verdana", 12)), sg.Button("Peruuta", font=("Verdana", 12))]]

    window = sg.Window("Haukiposti - asetukset", layout)

    # -- Window functionality --
    while True:
        event, values = window.read()

        if event == "Peruuta":
            break

        elif event == "Poista kirjautumistiedot":
            deleteLogin()

        elif event == "Tallenna":
            try:
                if values["themelight"]:
                    theme = "reddit"
                else:
                    theme = "darkblue14"
                
                if values["accnum"][2:].replace(' ', '').isdigit() == False or len(values["accnum"].replace(' ', '')) != 18:
                    sg.PopupOK("Tarkista tilinumero.")
                    continue

                #Parses the member classes input field and creates a string to be written to the configs file,
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
                
                bankBIC = bankToBIC(values["bank"])
                createSettingFile(theme, values["paymentreceiver"], values["accnum"], writeString, bankBIC)
                sg.PopupOK("Tallennettu", font=("Verdana", 12))
                break
            except:
                sg.PopupOK("Jokin meni pieleen tallennettaessa, todennäköisesti jäsenluokissa.\nTarkista, että ne ovat kirjoitettu oikeassa muodossa.", font=("Verdana", 10))

        elif event == "Apua":
            sg.PopupOK("Asetukset. Muokkaa sovelluksen asetuksia.\n\nKirjoita jäsenlajit muodossa (jäsenlaji): (hinta)\nErota jäsenlajit toisistaan rivin vaihdolla (enter)\nEsim\nPerusjäsen: 10.00\nErikoisjäsen: 20.00\nKäytä senttierottimena pistettä! Senttejä ei ole kuitenkaan pakko merkitä.", font=("Verdana", 10))
        elif event == "Tietoa":
            sg.PopupOK("Haukiposti {0}\n\nRami Saarivuori\nAarne Savolainen\n(c) 2020".format(common.version()), font=("Verdana", 12))
        elif event == "Lisenssit":
            sg.popup_scrolled(common.licenses(), font=("Verdana", 12), title="Haukiposti - Lisenssit")
        elif event in (None, "Poistu"):
            exit()

    window.close()