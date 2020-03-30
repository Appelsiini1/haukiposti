import PySimpleGUI as sg

import emailFunc as mail
import logging

def TagsToHTML(text):
    # **text** = <b></b> bolding
    # __text__ = <i></i> italic
    # ||text|| = <u></u> underlined
    # @@link@@text@@ = <a href="">*text*</a> link
    # $$img$$ = <p><img src="cid:0"></p> embedded image (cid:x number of image)
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
        text = text.replace('$$img$$', ('<p><img src="cid:'+i+ '"></p>'), 1)
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
                [sg.Text("Vastaanottajat", font=("Verdana", 10))],
                [sg.Input("", key="receivers"), sg.FileBrowse("Tuo vastaanottajat")],
                [sg.Text("Aihe", font=("Verdana", 10))],
                [sg.InputText()],
                [sg.Text("Viesti", font=("Verdana", 10))],
                [sg.Multiline(key="messageText", size=(60,10))],
                [sg.Text("Liite", font=("Verdana", 10)), sg.Input("", key="attachment"), sg.FileBrowse("Selaa...", font=("Verdana", 10))],
                [sg.Button("Lähetä", font=("Verdana", 10)), sg.Button("Esikatsele", font=("Verdana", 10)), sg.Button("Peruuta", font=("Verdana", 10))]]

    window = sg.Window("Haukiposti - massaposti", layout)

    # -- Window functionality --
    while True:
        event, values = window.read()

        if event == "Peruuta":
            break
        elif event == "Apua":
            sg.PopupOK("Massaposti. Täältä voit lähettää massapostia.\nValitse vastaanottajat sisältävä CSV tiedosto, kirjoita heille viesti ja lähetä.", font=("Verdana", 10))
        elif event == "Tietoa":
            sg.PopupOK("Rami Saarivuori\nAarne Savolainen\n2020", font=("Verdana", 10))
        elif event in (None, "Poistu"):
            exit()

    window.close()