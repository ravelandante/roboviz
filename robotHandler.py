from distutils.command.config import config
from environment import Environment
from robotComp import RobotComp
from connection import Connection
from robot import Robot
from hinge import Hinge
from brick import Brick

import json
import sys

comp1 = Brick('comp1', 'CoreComponent', True, 0)
comp2 = Brick('comp2', 'FixedBrick', False, 0)
comp3 = Brick('comp3', 'FixedBrick', False, 0)
comp4 = Hinge('comp4', 'ActiveHinge', False, 0)
comp5 = Hinge('comp5', 'PassiveHinge', False, 0)

positions = []  # this will store a bunch of smaller position arrays
configuration = []  # this stores the x,y and z of the environment + the swarm size
if(len(sys.argv) == 4):
    # Positions parsing BEGIN
    try:
        # with open('robotPositions.txt', 'r') as f:
        with open(sys.argv[1], 'r') as f:
            for line in f:
                robot_position = []
                robot_position.append(int(line.split(' ')[0]))
                robot_position.append(int(line.split(' ')[1]))
                robot_position.append(int(line.split(' ')[2]))
                positions.append(robot_position)
        print(positions)
    except IOError:
        print("couldn't find robotPositions.txt")
        quit()
    # Positions parsing END
    # Configuration parsing BEGIN
    try:
        # with open('config.txt', 'r') as f:
        with open(sys.argv[2], 'r') as f:
            for line in f:
                configuration.append(int(line))
    except IOError:
        print("couldn't find config.txt")
        quit()
    # Configuration parsing END
    # Robot JSON parsing BEGIN
    try:
        with open(sys.argv[3], 'r') as f:
            data = json.load(f)

        body = data["body"]
        roboId = data["id"]
        bodyComp = body["part"]
        compArr = []

        for i in bodyComp:
            id = i['id']
            type = i['type']
            root = i['root']
            orient = i['orientation']
            newComp = RobotComp(id, type, root, orient)
            # print(newComp)
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
            # print(newCon)
            connArr.append(newCon)

    except IOError:
        print("couldn't find config.txt")
        quit()
    # Robot JSON parsing END
else:
    print("All files not listed")
    quit()

robot = Robot(roboId, connArr, positions[0])    # create robot

app = Environment(int(configuration[0]), int(configuration[1]), int(configuration[2]))  # create environment
app.traverseTree(robot)
app.run()
