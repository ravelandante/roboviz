# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 23/08/22
# ---------------------------------------------------------------------------

import PySimpleGUI as sg
import os
from os.path import exists
import subprocess

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

    def __init__(self, config_path='', pos_path='', robot_path='', cli=False):
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
        self.cli = cli
        self.utils = RobotUtils(self.config_path, self.pos_path, self.robot_path)
        self.bgColour = "Black"

    def help_window(self, type):
        """
        Displays the help window
        Args:
            `type`: type of help info to display (file or build), (String)
        """
        if type == 'file':
            help = "To load a robot:\n  * browse for and choose a configuration, robot positions, and robot JSON file\n  * click on the 'Submit' button to start the simulation\n(file formats are available in './docs/User_Manual.md' under Appendix: File Formats)\n\nTo use auto-pack:\n  * toggle the 'auto-pack' check box\n  * browse for and choose a configuration and robot JSON file\n  * click on the 'Submit' button\n(positions will be automatically calculated and environment will be resized if needed)\n\nFull docs available under './docs/User_Manual.md'"
        elif type == 'build':
            help = "To add a component:\n  * click the desired parent component in the tree\n  * select the desired type of component from the dropdown\n  * give the component an ID in the text box ('comp_id')\n  * click the '+' button and fill in the source & destination slots and orientation\n  * click on the 'Submit' button to start the simulation\n\nTo load a robot from a JSON file click on the 'Browse' button and select a robot JSON file\n\nBuilt robots can also be saved by checking 'Write to file', giving it a name and clicking 'Submit'\n\nFull docs available under './docs/User_Manual.md'"
        layout = [[sg.Multiline(default_text=help, disabled=True, size=(70, 15), no_scrollbar=True)],
                  [sg.Button('Ok')]]
        sg.theme(self.bgColour)
        window = sg.Window('Help', layout, modal=True)
        while True:
            event, _ = window.read()
            if event == sg.WIN_CLOSED or event == 'Ok':
                break
        window.close()

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

        sg.theme(self.bgColour)
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
        sg.theme(self.bgColour)
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
        layout = [[sg.Button('+', size=3, tooltip='add component'), sg.Combo(values=COMPONENTS, default_value=COMPONENTS[0], key='-C_COMBO-', tooltip='component type'),
                   sg.InputText(key='-COMP_ID-', size=30, default_text='comp_id')],
                  [sg.Text('Components')],
                  [sg.Tree(data=treedata, key="-COMP_TREE-", auto_size_columns=True, num_rows=20, headings=['Type', 'Orientation'], col0_width=30, expand_x=True, show_expanded=True), ],
                  [sg.Button('Submit', tooltip='start simulation'), sg.Button('Help', tooltip='help menu'), sg.Button('Back', tooltip='return to file menu'), sg.FileBrowse(initial_folder=self.working_directory, file_types=[("Robot file", "*.json")], target='-LOAD-', tooltip='load robot JSON'),
                  sg.Input(key='-LOAD-', enable_events=True, visible=False), sg.Checkbox('Write to file', default=True, key='-FILE-', tooltip='write robot to JSON'),
                  sg.InputText(key='-F_NAME-', size=30, default_text='robot_name')]]
        sg.theme(self.bgColour)
        window = sg.Window("Build a Robot", layout, modal=True)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                quit()
            if event == 'Back':
                break
            if event == 'Help':
                self.help_window('build')
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

            """if event == '-':
                # delete selected component (NOT WORKING)
                if len(values['-COMP_TREE-']) == 0:
                    sg.popup("Please select a component")
                    continue
                else:
                    sel_comp = values['-COMP_TREE-'][0]
                del_comp = next(comp for comp in components if comp.id == sel_comp)
                components.remove(del_comp)"""

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

                treedata.Insert(parent=sel_comp, key=id, text=id, values=[type, orientation])   # insert new node
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
                self.runSim(config=config, robots=[robot], file=False)

        window.close()

    def startGUI(self):
        """Displays the file input GUI window"""

        LastRender = False
        configError = sg.Text("", visible=False, text_color='Red', background_color=self.bgColour)
        posError = sg.Text("", visible=False, text_color='Red', background_color=self.bgColour)
        jsonError = sg.Text("", visible=False, text_color='Red', background_color=self.bgColour)

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
                [sg.Button('Submit', tooltip='start simulation'), sg.Button('Help', tooltip='help menu'), sg.Button(
                    'Build', tooltip='open robot building menu'), sg.Exit(), sg.Checkbox('Auto-pack', key='-A_PACK-', tooltip='auto-position robots')]
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
                [sg.Button('Submit', tooltip='start simulation'), sg.Button('Help', tooltip='help menu'), sg.Button(
                    'Build', tooltip='open robot building menu'), sg.Exit(), sg.Checkbox('Auto-pack', key='-A_PACK-', tooltip='auto-position robots')]
            ]

        sg.theme(self.bgColour)
        window = sg.Window("RoboViz", layout, icon='resources/r_icon.ico')

        # Main Program Loop
        while True:
            auto_pack = False
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Exit':
                break

            elif (event == "Help"):
                self.help_window('file')

            elif (event == "Build"):
                window.hide()
                self.build_window()
                window.UnHide()

            elif (event == "Submit" and values["-FILE_PATH-"] == ""):
                configError.update(value="Configuration file not included", visible=True)
            else:
                configError.update(visible=False)

            if (event == "Submit" and values["-FILE_PATH-0"] == "" and not values['-A_PACK-']):
                posError.update(value="Positions file not included", visible=True)
            else:
                posError.update(visible=False)

            if (event == "Submit" and values["-FILE_PATH-2"] == ""):
                jsonError.update(value="Robots file not included", visible=True)
            else:
                jsonError.update(visible=False)

            if ((event == "Submit" and values["-FILE_PATH-"] != "" and values["-FILE_PATH-0"] != "" and values["-FILE_PATH-2"] != "") or (event == 'Submit' and values['-A_PACK-'])):
                if values['-A_PACK-']:
                    auto_pack = True
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

                # GUI parsing and error checking
                self.utils = RobotUtils(self.config_path, self.pos_path, self.robot_path)
                config = self.utils.configParse()
                if not config:
                    configError.update(value="Incorrect configuration file format", visible=True)
                    continue
                else:
                    configError.update(visible=False)
                if not auto_pack:
                    positions = self.utils.posParse()
                    if not positions:
                        posError.update(value="Incorrect positions file format", visible=True)
                        continue
                    else:
                        posError.update(visible=False)
                else:
                    positions = [[0, 0, 0]]*int(config[2])
                robots = self.utils.robotParse(int(config[2]), positions)
                if not robots:
                    jsonError.update(value="Incorrect robot file format", visible=True)
                    continue
                elif robots == True:
                    posError.update(value="Incorrect amount of robot positions given", visible=True)
                    continue
                else:
                    jsonError.update(visible=False)

                if len(robots) != config[2]:
                    configError.update(value="Mismatch between swarm size and number of robots given", visible=True)
                    continue

                if len(positions) != config[2]:
                    posError.update(value="Mismatch between number of positions and swarm size given", visible=True)
                    continue

                window.hide()                                                   # hide GUI window
                self.runSim(config, robots, auto_pack=auto_pack)                # start simulation (Panda)
                window.UnHide()                                                 # show GUI window again after exiting Panda

        window.close()

    def runSim(self, config='', robots='', auto_pack=False):
        """
        Creates the Environment and runs the simulation
        Args:
            `auto_pack`: whether the packing algorithm will be used to auto-position the robots (Boolean) **optional**
            `config`: configuration parameters (int[]) **optional**, only used when building a robot  
            `robots`: array of Robots (Robot[]) **optional**, only used when building a robot  
            `file`: whether or not the robots have been loaded from a file (boolean) **optional**
        """
        # CLI parsing and error checking
        if self.cli:
            config = self.utils.configParse()
            if not config:
                print("[ERROR] Incorrect configuration file format or file not found")
                quit()

            positions = self.utils.posParse()
            if not positions:
                print("[ERROR] Incorrect positions file format or file not found")
                quit()

            robots = self.utils.robotParse(int(config[2]), positions)
            if not robots:
                print("[ERROR] Incorrect robot file format or file not found")
                quit()
            elif robots == True:
                print('[ERROR] Incorrect amount of robot positions given')
                quit()

            if len(robots) != config[2]:
                print('[ERROR] Mismatch between number of robots and swarm size given')
                quit()

            if len(positions) != config[2]:
                print('[ERROR] Mismatch between number of positions and swarm size given')
                quit()

        env = Environment(int(config[0]), int(config[1]), int(config[2]))
        print('Rendering Robots...')
        for i, robot in enumerate(robots):                                      # loop through robots in swarm
            env.renderRobot(robot)                                  # render robot
            # get any out of bounds/collisions
            if not self.cli:
                out_of_bounds = robot.outOfBoundsDetect(int(config[0]), int(config[1]))
                if out_of_bounds != 'none':
                    self.out_of_bounds_all.append([i, out_of_bounds])
        print('...Done')
        if auto_pack:
            print('Auto-packing Robots...')
            env.reposition(self.utils.autoPack(robots, config[0], config[1]))
            print('...Done')
        env.initialView()
        if not auto_pack:
            if not self.cli:
                print('Detecting collisions...')
                self.collisions = self.utils.collisionDetect(robots)                  # get any possible collisions between robots
                print('...Done')
                if len(self.collisions) > 0 or len(self.out_of_bounds_all) > 0:
                    self.error_window()
        print('Rendering Environment...')
        env.run()
