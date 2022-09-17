# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------
"""Represents a connection between 2 robot components"""


class Connection:
    def __init__(self, src, dst, src_slot, dst_slot):
        self.src = src                  # source robotComp
        self.dst = dst                  # destination robotComp
        self.src_slot = src_slot        # side of connection at source
        self.dst_slot = dst_slot        # side of connection at destination

    def standardiseSlots(self):
        if 'Hinge' in self.src.type and self.src_slot == 1:     # standardise source hinge slots
            self.src_slot = 2
        if 'Hinge' in self.dst.type and self.dst_slot == 1:     # standardise destination hinge slots
            self.dst_slot = 2
        if self.src.type == 'FixedBrick' or self.src.type == 'CoreComponent':
            if self.src_slot == 3:
                self.src_slot = 1
            elif self.src_slot == 2:
                self.src_slot = 3
            elif self.src_slot == 1:
                self.src_slot = 2
        if self.dst.type == 'FixedBrick' or self.dst.type == 'CoreComponent':
            if self.dst_slot == 3:
                self.dst_slot = 1
            elif self.dst_slot == 2:
                self.dst_slot = 3
            elif self.dst_slot == 1:
                self.dst_slot = 2

    def __str__(self):
        return f"src: {self.src}, dest: {self.dst}, src_slot: {self.src_slot}, dst_slot: {self.dst_slot}"
