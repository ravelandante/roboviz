# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 23/08/22
# ---------------------------------------------------------------------------

import PySimpleGUI as sg
import os
from os.path import exists
import subprocess
import threading

from robotUtils import RobotUtils
from environment import Environment
from hinge import Hinge
from brick import Brick
from connection import Connection
from robot import Robot

COMPONENTS = ['FixedBrick', 'ActiveHinge', 'PassiveHinge']


def formatCollisions(collisions):
    """
    Formats List of collisions into displayable format
    Args:
        `collisions`: possible collisions between robots (int[][])
    Returns:
        `collision_text`: text format of robot collisions (String)
    """
    collision_text = 'Possible Collision Between:\n'
    for collision in collisions:
        collision_text += 'Robot {}, Robot {}\n'.format(collision[0], collision[1])
    return collision_text


def formatOutOfBounds(out_of_bounds):
    """
    Formats List of out of bounds robots into displayable format
    Args:
        `out_of_bounds`: robots that are out of bounds + units ([int, LVector3f])
    Returns:
        `out_of_bounds_text`: text format of out of bounds robots (String)
    """
    out_of_bounds_text = ''
    for robot in out_of_bounds:
        out_of_bounds_text += 'Robot {}:\n'.format(robot[0])
        if robot[1][0] != 0:
            out_of_bounds_text += 'x-axis = {} units\n'.format(int(robot[1][0]))
        if robot[1][1] != 0:
            out_of_bounds_text += 'y-axis = {} units\n\n'.format(int(robot[1][1]))
    return out_of_bounds_text


