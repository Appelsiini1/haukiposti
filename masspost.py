import PySimpleGUI as sg
import emailFunc as mail
import logging
#from PIL import Image

# def getRes(imagePath):
#     try:
#         image = Image.open(imagePath)
#     except Exception as e:
#         logging.error(e)
#         return -1
#     size = image.size # returns tuple (x,y)
#     # TODO: resize image based on original and size option
    

def TagsToHTML(text, images):
    # **text** = <b></b> bolding
    # __text__ = <i></i> italic
    # ||text|| = <u></u> underlined
    # @@link@@text@@ = <a href="">*text*</a> link
    # $$img$$ = <p><img src="cid:0"></p> embedded image (cid:x number of image)
    # TODO: Size option to images??
    # Font is spesified to 'Calibri'

    start = '<html><body><font face="Calibri">'
    end = '</font></body></html>'

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
    while True:
        # resolution = getRes(images[i])
        # if resolution == -1:
        #     return
        text = text.replace('$$img$$', ('<p><img src="cid:'+i+'" alt="image" height="700" width="700"></p>'), 1)
        if text == tempText:
            break
        else:
            tempText = text
            i = i + 1

    text = start + text + end
    return text

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
                [sg.Text("Liite", font=("Verdana", 12)), sg.Input("", key="attachment"), sg.FileBrowse("Selaa...", font=("Verdana", 12))],
                [sg.Button("Lähetä", font=("Verdana", 12)), sg.Button("Esikatsele", font=("Verdana", 12)), sg.Button("Peruuta", font=("Verdana", 12))]]

    window = sg.Window("Haukiposti - massaposti", layout)

    # -- Window functionality --
    while True:
        event, values = window.read()

        if event == "Peruuta":
            break
        elif event == "Apua":
            sg.PopupOK("Massaposti. Täältä voit lähettää massapostia.\nValitse vastaanottajat sisältävä CSV tiedosto, kirjoita heille viesti ja lähetä.", font=("Verdana", 12))
        elif event == "Tietoa":
            sg.PopupOK("Rami Saarivuori\nAarne Savolainen\n2020", font=("Verdana", 12))
        elif event in (None, "Poistu"):
            exit()

    window.close()