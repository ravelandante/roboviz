# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------
"""Renders environment terrain and robot components"""

# TODO: reparent components to core of robot (facilitates easy moving of robots)
#       move calcPos to robotComp/hinge/brick objects
#       LICENSING
# EXTRA: toggle plane on/off, toggle colours on/off, bad orientation/slot warning + autocorrect option, move robots around with mouse

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight
from panda3d.core import LVector3f
from panda3d.core import Mat4

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import TextNode
from panda3d.core import NodePath


SRC_SLOTS = {0: 180, 1: 90, 2: 0, 3: 270}
DST_SLOTS = {0: 0, 1: 90, 2: 180, 3: 270}
DIRECTION = {0: 0, 90: 1, 180: 2, 270: 3}
BUFFER = LVector3f(1.5, 1.5, 0)


class Environment(ShowBase):
    def __init__(self, x_length, y_length, swarm_size):
        ShowBase.__init__(self)

        self.robot_pos = []                                             # positions of robot cores
        self.focus_switch_counter = 0

        self.set_background_color(0.6, 0.6, 0.6, 1)                     # set background colour to a lighter grey
        self.focus = NodePath('focus')                                  # create focus point (origin) of camera
        self.focus.reparentTo(self.render)
        self.camera.reparentTo(self.focus)

        self.x_length = x_length
        self.y_length = y_length
        self.swarm_size = swarm_size

        self.plane = self.loader.loadModel('./models/BAM/plane.bam')    # load 'terrain' plane
        self.plane.setScale(self.x_length, self.y_length, 0)            # scale up to specified dimensions
        self.plane.reparentTo(self.render)

        alight = AmbientLight('alight')                                 # create ambient light
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        proto_text = "RoboViz Prototype"                                # add prototype text
        proto_textNode = OnscreenText(text=proto_text, pos=(0.95, 0.85), scale=0.04,
                                      fg=(1, 0.5, 0.5, 1), align=TextNode.ACenter, mayChange=0)

        self.accept('c', self.switchFocus)                              # listen for 'c' keypress

    def switchFocus(self):
        self.focus_switch_counter += 1
        while self.focus_switch_counter > self.swarm_size - 1:          # loop back around to start of list
            self.focus_switch_counter -= self.swarm_size
        print(f'Moving camera to robot {self.focus_switch_counter} at {self.robot_pos[self.focus_switch_counter]}')
        self.moveCamera(self.robot_pos[self.focus_switch_counter])

    def moveCamera(self, pos):
        self.focus.setPos(pos)                                          # move focus of camera
        self.disableMouse()
        self.camera.setPos(LVector3f(0, 0, 400))                        # move camera relative to focus
        self.camera.setHpr(0, -90, 0)

        mat = Mat4(self.camera.getMat())
        mat.invertInPlace()
        self.mouseInterfaceNode.setMat(mat)
        self.enableMouse()

    def displayLabel(self, text, pos):
        label = TextNode('id_label')                                    # add text node
        label.setText(text)
        label.setTextColor(1, 1, 1, 1)
        label.setAlign(TextNode.ACenter)
        label.setCardColor(1, 1, 1, 0.3)                                # add text frame
        label.setCardAsMargin(0, 0, 0, 0)
        label.setCardDecal(True)

        self.text3d = NodePath(label)                                   # add text to node
        self.text3d.setScale(3, 3, 3)
        self.text3d.setPos(pos + LVector3f(0, 0, 20))                   # set pos above component model
        self.text3d.setTwoSided(True)
        self.text3d.setBillboardPointEye()                              # make text billboard (move with camera)
        self.text3d.reparentTo(self.render)

    def calcPos(self, src, dst, connection):
        src_pos = connection.src.pos
        src_min, src_max = src.getTightBounds()
        src_dims = (src_max - src_min)/2                                # get distance from centre of source model to edge

        src_dims -= BUFFER                                              # buffer to slot hinges and bricks together

        dst_min, dst_max = dst.getTightBounds()
        dst_dims = (dst_max - dst_min)/2                                # get distance from centre of dest model to edge

        src_slot = connection.src_slot - connection.src.direction     # get slot number relative to orientation of model
        if src_slot < 0:
            src_slot += 4

        # heading = ORIENTATION[connection.dst.orientation]               # heading/orientation of dst model
        heading = SRC_SLOTS[src_slot] + DST_SLOTS[connection.dst_slot]   # heading of dst model, depending on src and dst slot
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
        return dst_pos

    def renderRobot(self, robot):
        nodes = []
        g_orientations = []
        # add position of robot core to list
        self.robot_pos.append(LVector3f(robot.core_pos[0], robot.core_pos[1], robot.core_pos[2]))
        for connection in robot.connections:
            if connection.src.root:
                src_path = "./models/BAM/" + connection.src.type + '.bam'       # get path of source model file
                self.src = self.loader.loadModel(src_path)                      # load model of source component
                # if component is root comp (core) set it's position to core position & place
                connection.src.pos = LVector3f(robot.core_pos[0], robot.core_pos[1], robot.core_pos[2])

                self.src.setPos(connection.src.pos)                             # set position of source model
                self.src.reparentTo(self.render)                                # set parent to render node

                # self.displayLabel(str(robot.id), connection.src.pos)            # display robot id label text
                nodes.append(self.src)
                g_orientations.append(connection.src.orientation)

            dst_path = "./models/BAM/" + connection.dst.type + '.bam'           # get path of destination model file
            self.dst = self.loader.loadModel(dst_path)                          # load model of source component

            if 'Hinge' in connection.src.type and connection.src_slot == 1:     # standardise hinge slots
                connection.src_slot = 2
            if 'Hinge' in connection.dst.type and connection.dst_slot == 1:
                connection.dst_slot = 2

            connection.dst.pos = self.calcPos(self.src, self.dst, connection)   # calc position of dest comp based on source position

            self.dst.setPos(connection.dst.pos)                                 # set position of destination model
            self.dst.setColor(connection.dst.colour)                            # set model to relevant colour
            self.dst.reparentTo(self.render)                                    # set parent to source node

            # self.displayLabel(connection.dst.id, connection.dst.pos)            # display component id label text

            nodes.append(self.dst)
            g_orientations.append(connection.dst.orientation)

            #print(f'Rendered \'{connection.dst.id}\' of type \'{connection.dst.type}\' at {connection.dst.pos}')

        self.moveCamera(self.robot_pos[self.focus_switch_counter])              # move camera to first robot loaded

        prev_node = self.render
        for i, node in enumerate(nodes):                                        # reorganise component nodes into robot tree
            orig_pos = node.getPos()
            orig_heading = node.getHpr()

            node.reparentTo(prev_node)

            node.setPos(self.render, orig_pos)
            node.setHpr(self.render, orig_heading)
            prev_node = node

        prev_node = self.render
        for i, node in enumerate(nodes):                                        # rotate nodes according to orientation
            node.setHpr(node.getHpr()[0], 0, node.getHpr()[2] + DST_SLOTS[g_orientations[i]])
            prev_node = node
