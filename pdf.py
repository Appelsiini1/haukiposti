try:
    import logging, common, barcode, os, random, datetime, time, csv
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.units import inch
    from pubcode import Code128
    import PySimpleGUI as sg
except Exception as e:
    logging.exception(e)

def getY(x):
    y = 48-x
    unit = 0
    unit += inch*(1/12)*y
    return unit


def createBarcode(reference, account, amount, duedate, i):
    """Create virtual barcode number & barcode image. 
    Return number as string and the path to barcode image.
    """
    try:

        code = "4"
        code = code + account[2:].replace(' ', '')
        if len(amount.split('.')) > 1:
            amount = amount.split('.')
            euro = amount[0]
            while len(euro) < 6:
                euro = "0" + euro
            cents = amount[1]
            while len(cents) < 2:
                cents = cents + "0"
        else:
            euro = amount
            while len(euro) < 6:
                euro = "0" + euro
            cents = "00"
        code = code + euro + cents
        code = code + "000"
        while len(reference) < 20:
            reference = "0" + reference
        code = code + reference
        due = duedate.split('.')
        code = code + due[2][2:]
        code = code + due[1]
        code = code + due[0]

        barcode = Code128(code, charset='C')
        img = barcode.image()

        name = "barcode" + str(i) + ".png"
        imgPath = os.path.join(os.getenv("APPDATA"), "Haukiposti", "barcodes", name)
        img.save(imgPath, "PNG")
    except Exception as e:
        logging.exception(e)

    return code, imgPath

def reference():
    """Create a reference number and check it's validity
    
    Returns reference number as string.
    """

    try:
        random.seed()
        raw = random.randint(100000000, 999999999)
        raw = str(raw)[::-1]
        j = 1
        res = 0
        for i in range(0, len(raw)):
            if j == 1:
                res += int(raw[i])*7
                j += 1
            elif j == 2:
                res += int(raw[i])*3
                j += 1
            elif j == 3:
                res += int(raw[i])
                j = 1

        k = 0
        res2 = res
        while True:
            res3 = str(res)
            if res3[len(res3)-1] == "0":
                break
            else:
                res += 1
                k += 1

        ref = raw[::-1] + str(k)
    except Exception as e:
        logging.exception(e)
        
    return ref

