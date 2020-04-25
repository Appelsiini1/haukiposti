try:
    import logging, common, barcode, os, random, datetime, time
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from pubcode import Code128
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
    due = duedate.split('.')
    code = code + due[2][2:]
    code = code + due[1]
    code = code + due[0]

    barcode = Code128(code, charset='C')
    img = barcode.image()

    name = "barcode" + str(i) + ".png"
    imgPath = os.path.join((os.getenv("APPDATA") + "\\Haukiposti"+ "\\barcodes"), name)
    img.save(imgPath, "PNG")

    return code, imgPath

def reference():
    """Create a reference number and check it's validity
    
    Returns reference number as string.
    """

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
    ref = ref[:5] + " " + ref[5:]
        
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
    #measurements
    leveys, korkeus = A4
    transSizeX = leveys / 210
    transSizeY = korkeus / 297
    base = common.resource_path("assets/Tilisiirto_pohja.jpg")
    margin = transSizeX*27
    margin2 = transSizeX*119
    margin3 = margin2+transSizeX*18

    # Document settings
    c.setAuthor(config[2])
    c.setTitle(subject)
    c.setSubject(subject)
    c.setCreator(("Haukiposti "+common.version))

    if logo:
        c.drawImage(logo, 25, korkeus-110, width=110, height=110, preserveAspectRatio=True)
    c.line(25, korkeus-100, leveys-25, korkeus-100)
    c.drawImage(base, 0, 0, width=(transSizeX*210), height=(transSizeY*101.6), preserveAspectRatio=True) # bank transfer base
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(250, korkeus-60, subject)
    c.setFont("Helvetica", 11)

    # Receiver information
    c.drawString(margin, getY(5), config[3]) # receiver account number
    c.drawString(margin, getY(11), config[2]) # payment receiver
    c.setFontSize(15)
    c.drawString(margin2, getY(5), "OKOYFIHH") # TODO: dynamic BIC code

    # Payer information
    textObject = c.beginText()
    textObject.setTextOrigin(margin, getY(16))
    textObject.setFont("Helvetica", 11)
    textObject.textLine((receiver.firstname+" "+receiver.lastname)) # payer name
    if receiver.contact != None:
        textObject.textLine(receiver.contact) # payer contact, if any
    textObject.textLine(receiver.address) # payer address
    textObject.textLine((receiver.postalno + " " + receiver.city)) # payer postalno and city

    c.drawText(textObject)
    c.setFontSize(11)

    # Reference information
    c.drawString(margin2, getY(25), "Käytäthän maksaessasi viitenumeroa.")
    c.drawString(margin3, getY(30), reference)
    c.drawString(margin3, getY(34), duedate)

    #TODO dynamic sum
    amount = None
    c.drawString((margin3+transSizeX*40), getY(34), "500,00€")

    virtualbc, bc_img = createBarcode(reference, config[3], amount, duedate, i)
    c.setFontSize(9.5)
    c.drawString(37, 22+transSizeY*12, virtualbc)
    c.drawImage(bc_img, 30, 17, transSizeX*105, transSizeY*12, preserveAspectRatio=False)


def createAllInvoices(config, receivers, subject, path, message, duedate, reference, logo=None):
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

    date = datetime.date.today().strftime("%d-%m-%Y")
    clock = time.strftime("%H-%M-%S")
    name = "Laskut_" + date + "_" + clock + ".pdf"
    pdfPath = os.path.join(path, name)
    c = canvas.Canvas(pdfPath, pagesize=A4)

    i = 0
    for item in receivers:
        definePage(c, config, receivers[i], path, message, duedate, subject, reference, i, logo)
        i += 1

    try:
        c.save()
    except PermissionError as e:
        logging.exception(e)
        return -1

    return pdfPath

def createInvoice(config, receiver, path, message, duedate, subject, reference, i, logo=None):
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

    Returns the path to the created pdf.
    Returns -1 if PermissionError (file opened in a another application)
    """
    #canvas settings
    name = receiver.firstname + "_" + receiver.lastname + ".pdf"
    pdfPath = os.path.join(path, name)
    c = canvas.Canvas(pdfPath, pagesize=A4)

    definePage(c, config, receiver, path, message, duedate, subject, reference, i, logo)

    # save document
    c.showPage()
    try:
        c.save()
    except PermissionError as e:
        logging.exception(e)
        return -1

    return pdfPath