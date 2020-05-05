import PySimpleGUI as sg
import pdf, common, datetime, logging, emailFunc, os, time, masspost

def billing(configs, service=None):

    year = datetime.date.today().strftime("%Y")

    # barcode folder
    barcodepath = os.path.join(os.getenv("APPDATA"), "Haukiposti", "barcodes")
    try:
        os.mkdir(barcodepath)
    except FileExistsError as e:
        logging.exception(e)
        pass

    # -- Theme --
    sg.theme(configs[0])

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Tietoa", ["Apua", "Tietoa", "Lisenssit"]]]

    # -- The layout --
    message_frame_layout = [[sg.Text("Aihe", font=("Verdana", 12))],
                            [sg.InputText("", key="subject")],
                            [sg.Text("Viesti", font=("Verdana", 12))],
                            [sg.Multiline(key="messageText", size=(60,9))],
                            [sg.Text("Liitteet", font=("Verdana", 12)), sg.Input("", key="attachment"), sg.FilesBrowse("Selaa...", font=("Verdana", 12))]]

    bill_frame_layout = [[sg.Text("Eräpäivä", font=("Verdana", 12))],
                [sg.Input("", key="duedate"), sg.CalendarButton("Valitse...", font=("Verdana", 12), key="duebtn", target=("invisible")), sg.Input("", key="invisible", enable_events=True, visible=False)],
                [sg.Text("Logo", font=("Verdana", 12)), sg.Input("", key='logo'), sg.FileBrowse("Selaa...", font=("Verdana", 12))],
                [sg.Text("Saate", font=("Verdana", 12))],
                [sg.Multiline(key="billText", size=(60,5))],
                [sg.Text("Laskujen kohdekansio:", font=("Verdana", 12)), sg.Input("", key=("folder")), sg.FolderBrowse("Selaa...", font=("Verdana", 12))],
                [sg.Checkbox('Älä luo laskuja jos maksuvuosi on {0}'.format(year), default=True, font=("Verdana", 12), key="paymentyear")]]

    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti - laskutus", font=("Verdana", 12, "bold"))],
                [sg.Text("Vastaanottajat", font=("Verdana", 12))],
                [sg.Input("", key="receivers"), sg.FileBrowse("Tuo vastaanottajat", font=("Verdana", 12), file_types=(('CSV taulukot', '*.csv'),))],
                [sg.Frame("Viesti", message_frame_layout, font=("Verdana", 12)), sg.Frame("Lasku", bill_frame_layout, font=("Verdana", 12))],
                [sg.Button("Luo laskut", font=("Verdana", 12)), sg.Button("Lähetä", font=("Verdana", 12)), sg.Button("Esikatsele", font=("Verdana", 12)), sg.Button("Peruuta", font=("Verdana", 12))]]

    window = sg.Window("Haukiposti - laskutus", layout)

    # reference number generation
    ref = pdf.reference()

    # -- Window functionality --
    while True:
        event, values = window.read()

        # Cancel
        if event == "Peruuta":
            break
        elif event == "invisible":
            date = values["invisible"]
            formattedDate = date[8:10] + "." + date[5:7] + "." + date[:4]
            window["duedate"].update(value=formattedDate)

        # Create invoices
        elif event == "Luo laskut":
            receivers = common.CSVparser(values["receivers"])
            if receivers == None:
                sg.PopupOK("Tuo ensin CSV-tiedosto")
                continue
            filesCombined = sg.Popup("Luo laskut erikseen vai yhteen tiedostoon?", custom_text=("Yhteen", "Erikseen"))

            # To one file
            if filesCombined == "Yhteen" and formattedDate and values['subject'] != "" and values['folder'] != "":
                ret = pdf.createAllInvoices(configs, receivers, values['subject'], values['folder'], values['billText'], formattedDate, ref, values['paymentyear'], values['logo'])
                if ret == -1 or ret  == -2:
                    sg.PopupOK("Tiedostoa ei voitu luoda")
            
            # To individual files
            elif filesCombined == "Erikseen" and formattedDate and values['subject'] != "" and values['folder'] != "":
                # Progress bar window layout
                limit = len(receivers)
                layout2 = [[sg.Text("Luodaan laskuja...", font=("Verdana", 12))],
                        [sg.ProgressBar(limit, orientation='h', size=(30, 20), key='progressbar')],
                        [sg.Button('Peruuta', font=("Verdana", 12))]]
                window2 = sg.Window('Laskujen luonti', layout2)
                progress_bar = window2['progressbar']
                
                # Loop for pdf creation
                i = 0
                k = 0
                ret = 0
                payyear = values['paymentyear']
                for receiver in receivers:
                    event, values2 = window2.read(timeout=1)
                    if event == 'Peruuta' or event is None:
                        break
                    # If payment year is ignored or is not the current year
                    if (payyear != True) or (payyear == True and receiver.paymentyear != year):
                        ret = pdf.createInvoice(configs, receiver, values['folder'], values['billText'], formattedDate, values['subject'], ref, i, values['logo'])
                        if ret == -1 or ret  == -2:
                            sg.PopupOK("Tiedostoa ei voitu luoda, keskeytetään.")
                            break
                        logging.debug("yearbool == False or (== True paymentyear != year)")
                    else:
                        logging.debug("Skipping invoice creation on condition; yearbool:{0}, year:{1}, payer:{2}".format(payyear, year, receiver.paymentyear))
                        k += 1
                        continue
                    i += 1
                    progress_bar.UpdateBar(i)
                    time.sleep(0.2)

                # Error checking
                if ret != -1 and ret != -2 and event != 'Peruuta':
                    window2.close()
                    sg.PopupOK("{0} laskua luotu kohdekansioon. Ohitettiin {1} vastaanottajaa.".format(i, k))
                    logging.info("{0} invoices created to {1}. Skipped {2} receivers".format(i, values['folder'], k))

            else:
                sg.PopupOK("Jotkin kohdat ovat tyhjiä. Varmista, että seuraavat kentät ovat täytetty: Aihe, Laskujen kohdekansio & Eräpäivä.")

        # Send
        elif event == "Lähetä":
            ok = sg.Popup("Haluatko varmasti lähettää viestin?", custom_text=("Kyllä", "Ei"))
            if ok == "Kyllä":
                if service == None:
                    yesno = sg.Popup("Et ole kirjautunut sisään. Haluatko kirjautua sisään nyt?", custom_text=("Kyllä", "Ei"))
                    if yesno == "Kyllä":
                        service = emailFunc.authenticate()
                    else:
                        continue

                receivers = common.CSVparser(values["receivers"])
                if receivers == None:
                    sg.PopupOK("Tuo ensin CSV-tiedosto")
                    continue

                # layout for progress bar window
                limit = len(receivers)
                layout2 = [[sg.Text("Luodaan laskut ja lähetetään viestit...", font=("Verdana", 12))],
                        [sg.ProgressBar(limit, orientation='h', size=(30, 20), key='progressbar')],
                        [sg.Button('Peruuta', font=("Verdana", 12))]]
                window2 = sg.Window('Laskujen luonti & lähetys', layout2)
                progress_bar = window2['progressbar']

                # loop for sending
                i = 0
                k = 0
                ret = 0
                for receiver in receivers:
                    event, values2 = window2.read(timeout=1)
                    if event == 'Peruuta' or event is None:
                        break

                    if receiver.email == "":
                        continue

                    # If payment year is ignored or is not the current year
                    if (values['paymentyear'] != True) or (values['paymentyear'] == True and receiver.paymentyear != year):
                        ret = pdf.createInvoice(configs, receiver, values['folder'], values['billText'], formattedDate, values['subject'], ref, 0, values['logo'])
                        if ret == -1 or ret  == -2:
                            sg.PopupOK("Tiedostoa ei voitu luoda, keskeytetään.")
                            break
                        else:
                            attachments = values["attachment"].split(';')
                            size = 0
                            attachments.append(ret) # add the invoice to attachments
                            if attachments[0] != '':
                                # size check
                                for item in attachments:
                                    size += os.path.getsize(item)
                                if size > 24000000:
                                    sg.PopupOK("Liitteiden koko on suurempi kuin salittu 23 Mt.")
                                    ret = -1
                                    break
                                else:
                                    # send message
                                    htmlText = common.markdownParserHTML(values["messageText"], attachments, preview=0)
                                    encMsg = emailFunc.createMail(configs[1], receiver.email, values["subject"], htmlText, attachments)
                                    if encMsg:
                                        msg = emailFunc.sendMail(service, 'me', encMsg)
                                        if msg:
                                            logging.debug(msg)
                                            logging.info("Message sent.")
                                    else:
                                        sg.PopupOK("Jokin meni vikaan viestiä luotaessa. Viestiä ei lähetetty. Keskeytetään.")
                                        break
                        logging.debug("yearbool == False or (== True paymentyear != year)")
                    else:
                        logging.debug("Skipping invoice creation on condition; yearbool:{0}, year:{1}, payer:{2}".format(values['paymentyear'], year, receiver.paymentyear))
                        k += 1
                        continue
                    i += 1
                    progress_bar.UpdateBar(i)
                    time.sleep(0.2)

                # error checking
                if ret != -1 and ret != -2 and event != 'Peruuta':
                    window2.close()
                    sg.PopupOK("{0} laskua luotiin kohdekansioon ja lähetettiin. Ohitettiin {1} vastaanottajaa.".format(i, k))
                    logging.info("{0} invoices created to {1}. Skipped {2} receivers".format(i, values['folder'], k))

        elif event == "Esikatsele":
            receivers = common.CSVparser(values["receivers"])
            if receivers == None:
                sg.PopupOK("Tuo ensin CSV-tiedosto")
                continue
            if (values['paymentyear'] != True) or (values['paymentyear'] == True):
                ret = pdf.createInvoice(configs, receivers[0], values['folder'], values['billText'], formattedDate, values['subject'], ref, 0, values['logo'])
                if ret == -1 or ret  == -2:
                    sg.PopupOK("Tiedostoa ei voitu luoda, keskeytetään.")
                    continue
                else:
                    command = 'cmd /c "start "" "' + ret + '"'
                    os.system(command)

                attachments = values["attachment"].split(';')
                text = values["messageText"]
                if masspost.preview(text, attachments) == -1:
                    sg.PopupOK("Tekstin muunnos epäonnistui. Todennäköisesti jotakin tiedostoa ei voitu avata.")
                

        elif event == "Apua":
            apua = """Laskutus. Täältä voit lähettää laskuja.\n
    Valitse vastaanottajat sisältävä CSV tiedosto, mahdolliset liitteet, kirjoita heille viesti ja lähetä.\n\n
    Tekstin erikoismerkit:\n
    **tekstiä** == Lihavoitu\n
    ||tekstiä|| == Kursivoitu\n
    __tekstiä__ == Alleviivattu\n
    @@linkki@@tekstiä@@ == Tekstin seassa oleva linkki. Mikäli haluat linkin näkyvän linkkinä, kopioi linkki myös tekstin paikalle.\n
    $$img$$ == Tekstin seassa olevat kuvat määritetään tällä tagilla. Valitse kuvat liitteeksi. Liitteiden järjestyksellä ei ole väliä.\n
    Jos haluat kuvan olevan linkki, laita $$img$$ tägi tekstin paikalle linkkitägissä. (eli @@linkki@@$$img$$@@)\n
    \nHUOM! Alleviivaus, linkit ja kuvat eivät toimi saatekirjeessä."""
            sg.PopupOK(apua, title="Apua", font=("Verdana", 12))
        elif event == "Tietoa":
            sg.PopupOK("Haukiposti {0}\n\nRami Saarivuori\nAarne Savolainen\n(c) 2020".format(common.version()), font=("Verdana", 12))
        elif event == "Lisenssit":
            sg.popup_scrolled(common.licenses(), font=("Verdana", 12), title="Haukiposti - Lisenssit")
        elif event in (None, "Poistu"):
            exit()

    window.close()