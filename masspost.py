import PySimpleGUI as sg
import emailFunc as mail
import logging, os, shutil, common


def preview(text, images):
    folder = os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "images")
    path = os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "preview.html")
    paths = []
    try:
        os.mkdir(folder)
    except FileExistsError as e:
        logging.exception(e)
        pass
    i = 0
    for item in images:
        if images[i][-4:].lower() == 'jpeg' or images[i][-4:].lower() == '.png' or images[i][-4:].lower() == '.jpg' or images[i][-4:].lower() == '.gif':
            shutil.copy(images[i], folder)
            temp = images[i].split('/')
            tempf = "images/" + temp[len(temp)-1]
            paths.append(tempf)
            i += 1
            
    preview = 1
    htmlText = common.TagsToHTML(text, images, preview, paths)
    if htmlText == -1:
        return -1
    try:
        html = open(path, "w")
        html.write(htmlText)
        html.close()
        command = 'cmd /c "start "" "' + path + '"'
        os.system(command)
    except Exception as e:
        logging.exception(e)
        sg.PopupOK("Jokin meni vikaan esikatselua avatessa.")

def massPost(configs, service):

    # -- Theme --
    sg.theme(configs[0])

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Tietoa", ["Apua", "Tietoa"]]]

    # -- The layout --
    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti - massaposti", font=("Verdana", 12, "bold"))],
                [sg.Text("Vastaanottajat", font=("Verdana", 12))],
                [sg.Input("", key="receivers"), sg.FileBrowse("Tuo vastaanottajat", file_types=(('CSV taulukot', '*.csv'),))],
                [sg.Text("Aihe", font=("Verdana", 12))],
                [sg.InputText("", key="subject")],
                [sg.Text("Viesti", font=("Verdana", 12))],
                [sg.Multiline(key="messageText", size=(60,10))],
                [sg.Text("Liitteet", font=("Verdana", 12)), sg.Input("", key="attachment"), sg.FilesBrowse("Selaa...", font=("Verdana", 12))],
                [sg.Button("Lähetä", font=("Verdana", 12)), sg.Button("Esikatsele", font=("Verdana", 12)), sg.Button("Peruuta", font=("Verdana", 12))]]

    window = sg.Window("Haukiposti - massaposti", layout)

    # -- Window functionality --
    while True:
        event, values = window.read()

        if event == "Peruuta":
            break
        elif event == "Esikatsele":
            attachements = values["attachment"].split(';')
            text = values["messageText"]
            if preview(text, attachements) == -1:
                sg.PopupOK("Tekstin muunnos epäonnistui. Todennäköisesti jotakin tiedostoa ei voitu avata.")
        elif event == "Lähetä":
            ok = sg.PopupOKCancel("Haluatko varmasti lähettää viestin?")
            if ok.lower() == "ok":
                attachements = values["attachment"].split(';')
                size = 0
                if attachements[0] != '':
                    for item in attachements:
                        size += os.path.getsize(item)
                    if size > 24000000:
                        sg.PopupOK("Liitteiden koko on suurempi kuin salittu 23 Mt.")
                    else:
                        text = values["messageText"]
                        htmlText = common.TagsToHTML(text, attachements, preview=0)
                        receivers = common.CSVparser(values["receivers"])
                        emailString = ""
                        if receivers:
                            for item in receivers:
                                emailString = emailString + item.email + ";"
                            encMsg = mail.createMail(configs[1], emailString, values["subject"], htmlText, attachements)
                            if encMsg:
                                msg = mail.sendMail(service, 'me', encMsg)
                                if msg:
                                    sg.PopupOK("Viestin lähetys onnistui.")
                                    logging.debug(msg)
                                    logging.info("Message sent.")
                            else:
                                sg.PopupOK("Jokin meni vikaan viestiä luotaessa. Viestiä ei lähetetty.")
                        else:
                            sg.PopupOK("CSV tiedostoa lukiessa tapahtui virhe.")
                else:
                    text = values["messageText"]
                    htmlText = common.TagsToHTML(text, attachements, preview=0)
                    receivers = common.CSVparser(values["receivers"])
                    emailString = ""
                    if receivers:
                        for item in receivers:
                            emailString = emailString + item.email + ";"
                        encMsg = mail.createMail(configs[1], emailString, values["subject"], htmlText, attachements)
                        if encMsg:
                            msg = mail.sendMail(service, 'me', encMsg)
                            if msg:
                                sg.PopupOK("Viestin lähetys onnistui.")
                                logging.debug(msg)
                                logging.info("Message sent.")
                        else:
                            sg.PopupOK("Jokin meni vikaan viestiä luotaessa. Viestiä ei lähetetty.")
                    else:
                        sg.PopupOK("CSV tiedostoa lukiessa tapahtui virhe.")

        elif event == "Apua":
            apua = """Massaposti. Täältä voit lähettää massapostia.\n
    Valitse vastaanottajat sisältävä CSV tiedosto, mahdolliset liitteet, kirjoita heille viesti ja lähetä.\n\n
    Tekstin erikoismerkit:\n
    **tekstiä** == Lihavoitu\n
    __tekstiä__ == Kursivoitu\n
    ||tekstiä|| == Alleviivattu\n
    @@linkki@@tekstiä@@ == Tekstin seassa oleva linkki. Mikäli haluat linkin näkyvän linkkinä, kopioi linkki myös tekstin paikalle.\n
    $$img$$ == Tekstin seassa olevat kuvat määritetään tällä tagilla. Valitse kuvat liitteeksi. Liitteiden järjestyksellä ei ole väliä.\n
    Jos haluat kuvan olevan linkki, laita $$img$$ tägi tekstin paikalle linkkitägissä. (eli @@linkki@@$$img$$@@)"""
            sg.PopupOK(apua, title="Apua", font=("Verdana", 12))
        elif event == "Tietoa":
            sg.PopupOK("Haukiposti {0}\n\nRami Saarivuori\nAarne Savolainen\n(c) 2020".format(common.version()), font=("Verdana", 12))
        elif event in (None, "Poistu"):
            exit()

    window.close()