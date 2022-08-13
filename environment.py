# TODO: add root (core) object somewhere so parent can always be set to it
# EXTRA: toggle plane on/off, toggle colours on/off, bad orientation/slot warning + autocorrect option

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight
from panda3d.core import LVector3f

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import TextNode


def calcPos(src, dst, connection):
    src_pos = connection.src.pos
    src_min, src_max = src.getTightBounds()
    src_dims = (src_max - src_min)/2

    #dst_min, dst_max = dst.getTightBounds()
    #dst_dims = (dst_max - dst_min)/2
    #orientation = connection.dst.orientation

    #src.setHpr(heading, 0, 0)

    dst_pos = src_pos + LVector3f(0, src_dims[1], 0)
    return dst_pos


class Environment(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.set_background_color(0.6, 0.6, 0.6, 1)                     # set background colour to a lighter grey

        # this is where the read config file code would be (maybe even in a separate method)
        self.x_length = 1000
        self.y_length = 1000
        self.swarm_size = 1

        self.plane = self.loader.loadModel('./models/BAM/plane.bam')    # load 'terrain' plane
        self.plane.setScale(self.x_length, self.y_length, 0)            # scale up to specified dimensions
        self.plane.reparentTo(self.render)

        alight = AmbientLight('alight')                                 # create ambient light
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        # self.useDrive()                                 # enable use of arrow keys

        bk_text = "RoboViz Prototype"                                           # add prototype text
        textObject = OnscreenText(text=bk_text, pos=(0.85, 0.85), scale=0.07,
                                  fg=(1, 0.5, 0.5, 1), align=TextNode.ACenter, mayChange=0)

    def traverseTree(self, robot):
        for connection in robot.connections:
            src_path = "./models/BAM/" + connection.src.type + '.bam'   # get path of source model file
            self.src = self.loader.loadModel(src_path)                  # load model of source component
            if connection.src.root:
                # if component is root comp (core) set it's posiition to core position
                connection.src.pos = LVector3f(robot.core_pos[0], robot.core_pos[1], robot.core_pos[2])

            self.src.setPos(connection.src.pos)                         # set position of source model
            self.src.reparentTo(self.render)                            # set parent to render node

            dst_path = "./models/BAM/" + connection.dst.type + '.bam'   # get path of destination model file
            self.dst = self.loader.loadModel(dst_path)                  # load model of source component

            connection.dst.pos = calcPos(self.src, self.dst, connection)          # calc position of dest comp based on source position
            self.dst.setPos(connection.dst.pos)                         # set position of destination model
            self.dst.reparentTo(self.src)                               # set parent to source node
