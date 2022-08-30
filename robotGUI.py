import PySimpleGUI as sg
import csv
import os


class RobotGUI:
    def __init__(self):
        self.configPath = ""
        self.positionsPath = ""
        self.robotsPath = ""

    def startGUI(self):
        working_directory = os.getcwd()

        layout = [
            [sg.Text("Choose a config file:")],
            [sg.InputText(key="-FILE_PATH-"),
                sg.FileBrowse(initial_folder=working_directory, file_types=[("Configuration file", "*.txt")])],
            [sg.Text("Choose a positions file:")],
            [sg.InputText(key="-FILE_PATH-"),
                sg.FileBrowse(initial_folder=working_directory, file_types=[("Position file", "*.txt")])],
            [sg.Text("Choose a robots file:")],
            [sg.InputText(key="-FILE_PATH-"),
                sg.FileBrowse(initial_folder=working_directory, file_types=[("Robot file", "*.json")])],
            [sg.Button('Submit'), sg.Exit()]
        ]

        window = sg.Window("Display config", layout)

        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Exit'):
                break
            elif event == "Submit":
                self.configPath = values["-FILE_PATH-"]

                #print("sorted \n NEXT FILE!!!!")
                self.positionsPath = values["-FILE_PATH-0"]

                #print("sorted \n NEXT FILE!!!!")
                self.robotsPath = values["-FILE_PATH-2"]

            window.close()

    def getConfig(self):
        return self.configPath

    def getPos(self):
        return self.positionsPath

    def getJSON(self):
        return self.robotsPath
