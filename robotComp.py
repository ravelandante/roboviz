# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 16/08/22
# ---------------------------------------------------------------------------

from panda3d.core import LVector3f

SRC_SLOTS = {0: 180, 1: 90, 2: 0, 3: 270}
DST_SLOTS = {0: 0, 1: 90, 2: 180, 3: 270}
DIRECTION = {0: 0, 90: 1, 180: 2, 270: 3}
BUFFER = LVector3f(1.5, 1.5, 0)


class RobotComp:
    """Represents a component of a robot"""

    def __init__(self, id, type, root, orientation):
        """
        Constructor
        Args:
            `id`: ID of Brick (String)  
            `type`: type of brick component (String)  
            `root`: whether this brick is the core of the robot or not (boolean)  
            `orientation`: orientation (roll) of this component relative to its parent (int)
        """
        self.id = id
        self.type = type                # component type
        self.root = root                # component is the root of the robot component tree
        self.orientation = orientation  # global orientation
        self.direction = 0

    def calcPos(self, src, dst, connection):
        """
        Calculates the position that the component should be placed at in the scene based on the source's position
        Args:
            `src`: source Panda3D node in connection (PandaNode)  
            `dst`: destination Panda3D node in connection (PandaNode)  
            `connection`: the Connection in question (Connection)
        Returns:
            `(dst_pos, heading)`: position and heading that component should be placed at in the scene (LVector3f, int)
        """
        connection.dst.bounds = dst.getTightBounds()

        if connection.src.root == True:
            connection.src.bounds = src.getTightBounds()
            connection.src.root = False

        src_min, src_max = connection.src.bounds[0], connection.src.bounds[1]
        src_dims = (src_max - src_min)/2                                # get distance from centre of source model to edge
        src_pos = connection.src.pos

        src_dims -= BUFFER                                              # buffer to slot hinges and bricks together

        dst_min, dst_max = connection.dst.bounds[0], connection.dst.bounds[1]
        dst_dims = (dst_max - dst_min)/2                                # get distance from centre of dest model to edge

        src_slot = connection.src_slot - connection.src.direction       # get slot number relative to orientation of model
        if src_slot < 0:                                                # wrap slots around (4 -> 0 etc.)
            src_slot += 4

        heading = SRC_SLOTS[src_slot] + DST_SLOTS[connection.dst_slot]  # heading of dst model, depending on src and dst slot
        connection.dst.direction = DIRECTION[heading]
        dst.setHpr(heading, 0, 0)

        if connection.src_slot in [0, 2]:                               # which dims to use to calculate new pos
            src_dim = src_dims[1]
        else:
            src_dim = src_dims[0]
        if connection.dst_slot in [0, 2]:
            dst_dim = dst_dims[1]
        else:
            dst_dim = dst_dims[0]

        if src_slot == 0:                                               # use src slot to determine which side to place dest model
            dst_pos = src_pos + LVector3f(0, -(src_dim + dst_dim), 0)
        elif src_slot == 1:
            dst_pos = src_pos + LVector3f(-(src_dim + dst_dim), 0, 0)
        elif src_slot == 2:
            dst_pos = src_pos + LVector3f(0, src_dim + dst_dim, 0)
        elif src_slot == 3:
            dst_pos = src_pos + LVector3f(src_dim + dst_dim, 0, 0)
        return (dst_pos, heading)

    def __str__(self):
        return f"ID: {self.id}, Type: {self.type}, root: {self.root}, orient: {self.orientation}"
