# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 16/08/22
# ---------------------------------------------------------------------------
"""Represents a component of a robot"""

from panda3d.core import LVector3f


class RobotComp:
    def __init__(self, id, type, root, orientation=0, direction=0):
        self.id = id
        self.type = type                # component type
        self.root = root                # component is the root of the robot component tree
        self.orientation = orientation  # global orientation
        self.direction = direction

    def __str__(self):
        return f"ID: {self.id}, Type: {self.type}, root: {self.root}, orient: {self.orientation}"
