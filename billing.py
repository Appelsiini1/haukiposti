import PySimpleGUI as sg
import pdf

def billing(configs):

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
                [sg.Text("Logo", font=("Verdana", 12)), sg.Input(""), sg.FileBrowse("Selaa...")],
                [sg.Text("Saate", font=("Verdana", 12))],
                [sg.Multiline(key="billText", size=(60,5))],
                [sg.Text("Laskujen kohdekansio:", font=("Verdana", 12)), sg.Input("", key=("folder")), sg.FolderBrowse("Selaa...")],
                [sg.Button("Lähetä", font=("Verdana", 12)), sg.Button("Esikatsele", font=("Verdana", 12)), sg.Button("Peruuta", font=("Verdana", 12)), sg.Button("Luo laskut", font=("Verdana", 12))]]

    window = sg.Window("Haukiposti - massaposti", layout)

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
            filesCombined = sg.Popup("Luo laskut erikseen vai yhteen tiedostoon?", custom_text=("Yhteen", "Erikseen"))
            print(filesCombined)
        elif event == "Lähetä":
            print(values["folder"])
            print(configs[4])
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
            sg.PopupOK("Haukiposti V0.5\n\nRami Saarivuori\nAarne Savolainen\n(c) 2020", font=("Verdana", 12))
        elif event in (None, "Poistu"):
            exit()

    window.close()