def definePage(c, config, receiver, path, message, duedate, subject, reference, i, logo=None):
    """
    Args:
    config = config list,
    receivers = list of receiver objects
    path = path to output folder
    message = message to be attached to the invoice
    duedate = due date of the invoice as a string
    subject = subject line of the invoice
    reference = Reference number for the invoice
    i = index number for barcode
    logo = path to the logo file if spesified. Default None
    """

    try:

        sg.theme(config[0])

        #measurements
        leveys, korkeus = A4
        transSizeX = leveys / 210
        transSizeY = korkeus / 297
        base = common.resource_path("Tilisiirto_pohja.jpg")
        margin = transSizeX*27
        margin2 = transSizeX*119
        margin3 = margin2+transSizeX*18

        # Document settings
        c.setAuthor(config[2])
        c.setTitle(subject)
        c.setSubject(subject)
        c.setCreator(("Haukiposti "+common.version()))

        if logo != "":
            c.drawImage(logo, 25, korkeus-110, width=110, height=110, preserveAspectRatio=True)
        c.line(25, korkeus-100, leveys-25, korkeus-100)
        c.drawImage(base, 0, 10, width=(transSizeX*210), height=(transSizeY*101.6), preserveAspectRatio=True) # bank transfer base
        
        c.setFont("Helvetica-Bold", 18)
        c.drawString(250, korkeus-60, subject)
        c.setFont("Helvetica", 11)

        # TODO Saate
        m = c.beginText()
        m.setTextOrigin(25, korkeus-135)
        newLines = message.split('\n')
        for item in newLines:
            line = common.markdownParserPDF(item)
            if line == -1:
                sg.PopupOK("Viallinen muotoilu saatteessa. Tarkista, että suljet ja aloita tagit oikein. Keskeytetään.")
                return -1
            logging.debug(line)
            if line == []:
                break
            elif len(line) == 2 and type(line[1]) == str:
                if line[0] == [False, False, False] or line[0] == [False, False, True]:
                    m.setFont("Helvetica", 12)
                elif line[0] == [True, False, False] or line[0] == [True, False, True]:
                    m.setFont("Helvetica-Bold", 12)
                elif line[0] == [False, True, False] or line[0] == [False, True, True]:
                    m.setFont("Helvetica-Oblique", 12)
                elif line[0] == [True, True, False] or line[0] == [True, True, True]:
                    m.setFont("Helvetica-BoldOblique", 12)
                m.textOut(line[1])
            else:
                for text in line:
                    if text[0] == [False, False, False] or text[0] == [False, False, True]:
                        m.setFont("Helvetica", 12)
                    elif text[0] == [True, False, False] or text[0] == [True, False, True]:
                        m.setFont("Helvetica-Bold", 12)
                    elif text[0] == [False, True, False] or text[0] == [False, True, True]:
                        m.setFont("Helvetica-Oblique", 12)
                    elif text[0] == [True, True, False] or text[0] == [True, True, True]:
                        m.setFont("Helvetica-BoldOblique", 12)
                    m.textOut(text[1])
            m.moveCursor(0, 12)
        c.drawText(m)

        # Receiver information
        account = config[3].replace(' ', '')
        account = account[:4] + " " + account[4:8] + " " + account[8:12] + " " + account[12:16] + " " + account[16:]

        c.drawString(margin, getY(5), account) # receiver account number
        c.drawString(margin, getY(11), config[2]) # payment receiver
        c.setFontSize(15)
        c.drawString(margin2, getY(5), config[5])

        # Payer information
        textObject = c.beginText()
        textObject.setTextOrigin(margin, getY(16))
        textObject.setFont("Helvetica", 11)
        textObject.textLine((receiver.firstname+" "+receiver.lastname)) # payer name
        if receiver.contact != "":
            textObject.textLine(receiver.contact) # payer contact, if any
        textObject.textLine(receiver.address) # payer address
        textObject.textLine((receiver.postalno + " " + receiver.city)) # payer postalno and city

        c.drawText(textObject)
        c.setFontSize(11)

        # Reference information
        c.drawString(margin2, getY(25), "Käytäthän maksaessasi viitenumeroa.")
        ref = reference[:5] + " " + reference[5:]
        c.drawString(margin3, getY(30), ref)
        c.drawString(margin3, getY(34), duedate)

        # Amount
        amount = None
        memberList = [config[4]]
        parser = csv.reader(memberList)
        memberString = []
        for fields in parser:
            for field in fields:
                string = field.split(",")
                member = string[0] + ":" + string[1]
                memberString.append(member)

        for item in memberString:
            cl = item.split(':')
            if cl[0].lower() == receiver.membertype.lower():
                if len(cl[1].split('.')) > 1:
                    amount = cl[1]
                else:
                    amount = cl[1] + ".00"

        if amount == None:
            amount = ""

        c.drawString((margin3+transSizeX*40), getY(34), amount)

        virtualbc, bc_img = createBarcode(reference, config[3], amount, duedate, i)
        c.setFontSize(9.4)
        c.drawString(37, 22+transSizeY*12, virtualbc)
        c.drawImage(bc_img, 30, 17, transSizeX*105, transSizeY*12, preserveAspectRatio=False)

        c.showPage()
    except Exception as e:
        logging.exception(e)


def createAllInvoices(config, receivers, subject, path, message, duedate, reference, yearbool, logo=None):
    """Create multiple invoices to one PDF
    Args:
    config = config list,
    receivers = list of receiver objects
    path = path to output folder
    message = message to be attached to the invoice
    duedate = due date of the invoice as a string
    subject = subject line of the invoice
    logo = path to the logo file if spesified. Default None
    
    Returns path to file.
    Returns -1 if PermissionError (file opened in a another application)
    """
    logging.info("Create All Invoices {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}".format(config, receivers, subject, path, message, duedate, reference, yearbool, logo))

    try:

        limit = len(receivers)
        sg.theme(config[0])
        layout = [[sg.Text("Luodaan laskuja...", font=("Verdana", 12))],
                [sg.ProgressBar(limit, orientation='h', size=(30, 20), key='progressbar')],
                [sg.Button('Peruuta', font=("Verdana", 12))]]

        window = sg.Window('Laskujen luonti', layout)
        progress_bar = window['progressbar']

        date = datetime.date.today().strftime("%d-%m-%Y")
        clock = time.strftime("%H-%M-%S")
        year = datetime.date.today().strftime("%Y")
        name = "Laskut_" + date + "_" + clock + ".pdf"
        pdfPath = os.path.join(path, name)
        c = canvas.Canvas(pdfPath, pagesize=A4)

        i = 0
        for item in receivers:
            event, values = window.read(timeout=1)
            if event == 'Peruuta' or event is None:
                return -2
            if yearbool != True:
                ret = definePage(c, config, receivers[i], path, message, duedate, subject, reference, i, logo)
                if ret == -1:
                    return -2
                logging.debug("yearbool == False")
            elif yearbool == True and receivers[i].paymentyear != year:
                ret = definePage(c, config, receivers[i], path, message, duedate, subject, reference, i, logo)
                if ret == -1:
                    return -2
                logging.debug("yearbool == True and paymentyear != year")
            else:
                logging.debug("Skipping invoice creation on condition; yearbool:{0}, year:{1}, payer:{2}".format(yearbool, year, receivers[i].paymentyear))
                i += 1
                continue
            i += 1
            progress_bar.UpdateBar(i)
            time.sleep(0.2)

        window.close()
    except Exception as e:
        logging.exception(e)

    try:
        c.save()
    except Exception as e:
        logging.exception(e)
        return -1

    return pdfPath

