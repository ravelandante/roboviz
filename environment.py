# TODO: add root (core) object somewhere so parent can always be set to it (currently set to self.render, if we want to move robots - won't work)
#       add components that make up other components (servo holder/passive hinge etc. - inheritance maybe?)
#       LICENSING
# EXTRA: toggle plane on/off, toggle colours on/off, bad orientation/slot warning + autocorrect option, move robots around with mouse, text showing component types etc.

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight
from panda3d.core import LVector3f

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import TextNode


ORIENTATION = {0: 0, 1: 90, 2: 180, 3: 270}


def calcPos(src, dst, connection):
    src_pos = connection.src.pos
    src_min, src_max = src.getTightBounds()
    src_dims = (src_max - src_min)/2                                    # get distance from centre of source model to edge

    dst_min, dst_max = dst.getTightBounds()
    dst_dims = (dst_max - dst_min)/2                                    # get distance from centre of dest model to edge

    print(connection.src_slot, connection.src.orientation)

    src_slot = connection.src_slot - connection.src.orientation
    if src_slot < 0:
        src_slot += 4

    heading = ORIENTATION[connection.dst.orientation]               # heading/orientation of dst model
    dst.setHpr(heading, 0, 0)

    if connection.dst.orientation in [0, 2]:                          # which dims to use to calculate new pos
        src_dim, dst_dim = src_dims[1], dst_dims[1]
    else:
        src_dim, dst_dim = src_dims[0], dst_dims[0]
    print(src_slot, '\n')
    if src_slot == 0:                                                   # use src slot to determine which side to place dest model
        dst_pos = src_pos + LVector3f(0, -(src_dim + dst_dim), 0)
    elif src_slot == 1:
        dst_pos = src_pos + LVector3f(-(src_dim + dst_dim), 0, 0)
    elif src_slot == 2:
        dst_pos = src_pos + LVector3f(0, src_dim + dst_dim, 0)
    elif src_slot == 3:
        dst_pos = src_pos + LVector3f(src_dim + dst_dim, 0, 0)
    return dst_pos


class Environment(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        #Claire Addition - added spinning camera
        self.disableMouse()
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

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
        cnt = 0
        for connection in robot.connections:
            if cnt == 12:
                break
            if connection.src.root:
                src_path = "./models/BAM/" + connection.src.type + '.bam'       # get path of source model file
                self.src = self.loader.loadModel(src_path)                      # load model of source component
                # if component is root comp (core) set it's position to core position & place
                connection.src.pos = LVector3f(robot.core_pos[0], robot.core_pos[1], robot.core_pos[2])

                self.src.setPos(connection.src.pos)                             # set position of source model
                self.src.reparentTo(self.render)                                # set parent to render node

            dst_path = "./models/BAM/" + connection.dst.type + '.bam'           # get path of destination model file
            self.dst = self.loader.loadModel(dst_path)                          # load model of source component

            if 'Hinge' in connection.src.type and connection.src_slot == 1:
                connection.src_slot = 2
            if 'Hinge' in connection.dst.type and connection.dst_slot == 1:
                connection.dst_slot = 2
            connection.dst.pos = calcPos(self.src, self.dst, connection)        # calc position of dest comp based on source position

            self.dst.setPos(connection.dst.pos)                                 # set position of destination model
            self.dst.reparentTo(self.render)                                    # set parent to source node
            cnt += 1