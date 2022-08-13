from environment import Environment
from robotComp import RobotComp
from connection import Connection
from robot import Robot

app = Environment()

comp1 = RobotComp('comp1', 'Core_FDM', True, 0)
comp2 = RobotComp('comp2', 'Connector2Bricks', False, 0)

connections = []
connections.append(Connection(comp1, comp2, 0, 0))
#connections.append(Connection(comp1, comp2, 1, 0))

robot1 = Robot('1', connections, [0, 0, 0])

app.traverseTree(robot1)
app.run()
