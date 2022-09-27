# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------


def slotSwap(slot, dir):
    """
    Convert RoboGen slots to RoboViz system
    Args:
        `slot`: slot number to be swapped (int)
        `dir`: direction of swap, standardise or unstandardise
    Returns:
        `slot`: swapped slot number (int)
    """
    if dir == 0:
        if slot == 3:
            slot = 1
        elif slot == 2:
            slot = 3
        elif slot == 1:
            slot = 2
        return slot
    elif dir == 1:
        if slot == 1:
            slot = 3
        elif slot == 3:
            slot = 2
        elif slot == 2:
            slot = 1
        return slot


class Connection:
    """Represents a connection between 2 robot components"""

    def __init__(self, src, dst, src_slot, dst_slot, standardised=False):
        """
        Constructor
        Args:
            `src`: source ('parent') component (RobotComp)
            `dst`: destination ('child') component (RobotComp)
            `src_slot`: side of source component to attach dest. to (int)
            `dst_slot`: side of dest. component to attach source to (int)
            `standardised`: whether or not the connection's slots have been standardised (boolean) **optional**
        """
        self.src = src                  # source robotComp
        self.dst = dst                  # destination robotComp
        self.src_slot = src_slot        # side of connection at source
        self.dst_slot = dst_slot        # side of connection at destination
        self.standardised = standardised

    def standardiseSlots(self):
        """Converts RoboGen's funky slot system to a more reasonable one (sides numbered clockwise 0->3 starting from side closest to viewer)"""
        # standardise hinge slots (1=2)
        if 'Hinge' in self.src.type and self.src_slot == 1:                     # source hinge slots
            self.src_slot = 2
        if 'Hinge' in self.dst.type and self.dst_slot == 1:                     # dest. hinge slots
            self.dst_slot = 2
        # standardise brick slots (1=2, 3=1, 2=3)
        if self.src.type == 'FixedBrick' or self.src.type == 'CoreComponent':   # source brick slots
            self.src_slot = slotSwap(self.src_slot, 0)
        if self.dst.type == 'FixedBrick' or self.dst.type == 'CoreComponent':   # dest. brick slots
            self.dst_slot = slotSwap(self.dst_slot, 0)
        self.standardised = True

    def unStandardiseSlots(self):
        """Converts back to RoboGen system for writing to file"""
        # unstandardise hinge slots
        if 'Hinge' in self.src.type and self.src_slot == 2:                     # source hinge slots
            self.src_slot = 1
        if 'Hinge' in self.dst.type and self.dst_slot == 2:                     # dest. hinge slots
            self.dst_slot = 1
        # unstandardise brick slots
        if self.src.type == 'FixedBrick' or self.src.type == 'CoreComponent':   # source brick slots
            self.src_slot = slotSwap(self.src_slot, 1)
        if self.dst.type == 'FixedBrick' or self.dst.type == 'CoreComponent':   # dest. brick slots
            self.dst_slot = slotSwap(self.dst_slot, 1)
        self.standardised = False

    def as_dict(self):
        """
        Represents a Connection object as a dictionary, for use in the RobotUtils **writeRobot** method
        Returns:
            `dict`: contains all Connection fields as a dict
        """
        dict = {}
        dict["src"] = self.src.id
        dict["dest"] = self.dst.id
        dict["srcSlot"] = self.src_slot
        dict["destSlot"] = self.dst_slot
        return dict

    def __str__(self):
        """
        toString for Connection object
        Returns:
            Connection in String form (String)
        """
        return f"src: {self.src}, dest: {self.dst}, src_slot: {self.src_slot}, dst_slot: {self.dst_slot}"
