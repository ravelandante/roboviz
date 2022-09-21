# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 16/08/22
# ---------------------------------------------------------------------------

from robotComp import RobotComp


class Brick(RobotComp):
    """Represents a CoreComponent or FixedBrick component"""

    def __init__(self, id, type, root, orientation):
        """
        Constructor
        Args:
            `id`: ID of Brick (String)  
            `type`: type of brick component (String)  
            `root`: whether this brick is the core of the robot or not (boolean)  
            `orientation`: orientation (roll) of this component relative to its parent (int)
        """
        super().__init__(id, type, root, orientation)
        self.colour = (1, 0, 0, 1)                      # colour of component
