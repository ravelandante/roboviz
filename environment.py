from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight
from panda3d.core import LVector3f

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import TextNode


def calcPos(src, src_pos):
    min, max = src.getTightBounds()
    dims = (max - min)/2
    dst_pos = src_pos + LVector3f(dims[0], 0, 0)
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
        self.plane.setScale(1, self.x_length, self.y_length)            # scale up to specified dimensions
        self.plane.reparentTo(self.render)

        #self.comp = self.loader.loadModel('./models/BAM/Core_FDM.bam')
        #self.comp.setColor(1, 0, 0, 1)
        # self.comp.reparentTo(self.render)

        alight = AmbientLight('alight')                                 # create ambient light
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        # self.useDrive()                                 # enable use of arrow keys

        bk_text = "RoboViz Prototype"
        textObject = OnscreenText(text=bk_text, pos=(0.85, 0.85), scale=0.07,
                                  fg=(1, 0.5, 0.5, 1), align=TextNode.ACenter,
                                  mayChange=0)

    def traverseTree(self, robot):
        for connection in robot.connections:
            src_path = "./models/BAM/" + connection.src.type + '.bam'
            self.src = self.loader.loadModel(src_path)
            if connection.src.root:
                connection.src.pos = LVector3f(robot.core_pos[0], robot.core_pos[1], robot.core_pos[2])

            self.src.setPos(connection.src.pos)
            self.src.reparentTo(self.render)

            dst_path = "./models/BAM/" + connection.dst.type + '.bam'
            self.dst = self.loader.loadModel(dst_path)
            connection.dst.pos = calcPos(self.src, connection.src.pos)
            self.dst.setPos(connection.dst.pos)
            self.dst.reparentTo(self.src)
