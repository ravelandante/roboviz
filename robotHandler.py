# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------
"""Reads in configuration, roboto positions & robot JSON files. Creates environment object and runs application"""

from environment import Environment
from hinge import Hinge
from brick import Brick
from connection import Connection
from robot import Robot

import json
import sys


positions = []  # stores smaller position arrays
configuration = []  # stores the x,y and z of the environment + the swarm size
if(len(sys.argv) == 1):
    try:                                                                    # Positions parsing BEGIN
        with open('positions/pos3.txt', 'r') as f:
            # with open(sys.argv[1], 'r') as f:
            for line in f:
                robot_position = []
                line = line.split(' ')
                robot_position.append(int(line[0]))                         # x value
                robot_position.append(int(line[1]))                         # y value
                robot_position.append(int(line[2]))                         # z value
                positions.append(robot_position)
    except IOError:
        print(f"Couldn't find positions file: {sys.argv[1]}")               # error if filepath invalid
        quit()                                                              # Positions parsing END
    try:                                                                    # Configuration parsing BEGIN
        # with open(sys.argv[2], 'r') as f:
        with open('config/config3.txt', 'r') as f:
            for line in f:
                configuration.append(int(line))
    except IOError:
        print(f"Couldn't find configuration file: {sys.argv[2]}")           # error if filepath invalid
        quit()                                                              # Configuration parsing END
    try:                                                                    # Robot JSON parsing BEGIN
        # with open(sys.argv[3], 'r') as f:
        with open('json/robot.json', 'r') as f:
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

    except IOError:
        print(f"Couldn't find Robot JSON file: {sys.argv[3]}")              # error if filepath invalid
        quit()                                                              # Robot JSON parsing END
else:
    print(f"Only {len(sys.argv) - 1}/3 filepaths entered")                  # error if user enters 0, 1, 2 files only
    quit()


app = Environment(int(configuration[0]), int(configuration[1]), int(configuration[2]))  # create environment
for i in range(int(configuration[2])):                                      # loop through robots in swarm
    robot = Robot(i, connArr, positions[i])                                 # create robot
    app.renderRobot(robot)                                                  # render robot
app.run()                                                                   # run visualiser
