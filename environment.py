# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------
"""Renders environment terrain and robot components"""

# TODO: change 'root' workings
#       physics/collision
#       LICENSING
# EXTRA: bad orientation/slot warning + autocorrect option, move robots around with mouse, method comments!

from panda3d.core import NodePath
from panda3d.core import TextNode
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import Mat4
from panda3d.core import LVector3f
from panda3d.core import LVector2f
from panda3d.core import LPoint3f
from panda3d.core import AmbientLight
from panda3d.core import BoundingBox
from direct.showbase.ShowBase import ShowBase

ORIENTATION = {0: 0, 1: 90, 2: 180, 3: 270}


class Environment(ShowBase):
    def __init__(self, x_length, y_length, swarm_size):
        ShowBase.__init__(self)

        self.labels = []                                                # labels in scene
        self.label_toggle = True                                        # whether labels are enabled or not

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

    def outOfBoundsDetect(self, robot):
        root_node = robot.connections[0].src.node
        robot_min, robot_max = root_node.getTightBounds()

        box = BoundingBox(robot_min, robot_max)
        vertices = box.getPoints()

        out = False
        out_of_bounds = LVector2f(0, 0)
        x_max, x_min, y_max, y_min = vertices[4][0], vertices[0][0], vertices[2][1], vertices[0][1]     # get bounds of robot bounding box
        if x_max > self.x_length/2:                             # if over +x
            out_of_bounds[0] = int(x_max - self.x_length/2)
        elif x_min < -self.x_length/2:                          # if over -x
            out_of_bounds[0] = int(self.x_length/2 + x_min)
        if y_max > self.y_length/2:                             # if over +y
            out_of_bounds[1] = int(y_max - self.y_length/2)
        elif y_min < -self.y_length/2:                          # if over -y
            out_of_bounds[1] = int(self.y_length/2 + y_min)
        return out_of_bounds

    def renderRobot(self, robot):
        # add position of robot core to list
        self.robot_pos.append(LVector3f(robot.core_pos[0], robot.core_pos[1], robot.core_pos[2]))

        robot.connections[0].src.root = True  # !!!!!CHANGE!!!!!
        for i, connection in enumerate(robot.connections):                      # loop through connections in robot
            if connection.src.root and i == 0:                                  # if source is the core component
                src_path = "./models/BAM/" + connection.src.type + '.bam'       # get path of source model file
                self.src = self.loader.loadModel(src_path)                      # load model of source component
                # set core's position to robot core_pos
                connection.src.pos = LVector3f(robot.core_pos[0], robot.core_pos[1], robot.core_pos[2])

                self.src.setPos(connection.src.pos)                             # set position of source model
                self.src.reparentTo(self.render)                                # set parent to render node
                self.src.setName(connection.src.id)                             # set name of node to component ID

                self.displayLabel(connection.src.pos, 'Robot ' + str(robot.id), self.src)   # display robot id label text
                connection.src.node = self.src                                              # add Panda3D node to robotComp

            dst_path = "./models/BAM/" + connection.dst.type + '.bam'           # get path of destination model file
            self.dst = self.loader.loadModel(dst_path)                          # load model of source component
            self.dst.setName(connection.dst.id)

            if 'Hinge' in connection.src.type and connection.src_slot == 1:     # standardise hinge slots
                connection.src_slot = 2
            if 'Hinge' in connection.dst.type and connection.dst_slot == 1:
                connection.dst_slot = 2

            # calc position of dest comp based on source position
            connection.dst.pos, heading = connection.dst.calcPos(self.src, self.dst, connection)

            self.dst.setColor(connection.dst.colour)                            # set model to relevant colour
            self.dst.reparentTo(connection.src.node)                            # reparent dst node to src node (add to tree)

            self.dst.setHpr(self.render, heading, 0, 0)                         # set heading of destination model
            self.dst.setPos(self.render, connection.dst.pos)                    # set position of destination model

            connection.dst.node = self.dst                                      # add Panda3D node to robotComp

            #print(f'Rendered \'{connection.dst.id}\' of type \'{connection.dst.type}\' at {connection.dst.pos}')

        self.moveCamera(self.robot_pos[self.focus_switch_counter])              # move camera to first robot loaded

        root = robot.connections[0].src
        # rotate root node
        root.node.setHpr(root.node.getHpr()[0], 0, root.node.getHpr()[2] + ORIENTATION[root.orientation])
        for i, connection in enumerate(robot.connections):
            node = connection.dst.node
            # rotate child nodes according to orientation
            node.setHpr(node.getHpr()[0], 0, node.getHpr()[2] + ORIENTATION[connection.dst.orientation])
            # display ID labels of components
            if i > 0:
                self.displayLabel(node.getPos(self.render), node.getName(), node)

        out_of_bounds = self.outOfBoundsDetect(robot)                           # check if robot is out of bounds
        if out_of_bounds != LVector2f(0, 0):
            return out_of_bounds
