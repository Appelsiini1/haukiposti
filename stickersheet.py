import PySimpleGUI as sg
import common, pdf, os, logging

def stickersheet(configs):

    # -- Theme --
    sg.theme(configs[0])

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Tietoa", ["Apua", "Tietoa", "Lisenssit"]]]

    # -- The layout --
    frame_layout = [[sg.Text("Tarroja leveyssuunnassa", size=(22,1), font=("Verdana", 12)), sg.Spin([i for i in range(1,7)], size=(2,1), key="x")],
                    [sg.Text("Tarroja korkeussuunnassa", size=(22,1), font=("Verdana", 12)), sg.Spin([i for i in range(1,16)], size=(2,1), key="y")],
                    [sg.Text("Tarraväli (mm)", font=("Verdana", 12)), sg.Slider(range=(0,10), default_value=0, resolution=(0.1), size=(20,15), orientation="horizontal", font=("Verdana", 9), key="div")],
                    [sg.Text("", font=("Verdana", 4))]]

    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti - tarra-arkki", font=("Verdana", 15, "bold"))],
                [sg.Text("Jäsentiedot", font=("Verdana", 12))],
                [sg.Input("", key="receivers"), sg.FileBrowse("Tuo jäsentiedot", file_types=(('CSV taulukot', '*.csv'),))],
                [sg.Checkbox("Vain ilman sähköpostia", font=("Verdana", 12), key="email")],
                [sg.Text("Paperikoko", font=("Verdana", 12), pad=(1,25)), sg.Combo(["A4"], key="paper")],
                [sg.Frame("Tarrakoko", frame_layout, font=("Verdana", 12))],
                [sg.Text("")], # some space between stuff
                [sg.Text("Kohdekansio:", font=("Verdana", 12)), sg.Input("", key="targetfolder"), sg.FolderBrowse("Selaa...", target="targetfolder")],
                [sg.Button("Luo", size=(7,1)), sg.Button("Peruuta", size=(7,1))]]

    window = sg.Window("Haukiposti - tarra-arkki", layout)

    # -- Window functionality --
    while True:
        event, values = window.read()

        if event == "Peruuta":
            break
        elif event == "Luo":
            try:
                receivers = common.CSVparser(values['receivers'])
                if receivers:
                    if values['targetfolder'] != "" and values['paper'] != "":
                        path = pdf.stickersheet(values['targetfolder'], receivers, values['paper'], int(values['x']), int(values['y']), values['div'], values['email'])
                        if path == -1:
                            sg.PopupOK("Tiedostoa ei voitu luoda, tiedosto on jonkin toisen prosessin käytössä.")
                        elif path == -2:
                            sg.PopupOK("Jokin meni vikaan arkkia luodessa.")
                        else:
                            command = 'cmd /c "start "" "' + path + '"'
                            os.system(command)
                    else:
                        sg.PopupOK("Tarkista, kaikki kentät on täytetty.")
                        logging.info("Some fields empty")
                else:
                    sg.PopupOK("CSV-tiedoston lukemisessa tapahtui virhe.")
                    logging.error("CSV read error")
            except Exception as e:
                logging.exception(e)
        elif event == "Apua":
            sg.PopupOK("Tarra-arkkien luonti. Määritä arkin koko, tarrojen lukumäärä (leveys- ja korkeussuunnassa)\nsekä anna vastaanottajat sisältävä CSV tiedosto. Tarra-arkit luodaan yhteen tiedostoon antamaasi kohdekansioon.", font=("Verdana", 12))
        elif event == "Tietoa":
            sg.PopupOK("Haukiposti {0}\n\nRami Saarivuori\nAarne Savolainen\n(c) 2020".format(common.version()), font=("Verdana", 12))
        elif event == "Lisenssit":
            sg.popup_scrolled(common.licenses(), font=("Verdana", 12), title="Haukiposti - Lisenssit")
        elif event in (None, "Poistu"):
            exit()

    window.close()