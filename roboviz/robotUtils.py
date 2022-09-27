# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------

from roboviz.hinge import Hinge
from roboviz.brick import Brick
from roboviz.connection import Connection
from roboviz.robot import Robot
from roboviz.brain import ann

import json
import rpack
from copy import deepcopy


CREATE_BRAIN = False        # create brain or not
PACK_BUFFER = 50            # buffer between auto-packed robots
INC_AMT = 100               # amount to increase environment dims by in auto-pack if unable to fit all robots


class RobotUtils:
    """Contains various utility functions (such as file IO) for creating robots"""

    def __init__(self, config_path, pos_path, robot_path):
        """
        Constructor
        Args:
            `config_path`: file path of configuration text file (String)  
            `pos_path`: file path of robot positions text file (String)  
            `robot_path`: file path of robot JSON file (String)
        """
        self.config_path = config_path
        self.pos_path = pos_path
        self.robot_path = robot_path

    def collisionDetect(self, robots):
        """
        Determines if there are any possible collisions between robots in the scene
            Args:
                `robots`: list of all robots in the scene (Robot[])
            Returns
                `collisions`: possible collisions between robots (int[][])
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

    def createBrain(self, components, brain, neurons):
        """
        Creates list of neurons based on JSON file ANN inputs
        Args:
            `components`: components in Robot (RobotComp[])  
            `brain`: connections in Robot brain (dict)  
            `neurons`: neurons in Robot brain (dict)
        """
        inputNeurons = 0
        outputNeurons = 0
        outputPortIds = []
        params = []
        types = []
        for i in neurons:
            type = i['type']
            # read in json file
            gain = i['gain']
            params.append(gain)
            if type == 'sigmoid':
                bias = i['bias']
                params.append(bias)
                types.append(1)
                outputNeurons = outputNeurons + 1
                outputPortIds.append(i['bodyPartId'])
            elif type == 'oscillator':
                phaseOffset = i['phaseOffset']
                period = i['period']
                params.append(period)
                params.append(phaseOffset)
                types.append(3)
                outputNeurons = outputNeurons + 1
                outputPortIds.append(i['bodyPartId'])
            else:
                inputNeurons = inputNeurons+1
        weightArr = []
        destComps = []
        # set up the weights & destination comps
        count = 0
        for j in components:
            for k in outputPortIds:
                if j.id in k:
                    destComps.append(j)
        for i in brain:
            weight = i['weight']
            weightArr.append(weight)
        return ann(destComps, inputNeurons, outputNeurons, weightArr, params, types)

    def writeRobot(self, robot, name):
        """
        Writes custom built Robot out to relevant files
        Args:
            `robot`: Robot to be written out (Robot)  
            `name`: name of Robot JSON file (String)
        """
        path = 'json/{}.json'.format(name)
        dict_outer = {}
        dict_inner = {}
        connections = list(robot.connections)
        components = list(robot.components)

        with open(path, 'w') as f:
            # get all components & connections as dicts
            for i, component in enumerate(components):
                components[i] = component.as_dict()
            for i, connection in enumerate(connections):
                connections[i].unStandardiseSlots()
                connections[i] = connection.as_dict()

            # construct JSON file sections
            dict_inner["part"] = components
            dict_inner["connection"] = connections
            dict_outer["id"] = robot.id
            dict_outer["body"] = dict_inner

            # write to JSON file
            json.dump(dict_outer, f, indent=4)

    def posParse(self):
        """
        Parses robot positions from positions file
        Returns:
            `positions`: positions of Robots in scene (int[])
        """
        try:
            positions = []
            with open(self.pos_path, 'r') as f:
                for line in f:
                    robot_position = []
                    line = line.split(' ')
                    robot_position.append(int(line[0]))  # x value
                    robot_position.append(int(line[1]))  # y value
                    robot_position.append(int(line[2]))  # z value
                    positions.append(robot_position)
            return positions
        except:
            # format error or file not found
            return False

    def configParse(self):
        """
        Parses environment and swarm size from configuration file
        Returns:
            `configuration`: environment and swarm size (int[])
        """
        try:
            configuration = []
            with open(self.config_path, 'r') as f:
                for line in f:
                    configuration.append(int(line))
            return configuration
        except:
            # format error or file not found
            return False

    def robotParse(self, swarm_size, positions, build=False):
        """
        Parses robot(s) from robot JSON file
        Args:
            `swarm_size`: number of robots in swarm (int)  
            `positions`: positions of each robot in swarm (int[])  
            `build`: whether or not robot is being loaded into builder (boolean) **optional**
        Returns:
            `robotArr`: all robots to be rendered in the scene (Robot[])
        """
        try:
            robotArr = []
            count = 0  # counting the positions
            with open(self.robot_path, 'r') as f:
                data = json.load(f)
            # HETERGENEOUS SWARM
            if("swarm" in data.keys()):
                swarm = data["swarm"]

                for robot in swarm:
                    roboId = robot["id"]
                    body = robot["body"]

                    bodyComp = body["part"]
                    compArr = []

                    for i in bodyComp:
                        id = i['id']
                        type = i['type']
                        root = i['root']
                        orient = i['orientation']
                        # determine component type
                        if 'Hinge' in type:
                            newComp = Hinge(id, type, root, orient)     # create new Hinge component
                        else:
                            newComp = Brick(id, type, root, orient)     # create new Brick component

                        compArr.append(newComp)

                    bodyConnect = body["connection"]
                    connArr = []

                    for i in bodyConnect:
                        src = i['src']
                        # find the component that is the source
                        for j in compArr:
                            compare = j.id
                            if src == compare:
                                src = j

                        dest = i['dest']
                        # find the component that is the destination
                        for j in compArr:
                            if dest == (j.id):
                                dest = j

                        srcSlot = i['srcSlot']
                        # find the component that is the source slot
                        for j in compArr:
                            if srcSlot == (j.id):
                                srcSlot = j

                        destSlot = i['destSlot']
                        # find the component that is the destination slot
                        for j in compArr:
                            if destSlot == (j.id):
                                srcSlot = j

                        newCon = Connection(src, dest, srcSlot, destSlot)               # construct new connection
                        connArr.append(newCon)                                          # add to list of connections

                    robot = Robot(roboId, connArr, compArr, positions[count - 1])
                    count += 1
                    robotArr.append(robot)
                return robotArr
            # HOMOGENOUS SWARM
            else:
                roboId = data["id"]
                body = data["body"]
                bodyComp = body["part"]
                compArr = []

                for i in bodyComp:
                    id = i['id']
                    type = i['type']
                    root = i['root']
                    orient = i['orientation']
                    if 'Hinge' in type:
                        newComp = Hinge(id, type, root, orient)                     # create new Hinge component
                    else:
                        newComp = Brick(id, type, root, orient)                     # create new Brick component
                    compArr.append(newComp)

                bodyConnect = body["connection"]
                connArr = []

                for i in bodyConnect:
                    src = i['src']
                    # find the component that is the source
                    for j in compArr:
                        compare = j.id
                        if src == compare:
                            src = j

                    dest = i['dest']
                    # find the component that is the destination
                    for j in compArr:
                        if dest == (j.id):
                            dest = j

                    srcSlot = i['srcSlot']
                    # find the component that is the source slot
                    for j in compArr:
                        if srcSlot == (j.id):
                            srcSlot = j

                    destSlot = i['destSlot']
                    # find the component that is the destination slot
                    for j in compArr:
                        if destSlot == (j.id):
                            srcSlot = j

                    newCon = Connection(src, dest, srcSlot, destSlot)
                    connArr.append(newCon)
                if CREATE_BRAIN:
                    network = data["brain"]
                    neurons = network["neuron"]
                    brain = network["connection"]
                    ann = self.createBrain(compArr, brain, neurons)
                for i in range(int(swarm_size)):                      # loop through robots in swarm
                    if not build:
                        connArr = deepcopy(connArr)
                    robotArr.append(Robot(i, connArr, compArr, positions[i]))
                return robotArr
        except IndexError:
            # means incorrect number of positions given
            return True
        except:
            # format error or file not found
            return False

    def autoPack(self, robots, x_length, y_length):
        """
        Calculates automatic positioning of Robots to fit within certain bounds (resizes environment if not possible)
        Args:
            `robots`: Robots in the Environment (Robot[])  
            `x_length`: current x-dim of the environment  
            `y_length`: current y-dim of the environment
        Returns:
            `(positions, x_length, y_length)`: new positions of Robots + new dims of environment
        """
        while True:
            try:
                sizes = []
                # get bounding box sizes for all robots
                for robot in robots:
                    bounds = robot.bounds
                    width = int(bounds[0]) - int(bounds[1]) + PACK_BUFFER
                    height = int(bounds[2]) - int(bounds[3]) + PACK_BUFFER
                    sizes.append((width, height))

                # calculate optimal packing positions
                positions = rpack.pack(sizes, max_width=y_length, max_height=x_length)
                box_size = rpack.bbox_size(sizes, positions)    # size of packed robots

                # adjust positions so that they're at the centre of each robot bounding box
                # (originally put at bottom left corner)
                for i, _ in enumerate(positions):
                    bounds = robots[i].bounds
                    core_pos = robot.core_pos
                    positions[i] = (positions[i][0] + core_pos[0] - bounds[1] - box_size[0]/2,
                                    positions[i][1] + core_pos[1] - bounds[3] - box_size[1]/2)
            except rpack.PackingImpossibleError:
                # can't pack into environment dims
                # resize environment and try again
                x_length += INC_AMT
                y_length += INC_AMT
                continue
            else:
                break
        return (positions, x_length, y_length)
