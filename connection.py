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

    def __str__(self):
        return f"src: {self.src}, dest: {self.dst}, src_slot: {self.src_slot}, dst_slot: {self.dst_slot}"
