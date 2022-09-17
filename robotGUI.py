import PySimpleGUI as sg
import os
from os.path import exists


class RobotGUI:
    def __init__(self):
        self.configPath = ""
        self.positionsPath = ""
        self.robotsPath = ""
        self.exit = False

    def startGUI(self):
        """Displays the GUI window"""
        working_directory = os.getcwd()

        bgColour = "Black"
        LastRender = False
        configError = sg.Text("Configuration file not included!", visible=False, text_color='Red', background_color=bgColour)
        posError = sg.Text("Positions file not included!", visible=False, text_color='Red', background_color=bgColour)
        jsonError = sg.Text("Robots file not included!", visible=False, text_color='Red', background_color=bgColour)

        if(not exists('LastRender.txt')):
            layout = [
                [sg.Text("Choose a config file:", background_color=bgColour)],
                [sg.InputText(key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Configuration file", "*.txt")])], [configError],
                [sg.Text("Choose a positions file:", background_color=bgColour)],
                [sg.InputText(key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Position file", "*.txt")])], [posError],
                [sg.Text("Choose a robots file:", background_color=bgColour)],
                [sg.InputText(key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Robot file", "*.json")])], [jsonError],
                [sg.Button('Submit'), sg.Button('Help'), sg.Exit()]
            ]
        else:
            LastRender = True
            PositionsPath = ""
            ConfigPath = ""
            JSONPath = ""
            with open('LastRender.txt', 'r') as f:
                i = 0
                for line in f:
                    line = line.strip()
                    if i == 0:
                        PositionsPath = line
                    elif i == 1:
                        ConfigPath = line
                    elif i == 2:
                        JSONPath = line
                    i += 1
            layout = [
                [sg.Text("Choose a config file:", background_color=bgColour)],
                [sg.InputText(default_text=ConfigPath, key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Configuration file", "*.txt")])], [configError],
                [sg.Text("Choose a positions file:", background_color=bgColour)],
                [sg.InputText(default_text=PositionsPath, key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Position file", "*.txt")])], [posError],
                [sg.Text("Choose a robots file:", background_color=bgColour)],
                [sg.InputText(default_text=JSONPath, key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Robot file", "*.json")])], [jsonError],
                [sg.Button('Submit'), sg.Button('Help'), sg.Exit()]
            ]

        sg.theme(bgColour)
        window = sg.Window("ROBO-VIZ", layout)
        if(LastRender):
            sg.popup("Last Robot Render Settings have been loaded!!!")
        while True:
            event, values = window.read()
            # if event in (sg.WIN_CLOSED, 'Exit'):
            if event == sg.WIN_CLOSED:
                break
            if (event == 'Exit'):
                self.exit = True
                break
            if(event == "Help"):
                sg.popup("some help info\nsome more help stuff ig\neven more help text wowow", title="HELP")

            if (event == "Submit" and values["-FILE_PATH-"] == ""):
                #sg.popup("Configuration file not included!!")
                configError.update(visible=True)
            else:
                configError.update(visible=False)

            if (event == "Submit" and values["-FILE_PATH-0"] == ""):
                #sg.popup("Positions file not included!!")
                posError.update(visible=True)
            else:
                posError.update(visible=False)

            if (event == "Submit" and values["-FILE_PATH-2"] == ""):
                #sg.popup("Robots file not included!!")
                jsonError.update(visible=True)
            else:
                jsonError.update(visible=False)

            if (event == "Submit" and values["-FILE_PATH-"] != "" and values["-FILE_PATH-0"] != "" and values["-FILE_PATH-2"] != ""):
                self.configPath = values["-FILE_PATH-"]
                #self.configPath = values
                #print("sorted \n NEXT FILE!!!!")
                self.positionsPath = values["-FILE_PATH-0"]

                #print("sorted \n NEXT FILE!!!!")
                self.robotsPath = values["-FILE_PATH-2"]
                window.close()
        window.close()

    def getConfig(self):
        return self.configPath

    def getPos(self):
        return self.positionsPath

    def getJSON(self):
        return self.robotsPath

    def setConfig(self, configFile):
        self.configPath = configFile

    def setPos(self, posFile):
        self.positionsPath = posFile

    def setJSON(self, JSONFile):
        self.robotsPath = JSONFile
