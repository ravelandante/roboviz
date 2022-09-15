# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------
"""Renders environment terrain and robot components"""

from numpy import deg2rad
import math
import copy

from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath
from panda3d.core import TextNode
from panda3d.core import GeomNode
from panda3d.core import Mat4
from panda3d.core import LVector3f
from panda3d.core import AmbientLight
from panda3d.core import CollisionNode
from panda3d.core import CollisionRay
from panda3d.core import CollisionHandlerQueue
from panda3d.core import CollisionTraverser

SHIFT_VALUE = 5     # number of units robots will be moved by
ORIENTATION = {0: 0, 1: 90, 2: 180, 3: 270}
SHIFT_DIRECTION = {0: LVector3f(0, SHIFT_VALUE, 0), 2: LVector3f(0, -SHIFT_VALUE, 0), 3: LVector3f(-SHIFT_VALUE, 0, 0),
                   1: LVector3f(SHIFT_VALUE, 0, 0), 4: LVector3f(0, 0, SHIFT_VALUE), 5: LVector3f(0, 0, -SHIFT_VALUE), }


class Environment(ShowBase):
    def __init__(self, x_length, y_length, swarm_size):
        ShowBase.__init__(self)

        # DEBUG/PROTOTYPE OPTIONS
        self.setFrameRateMeter(True)
        proto_text = 'RoboViz Prototype'                                # add prototype text
        proto_textNode = OnscreenText(text=proto_text, pos=(0.95, 0.85), scale=0.04,
                                      fg=(1, 0.5, 0.5, 1), align=TextNode.ACenter, mayChange=0)

        self.robotNode = NodePath('robotNode')
        self.robotNode.reparentTo(self.render)

        self.x_length = x_length
        self.y_length = y_length
        self.swarm_size = swarm_size

        self.labels = []                                                # labels in scene
        self.label_toggle = True                                        # whether labels are enabled or not

        self.robot_pos = {}                                             # positions of robot cores
        self.focus_switch_counter = 0

        self.myHandler = CollisionHandlerQueue()
        self.myTraverser = CollisionTraverser()

        pickerNode = CollisionNode('mouseRay')                          # for selecting robots
        pickerNP = self.camera.attachNewNode(pickerNode)
        pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()
        pickerNode.addSolid(self.pickerRay)
        self.myTraverser.addCollider(pickerNP, self.myHandler)

        self.set_background_color(0.6, 0.6, 0.6, 1)                     # set background colour to a lighter grey
        self.focus = NodePath('focus')                                  # create focus point (origin) of camera
        self.focus.reparentTo(self.render)
        self.camera.reparentTo(self.focus)

        self.plane = self.loader.loadModel('./models/BAM/plane.bam')    # load 'terrain' plane
        self.plane.setScale(self.x_length, self.y_length, 0)            # scale up to specified dimensions
        self.plane.reparentTo(self.render)

        alight = AmbientLight('alight')                                 # create ambient light
        alight.setColor((0.4, 0.4, 0.4, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        help_text = 'Controls:\nC - switch camera focus\nL - toggle component labels\nH - hide this help menu'  # add help text
        self.help_textNode = OnscreenText(text=help_text, pos=(0.95, 0.8), scale=0.04,
                                          fg=(1, 1, 1, 1), bg=(0.3, 0.3, 0.3, 0.6), align=TextNode.ACenter, mayChange=0)

        # KEYPRESSES
        self.accept('c', self.switchFocus)                              # listen for 'c' keypress
        self.accept('l', self.toggleLabels)                             # listen for 'l' keypress
        self.accept('h', self.toggleHelp)                               # listen for 'l' keypress
        self.accept('mouse1', self.select)                              # listen for 'mouse1' keypress

        # moving robots
        self.accept('arrow_up-repeat', self.moveRobot, [0])
        self.accept('arrow_up', self.moveRobot, [0])
        self.accept('arrow_down-repeat', self.moveRobot, [2])
        self.accept('arrow_down', self.moveRobot, [2])
        self.accept('arrow_left-repeat', self.moveRobot, [3])
        self.accept('arrow_left', self.moveRobot, [3])
        self.accept('arrow_right-repeat', self.moveRobot, [1])
        self.accept('arrow_right', self.moveRobot, [1])
        self.accept('control-arrow_up-repeat', self.moveRobot, [4])
        self.accept('control-arrow_up', self.moveRobot, [4])
        self.accept('control-arrow_down-repeat', self.moveRobot, [5])
        self.accept('control-arrow_down', self.moveRobot, [5])

        # rotating robots
        self.accept('control-arrow_left', self.rotateRobot, ['left'])
        self.accept('control-arrow_right', self.rotateRobot, ['right'])

    def toggleHelp(self):
        """Toggles visibility of the help menu"""
        if self.help_textNode.isHidden():                               # if text is 'on'
            self.help_textNode.show()                                   # hide text
        else:                                                           # if text is 'off'
            self.help_textNode.hide()                                   # show text

    def toggleLabels(self, first=False):
        """Toggles visibility of component labels"""
        if self.label_toggle == True:                                   # if labels are 'on'
            if first:
                for label in self.labels:
                    label.node().setTextColor(1, 1, 1, 1)               # set label colours after node flattening
                    label.node().setCardColor(1, 1, 1, 0.3)
                    label.hide()                                        # hide labels
            else:
                for label in self.labels:
                    label.hide()                                        # hide labels
            self.label_toggle = False                                   # set to 'off'
        else:                                                           # if labels are 'off'
            for label in self.labels:
                label.show()                                            # show labels
            self.label_toggle = True                                    # set to 'on'

    def toggleBounding(self):
        """Toggles visibility of robot bounding box (selection box)"""
        children = self.selected_robot.getChildren()
        for child in children:
            if child.getName().split('/')[-1] == 'lines':               # find line node in children of root
                if child.isHidden():                                    # if bounding box is hidden
                    child.show()
                else:                                                   # if bounding box is visible
                    child.hide()
                break

    def switchFocus(self):
        """Switches camera focus (origin) between robots in scene"""
        while self.focus_switch_counter > self.swarm_size - 1:          # loop 1 around to start of list
            self.focus_switch_counter -= self.swarm_size
        # print(f'Moving camera to robot {self.focus_switch_counter} at {list(self.robot_pos.values())[self.focus_switch_counter]}')
        self.moveCamera(list(self.robot_pos.values())[self.focus_switch_counter], 400)      # move camera to next robot
        self.focus_switch_counter += 1

    def moveCamera(self, pos, z_dist):
        """Moves camera to point above pos in scene (looking down)
        Args:
            pos (LVector3f): position of camera
            z_dist (int): distance above pos that camera is placed at
        """
        self.focus.setPos(pos)                                          # move focus of camera
        self.disableMouse()
        self.camera.setPos(LVector3f(0, 0, z_dist))                     # move camera relative to focus
        self.camera.setHpr(0, -90, 0)

        mat = Mat4(self.camera.getMat())
        mat.invertInPlace()
        self.mouseInterfaceNode.setMat(mat)
        self.enableMouse()

    def enlargeLabel(self, pickedObj):
        """Enlarges component label when component is selected
        Args:
            pickedObj (PandaNode): newly selected component
        """
        for child in pickedObj.getChildren():
            if child.getName() == 'id_label':                           # find label of newly selected component
                child.setScale(6, 6, 6)
                break
        if hasattr(self, 'selected_comp'):
            for child in self.selected_comp.getChildren():
                if child.getName() == 'id_label':                       # find label of old selected component
                    child.setScale(3, 3, 3)
                    break

    def displayLabel(self, pos, text, parent):
        """Displays a text label in the scene
        Args:
            pos (LVector3f): position of label
            text (String): text of label
            parent (NodePath): parent of label
        """
        label = TextNode('id_label')                                    # add text node
        label.setText(text)
        label.setAlign(TextNode.ACenter)
        label.setCardAsMargin(0, 0, 0, 0)
        label.setCardDecal(True)

        self.text3d = NodePath(label)                                   # add text to node
        self.text3d.setScale(3, 3, 3)
        self.text3d.setTwoSided(True)
        self.text3d.setBillboardPointEye()                              # make text billboard (move with camera)
        self.text3d.reparentTo(parent)
        self.text3d.setPos(self.render, pos + LVector3f(0, 0, 20))      # set pos above component model
        self.labels.append(self.text3d)

    def select(self):
        """Determines which robot is selected (by mouse click), updates self.selected_robot to represent this"""
        mpos = self.mouseWatcherNode.getMouse()
        self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

        self.myTraverser.traverse(self.render)
        if self.myHandler.getNumEntries() > 0:
            self.myHandler.sortEntries()                                # get closest object to mouse click
            pickedObj = self.myHandler.getEntry(0).getIntoNodePath()
            pickedObj = pickedObj.findNetTag('robot')                   # find object by tag
            if not pickedObj.isEmpty():
                if hasattr(self, 'selected_robot'):
                    self.toggleBounding()                               # hide old selection box

                self.enlargeLabel(pickedObj)
                self.selected_comp = pickedObj

                while True:
                    if 'Core' not in pickedObj.getName():
                        pickedObj = pickedObj.parent
                    else:
                        break
                self.selected_robot = pickedObj                               # set class attribute to selected robot core
                self.toggleBounding()                                   # show new selection box
                # print('Selected Robot', pickedObj.getName()[0])

    def moveRobot(self, direction):
        """Moves selected robot in the given direction relative to the camera view
        Args:
            direction (int): direction of robot movement (0:forward, 1:back, 2:left, 3:right, 4:up, 5:down)
        """
        heading = int(self.camera.getHpr()[0])
        rotation = int(self.camera.getHpr()[2])
        if direction not in [4, 5]:                                         # if moving along xy plane
            if heading in range(-45, 45):
                heading = 0
            elif heading in range(45, 135):
                heading = 1
            elif heading in range(135, 181) or heading in range(-180, -135):
                heading = 2
            elif heading in range(-135, -45):
                heading = 3
            if rotation in range(90, 181) or rotation in range(-180, -90):  # if camera is rotated around 180
                if direction in [1, 3]:
                    if direction == 1:
                        direction = 3
                    elif direction == 3:
                        direction = 1
            direction = int(direction) - heading
            if direction < 0:
                direction += 4
        else:                                                               # if moving along z axis
            if rotation in range(90, 181) or rotation in range(-180, -90):  # if camera is rotated around 180
                if direction == 4:                                          # switch up and down
                    direction = 5
                elif direction == 5:
                    direction = 4
        shift = SHIFT_DIRECTION[direction]                                  # get direction of shift
        self.selected_robot.setPos(self.render, self.selected_robot.getPos(self.render) + shift)
        self.robot_pos[int(self.selected_robot.getName()[0])] = self.selected_robot.getPos(self.render)

    def rotateRobot(self, direction):
        """Rotates selected robot in the given direction
        Args:
            direction (int): direction of rotation (left or right)
        """
        if direction == 'left':                                             # get direction of rotation
            rotation = LVector3f(90, 0, 0)
        elif direction == 'right':
            rotation = LVector3f(-90, 0, 0)
        self.selected_robot.setHpr(self.render, self.selected_robot.getHpr(self.render) + rotation)

    def initialView(self):
        # move + zoom camera to overlook all robots
        bounds = self.robotNode.getBounds()                                             # bounding box of all robots together
        centre = bounds.getCenter()                                                     # centre of bounding box
        fov = self.camLens.getFov()
        distance = bounds.getRadius() / math.tan(deg2rad(min(fov[0], fov[1]) * 0.6))    # calc distance needed to see all robots
        self.moveCamera(centre, distance)

    def renderRobot(self, robot):
        """Renders 1 robot in the scene by iterating through its Connections
        Args:
            robot (Robot): robot object to render
        """
        # add position of robot core to list (for camera focus switching)
        self.robot_pos[robot.id] = LVector3f(robot.core_pos[0], robot.core_pos[1], robot.core_pos[2])

        robot.connections[0].src.root = True  # !!!!!CHANGE!!!!!
        for i, connection in enumerate(robot.connections):                      # loop through connections in robot
            if connection.src.root and i == 0:                                  # if source is the core component
                src_path = './models/BAM/' + connection.src.type + '.bam'       # get path of source model file
                self.src = self.loader.loadModel(src_path)                      # load model of source component
                # set core's position to robot core_pos
                connection.src.pos = LVector3f(robot.core_pos[0], robot.core_pos[1], robot.core_pos[2])

                self.src.setPos(connection.src.pos)                             # set position of source model
                self.src.reparentTo(self.robotNode)                             # set parent to robotNode
                self.src.setName(str(robot.id) + connection.src.id)             # set name of node to component ID
                self.src.setTag('robot', str(robot.id) + connection.src.id)

                self.displayLabel(connection.src.pos, 'Robot ' + str(robot.id), self.src)   # display robot id label text
                connection.src.node = self.src                                              # add Panda3D node to robotComp

            dst_path = './models/BAM/' + connection.dst.type + '.bam'           # get path of destination model file
            self.dst = self.loader.loadModel(dst_path)                          # load model of source component
            self.dst.setName(connection.dst.id)
            self.dst.setTag('robot', connection.dst.id)

            if 'Hinge' in connection.src.type and connection.src_slot == 1:     # standardise source hinge slots
                connection.src_slot = 2
            if 'Hinge' in connection.dst.type and connection.dst_slot == 1:     # standardise destination hinge slots
                connection.dst_slot = 2

            # calc position of dest comp based on source position
            connection.dst.pos, heading = connection.dst.calcPos(self.src, self.dst, connection)

            self.dst.setColor(connection.dst.colour)                            # set model to relevant colour
            self.dst.reparentTo(connection.src.node)                            # reparent dst node to src node (add to tree)

            self.dst.setHpr(self.render, heading, 0, 0)                         # set heading of destination model
            self.dst.setPos(self.render, connection.dst.pos)                    # set position of destination model

            connection.dst.node = self.dst                                      # add Panda3D node to robotComp

            # print(f'Rendered \'{connection.dst.id}\' of type \'{connection.dst.type}\' at {connection.dst.pos}')

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
        robot.drawBounds()
        root.node.flattenStrong()                                               # hide labels and set colours after flattening
        self.toggleLabels(True)
