# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 16/08/22
# ---------------------------------------------------------------------------
"""Represents a robot and it's connections"""


class Robot:
    def __init__(self, id, connections, core_pos):
        self.id = id
        self.connections = connections
        self.core_pos = core_pos            # position (x, y, z) of robot core component
