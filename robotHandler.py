from distutils.command.config import config
from environment import Environment
from robotComp import RobotComp
from connection import Connection
from robot import Robot

import json
import sys


positions = []  # this will store a bunch of smaller position arrays
configuration = []  # this stores the x,y and z of the environment + the swarm size
if(len(sys.argv) == 4):
    # Positions parsing BEGIN
    try:
        with open('positions/robotPositions.txt', 'r') as f:
            # with open(sys.argv[1], 'r') as f:
            for line in f:
                robot_position = []
                robot_position.append(int(line.split(' ')[0]))
                robot_position.append(int(line.split(' ')[1]))
                robot_position.append(int(line.split(' ')[2]))
                positions.append(robot_position)
    except IOError:
        print(f"Couldn't find positions file: {sys.argv[1]}")
        quit()
    # Positions parsing END
    # Configuration parsing BEGIN
    try:
        with open('config/config.txt', 'r') as f:
            # with open(sys.argv[2], 'r') as f:
            for line in f:
                configuration.append(int(line))
    except IOError:
        print(f"Couldn't find configuration file: {sys.argv[2]}")
        quit()
    # Configuration parsing END
    # Robot JSON parsing BEGIN
    try:
        with open('json/robot_edit.json', 'r') as f:
            # with open(sys.argv[3], 'r') as f:
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

    except IOError:
        print(f"Couldn't find Robot JSON file: {sys.argv[3]}")
        quit()
    # Robot JSON parsing END
else:
    print(f"Only {len(sys.argv) - 1}/3 filepaths entered")
    quit()


app = Environment(int(configuration[0]), int(configuration[1]), int(configuration[2]))  # create environment
for i in range(int(configuration[2])):                              # loop through robots in swarm
    robot = Robot(i, connArr, positions[i])                         # create robot
    app.traverseTree(robot)                                         # render robot
app.run()                                                           # run visualiser