class RobotGUI:
    """Initialises the GUI for inputting files, building robots and reporting errors"""

    def __init__(self, config_path='', pos_path='', robot_path=''):
        """
        Constructor
        Args:
            `config_path`: file path of configuration text file (String) **optional**, only used when building a robot  
            `pos_path`: file path of robot positions text file (String) **optional**, only used when building a robot  
            `robot_path`: file path of robot JSON file (String) **optional**, only used when building a robot
        """
        self.config_path = config_path
        self.pos_path = pos_path
        self.robot_path = robot_path
        self.working_directory = os.getcwd()
        self.out_of_bounds_all = []
        self.collisions = []
        self.utils = RobotUtils(self.config_path, self.pos_path, self.robot_path)
        self.bgColour = "Black"

    def error_window(self):
        """Displays the error reporting window"""
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
            event, _ = window.read()
            if event == "Continue" or event == sg.WIN_CLOSED:
                break
            if event == "Cancel":
                quit()

        window.close()

    def connection_window(self):
        """
        Displays the component connection window for specifying specific connection parameters
        Returns:
            `(src_slot, dst_slot, orientation)`: source, dest slots + orientation of component ((int, int, int)) (returns (-1, -1, -1) if window closed)
        """
        layout = [[sg.Text('SRC Slot:'), sg.Combo(values=[0, 1, 2, 3], default_value=0, key='-SRC_COMBO-')],
                  [sg.Text('DST Slot:'), sg.Combo(values=[0, 1, 2, 3], default_value=0, key='-DST_COMBO-')],
                  [sg.Text('Orientation:'), sg.Combo(values=[0, 1, 2, 3], default_value=0, key='-O_COMBO-')],
                  [sg.Button('Submit')]]
        window = sg.Window("Enter Slots", layout, modal=True)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                window.close()
                return (-1, -1, -1)
            if event == 'Submit':
                window.close()
                return (values['-SRC_COMBO-'], values['-DST_COMBO-'], values['-O_COMBO-'])

    def build_window(self):
        """Displays the Robot building window"""
        components = []
        connections = []
        treedata = sg.TreeData()
        core = Brick('Core', 'CoreComponent', True, 0)
        components.append(core)
        treedata.insert(parent='', key=core.id, text=core.id, values=['CoreComponent', core.orientation])
        layout = [[sg.Button('+', size=3), sg.Button('-', size=3), sg.Combo(values=COMPONENTS, default_value=COMPONENTS[0], key='-C_COMBO-'),
                   sg.InputText(key='-COMP_ID-', size=30, default_text='comp_id')],
                  [sg.Text('Components')],
                  [sg.Tree(data=treedata, key="-COMP_TREE-", auto_size_columns=True, num_rows=20, headings=['Type', 'Orientation'], col0_width=30, expand_x=True, show_expanded=True), ],
                  [sg.Button('Submit'), sg.Button('Help'), sg.Button('Back'), sg.FileBrowse(initial_folder=self.working_directory, file_types=[("Robot file", "*.json")], target='-LOAD-'),
                  sg.Input(key='-LOAD-', enable_events=True, visible=False), sg.Checkbox('Write to file', default=True, key='-FILE-'),
                  sg.InputText(key='-F_NAME-', size=30, default_text='robot_name')]]
        window = sg.Window("Build a Robot", layout, modal=True)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                quit()
            if event == 'Back':
                break
            if event == 'Help':
                sg.popup("some help info\nsome more help stuff ig\neven more help text wowow", title="Help")
            if event == '-LOAD-':
                if values['-LOAD-'] == '':
                    continue
                self.utils.robot_path = values['-LOAD-']
                robot = self.utils.robotParse(1, [[0, 0, 0]])[0]
                for connection in robot.connections:
                    dst = connection.dst
                    treedata.Insert(parent=connection.src.id, key=dst.id, text=dst.id, values=[dst.type, dst.orientation])
                window.Element('-COMP_TREE-').update(treedata)
                components = robot.components
                connections = robot.connections

            if event == '-':
                # delete selected component (NOT WORKING)
                if len(values['-COMP_TREE-']) == 0:
                    sg.popup("Please select a component")
                    continue
                else:
                    sel_comp = values['-COMP_TREE-'][0]
                del_comp = next(comp for comp in components if comp.id == sel_comp)
                components.remove(del_comp)

            if event == '+':
                # add new component
                if values['-COMP_ID-'] in treedata.tree_dict:                           # if component id already exists in tree
                    sg.popup("Component {} already exists".format(values['-COMP_ID-']))
                    continue
                if ' ' in values['-COMP_ID-']:
                    sg.popup("No spaces in component ID")
                    continue
                if len(values['-COMP_TREE-']) == 0:                                     # if nothing selected, continue
                    sg.popup("Please select a component")
                    continue
                else:
                    sel_comp = values['-COMP_TREE-'][0]

                id = values['-COMP_ID-']
                type = values['-C_COMBO-']
                src_slot, dst_slot, orientation = self.connection_window()
                parent = next(comp for comp in components if comp.id == sel_comp)

                if src_slot == -1 or dst_slot == -1 or orientation == -1:
                    continue
                if 'Hinge' in parent.type:
                    if src_slot in [2, 3]:
                        sg.popup("Invalid source slot for Hinge")
                        continue
                if 'Hinge' in type:
                    if dst_slot in [2, 3]:
                        sg.popup("Invalid destination slot for Hinge")
                        continue
                    comp = Hinge(id, type, False, orientation)
                else:
                    comp = Brick(id, type, False, orientation)

                treedata.Insert(parent=sel_comp, key=id, text=id, values=[type, orientation])
                window.Element('-COMP_TREE-').update(treedata)

                components.append(comp)
                connections.append(Connection(parent, comp, src_slot, dst_slot))

            if event == 'Submit':
                if len(components) == 1:
                    sg.popup("Please add more than one component")
                    continue
                if ' ' in values['-F_NAME-']:
                    sg.popup("No spaces in file name")
                    continue
                robot = Robot(0, connections, components, [0, 0, 0])
                config = [1000, 1000, 1]
                if (values['-FILE-']):
                    self.utils.writeRobot(robot, values['-F_NAME-'])
                self.runSim(config, [robot], file=False)

        window.close()

    def startGUI(self):
        """Displays the file input GUI window"""

        LastRender = False
        configError = sg.Text("Configuration file not included!", visible=False, text_color='Red', background_color=self.bgColour)
        posError = sg.Text("Positions file not included!", visible=False, text_color='Red', background_color=self.bgColour)
        jsonError = sg.Text("Robots file not included!", visible=False, text_color='Red', background_color=self.bgColour)

        if(not exists('LastRender.txt')):
            layout = [
                [sg.Text("Choose a config file:", background_color=self.bgColour)],
                [sg.InputText(key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=self.working_directory, file_types=[("Configuration file", "*.txt")])], [configError],
                [sg.Text("Choose a positions file:", background_color=self.bgColour)],
                [sg.InputText(key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=self.working_directory, file_types=[("Position file", "*.txt")])], [posError],
                [sg.Text("Choose a robots file:", background_color=self.bgColour)],
                [sg.InputText(key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=self.working_directory, file_types=[("Robot file", "*.json")])], [jsonError],
                [sg.Button('Submit'), sg.Button('Help'), sg.Button('Build'), sg.Exit(), sg.Checkbox('Auto-pack', key='-A_PACK-')]
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
                 sg.FileBrowse(initial_folder=self.working_directory, file_types=[("Configuration file", "*.txt")])], [configError],
                [sg.Text("Choose a positions file:", background_color=self.bgColour)],
                [sg.InputText(default_text=pos_path, key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=self.working_directory, file_types=[("Position file", "*.txt")])], [posError],
                [sg.Text("Choose a robots file:", background_color=self.bgColour)],
                [sg.InputText(default_text=robot_path, key="-FILE_PATH-"),
                 sg.FileBrowse(initial_folder=self.working_directory, file_types=[("Robot file", "*.json")])], [jsonError],
                [sg.Button('Submit'), sg.Button('Help'), sg.Button('Build'), sg.Exit(), sg.Checkbox('Auto-pack', key='-A_PACK-')]
            ]

        sg.theme(self.bgColour)
        window = sg.Window("RoboViz", layout, icon='resources/r_icon.ico')
        auto_pack = False

        # Main Program Loop
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Exit':
                break

            elif (event == "Help"):
                sg.popup("some help info\nsome more help stuff ig\neven more help text wowow", title="Help")

            elif (event == "Build"):
                window.hide()
                self.build_window()
                window.UnHide()

            elif (event == "Submit" and values["-FILE_PATH-"] != "" and values["-FILE_PATH-2"] != "" and values["-A_PACK-"]):
                auto_pack = True
            elif (event == "Submit" and values["-FILE_PATH-"] == ""):
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

                # x = threading.Thread(target=self.runSim)
                # x.start()
                # x.join()

                # window.hide()
                self.runSim(auto_pack=auto_pack)

        window.close()

    def runSim(self, auto_pack=False, config=0, robots=0, file=True):
        """
        Creates the Environment and runs the simulation
        Args:
            `auto_pack`: whether the packing algorithm will be used to auto-position the robots (Boolean) **optional**
            `config`: configuration parameters (int[]) **optional**, only used when building a robot  
            `robots`: array of Robots (Robot[]) **optional**, only used when building a robot  
            `file`: whether or not the robots have been loaded from a file (boolean) **optional**
        """
        if file:
            self.utils = RobotUtils(self.config_path, self.pos_path, self.robot_path)
            config = self.utils.configParse()
            if not auto_pack:
                positions = self.utils.posParse()
            else:
                positions = [[0, 0, 0]]*int(config[2])
            robots = self.utils.robotParse(int(config[2]), positions)

        env = Environment(int(config[0]), int(config[1]), int(config[2]))
        for i, robot in enumerate(robots):                                      # loop through robots in swarm
            env.renderRobot(robot)                                  # render robot
            # get any out of bounds/collisions
            out_of_bounds = robot.outOfBoundsDetect(int(config[0]), int(config[1]))
            if out_of_bounds != 'none':
                self.out_of_bounds_all.append([i, out_of_bounds])
        if auto_pack:
            env.auto_pack(self.utils.autoPack(robots))
        env.initialView()
        if not auto_pack:
            self.collisions = self.utils.collisionDetect(robots)                  # get any possible collisions between robots
            if len(self.collisions) > 0 or len(self.out_of_bounds_all) > 0:
                self.error_window()

        env.run()
