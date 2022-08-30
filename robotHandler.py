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
from robotGUI import RobotGUI

import json
import sys


window = RobotGUI()
window.startGUI()   # opens the GUI for the user to input files

robotArr = []
positions = []  # stores smaller position arrays
configuration = []  # stores the x,y and z of the environment + the swarm size
if((window.getPos() != "") & (window.getConfig() != "") & (window.getJSON() != "")):
    try:                                                                    # Positions parsing BEGIN
        # with open('robotPositions.txt', 'r') as f:
        with open(window.getPos(), 'r') as f:
            for line in f:
                robot_position = []
                line = line.split(' ')
                robot_position.append(int(line[0]))                         # x value
                robot_position.append(int(line[1]))                         # y value
                robot_position.append(int(line[2]))                         # z value
                positions.append(robot_position)
    except IOError:
        print(f"Couldn't find positions file:", window.getPos())               # error if filepath invalid
        quit()                                                              # Positions parsing END
    try:                                                                    # Configuration parsing BEGIN
        # with open(sys.argv[2], 'r') as f:
        with open('config/config3.txt', 'r') as f:
            for line in f:
                configuration.append(int(line))
    except IOError:
        print(f"Couldn't find configuration file:", window.getConfig())           # error if filepath invalid
        quit()                                                              # Configuration parsing END
    count = 0  # counting the positions
    try:                                                                    # Robot JSON parsing BEGIN
        with open(window.getJSON(), 'r') as f:
            data = json.load(f)
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
                print(robot)
                robotArr.append(robot)

            app = Environment(int(configuration[0]), int(configuration[1]), int(configuration[2]))  # create environment
            for r in robotArr:
                app.renderRobot(r)
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
                # print(newCon)
                connArr.append(newCon)

            app = Environment(int(configuration[0]), int(configuration[1]), int(configuration[2]))  # create environment
            for i in range(int(configuration[2])):                                      # loop through robots in swarm
                robot = Robot(i, connArr, positions[i])                                 # create robot
                app.renderRobot(robot)
    except IOError:
        print("Couldn't find Robot JSON file:", window.getJSON())
        quit()
    # Robot JSON parsing END
else:
    print("All files not listed")
    quit()
f.close()

app.run()
