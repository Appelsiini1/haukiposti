import sys, os, logging
from PIL import Image

class receiverClass():
    def __init__(self, firstname, lastname, contact, email, address, postalno, city, paymentyear, membertype, paper):
        self.firstname = firstname
        self.lastname = lastname
        self.contact = contact
        self.email = email
        self.address = address
        self.postalno = postalno
        self.city = city
        self.paymentyear = paymentyear
        self.membertype = membertype
        self.paper = paper

    def debugPrint(self):
        print("Firstname: ", self.firstname)
        print("Lastname: ", self.lastname)
        print("Contact: ", self.contact)
        print("Email: ", self.email)
        print("Address: ", self.address)
        print("Postalno: ", self.postalno)
        print("City: ", self.city)
        print("Payment year: ", self.paymentyear)
        print("Membertype: ", self.membertype)
        print("Paper: ", self.paper)

def version():
    return "V0.9.0"

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
        size = image.size # returns tuple (x,y)
    except Exception as e:
        logging.exception(e)
        return -1
    finally:
        image.close()
    x = size[0]
    y = size[1]
    while x > 600 or y > 600:
        x -= 100
        y -= 100
    newSize = (x, y)

    return newSize
    
def CSVparser(file):
    try:
        with open(file, "r", encoding='utf-8-sig') as fil:
            firstnamePos = None
            lastnamePos = None
            contactPos = None
            emailPos = None
            addressPos = None
            postalnoPos = None
            cityPos = None
            membertypePos = None
            paperPos = None
            paymentyearPos = None

            # Check the positions of information from the header row
            i = 0
            one = fil.readline().split(';')
            for item in one:
                if one[i].lower().strip() == "etunimi":
                    firstnamePos = i
                elif one[i].lower().strip() == "sukunimi":
                    lastnamePos = i
                elif one[i].lower().strip() == "yhteystieto":
                    contactPos = i
                elif one[i].lower().strip() == "sähköpostiosoite":
                    emailPos = i
                elif one[i].lower().strip() == "lähiosoite":
                    addressPos = i
                elif one[i].lower().strip() == "postinumero":
                    postalnoPos = i
                elif one[i].lower().strip() == "postitoimipaikka":
                    cityPos = i
                elif one[i].lower().strip() == "jäsentyyppi":
                    membertypePos = i
                elif one[i].lower().strip() == "paperikirje":
                    paperPos = i
                elif one[i].lower().strip() == "maksuvuosi":
                    paymentyearPos = i
                i += 1
            emails = []

            # Read the information rows
            line = fil.readline().split(';')
            while len(line) > 1:
                # Check if any of the positions is None, meaning the program couldn't find the information from the file
                # if yes then replace with an empty string, if no then get information from the row
                if firstnamePos != None:
                    firstname = line[firstnamePos]
                else:
                    firstname = ""
                if lastnamePos != None:
                    lastname = line[lastnamePos]
                else:
                    lastname = ""
                if contactPos != None:
                    contact = line[contactPos]
                else:
                    contact = ""
                if emailPos != None:
                    email = line[emailPos]
                else:
                    email = ""
                if addressPos != None:
                    address = line[addressPos]
                else:
                    address = ""
                if postalnoPos != None:
                    postalno = line[postalnoPos]
                else:
                    postalno = ""
                if cityPos != None:
                    city = line[cityPos]
                else:
                    city = ""
                if membertypePos != None:
                    membertype = line[membertypePos]
                else:
                    membertype = ""
                if paymentyearPos != None:
                    paymentyear = line[paymentyearPos]
                else:
                    paymentyear = ""
                if paperPos != None:
                    if line[paperPos].strip() != "":
                        paper = True
                    else:
                        paper = False
                else:
                    paper = False

                # Create an instance of receiverClass with read information and append it to a list
                receiver = receiverClass(firstname, lastname, contact, email, address, postalno, city, paymentyear, membertype, paper)
                emails.append(receiver)
                line = fil.readline().split(';')
    except Exception as e:
        logging.exception(e)
        return None

    # old crap
    
    # i = 0
    # pos = None
    # for item in one:
    #     if one[i].lower() == "sähköpostiosoite":
    #         pos = i
    #         logging.debug("OK")
    #         logging.debug(pos)
    #         break
    #     else: 
    #         print(one[i].lower())
    #         i += 1
    # logging.debug(i)
    # if pos == None:
    #     return None
    # emails = ""
    # line = fil.readline().split(';')
    # while len(line) > 1:
    #     emails = emails + line[pos] + ";"
    #     line = fil.readline().split(';')
    # fil.close()
    return emails

def markdownParserHTML(text, paths, preview, *args):
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
        text = text.replace('||', '<i>', 1)
        text = text.replace('||', '</i>', 1)
        if text == tempText:
            break
        else:
            tempText = text
    
    #underlined
    tempText = text
    while True:
        text = text.replace('__', '<u>', 1)
        text = text.replace('__', '</u>', 1)
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

def finder(text):

    bold = text.find('**')
    ital = text.find('||')
    under = text.find('__')

    if bold == -1:
        bold = 9999999
    if ital == -1:
        ital = 9999999
    if under == -1:
        under = 9999999

    if bold < ital and bold < under:
        return ([True, False, False], bold)
    elif ital < bold and ital < under:
        return ([False, True, False], ital)
    elif under < bold and under < ital:
        return ([False, False, True], under)
    else:
        return None


def markdownParserPDF(text):
    # **text** = <b></b> bolding
    # __text__ = <i></i> italic
    # ||text|| = <u></u> underlined

    finalList = []

    res = finder(text)
    if res == None:
        return [[False, False, False], text]
    if res[1] > 0:
        finalList.append(([False, False, False], text[:res[1]]))
        text = text[res[1]:]

    while res != -1:
        res2 = finder(text[2:])

        if res[0] == res2[0]:
            finalList.append((res[0], text[2:res2[1]+2]))
            text = text[res2[1]+4:]
        else:
            res3 = finder(text[res2[1]+4:])
            tempBool = [False, False, False]
            if res3[0] == res2[0]:
                if res3[0][0] or res2[0][0] or res[0][0]:
                    tempBool[0] = True
                if res[0][1] or res2[0][1] or res3[0][1]:
                    tempBool[1] = True
                if res[0][2] or res2[0][2] or res3[0][2]:
                    tempBool[2] = True
                finalList.append((tempBool, text[4:res3[1]+4]))
                text = text[res3[1]+8:]
            else:
                res4 = finder(text[res3[1]+6:])
                finalList.append(([True, True, True], text[res3[1]+6:res4[1]+6]))
                text = text[res4[1]+12:]
        
        res = finder(text)
        if res == None:
            finalList.append(([False, False, False], text))
            break
        elif res[1] > 0:
            finalList.append(([False, False, False], text[:res[1]]))
            text = text[res[1]:]
            res = finder(text)

    return finalList