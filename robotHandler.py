from environment import Environment
from robotComp import RobotComp
from connection import Connection
from robot import Robot
from hinge import Hinge
from brick import Brick

app = Environment(1000, 1000, 1)

comp1 = Brick('comp1', 'CoreComponent', True, 0)
comp2 = Brick('comp2', 'FixedBrick', False, 0)
comp3 = Brick('comp3', 'FixedBrick', False, 0)
comp4 = Hinge('comp4', 'ActiveHinge', False, 0)
comp5 = Hinge('comp5', 'PassiveHinge', False, 0)

connections = []
connections.append(Connection(comp1, comp2, 0, 0))
connections.append(Connection(comp2, comp3, 0, 0))
connections.append(Connection(comp3, comp4, 1, 0))
connections.append(Connection(comp1, comp5, 3, 0))

robot1 = Robot('1', connections, [0, 0, 0])

app.traverseTree(robot1)
app.run()
