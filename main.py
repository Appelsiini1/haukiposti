#Haukiposti V1.0.4
#14.09.2020
# (c) Rami Saarivuori & Aarne Savolainen

try:
    import logging, os, configparser, masspost, settings, common, billing, stickersheet, sys
    import emailFunc as mail
    import PySimpleGUI as sg
except Exception:
    exit(-1)

    
# Reads the config file from /AppData/Roaming/Haukiposti and saves the information to a configs list
def configParsing():
    configs = []
    # 0 = theme, 1 = sender email, 2 = payment receiver, 3 = account number, 4 = member classes, 5 = bank BIC
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
        configs.append(config["haukiposti"]["bank"])
        logging.info("Settings retrieved succesfully.")
    except:
        configs.append("reddit")
        configs.append("")
        configs.append("")
        configs.append("")
        configs.append("")
        configs.append("")
        logging.error("No settings file.")
        sg.PopupOK("Ohjelma ei pystynyt löytämään asetustiedostoa.\nViemme sinut ensin asetuksiin, jotta voit laittaa ne kuntoon.")
        settings.settings(configs)
        configs = updateConfig(configs)

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
        configs[5] = config["haukiposti"]["bank"]

        return configs

    except:
        sg.PopupOK("Virhe asetustiedoston päivittämisessä.")


def main():
    try:
        logname = os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "haukilog.log")
        logpath = (os.getenv("APPDATA") + "\\Haukiposti")
        if os.path.exists(logpath) == False:
            os.mkdir(logpath)
        logging.basicConfig(filename=logname, level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

        logging.info("HaukiPosti {0} - Rami Saarivuori & Aarne Savolainen (c) 2020".format(common.version()))
        configs = configParsing()

        # -- Theme --
        sg.theme(configs[0])

        # -- Menu definition --
        menu_def = [["Tiedosto", ["Poistu"]],
                    ["Tietoa", ["Apua", "Tietoa", "Lisenssit"]]]

        # -- The layout --
        layout = [ [sg.Menu(menu_def)],
                    [sg.Image(common.resource_path(r"haukiposti_small.png"), pad=(26,0))],
                    [sg.Text("Haukiposti", font=("Verdana", 15, "bold"), size=(10,1), justification="center")],
                    [sg.Button("Kirjaudu", font=("Verdana", 12), size=(15, 1), key="login")],
                    [sg.Button("Massaposti", font=("Verdana", 12), size=(15, 1))],
                    [sg.Button("Laskutus", font=("Verdana", 12), size=(15, 1))],
                    [sg.Button("Tarra-arkit", font=("Verdana", 12), size=(15, 1))],
                    [sg.Button("Asetukset", font=("Verdana", 12), size=(15, 1))],
                    [sg.Button("Poistu", font=("Verdana", 12), size=(15, 1))]]

        # -- Window creation --
        window1 = sg.Window("Haukiposti", layout)

        # -- Window functionality --
        service = None
        while True:
            event, values = window1.read()

            if event == "Massaposti":
                window1.Hide()
                logging.info("Masspost")
                masspost.massPost(configs, service)
                window1.UnHide()
            elif event == "Laskutus":
                window1.Hide()
                logging.info("Billing")
                billing.billing(configs, service)
                window1.UnHide()
            elif event == "Tarra-arkit":
                window1.Hide()
                logging.info("Stickerheet")
                stickersheet.stickersheet(configs)
                window1.UnHide()
            elif event == "Asetukset":
                window1.Hide()
                logging.info("Settings")
                settings.settings(configs)
                configs = updateConfig(configs)
                if os.path.exists(os.getenv("APPDATA") + "\\Haukiposti\\token.pickle") == False:
                    window1["login"].update("Kirjaudu", disabled=False)
                    service = None
                window1.UnHide()
            elif event == "login":
                service = mail.authenticate()
                if service:
                    sg.PopupOK("Todennus onnistui.", font=("Verdana", 12))
                    window1["login"].update("Kirjauduttu", disabled=True)
                    logging.info("Login succesful")
                else:
                    sg.PopupOK("Todennus epäonnistui.", font=("Verdana", 12))
                    logging.error("Login unsuccesful")
            elif event == "Apua":
                sg.PopupOK("Tämä on päänäkymä. Valitse mitä haluat tehdä painamalla nappia.", font=("Verdana", 12))
            elif event == "Tietoa":
                sg.PopupOK("Haukiposti {0}\n\nRami Saarivuori\nAarne Savolainen\n(c) 2020".format(common.version()), font=("Verdana", 12))
            elif event == "Lisenssit":
                sg.popup_scrolled(common.licenses(), font=("Verdana", 12), title="Haukiposti - Lisenssit")
            elif event in (None, "Poistu"):
                break
        if os.path.exists(os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "preview.html")):
            os.remove(os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "preview.html"))
            folderpath = os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "images")
            for i in os.listdir(folderpath):
                os.remove(folderpath+ "/"+i)
            os.rmdir(folderpath)
            logging.info("Message previews deleted.")
        if os.path.exists(os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "barcodes")):
            folderpath = os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "barcodes")
            for i in os.listdir(folderpath):
                os.remove(folderpath+ "/"+i)
            os.rmdir(folderpath)
            logging.info("Barcodes deleted.")
        if os.path.exists(os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "preview.pdf")):
            os.remove(os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "preview.pdf"))
            logging.info("Invoice preview deleted.")
        window1.close()
        logging.info("Exit, Code 0")
        sys.exit(0)
    except Exception as e:
        logging.exception(e)


if __name__ == "__main__":
    main()