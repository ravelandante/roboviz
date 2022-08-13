from environment import Environment
from robotComp import RobotComp
from connection import Connection
from robot import Robot

app = Environment()

comp1 = RobotComp('comp1', 'CoreComponent', True, 0)
comp2 = RobotComp('comp2', 'ActiveHinge', False, 0)

connections = []
connections.append(Connection(comp1, comp2, 0, 0))
connections.append(Connection(comp1, comp2, 3, 3))

robot1 = Robot('1', connections, [0, 0, 0])

app.traverseTree(robot1)
app.run()
