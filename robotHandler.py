import json

from environment import Environment
from robotComp import RobotComp
from connection import Connection
from robot import Robot

from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase

from direct.task import Task
# for moving the camera
from direct.actor.Actor import Actor




app = Environment()

with open('robot.json', 'r') as f:
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
    #print(newComp)
    compArr.append(newComp)

bodyConnect = body["connection"]
connArr = []

for i in bodyConnect:
    src = i['src']
    #find the component that is the source
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
    #print(newCon)
    connArr.append(newCon)



f.close()

robot1 = Robot(roboId, connArr, [0, 0, 0])
print(robot1)

app.traverseTree(robot1)
app.run()
