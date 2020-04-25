import PySimpleGUI as sg
import common

def stickersheet(configs):

    # -- Theme --
    sg.theme(configs[0])

    # -- Menu definition --
    menu_def = [["Tiedosto", ["Poistu"]],
                ["Tietoa", ["Apua", "Tietoa"]]]

    # -- The layout --
    frame_layout = [[sg.Text("Tarroja leveyssuunnassa", size=(22,1), font=("Verdana", 12)), sg.Spin([i for i in range(1,11)], size=(2,1))],
                    [sg.Text("Tarroja korkeussuunnassa", size=(22,1), font=("Verdana", 12)), sg.Spin([i for i in range(1,11)], size=(2,1))],
                    [sg.Text("Tarraväli (mm)", font=("Verdana", 12)), sg.Slider(range=(0,10), default_value=0, resolution=(0.1), size=(20,15), orientation="horizontal", font=("Verdana", 9))],
                    [sg.Text("", font=("Verdana", 4))]]

    layout = [ [sg.Menu(menu_def)],
                [sg.Text("Haukiposti - tarra-arkki", font=("Verdana", 15, "bold"))],
                [sg.Input("", key="receivers"), sg.FileBrowse("Tuo jäsentiedot", file_types=(('CSV taulukot', '*.csv*'),))],
                [sg.Checkbox("Vain ilman sähköpostia", font=("Verdana", 12))],
                [sg.Text("Paperikoko", font=("Verdana", 12), pad=(1,25)), sg.Combo(["choice 1", "choice 2"])],
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
        elif event == "Apua":
            sg.PopupOK("Tarra-arkit.")
        elif event == "Tietoa":
            sg.PopupOK("Haukiposti {0}\n\nRami Saarivuori\nAarne Savolainen\n(c) 2020".format(common.version()), font=("Verdana", 12))
        elif event in (None, "Poistu"):
            exit()

    window.close()