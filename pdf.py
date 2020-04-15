try:
    import logging, common, barcode, os, random, datetime, time
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
except Exception as e:
    logging.error(e)

def getY(x):
    y = 48-x
    unit = 0
    unit += inch*(1/12)*y
    return unit

def createBarcode():
    """Create barcode image"""
    pass

def virtualBarcode():
    """Create virtual barcode number and return it as a string"""
    pass

def reference():
    """Create a reference number and check it's validity"""

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

    i = 0
    for item in receivers:
        if logo:
            c.drawImage(logo, 25, korkeus-110, width=110, height=110, preserveAspectRatio=True)
        c.line(25, korkeus-100, leveys-25, korkeus-100)
        c.drawImage(base, 0, 0, width=(transSizeX*210), height=(transSizeY*101.6), preserveAspectRatio=True) # bank transfer base
        
        c.setFont("Helvetica-Bold", 18)
        c.drawString(250, korkeus-60, subject)
        c.setFont("Helvetica", 11)

        c.drawString(margin, getY(5), config[3]) # receiver account number
        c.drawString(margin, getY(11), config[2]) # payment receiver
        c.setFontSize(15)
        c.drawString(margin2, getY(5), "OKOYFIHH") # TODO: dynamic BIC code

        # Payer information
        textObject = c.beginText()
        textObject.setTextOrigin(margin, getY(16))
        textObject.setFont("Helvetica", 11)
        textObject.textLine((receivers[i].firstname+" "+receivers[i].lastname)) # payer name
        if receivers[i].contact != None:
            textObject.textLine(receivers[i].contact) # payer contact, if any
        textObject.textLine(receivers[i].address) # payer address
        textObject.textLine((receivers[i].postalno + " " + receivers[i].city)) # payer postalno and city

        c.drawText(textObject)
        c.setFontSize(11)

        c.drawString(margin2, getY(25), "Käytäthän maksaessasi viitenumeroa.")
        c.drawString(margin3, getY(30), reference)
        c.drawString(margin3, getY(34), duedate)
        c.showPage() #Finish page

    try:
        c.save()
    except PermissionError as e:
        logging.error(e)
        return -1

    return pdfPath

def createInvoice(config, receiver, path, message, duedate, subject, reference, logo=None):
    """Create invoices for single receiver.
    Args:
    config = config list,
    receivers = list of receiver objects
    path = path to output folder
    message = message to be attached to the invoice
    duedate = due date of the invoice as a string
    subject = subject line of the invoice
    reference = Reference number for the invoice
    logo = path to the logo file if spesified. Default None

    Returns the path to the created pdf.
    Returns -1 if PermissionError (file opened in a another application)
    """
    #canvas settings
    name = receiver.firstname + "_" + receiver.lastname + ".pdf"
    pdfPath = os.path.join(path, name)
    c = canvas.Canvas(pdfPath, pagesize=A4)

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

    c.drawString(margin2, getY(25), "Käytäthän maksaessasi viitenumeroa.")
    c.drawString(margin3, getY(30), reference)
    c.drawString(margin3, getY(34), duedate)

    #TODO dynamic sum
    c.drawString((margin3+transSizeX*40), getY(34), "500,00€")

    # save document
    c.showPage()
    try:
        c.save()
    except PermissionError as e:
        logging.error(e)
        return -1

    return pdfPath