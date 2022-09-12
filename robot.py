# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 16/08/22
# ---------------------------------------------------------------------------
"""Represents a robot and it's connections"""

from panda3d.core import BoundingBox
from panda3d.core import LVector2f


class Robot:
    def __init__(self, id, connections, core_pos):
        self.id = id
        self.connections = connections
        self.core_pos = core_pos            # position (x, y, z) of robot core component

    def outOfBoundsDetect(self, x_length, y_length):
        root_node = self.connections[0].src.node                       # get root
        robot_min, robot_max = root_node.getTightBounds()               # get bounds

        box = BoundingBox(robot_min, robot_max)
        vertices = box.getPoints()                                      # get corners of bounding box

        out_of_bounds = LVector2f(0, 0)
        # get bounds of robot bounding box
        x_max, x_min, y_max, y_min, z_max, z_min = vertices[4][0], vertices[0][0], vertices[2][1], vertices[0][1], vertices[1][2], vertices[2][2]
        self.bounds = [x_max, x_min, y_max, y_min, z_max, z_min]       # set bounds of robot
        if x_max > x_length/2:                                     # if over +x
            out_of_bounds[0] = int(x_max - x_length/2)
        elif x_min < -x_length/2:                                  # if over -x
            out_of_bounds[0] = int(x_length/2 + x_min)
        if y_max > y_length/2:                                     # if over +y
            out_of_bounds[1] = int(y_max - y_length/2)
        elif y_min < -y_length/2:                                  # if over -y
            out_of_bounds[1] = int(y_length/2 + y_min)
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
