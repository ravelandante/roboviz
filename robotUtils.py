from hinge import Hinge
from brick import Brick
from connection import Connection
from robot import Robot
from brain import Neuron, Network
from robotComp import RobotComp

import json
import numpy as np


class RobotUtils:
    def __init__(self, config_path, pos_path, robot_path):
        self.config_path = config_path
        self.pos_path = pos_path
        self.robot_path = robot_path

    def collisionDetect(self, robots):
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

    def createBrain(self, neurons, brain, compArr):
        """Creates list of neurons based on JSON file ANN inputs
        Args:
            neurons (List): list of neurons and their info from JSON file
            brain (List): list of connections between neurons from JSON file
            compArr (List of RobotComp objects): list of components that neurons are connected to
        """
        inputNeurons = []
        outputNeurons = []
        other = []
        for i in neurons:
            id = i['id']
            layer = i['layer']
            type = i['type']
            # read in json file
            bodyPartId = i['bodyPartId']
            for j in compArr:
                if j.id == bodyPartId:
                    bodyPartId = j
            # set the body part id to a specific component
            ioId = i['ioId']
            gain = i['gain']
            if type == 'sigmoid':
                bias = i['bias']
                phaseOffset = 0
                period = 0
            elif type == 'oscillator':
                phaseOffset = i['phaseOffset']
                period = i['period']
                bias = 0
            else:
                phaseOffset = 0
                period = 0
                bias = 0
            neuron = Neuron(id, layer, type, bodyPartId, ioId, gain, bias, phaseOffset, period)
            # create the neuron
            if layer == 'input':
                inputNeurons.append(neuron)
            elif layer == 'output':
                inputNeurons.append(neuron)
            else:
                other.append(neuron)
                # in case there is a middle layer

        # set up the weights & destination comps
        for i in brain:
            src = i['src']
            dest = i['dest']
            weight = i['weight']
            w = 0
            comp = RobotComp(0, 0, 0, 0)
            for j in compArr:
                if j.id in dest:
                    comp = j
                    w = weight
                    break
            for j in inputNeurons:
                if j.id in src:
                    j.setWeight(w)
                    j.setDestComp(comp)
                    break
            for j in outputNeurons:
                if j.id in src:
                    j.setWeight(w)
                    j.setDestComp(comp)
                    break

        X_train = np.array([[0, 0, 1, 1], [0, 1, 0, 1]])  # dim x m
        Y_train = np.array([[0, 1, 1, 0]])  # 1 x m
        L, E = 0.15, 100
        net = Network(inputNeurons, outputNeurons, X_train, Y_train, epochs=E, lr=L)
        return net

    def posParse(self):
        positions = []
        with open(self.pos_path, 'r') as f:
            for line in f:
                robot_position = []
                line = line.split(' ')
                robot_position.append(int(line[0]))                         # x value
                robot_position.append(int(line[1]))                         # y value
                robot_position.append(int(line[2]))                         # z value
                positions.append(robot_position)
        return positions

    def configParse(self):
        configuration = []
        with open(self.config_path, 'r') as f:
            for line in f:
                configuration.append(int(line))
        return configuration

    def robotParse(self, swarm_size, positions):
        robotArr = []
        count = 0  # counting the positions
        with open(self.robot_path, 'r') as f:
            data = json.load(f)
        if("swarm" in data.keys()):
            swarm = data["swarm"]
            #neurons = swarm["neuron"]
            #brain = swarm["connection"]

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

                    newCon = Connection(src, dest, srcSlot, destSlot)               # construct new connection
                    connArr.append(newCon)                                          # add to list of connections

                robot = Robot(roboId, connArr, positions[count - 1])
                count += 1
                robotArr.append(robot)
                #ANN = createBrain(neurons, brain, compArr)

                return robotArr
        else:
            roboId = data["id"]
            body = data["body"]
            bodyComp = body["part"]
            compArr = []
            part2 = data["brain"]
            neurons = part2["neuron"]
            brain = part2["connection"]

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
            #ANN = createBrain(neurons, brain, compArr)
            for i in range(int(swarm_size)):                      # loop through robots in swarm
                robotArr.append(Robot(i, connArr, positions[i]))
            return robotArr
