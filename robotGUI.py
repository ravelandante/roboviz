import PySimpleGUI as sg
import os
from os.path import exists

from fileIO import FileIO
from environment import Environment


def collisionDetect(robots):
    """Determines if there are any possible collisions between robots in the scene
        Args:
            robots (List of Robot objects): list of all robots in the scene
    """
    collisions = []
    for i, first_robot in enumerate(robots):
        for second_robot in robots[i + 1:]:
            # if robots cross each other's z bounds
            if first_robot.bounds[4] >= second_robot.bounds[5] and first_robot.bounds[5] <= second_robot.bounds[4]:
                # if robots cross each other's x bounds
                if first_robot.bounds[0] >= second_robot.bounds[1] and first_robot.bounds[1] <= second_robot.bounds[0]:
                    # if robots cross each other's y bounds
                    if first_robot.bounds[2] >= second_robot.bounds[3] and first_robot.bounds[3] <= second_robot.bounds[2]:
                        collisions.append([first_robot.id, second_robot.id])
    return collisions


def formatCollisions(collisions):
    collision_text = 'Possible Collision Between:\n'
    for collision in collisions:
        collision_text += 'Robot {}, Robot {}\n'.format(collision[0], collision[1])
    return collision_text


def formatOutOfBounds(out_of_bounds):
    out_of_bounds_text = 'Robots out of bounds:\n'
    for robot in out_of_bounds:
        print(robot)
        out_of_bounds_text += 'Robot {}:\nx-axis = {} units\ny-axis = {}\n'.format(robot, robot[1][0], robot[1][1])


class RobotGUI:
    def __init__(self):
        self.configPath = ""
        self.positionsPath = ""
        self.robotsPath = ""
        self.out_of_bounds_all = []
        self.collisions = []
        self.exit = False
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

        #LastRender = False
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
            #LastRender = True
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
                [sg.Text("Choose a config file:", background_color=self.bgColour)],
                [sg.InputText(default_text=ConfigPath, key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Configuration file", "*.txt")])], [configError],
                [sg.Text("Choose a positions file:", background_color=self.bgColour)],
                [sg.InputText(default_text=PositionsPath, key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Position file", "*.txt")])], [posError],
                [sg.Text("Choose a robots file:", background_color=self.bgColour)],
                [sg.InputText(default_text=JSONPath, key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=working_directory, file_types=[("Robot file", "*.json")])], [jsonError],
                [sg.Button('Submit'), sg.Button('Help'), sg.Exit()]
            ]

        sg.theme(self.bgColour)
        window = sg.Window("RoboViz", layout)
        # if(LastRender):
        #    sg.popup("Last Robot Render Settings have been loaded!!!")

        # Main Program Loop
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break
            if (event == 'Exit'):
                self.exit = True
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
                fileio = FileIO(values["-FILE_PATH-"], values["-FILE_PATH-0"], values["-FILE_PATH-2"])
                positions = fileio.posParse()
                config = fileio.configParse()
                robots = fileio.robotParse(int(config[2]), positions)
                env = Environment(int(config[0]), int(config[1]), int(config[2]))
                for i, robot in enumerate(robots):                                      # loop through robots in swarm
                    env.renderRobot(robot)                                  # render robot
                    # get any out of bounds/collisions
                    out_of_bounds = robot.outOfBoundsDetect(int(config[0]), int(config[1]))
                    if out_of_bounds != 'none':
                        self.out_of_bounds_all.append([i, out_of_bounds])
                env.initialView()
                self.collisions = collisionDetect(robots)                  # get any possible collisions between robots
                if len(self.collisions) > 0 or len(self.out_of_bounds_all) > 0:
                    self.error_window()

                # window.hide()
                env.run()
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


window = RobotGUI()
window.startGUI()
