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
    x = size[0]
    y = size[1]
    while x > 600 or y > 600:
        x -= 100
        y -= 100
    newSize = (x, y)

    return newSize
    

def TagsToHTML(text, images, preview):
    # **text** = <b></b> bolding
    # __text__ = <i></i> italic
    # ||text|| = <u></u> underlined
    # @@link@@text@@ = <a href="">*text*</a> link
    # $$img$$ = <p><img src="cid:0"></p> embedded image (cid:x number of image)
    # TODO: Size option to images??
    # Font is spesified to 'Calibri'

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
    
    #embedded image
    tempText = text
    i = 0
    for j in images:
        resolution = getRes(images[i])
        if resolution == -1:
            return
        if preview == 1:
            text = text.replace('$$img$$', ('<img src="'+images[i]+'" alt="image" height="' + resolution[1] + '" width="'+ resolution[0]+'">'), 1)
        else:
            text = text.replace('$$img$$', ('<img src="cid:'+i+'" alt="image" height="' + resolution[1] + '" width="'+ resolution[0]+'">'), 1)

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
        if images[i][-4:].lower() == 'jpeg' or images[i][-4:].lower() == '.png' or images[i][-4:].lower() == '.jpg' or images[i][-4:].lower() == '.gif' or images[i][-4:] == '.png':
            shutil.copy(images[i], folder)
            temp = images[i].split('/')
            tempf = "images/" + temp[len(temp)-1]
            paths.append(tempf)
            i = i + 1
            

    htmlText = TagsToHTML(text, paths, preview=1)
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
                [sg.Input("", key="receivers"), sg.FileBrowse("Tuo vastaanottajat")],
                [sg.Text("Aihe", font=("Verdana", 12))],
                [sg.InputText()],
                [sg.Text("Viesti", font=("Verdana", 12))],
                [sg.Multiline(key="messageText", size=(60,10))],
                [sg.Text("Liite", font=("Verdana", 12)), sg.Input("", key="attachment"), sg.FilesBrowse("Selaa...", font=("Verdana", 12))],
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
        elif event == "Apua":
            sg.PopupOK("Massaposti. Täältä voit lähettää massapostia.\nValitse vastaanottajat sisältävä CSV tiedosto, kirjoita heille viesti ja lähetä.", font=("Verdana", 12))
        elif event == "Tietoa":
            sg.PopupOK("Rami Saarivuori\nAarne Savolainen\n2020", font=("Verdana", 12))
        elif event in (None, "Poistu"):
            exit()

    window.close()