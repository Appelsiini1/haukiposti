try:
    import logging, common, barcode, os
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
except Exception as e:
    logging.error(e)

def createBarcode():
    """Create barcode image"""
    pass

def virtualBarcode():
    """Create virtual barcode number and return it as a string"""
    pass

def tilisiirto():
    #Might be unnecessary
    pass

def reference():
    """Create a reference number and check it's validity"""
    pass

def createAllInvoices(config, receivers, path, message, duedate, logo, subject):
    """Create multiple invoices to one PDF
    Args:
    config = config list,
    receivers = list of receiver objects
    path = path to output folder
    message = message to be attached to the invoice
    duedate = due date of the invoice as a string
    logo = path to the logo file if spesified. Can be None
    subject = subject line of the invoice
    """
    pdfPath = None
    c = canvas.Canvas(pdfPath, pagesize=A4)
    leveys, korkeus = A4

    for i in receivers:
        #TODO: invoice definition
        c.showPage() #Finish page

    c.save()

def createInvoice(config, receiver, path, message, duedate, logo, subject):
    """Create invoices for single receiver.
    Args:
    config = config list,
    receivers = list of receiver objects
    path = path to output folder
    message = message to be attached to the invoice
    duedate = due date of the invoice as a string
    logo = path to the logo file if spesified. Can be None
    subject = subject line of the invoice
    """
    pdfPath = None
    c = canvas.Canvas(pdfPath, pagesize=A4)
    leveys, korkeus = A4


    c.showPage()
    c.save()