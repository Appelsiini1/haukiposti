import PySimpleGUI as sg
import emailFunc as mail
import logging, os, shutil
from PIL import Image

def getRes(imagePath):
    try:
        image = Image.open(imagePath)
    except Exception as e:
        logging.error(e)
        return -1
    size = image.size # returns tuple (x,y)
    image.close()
    x = size[0]
    y = size[1]
    while x > 600 or y > 600:
        x -= 100
        y -= 100
    newSize = (x, y)

    return newSize
    

def TagsToHTML(text, paths, preview, *args):
    # **text** = <b></b> bolding
    # __text__ = <i></i> italic
    # ||text|| = <u></u> underlined
    # @@link@@text@@ = <a href="">*text*</a> link
    # $$img$$ = <p><img src="cid:0"></p> embedded image (cid:x number of image)
    # TODO: Size option to images??
    # Font is spesified to 'Calibri'

    try:
        images = args[0]
    except IndexError as identifier:
        pass
    
    start = '<html><body><font face="Calibri">'
    end = '</font></body></html>'

    # newline
    text = "<p>" + text
    text = text.replace('\n', '</p><p>')
    text = "</p>" + text

    #bolding
    tempText = text
    while True:
        text = text.replace('**', '<b>', 1)
        text = text.replace('**', '</b>', 1)
        if text == tempText:
            break
        else:
            tempText = text

    #italic
    tempText = text
    while True:
        text = text.replace('__', '<i>', 1)
        text = text.replace('__', '</i>', 1)
        if text == tempText:
            break
        else:
            tempText = text
    
    #underlined
    tempText = text
    while True:
        text = text.replace('||', '<u>', 1)
        text = text.replace('||', '</u>', 1)
        if text == tempText:
            break
        else:
            tempText = text

    #links
    tempText = text
    while True:
        text = text.replace('@@', '<a href="', 1)
        text = text.replace('@@', '">', 1)
        text = text.replace('@@', '</a>', 1)
        if text == tempText:
            break
        else:
            tempText = text
    
    if text.find("$$img$$") != -1:
        #embedded image
        tempText = text
        i = 0
        for j in paths:
            resolution = getRes(paths[i])
            if resolution == -1:
                return
            if preview == 1:
                text = text.replace('$$img$$', ('<img src="'+images[i]+'" alt="image" height="' + str(resolution[1]) + '" width="'+ str(resolution[0])+'">'), 1)
            else:
                kuva = j.split('/')
                text = text.replace('$$img$$', ('<img src="cid:'+str(kuva[len(kuva)-1])+'" alt="kuva" height="' + str(resolution[1]) + '" width="'+ str(resolution[0])+'">'), 1)
                logging.debug(text)
            if text == tempText:
                break
            else:
                tempText = text
                i = i + 1

    text = start + text + end
    return text

def preview(text, images):
    folder = os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "images")
    path = os.path.join((os.getenv("APPDATA") + "\\Haukiposti"), "preview.html")
    paths = []
    try:
        os.mkdir(folder)
    except FileExistsError as e:
        logging.error(e)
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
    htmlText = TagsToHTML(text, images, preview, paths)
    if htmlText == -1:
        return -1
    try:
        html = open(path, "w")
        html.write(htmlText)
        html.close()
        command = 'cmd /c "start "" "' + path + '"'
        os.system(command)
    except Exception as e:
        logging.error(e)
        sg.PopupOK("Jokin meni vikaan esikatselua avatessa.")

def CSVparser(file):
    try:
        fil = open(file, "r", encoding='utf-8')
    except Exception as e:
        logging.error(e)
        return None
    one = fil.readline().split(';')
    logging.debug(one)
    i = 0
    pos = None
    for item in one:
        if one[i].lower() == "sähköpostiosoite":
            pos = i
            logging.debug("OK")
            logging.debug(pos)
            break
        else: 
            print(one[i].lower())
            i += 1
    logging.debug(i)
    if pos == None:
        return None
    emails = ""
    line = fil.readline().split(';')
    while len(line) > 1:
        emails = emails + line[pos] + ";"
        line = fil.readline().split(';')
    fil.close()
    return emails
    


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
                [sg.Input("", key="receivers"), sg.FileBrowse("Tuo vastaanottajat", file_types=(('CSV taulukot', '*.csv*'),))],
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
                        htmlText = TagsToHTML(text, attachements, preview=0)
                        receivers = CSVparser(values["receivers"])
                        if receivers:
                            encMsg = mail.createMail(configs[1], receivers, values["subject"], htmlText, attachements)
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
                    htmlText = TagsToHTML(text, attachements, preview=0)
                    receivers = CSVparser(values["receivers"])
                    if receivers:
                        encMsg = mail.createMail(configs[1], receivers, values["subject"], htmlText, attachements)
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
            sg.PopupOK("Haukiposti V0.5\n\nRami Saarivuori\nAarne Savolainen\n(c) 2020", font=("Verdana", 12))
        elif event in (None, "Poistu"):
            exit()

    window.close()