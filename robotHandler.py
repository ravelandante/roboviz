from environment import Environment
from robotComp import RobotComp
from connection import Connection
from robot import Robot

app = Environment(1000, 1000, 1)

comp1 = RobotComp('comp1', 'CoreComponent', True, 0)
comp2 = RobotComp('comp2', 'FixedBrick', False, 0)
comp3 = RobotComp('comp3', 'FixedBrick', False, 0)
comp4 = RobotComp('comp4', 'ActiveHinge', False, 0)
comp5 = RobotComp('comp5', 'PassiveHinge', False, 0)

connections = []
connections.append(Connection(comp1, comp2, 0, 0))
connections.append(Connection(comp2, comp3, 0, 0))
connections.append(Connection(comp3, comp4, 1, 0))
connections.append(Connection(comp1, comp5, 3, 0))

robot1 = Robot('1', connections, [0, 0, 0])

app.traverseTree(robot1)
app.run()
