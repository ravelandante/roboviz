# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 16/08/22
# ---------------------------------------------------------------------------
"""Represents an ActiveHinge or PassiveHinge component"""

from robotComp import RobotComp


class Hinge(RobotComp):
    def __init__(self, id, type, root, orientation):
        super().__init__(id, type, root, orientation)
        self.colour = (0, 1, 0, 1)                      # colour of component
