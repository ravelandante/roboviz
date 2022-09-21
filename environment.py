# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------

from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerQueue
from panda3d.core import CollisionRay
from panda3d.core import CollisionNode
from panda3d.core import AmbientLight
from panda3d.core import LVector3f
from panda3d.core import Mat4
from panda3d.core import GeomNode
from panda3d.core import TextNode
from panda3d.core import NodePath
from panda3d.core import WindowProperties
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import PandaSystem

from numpy import deg2rad
import math


SHIFT_VALUE = 5     # number of units robots will be moved by
ORIENTATION = {0: 0, 1: 90, 2: 180, 3: 270}
SHIFT_DIRECTION = {0: LVector3f(0, SHIFT_VALUE, 0), 2: LVector3f(0, -SHIFT_VALUE, 0), 3: LVector3f(-SHIFT_VALUE, 0, 0),
                   1: LVector3f(SHIFT_VALUE, 0, 0), 4: LVector3f(0, 0, SHIFT_VALUE), 5: LVector3f(0, 0, -SHIFT_VALUE), }


class Environment(ShowBase):
    """Renders environment terrain and robot components"""

    def __init__(self, x_length, y_length, swarm_size):
        """
        Constructor   
        Args:  
            `x_length`: the x size of the environment plane (int)  
            `y_length`: the y size of the environment plane (int)  
            `swarm_size`: the number of Robots in the swarm (int)
        """
        ShowBase.__init__(self)

        # DEBUG/PROTOTYPE OPTIONS
        self.setFrameRateMeter(True)
        proto_text = 'RoboViz Prototype'                                # add prototype text
        proto_textNode = OnscreenText(text=proto_text, pos=(0.95, 0.85), scale=0.04,
                                      fg=(1, 0.5, 0.5, 1), align=TextNode.ACenter, mayChange=0)
        print("Panda version:", PandaSystem.getVersionString())

        props = WindowProperties()
        props.setTitle('RoboViz')
        #props.setSize(1200, 780)
        props.setIconFilename('resources/r_icon.ico')
        self.win.requestProperties(props)

        self.robotNode = NodePath('robotNode')
        self.robotNode.reparentTo(self.render)

        self.x_length = x_length
        self.y_length = y_length
        self.swarm_size = swarm_size

        self.labels = []                                                # labels in scene
        self.label_toggle = False                                       # whether labels are enabled or not

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
        self.help_textNode = OnscreenText(text=help_text, pos=(1, 0.7), scale=0.04,
                                          fg=(1, 1, 1, 1), bg=(0.3, 0.3, 0.3, 0.6), align=TextNode.ACenter, mayChange=0)
        sel_text = 'Selected Robot: none\nSelected Component: none'                                             # add selected text
        self.sel_textNode = OnscreenText(text=sel_text, pos=(1, 0.8), scale=0.04,
                                         fg=(1, 1, 1, 1), bg=(0.3, 0.3, 0.3, 0.6), align=TextNode.ACenter, mayChange=1)

        # KEYPRESSES
        self.accept('c', self.switchFocus)
        self.accept('l', self.toggleLabels)
        self.accept('h', lambda: self.help_textNode.show() if self.help_textNode.isHidden() else self.help_textNode.hide())
        self.accept('mouse1', self.select)

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
        self.accept('control-arrow_left', lambda: self.selected_robot.setHpr(self.render, self.selected_robot.getHpr(self.render) + LVector3f(90, 0, 0)))
        self.accept('control-arrow_right', lambda: self.selected_robot.setHpr(self.render, self.selected_robot.getHpr(self.render) + LVector3f(-90, 0, 0)))

    # def finalizeExit(self):
        # self.closeWindow(self.win)
        # self.destroy()

    def toggleLabels(self, first=False):
        """
        Toggles visibility of component labels
        Args:
            `first`: first display of labels or not (Boolean) **optional**  
        """
        if first:
            for label in self.labels:
                label.node().setTextColor(1, 1, 1, 1)                   # set label colours after node flattening
                label.node().setCardColor(1, 1, 1, 0.3)
                label.hide()                                            # hide labels
        elif self.label_toggle == True:                                 # if labels are 'on'
            for label in self.labels:
                label.hide()                                            # hide labels
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
        self.moveCamera(pos=list(self.robot_pos.values())[self.focus_switch_counter], z_dist=400)      # move camera to next robot
        self.focus_switch_counter += 1

    def moveCamera(self, pos, z_dist):
        """
        Moves camera to point above pos in scene (looking down)
        Args:
            `pos`: position of camera (LVector3f)  
            `z_dist`: distance above pos that camera is placed at (int)
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
        """
        Enlarges component label when component is selected
        Args:
            `pickedObj`: newly selected component (PandaNode)
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
        """
        Displays a text label in the scene
        Args:
            `pos`: position of label (LVector3f)  
            `text`: text of label (String)  
            `parent`: parent of label (NodePath)
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
                self.selected_robot = pickedObj                         # set class attribute to selected robot core
                self.toggleBounding()                                   # show new selection box
                if self.selected_robot.getName()[0].isdigit() and self.selected_robot.getName()[1].isdigit():
                    sel_text = 'Selected Robot: ' + self.selected_robot.getName()[0:2] + '\nSelected Component: ' + self.selected_comp.getName()
                else:
                    sel_text = 'Selected Robot: ' + self.selected_robot.getName()[0] + '\nSelected Component: ' + self.selected_comp.getName()
                self.sel_textNode.setText(sel_text)

    def moveRobot(self, direction):
        """
        Moves selected robot in the given direction for the given units relative to the camera view
        Args:
            `direction`: direction of robot movement (0:forward, 1:back, 2:left, 3:right, 4:up, 5:down) (int)  
            `units`: number of units to move robot by (int)
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

    def initialView(self):
        """Moves and zooms camera so that all robots are initially placed in the camera's view"""
        # move + zoom camera to overlook all robots
        bounds = self.robotNode.getBounds()                                             # bounding box of all robots together
        centre = bounds.getCenter()                                                     # centre of bounding box
        fov = self.camLens.getFov()
        distance = bounds.getRadius() / math.tan(deg2rad(min(fov[0], fov[1]) * 0.6))    # calc distance needed to see all robots
        self.moveCamera(pos=centre, z_dist=distance)

    def renderRobot(self, robot):
        """
        Renders 1 robot in the scene by iterating through its Connections
        Args:
            `robot`: robot object to render (Robot)
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

                self.displayLabel(pos=connection.src.pos, text='Robot ' + str(robot.id), parent=self.src)   # display robot id label text
                connection.src.node = self.src                                              # add Panda3D node to robotComp

            dst_path = './models/BAM/' + connection.dst.type + '.bam'           # get path of destination model file
            self.dst = self.loader.loadModel(dst_path)                          # load model of source component
            self.dst.setName(connection.dst.id)
            self.dst.setTag('robot', connection.dst.id)

            connection.standardiseSlots()

            # calc position of dest comp based on source position
            connection.dst.pos, heading = connection.dst.calcPos(self.src, self.dst, connection)

            self.dst.setColor(connection.dst.colour)                            # set model to relevant colour
            self.dst.reparentTo(connection.src.node)                            # reparent dst node to src node (add to tree)

            self.dst.setHpr(self.render, heading, 0, 0)                         # set heading of destination model
            self.dst.setPos(self.render, connection.dst.pos)                    # set position of destination model
            if 'Hinge' in connection.dst.type:
                connection.dst.orientation += connection.src.orientation
                while connection.dst.orientation > 3:
                    connection.dst.orientation -= 4
                self.dst.setR(self.render, ORIENTATION[connection.dst.orientation])

            connection.dst.node = self.dst                                      # add Panda3D node to robotComp

            # print(f'Rendered \'{connection.dst.id}\' of type \'{connection.dst.type}\' at {connection.dst.pos}')

        for i, connection in enumerate(robot.connections):
            node = connection.dst.node
            if i > 0:
                self.displayLabel(pos=node.getPos(self.render), text=node.getName(), parent=node)
        robot.drawBounds()
        robot.connections[0].src.node.flattenStrong()                                               # hide labels and set colours after flattening
        self.toggleLabels(first=True)
