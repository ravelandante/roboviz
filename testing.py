from robotComp import RobotComp
from hinge import Hinge
from brick import Brick
from connection import Connection
from robot import Robot
from environment import Environment
from robotUtils import RobotUtils
from robotGUI import RobotGUI
import pytest

from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerQueue
from panda3d.core import CollisionRay
from panda3d.core import CollisionNode
from panda3d.core import AmbientLight
from panda3d.core import LVector3f
from panda3d.core import LVector2f
from panda3d.core import Mat4
from panda3d.core import GeomNode
from panda3d.core import TextNode
from panda3d.core import NodePath
from panda3d.core import WindowProperties


class TestClass():

    core = Brick('core', 'FixedBrick', False, 0)
    hinge = Hinge('hinge', 'ActiveHinge', False, 1)
    brick = Brick('brick', 'FixedBrick', False, 0)
    components = [core, brick, hinge]

    con1 = Connection(core, hinge, 2, 0)
    con2 = Connection(hinge, brick, 1, 3)
    connections = [con1, con2]

    config = [1000, 1000, 1]
    pos = [[0, 0, 0], [100, 0, 0], [0, 100, 0]]
    #env = Environment(config[0], config[1], config[2])

    config_path = 'config/'
    pos_path = 'positions/'
    robot_path = 'json/'

    robot1 = Robot(1, connections, components, [0, 0, 0])
    #env.renderRobot(robot1)

###########################################################################################################################################################################
    # Test Robot rendering helper functions
    def test_standardiseSlots(self):
        self.con1.standardiseSlots()
        assert self.con1.src_slot == 3 and self.con1.dst_slot == 0
        self.con2.standardiseSlots()
        assert self.con2.src_slot == 2 and self.con2.dst_slot == 1

    """def test_calcPos(self):
        src_path = './models/BAM/' + self.con1.src.type + '.bam'
        src = self.loader.loadModel(src_path)
        dst_path = './models/BAM/' + self.con1.dst.type + '.bam'
        dst = self.loader.loadModel(dst_path)
        assert self.con1.src.calcPos(src, dst) == [LVector3f(20, 0, 0), 90]"""

###########################################################################################################################################################################
    # Test RobotGUI Error Handling

    def test_runSim_format1(self, capfd):
        gui = RobotGUI(config_path=self.config_path + 'pos.txt', pos_path=self.pos_path + 'pos.txt', robot_path=self.robot_path + 'robot.json', cli=True)
        with pytest.raises(SystemExit):
            gui.runSim()
        out, err = capfd.readouterr()
        assert out == '[ERROR] Incorrect configuration file format or file not found\n'

    def test_runSim_format2(self, capfd):
        gui = RobotGUI(config_path=self.config_path + 'config.txt', pos_path=self.pos_path + 'config.txt', robot_path=self.robot_path + 'robot.json', cli=True)
        with pytest.raises(SystemExit):
            gui.runSim()
        out, err = capfd.readouterr()
        assert out == '[ERROR] Incorrect positions file format or file not found\n'

    def test_runSim_format3(self, capfd):
        gui = RobotGUI(config_path=self.config_path + 'config.txt', pos_path=self.pos_path + 'pos.txt', robot_path=self.robot_path + 'config.json', cli=True)
        with pytest.raises(SystemExit):
            gui.runSim()
        out, err = capfd.readouterr()
        assert out == '[ERROR] Incorrect robot file format or file not found\n'

    def test_runSim_logic1(self, capfd):
        gui = RobotGUI(config_path=self.config_path + 'config4.txt', pos_path=self.pos_path + 'pos.txt', robot_path=self.robot_path + 'robot.json', cli=True)
        with pytest.raises(SystemExit):
            gui.runSim()
        out, err = capfd.readouterr()
        assert out == '[ERROR] Incorrect amount of robot positions given\n'

    def test_runSim_logic2(self, capfd):
        gui = RobotGUI(config_path=self.config_path + 'config.txt', pos_path=self.pos_path + 'pos4.txt', robot_path=self.robot_path + 'robot.json', cli=True)
        with pytest.raises(SystemExit):
            gui.runSim()
        out, err = capfd.readouterr()
        assert out == '[ERROR] Mismatch between number of positions and swarm size given\n'

    def test_runSim_logic3(self, capfd):
        gui = RobotGUI(config_path=self.config_path + 'config.txt', pos_path=self.pos_path + 'pos4.txt', robot_path=self.robot_path + 'multipleRobots.json', cli=True)
        with pytest.raises(SystemExit):
            gui.runSim()
        out, err = capfd.readouterr()
        assert out == '[ERROR] Mismatch between number of robots and swarm size given\n'
###########################################################################################################################################################################
    # Test Robot out of bounds detection

    def test_out_of_bounds(self):
        bounds_normal = [0, -160, 300, -300, 50, 0]
        bounds_edge = [500, -500, 500, -300, 50, 0]
        bounds_out = [670, -200, 100, -850, 50, 0]
        self.robot1.bounds = bounds_normal
        assert self.robot1.outOfBoundsDetect(1000, 1000, test=True) == 'none'
        self.robot1.bounds = bounds_edge
        assert self.robot1.outOfBoundsDetect(1000, 1000, test=True) == 'none'
        self.robot1.bounds = bounds_out
        assert self.robot1.outOfBoundsDetect(1000, 1000, test=True) == LVector2f(170, -350)
        

###########################################################################################################################################################################