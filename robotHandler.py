# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------
"""Reads in configuration, robot positions & robot JSON files. Creates environment object and runs application"""

from environment import Environment
from hinge import Hinge
from brick import Brick
from connection import Connection
from robot import Robot
from brain import Neuron, Network
from robotGUI import RobotGUI
from robotComp import RobotComp

from os.path import exists
import os
import subprocess
import json
import sys
import numpy as np


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


def createBrain(neurons, brain, compArr):
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


window = RobotGUI()
if((not exists('LastRender.txt')) and (len(sys.argv) != 4)):  # checking to see if theres a saved render file so new JSON, positions and configuration files dont have to be entered
    window.startGUI()   # opens the GUI for the user to input files
elif(len(sys.argv) == 4):
    window.setConfig(sys.argv[2])
    window.setJSON(sys.argv[3])
    window.setPos(sys.argv[1])

if(window.exit):
    quit()
robotArr = []           # stores robots
positions = []          # stores smaller position arrays
configuration = []      # stores the x and y + the swarm size
collisions = []         # stores collisions between robots
out_of_bounds_all = []  # stores any robots that are out of bounds

if((window.getPos() != "") & (window.getConfig() != "") & (window.getJSON() != "") or (exists('LastRender.txt'))):
    PositionsPath = window.getPos()
    ConfigPath = window.getConfig()
    JSONPath = window.getJSON()

    try:                                                                    # Basically checking to see if a LastRender.txt exists and uses those old values to Render robots
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
    except IOError:                                                         # If LastRender.txt doesnt exist, it will be created and the last files used to render robots will be stored inside
        lines = [window.getPos(), window.getConfig(), window.getJSON()]
        with open('LastRender.txt', 'w') as f:
            for line in lines:
                f.write(line)
                f.write(' \n')

    try:                                                                    # Positions parsing BEGIN
        # with open('robotPositions.txt', 'r') as f:
        with open(PositionsPath, 'r') as f:
            for line in f:
                robot_position = []
                line = line.split(' ')
                robot_position.append(int(line[0]))                         # x value
                robot_position.append(int(line[1]))                         # y value
                robot_position.append(int(line[2]))                         # z value
                positions.append(robot_position)
    except IOError:
        print(f"Couldn't find positions file:", PositionsPath)               # error if filepath invalid
        quit()                                                              # Positions parsing END
    try:                                                                    # Configuration parsing BEGIN
        # with open(sys.argv[2], 'r') as f:
        with open(ConfigPath, 'r') as f:
            for line in f:
                configuration.append(int(line))
    except IOError:
        print(f"Couldn't find configuration file:", ConfigPath)           # error if filepath invalid
        quit()                                                              # Configuration parsing END
    count = 0  # counting the positions
    try:                                                                    # Robot JSON parsing BEGIN
        with open(JSONPath, 'r') as f:
            data = json.load(f)
        if("swarm" in data.keys()):
            swarm = data["swarm"]
            neurons = swarm["neuron"]
            brain = swarm["connection"]

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
                count = count+1
                robotArr.append(robot)
                ANN = createBrain(neurons, brain, compArr)

            if((len(robotArr) == len(positions)) and (len(robotArr) == configuration[2])):
                app = Environment(int(configuration[0]), int(configuration[1]), int(configuration[2]))  # create environment
                for robot in robotArr:
                    app.renderRobot(robot)
                    # get any out of bounds/collisions
                    out_of_bounds = robot.outOfBoundsDetect(int(configuration[0]), int(configuration[1]))
                    if out_of_bounds != 'none':
                        out_of_bounds_all.append([i, out_of_bounds])
                    robotArr.append(robot)
                app.initialView()
                collisions = collisionDetect(robotArr)                  # get any possible collisions between robots
            else:
                print("Contradicting swarm sizes!")
                if os.path.isfile('LastRender.txt'):
                    os.remove('LastRender.txt')
                quit()

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
            if(len(positions) == configuration[2]):
                ANN = createBrain(neurons, brain, compArr)
                app = Environment(int(configuration[0]), int(configuration[1]), int(configuration[2]))  # create environment
                for i in range(int(configuration[2])):                                      # loop through robots in swarm
                    robot = Robot(i, connArr, positions[i])                 # create robot
                    app.renderRobot(robot)                                  # render robot
                    # get any out of bounds/collisions
                    out_of_bounds = robot.outOfBoundsDetect(int(configuration[0]), int(configuration[1]))
                    if out_of_bounds != 'none':
                        out_of_bounds_all.append([i, out_of_bounds])
                    robotArr.append(robot)
                app.initialView()
                collisions = collisionDetect(robotArr)                  # get any possible collisions between robots
            else:
                print("Contradicting swarm sizes!")
                if os.path.isfile('LastRender.txt'):
                    os.remove('LastRender.txt')
                quit()
    except IOError:
        print("Couldn't find Robot JSON file:", JSONPath)
        quit()
    # Robot JSON parsing END
subprocess.check_call(["attrib", "+H", "LastRender.txt"])   # hide saved file paths file
f.close()

print(collisions)
print(out_of_bounds_all)

app.run()
