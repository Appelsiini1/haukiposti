import sys, os, logging
from PIL import Image

class receiver():
    def __init__(self, firstname, lastname, contant, address, postalno, city, membertype, paper):
        self.firstname = firstname
        self.lastname = lastname
        self.contant = contant
        self.address = address
        self.postalno = postalno
        self.city = city
        self.membertype = membertype
        self.paper = paper

def version():
    return "V0.6.1"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS # pylint: disable=no-member
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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