# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 23/08/22
# ---------------------------------------------------------------------------
"""Initialises the GUI for inputting files and reporting errors"""

import PySimpleGUI as sg
import os
from os.path import exists
import subprocess
import threading

from robotUtils import RobotUtils
from environment import Environment


def formatCollisions(collisions):
    collision_text = 'Possible Collision Between:\n'
    for collision in collisions:
        collision_text += 'Robot {}, Robot {}\n'.format(collision[0], collision[1])
    return collision_text


def formatOutOfBounds(out_of_bounds):
    out_of_bounds_text = ''
    for robot in out_of_bounds:
        out_of_bounds_text += 'Robot {}:\n'.format(robot[0])
        if robot[1][0] != 0:
            out_of_bounds_text += 'x-axis = {} units\n'.format(int(robot[1][0]))
        if robot[1][1] != 0:
            out_of_bounds_text += 'y-axis = {} units\n\n'.format(int(robot[1][1]))
    return out_of_bounds_text


class RobotGUI:
    def __init__(self, config_path='', pos_path='', robot_path=''):
        self.config_path = config_path
        self.pos_path = pos_path
        self.robot_path = robot_path
        self.out_of_bounds_all = []
        self.collisions = []
        self.bgColour = "Black"

    def error_window(self):
        if len(self.collisions) > 0:
            collision_text = formatCollisions(self.collisions)
            if len(self.out_of_bounds_all) > 0:
                out_of_bounds_text = formatOutOfBounds(self.out_of_bounds_all)
                layout = [[sg.Text("Robot Collisions", background_color=self.bgColour)],
                          [sg.Multiline(size=(50, 7), default_text=collision_text,  key='-COL_BOX-', echo_stdout_stderr=True, disabled=True)],
                          [sg.Text("Robots out of bounds", background_color=self.bgColour)],
                          [sg.Multiline(size=(50, 7), default_text=out_of_bounds_text,  key='-OOB_BOX-', echo_stdout_stderr=True, disabled=True)],
                          [sg.Button('Continue'), sg.Button('Cancel')]]
            else:
                layout = [[sg.Text("Robot Collisions", background_color=self.bgColour)],
                          [sg.Multiline(size=(50, 7), default_text=collision_text,  key='-COL_BOX-', echo_stdout_stderr=True, disabled=True)],
                          [sg.Button('Continue'), sg.Button('Cancel')]]
        elif len(self.out_of_bounds_all) > 0:
            out_of_bounds_text = formatOutOfBounds(self.out_of_bounds_all)
            layout = [[sg.Text("Robots out of bounds", background_color=self.bgColour)],
                      [sg.Multiline(size=(50, 7), default_text=out_of_bounds_text,  key='-OOB_BOX-', echo_stdout_stderr=True, disabled=True)],
                      [sg.Button('Continue'), sg.Button('Cancel')]]

        window = sg.Window("Errors", layout, modal=True)
        while True:
            event, values = window.read()
            if event == "Continue" or event == sg.WIN_CLOSED:
                break
            if event == "Cancel":
                quit()

        window.close()

    def startGUI(self):
        """Displays the GUI window"""
        working_directory = os.getcwd()

        LastRender = False
        configError = sg.Text("Configuration file not included!", visible=False, text_color='Red', background_color=self.bgColour)
        posError = sg.Text("Positions file not included!", visible=False, text_color='Red', background_color=self.bgColour)
        jsonError = sg.Text("Robots file not included!", visible=False, text_color='Red', background_color=self.bgColour)

        if(not exists('LastRender.txt')):
            layout = [
                [sg.Text("Choose a config file:", background_color=self.bgColour)],
                [sg.InputText(key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Configuration file", "*.txt")])], [configError],
                [sg.Text("Choose a positions file:", background_color=self.bgColour)],
                [sg.InputText(key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Position file", "*.txt")])], [posError],
                [sg.Text("Choose a robots file:", background_color=self.bgColour)],
                [sg.InputText(key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Robot file", "*.json")])], [jsonError],
                [sg.Button('Submit'), sg.Button('Help'), sg.Exit()]
            ]
        else:
            LastRender = True
            pos_path = ""
            config_path = ""
            robot_path = ""
            with open('LastRender.txt', 'r') as f:
                i = 0
                for line in f:
                    line = line.strip()
                    if i == 0:
                        pos_path = line
                    elif i == 1:
                        config_path = line
                    elif i == 2:
                        robot_path = line
                    i += 1
            layout = [
                [sg.Text("Choose a config file:", background_color=self.bgColour)],
                [sg.InputText(default_text=config_path, key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Configuration file", "*.txt")])], [configError],
                [sg.Text("Choose a positions file:", background_color=self.bgColour)],
                [sg.InputText(default_text=pos_path, key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Position file", "*.txt")])], [posError],
                [sg.Text("Choose a robots file:", background_color=self.bgColour)],
                [sg.InputText(default_text=robot_path, key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Robot file", "*.json")])], [jsonError],
                [sg.Button('Submit'), sg.Button('Help'), sg.Exit()]
            ]

        sg.theme(self.bgColour)
        window = sg.Window("RoboViz", layout, icon='resources/r_icon.ico')

        # Main Program Loop
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if(event == "Help"):
                sg.popup("some help info\nsome more help stuff ig\neven more help text wowow", title="HELP")

            if (event == "Submit" and values["-FILE_PATH-"] == ""):
                configError.update(visible=True)
            else:
                configError.update(visible=False)

            if (event == "Submit" and values["-FILE_PATH-0"] == ""):
                posError.update(visible=True)
            else:
                posError.update(visible=False)

            if (event == "Submit" and values["-FILE_PATH-2"] == ""):
                jsonError.update(visible=True)
            else:
                jsonError.update(visible=False)

            if (event == "Submit" and values["-FILE_PATH-"] != "" and values["-FILE_PATH-0"] != "" and values["-FILE_PATH-2"] != ""):
                self.config_path = values["-FILE_PATH-"]
                self.pos_path = values["-FILE_PATH-0"]
                self.robot_path = values["-FILE_PATH-2"]

                if (not LastRender):
                    lines = [self.pos_path, self.config_path, self.robot_path]
                    with open('LastRender.txt', 'w') as f:
                        for line in lines:
                            f.write(line)
                            f.write(' \n')
                subprocess.check_call(["attrib", "+H", "LastRender.txt"])   # hide saved file paths file

                #x = threading.Thread(target=self.runSim)
                # x.start()
                # x.join()

                window.hide()
                self.runSim()

            window.close()

    def runSim(self):
        utils = RobotUtils(self.config_path, self.pos_path, self.robot_path)

        positions = utils.posParse()
        config = utils.configParse()
        robots = utils.robotParse(int(config[2]), positions)

        #ANN = createBrain(neurons, brain, compArr)
        env = Environment(int(config[0]), int(config[1]), int(config[2]))
        for i, robot in enumerate(robots):                                      # loop through robots in swarm
            env.renderRobot(robot)                                  # render robot
            # get any out of bounds/collisions
            out_of_bounds = robot.outOfBoundsDetect(int(config[0]), int(config[1]))
            if out_of_bounds != 'none':
                self.out_of_bounds_all.append([i, out_of_bounds])
        env.initialView()
        self.collisions = utils.collisionDetect(robots)                  # get any possible collisions between robots

        if len(self.collisions) > 0 or len(self.out_of_bounds_all) > 0:
            self.error_window()

        env.run()