def createInvoice(config, receiver, path, message, duedate, subject, reference, i, logo=None, preview=False):
    """Create invoices for single receiver.
    Args:
    config = config list,
    receivers = list of receiver objects
    path = path to output folder
    message = message to be attached to the invoice
    duedate = due date of the invoice as a string
    subject = subject line of the invoice
    reference = Reference number for the invoice
    i = index number for barcode
    logo = path to the logo file if spesified. Default None
    preview = Wheter the created file should be named preview, default False

    Returns the path to the created pdf.
    Returns -1 if PermissionError (file opened in a another application)
    Returns -2 if other error
    """
    logging.info("Create Invoice {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}".format(config, receiver, subject, path, message, duedate, reference, logo, preview))

    try:

        #canvas settings
        if preview == False:
            name = receiver.firstname + "_" + receiver.lastname + ".pdf"
        else:
            path = os.path.join(os.getenv("APPDATA") + "\\Haukiposti")
            name = "preview.pdf"
        pdfPath = os.path.join(path, name)
        c = canvas.Canvas(pdfPath, pagesize=A4)

        ret = definePage(c, config, receiver, path, message, duedate, subject, reference, i, logo)
        if ret == -1:
            return -2
    except Exception as e:
        logging.exception(e)

    # save document
    try:
        c.save()
    except Exception as e:
        logging.exception(e)
        return -1

    return pdfPath

def sticker(c, name, address, postal, contact, x, y, fontsize):
    textObject = c.beginText()
    textObject.setTextOrigin(x, y)
    textObject.setFont("Helvetica", fontsize)
    textObject.textLine(name)
    if contact != "":
        textObject.textLine(contact)
    textObject.textLine(address)
    textObject.textLine(postal)

    c.drawText(textObject)


def stickersheet(path, receivers, paper, sx, sy, div):
    """Makes a stickersheet.
    Args:
    path = Path to output folder
    receivers = list of receiver objects
    paper = paper size
    sx = number of stickers in x direction
    sy = number of stickers in y direction
    div = amount of empty space between stickers in mm in x direction

    Returns path to file on success, -1 if PermissionError, -2 if other error"""
    
    logging.info("Create stickersheet {0}, {1}, {2}, {3}, {4}, {5}".format(path, receivers, paper, sx, sy, div))
    if paper == "A4":
        page = A4
        leveys, korkeus = A4
        transSizeX = leveys / 210
        transSizeY = korkeus / 297
    else:
        return -2

    date = datetime.date.today().strftime("%d-%m-%Y")
    clock = time.strftime("%H-%M-%S")
    year = datetime.date.today().strftime("%Y")
    name = "Tarra-arkki_" + date + "_" + clock + ".pdf"
    pdfPath = os.path.join(path, name)
    c = canvas.Canvas(pdfPath, pagesize=page)
    # c.translate(leveys, korkeus)

    c.setSubject("Tarra-arkit")
    c.setCreator(("Haukiposti "+common.version()))

    stickerx = ((210-((sx-1)*div))/sx)*mm
    stickery = ((297-sy)/sy)*mm
    totalPerPage = sx*sy
    marginx = 5*mm
    marginy = 4*mm
    div = div*mm

    # font
    if sx < 5:
        fontsize = 13
    elif sx < 6 :
        fontsize = 9
    elif sx < 7:
        fontsize = 5
    

    i = 1
    j = 1
    k = 1
    x = marginx
    y = korkeus-marginy-3*mm
    for receiver in receivers:
        logging.debug("begin, {0}".format(k))
        name = receiver.firstname + " " + receiver.lastname
        postal = receiver.postalno + " " + receiver.city
        sticker(c, name, receiver.address, postal, receiver.contact, x, y, fontsize)
        k += 1

        if j == sy and i == sx:
            c.showPage()
            i = 1
            j = 1
            x = marginx
            y = korkeus-marginy-4*mm
            logging.debug("j == sy, {0}, {1}".format(x, y))
        elif i < sx:
            x += stickerx + div
            i += 1
            logging.debug("i<sx, {0}".format(x))
        elif i == sx:
            x = marginx
            y -= stickery
            i = 1
            j += 1
            logging.debug("i == sx, {0}, {1}, {2}, {3}".format(x, y, j, sy))

    try:
        c.save()
    except PermissionError as e:
        logging.exception(e)
        return -1

    return pdfPath