from hinge import Hinge
from brick import Brick
from connection import Connection
from robot import Robot
from brain import Neuron, Network
from robotComp import RobotComp

from os.path import exists
import os
import subprocess
import json
import sys
import numpy as np


class FileIO:
    def __init__(self, config_path, pos_path, json_path):
        self.config_path = config_path
        self.pos_path = pos_path
        self.json_path = json_path

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
        with open(self.json_path, 'r') as f:
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
