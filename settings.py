import PySimpleGUI as sg
import csv
import configparser

def createSettingFile(theme, accnum, writeString):
    config = configparser.ConfigParser()
    config["haukiposti"] = {"theme": theme,
                            "accountnumber": accnum,
                            "memberclasses": writeString}
    
    with open("haukiposticonfig.ini", "w") as configfile:
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
                ["Apua", ["a PU a"]]]

    # -- The layout --
    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti - asetukset")],
                [sg.Text("Teema"), sg.Radio("Vaalea", "THEME", key="themelight", default=light), sg.Radio("Tumma", "THEME", key="themedark", default=dark)],
                [sg.Text("Huom! Vaatii uudelleenkäynnistyksen")],
                [sg.Text("")], # some space between stuff
                [sg.Text("Tilinumero"), sg.InputText(configs[1], key="accnum")],
                [sg.Text("Jäsenlajit")],
                [sg.Multiline(memberString, key="memberClasses", size=(60,6))],
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

        elif event in (None, "Poistu"):
            exit()

    window.close()