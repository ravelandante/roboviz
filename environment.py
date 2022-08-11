from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath
from panda3d.core import MeshDrawer


class Environment(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # this is where the read config file code would be (maybe even in a separate method)
        self.x_length = 100
        self.y_length = 100
        self.swarm_size = 1

        self.useDrive()                                 # enable use of arrow keys
