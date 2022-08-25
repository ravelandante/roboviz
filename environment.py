# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------
"""Renders environment terrain and robot components"""

# TODO: reparent components to core of robot (facilitates easy moving of robots)
#       move calcPos to robotComp/hinge/brick objects
#       LICENSING
# EXTRA: toggle plane on/off, bad orientation/slot warning + autocorrect option, move robots around with mouse, method docs

from panda3d.core import NodePath
from panda3d.core import TextNode
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import Mat4
from panda3d.core import LVector3f
from panda3d.core import AmbientLight
from direct.showbase.ShowBase import ShowBase
#from panda3d.core import loadPrcFileData
# loadPrcFileData("", "want-directtools #t")
# loadPrcFileData("", "want-tk #t")


SRC_SLOTS = {0: 180, 1: 90, 2: 0, 3: 270}
DST_SLOTS = {0: 0, 1: 90, 2: 180, 3: 270}
DIRECTION = {0: 0, 90: 1, 180: 2, 270: 3}
BUFFER = LVector3f(1.5, 1.5, 0)


class Environment(ShowBase):
    def __init__(self, x_length, y_length, swarm_size):
        ShowBase.__init__(self)

        self.labels = []
        self.label_toggle = True

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
        self.accept('l', self.toggleLabels)                             # listen for 'l' keypress

    def toggleLabels(self):
        if self.label_toggle == True:                                   # if labels are 'on'
            for label in self.labels:
                label.hide()                                            # hide labels
            self.label_toggle = False                                   # set to 'off'
        else:                                                           # if labels are 'off'
            for label in self.labels:
                label.show()                                            # show labels
            self.label_toggle = True                                    # set to 'on'

    def switchFocus(self):
        self.focus_switch_counter += 1
        while self.focus_switch_counter > self.swarm_size - 1:          # loop back around to start of list
            self.focus_switch_counter -= self.swarm_size
        print(f'Moving camera to robot {self.focus_switch_counter} at {self.robot_pos[self.focus_switch_counter]}')
        self.moveCamera(self.robot_pos[self.focus_switch_counter])      # move camera to next robot

    def moveCamera(self, pos):
        self.focus.setPos(pos)                                          # move focus of camera
        self.disableMouse()
        self.camera.setPos(LVector3f(0, 0, 400))                        # move camera relative to focus
        self.camera.setHpr(0, -90, 0)

        mat = Mat4(self.camera.getMat())
        mat.invertInPlace()
        self.mouseInterfaceNode.setMat(mat)
        self.enableMouse()

    def displayLabel(self, pos, text, parent):
        label = TextNode('id_label')                                    # add text node
        label.setText(text)
        label.setTextColor(1, 1, 1, 1)
        label.setAlign(TextNode.ACenter)
        label.setCardColor(1, 1, 1, 0.3)                                # add text frame
        label.setCardAsMargin(0, 0, 0, 0)
        label.setCardDecal(True)

        self.text3d = NodePath(label)                                   # add text to node
        self.text3d.setScale(3, 3, 3)
        self.text3d.setTwoSided(True)
        self.text3d.setBillboardPointEye()                              # make text billboard (move with camera)
        self.text3d.reparentTo(parent)
        self.text3d.setPos(self.render, pos + LVector3f(0, 0, 20))      # set pos above component model
        self.labels.append(self.text3d)

    def calcPos(self, src, dst, connection):
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

    def renderRobot(self, robot):
        nodes = []                                                              # nodes in scene graph/tree
        g_orientations = []                                                     # orientations of nodes in scene
        # add position of robot core to list
        self.robot_pos.append(LVector3f(robot.core_pos[0], robot.core_pos[1], robot.core_pos[2]))
        robot.connections[0].src.root = True  # !!!!!CHANGE!!!!!
        for i, connection in enumerate(robot.connections):
            if connection.src.root and i == 0:
                src_path = "./models/BAM/" + connection.src.type + '.bam'       # get path of source model file
                self.src = self.loader.loadModel(src_path)                      # load model of source component
                # if component is root comp (core) set it's position to core position & place
                connection.src.pos = LVector3f(robot.core_pos[0], robot.core_pos[1], robot.core_pos[2])

                self.src.setPos(connection.src.pos)                             # set position of source model
                self.src.reparentTo(self.render)                                # set parent to render node
                self.src.setName(connection.src.id)                             # set name of node to component ID

                self.displayLabel(connection.src.pos, 'Robot ' + str(robot.id), self.src)  # display robot id label text
                nodes.append(self.src)
                g_orientations.append(connection.src.orientation)

            dst_path = "./models/BAM/" + connection.dst.type + '.bam'           # get path of destination model file
            self.dst = self.loader.loadModel(dst_path)                          # load model of source component
            self.dst.setName(connection.dst.id)

            if 'Hinge' in connection.src.type and connection.src_slot == 1:     # standardise hinge slots
                connection.src_slot = 2
            if 'Hinge' in connection.dst.type and connection.dst_slot == 1:
                connection.dst_slot = 2

            # calc position of dest comp based on source position
            connection.dst.pos, heading = self.calcPos(self.src, self.dst, connection)

            self.dst.setColor(connection.dst.colour)                            # set model to relevant colour

            for i, node in enumerate(nodes):                                    # find src node in tree and reparent to
                if node.getName() == connection.src.id:
                    self.dst.reparentTo(node)
                    break

            self.dst.setHpr(self.render, heading, 0, 0)
            self.dst.setPos(self.render, connection.dst.pos)                    # set position of destination model

            nodes.append(self.dst)                                              # append component to node list
            g_orientations.append(connection.dst.orientation)                   # append orientation of comp to list

            #print(f'Rendered \'{connection.dst.id}\' of type \'{connection.dst.type}\' at {connection.dst.pos}')

        self.moveCamera(self.robot_pos[self.focus_switch_counter])              # move camera to first robot loaded

        for i, node in enumerate(nodes):
            # rotate nodes according to orientation
            node.setHpr(node.getHpr()[0], 0, node.getHpr()[2] + DST_SLOTS[g_orientations[i]])
            # display ID labels of components
            if i > 0:
                self.displayLabel(node.getPos(self.render), node.getName(), node)
