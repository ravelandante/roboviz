# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 16/08/22
# ---------------------------------------------------------------------------


from panda3d.core import BoundingBox
from panda3d.core import LVector2f
from panda3d.core import NodePath
from panda3d.core import LineSegs

LINE_THICKNESS = 1


class Robot:
    """Represents a robot and its connections"""

    def __init__(self, id, connections, components, core_pos):
        """
        Constructor
        Args:
            `id`: ID of robot (int)  
            `connections`: connections between components that make up the robot (Connection[])  
            `core_pos`: positions of the core component of the robot (int[])
        """
        self.id = id
        self.connections = connections
        self.core_pos = core_pos            # position (x, y, z) of robot core component
        self.components = components

        self.ls = LineSegs()
        self.ls.setThickness(LINE_THICKNESS)
        self.ls.setColor(1, 1, 1, 1)

    def setBounds(self):
        """Calculates and sets the bounds (bounding box) of the robot"""
        root_node = self.connections[0].src.node

        robot_min, robot_max = root_node.getTightBounds()
        box = BoundingBox(robot_min, robot_max)
        vertices = box.getPoints()

        # calc bounds of robot bounding box
        x_max, x_min, y_max, y_min, z_max, z_min = vertices[4][0], vertices[0][0], vertices[2][1], vertices[0][1], vertices[1][2], vertices[2][2]
        self.bounds = [x_max, x_min, y_max, y_min, z_max, z_min]       # set bounds of robot

    def drawBounds(self):
        """Draws LineSegs between all points of the robot bounding box"""
        root_node = self.connections[0].src.node                            # root node
        robot_min, robot_max = root_node.getTightBounds(root_node)          # get bounds of robot
        box = BoundingBox(robot_min, robot_max)
        vertices = box.getPoints()                                          # get points of robot bounding box

        for z in range(0, len(vertices), 4):                                # draw 'side' boxes
            self.ls.moveTo(vertices[z])
            self.ls.drawTo(vertices[z + 1])
            self.ls.drawTo(vertices[z + 3])
            self.ls.drawTo(vertices[z + 2])
            self.ls.drawTo(vertices[z])

        for xy in range(0, len(vertices)//2):                               # draw 'top and bottom' boxes
            self.ls.moveTo(vertices[xy])
            self.ls.drawTo(vertices[xy + len(vertices)//2])

        bounds_node = self.ls.create()
        self.bounding_box = NodePath(bounds_node)
        self.bounding_box.reparentTo(root_node)                             # reparent bounding box to robot root
        self.bounding_box.hide()                                            # hide bounding box

    def outOfBoundsDetect(self, x_length, y_length):
        """
        Determines if robot exceeds the dimensions of the environment
        Args:
            `x_length`: x length of the environment (int)  
            `y_length`: y length of the environment (int)
        Returns:
            `out_of_bounds`: x and y values of how far the robot is out of bounds (LVector3f), returns `'none'` if not out of bounds
        """
        self.setBounds()                                                    # calc & set bounds of robot

        out_of_bounds = LVector2f(0, 0)
        if self.bounds[0] > x_length/2:                                     # if over +x
            out_of_bounds[0] = int(self.bounds[0] - x_length/2)
        elif self.bounds[1] < -x_length/2:                                  # if over -x
            out_of_bounds[0] = int(x_length/2 + self.bounds[1])
        if self.bounds[2] > y_length/2:                                     # if over +y
            out_of_bounds[1] = int(self.bounds[2] - y_length/2)
        elif self.bounds[3] < -y_length/2:                                  # if over -y
            out_of_bounds[1] = int(y_length/2 + self.bounds[3])
        if out_of_bounds != LVector2f(0, 0):
            return out_of_bounds
        else:
            return 'none'

    def __str__(self):
        count = 0
        s = f"ID: {self.id}, Connections: "
        for i in self.connections:
            s = s + f"\n{count+1}: {i}"
            count = count+1
        s = s + f"\nCore: {self.core_pos}"
        s = s+f"\nTotal connections: {count}"
        return s
