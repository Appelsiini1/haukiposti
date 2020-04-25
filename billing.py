import PySimpleGUI as sg
import pdf, common, datetime, logging, emailFunc, os, time

def billing(configs, service=None):

    year = datetime.date.today().strftime("%Y")

    # -- Theme --
    sg.theme(configs[0])

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Tietoa", ["Apua", "Tietoa"]]]

    # -- The layout --
    message_frame_layout = [[sg.Text("Aihe", font=("Verdana", 12))],
                            [sg.InputText("", key="subject")],
                            [sg.Text("Viesti", font=("Verdana", 12), key="messageText")],
                            [sg.Multiline(key=("messageText"), size=(60,9))],
                            [sg.Text("Liitteet", font=("Verdana", 12)), sg.Input("", key="attachment"), sg.FilesBrowse("Selaa...", font=("Verdana", 12))]]

    bill_frame_layout = [[sg.Text("Eräpäivä", font=("Verdana", 12))],
                [sg.Input("", key="duedate"), sg.CalendarButton("Valitse...", font=("Verdana", 12), key="duebtn", target=("invisible")), sg.Input("", key="invisible", enable_events=True, visible=False)],
                [sg.Text("Logo", font=("Verdana", 12)), sg.Input(""), sg.FileBrowse("Selaa...", font=("Verdana", 12))],
                [sg.Text("Saate", font=("Verdana", 12))],
                [sg.Multiline(key="billText", size=(60,5))],
                [sg.Text("Laskujen kohdekansio:", font=("Verdana", 12)), sg.Input("", key=("folder")), sg.FolderBrowse("Selaa...", font=("Verdana", 12))],
                [sg.Checkbox('Älä luo laskuja jos maksuvuosi on {0}'.format(year), default=True, font=("Verdana", 12), key="paymentyear")]]

    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti - laskutus", font=("Verdana", 12, "bold"))],
                [sg.Text("Vastaanottajat", font=("Verdana", 12))],
                [sg.Input("", key="receivers"), sg.FileBrowse("Tuo vastaanottajat", font=("Verdana", 12), file_types=(('CSV taulukot', '*.csv*'),))],
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
                if ret == -1:
                    sg.PopupOK("Tiedostoa ei voitu luoda")
            
            # To individual files
            elif filesCombined == "Erikseen" and formattedDate and values['subject'] != "" and values['folder'] != "":
                # Progress bar window layout
                limit = len(receivers)
                layout2 = [[sg.Text("Luodaan laskuja...", font=("Verdana", 12))],
                        [sg.ProgressBar(limit, orientation='h', size=(30, 20), key='progressbar')],
                        [sg.Button('Peruuta', font=("Verdana", 12))]]
                window2 = sg.Window('Laskujen luonti', layout2)
                progress_bar = window['progressbar']
                
                # Loop for pdf creation
                i = 0
                k = 0
                for receiver in receivers:
                    event, values = window2.read(timeout=1)
                    if event == 'Peruuta' or event is None:
                        break
                    # If payment year is ignored or is not the current year
                    if (values['paymentyear'] != True) or (values['paymentyear'] == True and receivers[i].paymentyear != year):
                        ret = pdf.createInvoice(configs, receivers, values['subject'], values['folder'], values['billText'], formattedDate, ref, i, values['logo'])
                        if ret == -1:
                            sg.PopupOK("Tiedostoa ei voitu luoda, keskeytetään.")
                            break
                        logging.debug("yearbool == False or (== True paymentyear != year)")
                    else:
                        logging.debug("Skipping invoice creation on condition; yearbool:{0}, year:{1}, payer:{2}".format(values['paymentyear'], year, receiver.paymentyear))
                        k += 1
                        continue
                    i += 1
                    progress_bar.UpdateBar(i)

                # Error checking
                if ret != -1 or event != 'Peruuta':
                    sg.PopupOK("{0} laskua luotu kohdekansioon. Ohitettiin {1} vastaanottajaa.".format(i, k))
                    logging.info("{0} invoices created to {1}. Skipped {2} receivers".format(i, values['folder'], k))

            else:
                sg.PopupOK("Jotkin kohdat ovat tyhjiä. Varmista, että seuraavat kentät ovat täytetty: Aihe, Laskujen kohdekansio & Eräpäivä.")

        # Send
        elif event == "Lähetä":
            ok = sg.PopupOKCancel("Haluatko varmasti lähettää viestin?")
            if ok.lower() == "ok":
                if service == None:
                    sg.PopupOK("Et ole kirjautunut. Sinut kirjataan nyt sisään.")
                    service = emailFunc.authenticate()

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
                progress_bar = window['progressbar']

                # loop for sending
                for receiver in receivers:
                    event, values = window2.read(timeout=1)
                    if event == 'Peruuta' or event is None:
                        break

                    # If payment year is ignored or is not the current year
                    if (values['paymentyear'] != True) or (values['paymentyear'] == True and receivers[i].paymentyear != year):
                        ret = pdf.createInvoice(configs, receivers, values['subject'], values['folder'], values['billText'], formattedDate, ref, i, values['logo'])
                        if ret == -1:
                            sg.PopupOK("Tiedostoa ei voitu luoda, keskeytetään.")
                            break
                        else:
                            attachements = values["attachment"].split(';')
                            size = 0
                            attachements.append(ret) # add the invoice to attachments
                            if attachements[0] != '':
                                # size check
                                for item in attachements:
                                    size += os.path.getsize(item)
                                if size > 24000000:
                                    sg.PopupOK("Liitteiden koko on suurempi kuin salittu 23 Mt.")
                                    ret = -1
                                    break
                                else:
                                    # send message
                                    htmlText = common.TagsToHTML(values["messageText"], attachements, preview=0)
                                    encMsg = emailFunc.createMail(configs[1], receiver.email, values["subject"], htmlText, attachements)
                                    if encMsg:
                                        msg = emailFunc.sendMail(service, 'me', encMsg)
                                        if msg:
                                            sg.PopupOK("Viestin lähetys onnistui.")
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
                    time.sleep(0.1)

                # error checking
                if ret != -1 or event != 'Peruuta':
                    sg.PopupOK("{0} laskua luotiin kohdekansioon ja lähetettiin. Ohitettiin {1} vastaanottajaa.".format(i, k))
                    logging.info("{0} invoices created to {1}. Skipped {2} receivers".format(i, values['folder'], k))

        elif event == "Apua":
            apua = """Laskutus. Täältä voit lähettää laskuja.\n
    Valitse vastaanottajat sisältävä CSV tiedosto, mahdolliset liitteet, kirjoita heille viesti ja lähetä.\n\n
    Tekstin erikoismerkit:\n
    **tekstiä** == Lihavoitu\n
    __tekstiä__ == Kursivoitu\n
    ||tekstiä|| == Alleviivattu\n
    @@linkki@@tekstiä@@ == Tekstin seassa oleva linkki. Mikäli haluat linkin näkyvän linkkinä, kopioi linkki myös tekstin paikalle.\n
    $$img$$ == Tekstin seassa olevat kuvat määritetään tällä tagilla. Valitse kuvat liitteeksi. Liitteiden järjestyksellä ei ole väliä.\n
    Jos haluat kuvan olevan linkki, laita $$img$$ tägi tekstin paikalle linkkitägissä. (eli @@linkki@@$$img$$@@)"""
            sg.PopupOK(apua, title="Apua", font=("Verdana", 12))
        elif event == "Tietoa":
            sg.PopupOK("Haukiposti {0}\n\nRami Saarivuori\nAarne Savolainen\n(c) 2020".format(common.version()), font=("Verdana", 12))
        elif event in (None, "Poistu"):
            exit()

    window.close()