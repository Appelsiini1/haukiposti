#Haukiposti V0.2
#15.3.2020
# (c) Rami Saarivuori & Aarne Savolainen

try:
    import logging, os, configparser, masspost, settings
    import emailFunc as mail
    import PySimpleGUI as sg
except Exception:
    exit(-1)
    
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
        logging.info("Settings retrieved succesfully.")
    except:
        configs.append("reddit")
        configs.append("")
        configs.append("")
        logging.error("No settings file.")
        sg.PopupOK("Ohjelma ei pystynyt löytämään asetustiedostoa.\nViemme sinut ensin asetuksiin, jotta voit laittaa ne kuntoon.")
        settings.settings(configs)

    return configs

def updateConfig(configs):
    config = configparser.ConfigParser()
    config.read("haukiposticonfig.ini")
    configs[1] = config["haukiposti"]["accountnumber"]
    configs[2] = config["haukiposti"]["memberclasses"]
    logging.info("Config updated.")

    return configs


def main():
    logname = "haukilog.log"
    logging.basicConfig(filename=logname, level=logging.DEBUG, format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

    configs = configParsing()

    # -- Theme --
    sg.theme(configs[0])

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Tietoa", ["Apua", "Tietoa"]]]

    # -- The layout --
    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti")],
                [sg.Button("Kirjaudu")],
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
        elif event == "Kirjaudu":
            service = mail.authenticate(configs[0])
            if service:
                sg.PopupOK("Todennus onnistui.")
            else:
                sg.PopupOK("Todennus epäonnistui.")
        elif event == "Apua":
            sg.PopupOK("Tämä on päänäkymä. Valitse mitä haluat tehdä painamalla nappia.")
        elif event == "Tietoa":
            sg.PopupOK("Rami Saarivuori\nAarne Savolainen\n2020")
        elif event in (None, "Poistu"):
            break

    window1.close()


if __name__ == "__main__":
    main()