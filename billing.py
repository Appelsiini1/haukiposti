import PySimpleGUI as sg
import pdf, common, datetime, logging, emailFunc

def billing(configs, service=None):

    year = datetime.date.today().strftime("%Y")

    # -- Theme --
    sg.theme(configs[0])

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Tietoa", ["Apua", "Tietoa"]]]

    # -- The layout --
    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti - laskutus", font=("Verdana", 12, "bold"))],
                [sg.Text("Vastaanottajat", font=("Verdana", 12))],
                [sg.Input("", key="receivers"), sg.FileBrowse("Tuo vastaanottajat", file_types=(('CSV taulukot', '*.csv*'),))],
                [sg.Text("Eräpäivä", font=("Verdana", 12))],
                [sg.Input("", key="duedate"), sg.CalendarButton("Valitse...", key="duebtn", target=("invisible")), sg.Input("", key="invisible", enable_events=True, visible=False)],
                [sg.Text("Aihe", font=("Verdana", 12))],
                [sg.InputText("", key="subject")],
                [sg.Text("Viesti", font=("Verdana", 12))],
                [sg.Multiline(key=("messageText"), size=(60,5))],
                [sg.Text("Logo", font=("Verdana", 12)), sg.Input("", key="logo"), sg.FileBrowse("Selaa...")],
                [sg.Text("Saate", font=("Verdana", 12))],
                [sg.Multiline(key="billText", size=(60,5))],
                [sg.Text("Laskujen kohdekansio:", font=("Verdana", 12)), sg.Input("", key=("folder")), sg.FolderBrowse("Selaa...")],
                [sg.Checkbox('Älä luo laskuja jos maksuvuosi on {0}'.format(year), default=True, font=("Verdana", 12), key="paymentyear")],
                [sg.Button("Luo laskut", font=("Verdana", 12)), sg.Button("Lähetä", font=("Verdana", 12)), sg.Button("Esikatsele", font=("Verdana", 12)), sg.Button("Peruuta", font=("Verdana", 12))]]

    window = sg.Window("Haukiposti - laskutus", layout)

    # reference number generation
    ref = pdf.reference()

    # -- Window functionality --
    while True:
        event, values = window.read()

        if event == "Peruuta":
            break
        elif event == "invisible":
            date = values["invisible"]
            formattedDate = date[8:10] + "." + date[5:7] + "." + date[:4]
            window["duedate"].update(value=formattedDate)
        elif event == "Luo laskut":
            receivers = common.CSVparser(values["receivers"])
            if receivers == None:
                sg.PopupOK("Tuo ensin CSV-tiedosto")
                continue
            filesCombined = sg.Popup("Luo laskut erikseen vai yhteen tiedostoon?", custom_text=("Yhteen", "Erikseen"))

            if filesCombined == "Yhteen" and formattedDate and values['subject'] != "" and values['folder'] != "":
                ret = pdf.createAllInvoices(configs, receivers, values['subject'], values['folder'], values['billText'], formattedDate, ref, values['paymentyear'], values['logo'])
                if ret == -1:
                    sg.PopupOK("Tiedostoa ei voitu luoda")
                    
            elif filesCombined == "Erikseen" and formattedDate and values['subject'] != "" and values['folder'] != "":
                limit = len(receivers)
                layout2 = [[sg.Text("Luodaan laskuja...", font=("Verdana", 12))],
                        [sg.ProgressBar(limit, orientation='h', size=(30, 20), key='progressbar')],
                        [sg.Button('Peruuta', font=("Verdana", 12))]]

                window2 = sg.Window('Laskujen luonti', layout2)
                progress_bar = window['progressbar']
                
                i = 0
                k = 0
                for receiver in receivers:
                    event, values = window2.read(timeout=1)
                    if event == 'Peruuta' or event is None:
                        break
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
                if ret != -1 or event != 'Peruuta':
                    sg.PopupOK("{0} laskua luotu kohdekansioon. Ohitettiin {1} vastaanottajaa.".format(i, k))
                    logging.info("{0} invoices created to {1}. Skipped {2} receivers".format(i, values['folder'], k))
            else:
                sg.PopupOK("Jotkin kohdat ovat tyhjiä. Varmista, että seuraavat kentät ovat täytetty: Aihe, Laskujen kohdekansio & Eräpäivä.")

        elif event == "Lähetä":
            if service == None:
                sg.PopupOK("Et ole kirjautunut. Sinut kirjataan nyt sisään.")
                service = emailFunc.authenticate()

            receivers = common.CSVparser(values["receivers"])
            if receivers == None:
                sg.PopupOK("Tuo ensin CSV-tiedosto")
                continue

            limit = len(receivers)
            layout2 = [[sg.Text("Luodaan laskut ja lähetetään viestit...", font=("Verdana", 12))],
                    [sg.ProgressBar(limit, orientation='h', size=(30, 20), key='progressbar')],
                    [sg.Button('Peruuta', font=("Verdana", 12))]]

            window2 = sg.Window('Laskujen luonti', layout2)
            progress_bar = window['progressbar']
            for receiver in receivers:
                pass
            

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