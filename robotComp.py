# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 16/08/22
# ---------------------------------------------------------------------------
"""Represents a component of a robot"""


class RobotComp:
    def __init__(self, id, type, root, orientation=0):
        self.id = id
        self.type = type                # component type
        self.root = root                # component is the root of the robot component tree
        self.orientation = orientation  # global orientation
