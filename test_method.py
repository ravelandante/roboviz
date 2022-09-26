import sys
from roboviz.hinge import Hinge
from roboviz.brick import Brick
from roboviz.connection import Connection
from roboviz.robot import Robot
from roboviz.robotUtils import RobotUtils
from roboviz.robotGUI import RobotGUI
import pytest
import os
from panda3d.core import LPoint3f
from panda3d.core import LVector2f
from panda3d.core import LVector3f


sys.path.append('../')


class TestClass():
    """Automatic testing class, invoke with 'pytest -q test_method.py'"""

    core = Brick('core', 'FixedBrick', False, 0)
    hinge = Hinge('hinge', 'ActiveHinge', False, 1)
    brick = Brick('brick', 'FixedBrick', False, 0)
    components = [core, brick, hinge]

    con1 = Connection(core, hinge, 2, 0)
    con2 = Connection(hinge, brick, 1, 3)
    connections = [con1, con2]

    con1.dst.bounds = (LPoint3f(-19.3838, -19.35, -17.05), LPoint3f(17.55, 19.3107, 17.0748))
    con1.src.bounds = (LPoint3f(-20.5, -20.5, 182.25), LPoint3f(20.5, 20.5, 222.37))
    con1.src.pos = LVector3f(0, 0, 0)

    con2.dst.bounds = (LPoint3f(-19.3838, -19.35, -17.05), LPoint3f(17.55, 19.3107, 17.0748))
    con2.src.bounds = (LPoint3f(-20.5, -20.5, 182.25), LPoint3f(20.5, 20.5, 222.37))
    con2.src.pos = LVector3f(38.3303, 0, 0)

    robot1 = Robot(0, connections, components, [0, 0, 0])
    robot2 = Robot(1, connections, components, [100, 0, 0])

###########################################################################################################################################################################
    # Test Robot rendering helper functions

    def test_standardiseSlots(self):
        self.con1.standardiseSlots()
        assert self.con1.src_slot == 3 and self.con1.dst_slot == 0
        self.con2.standardiseSlots()
        assert self.con2.src_slot == 2 and self.con2.dst_slot == 1

    def test_calcPos1(self):
        src = ''
        dst = ''
        dst_pos, heading = self.con1.src.calcPos(src, dst, self.con1, test=True)
        assert dst_pos[0] == 39.5
        assert dst_pos[1] == 0
        assert dst_pos[2] == 0
        assert heading == 270

    def test_calcPos2(self):
        src = ''
        dst = ''
        dst_pos, heading = self.con2.src.calcPos(src, dst, self.con2, test=True)
        assert int(dst_pos[0]) == 75
        assert int(dst_pos[1]) == 0
        assert int(dst_pos[2]) == 0
        assert heading == 360

###########################################################################################################################################################################
    # Test RobotGUI Error Handling

    config_path = 'config/'
    pos_path = 'positions/'
    robot_path = 'json/'

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
    # Test Robot out of bounds and collision detection

    def test_outOfBoundsDetect(self):
        bounds_normal = [0, -160, 300, -300, 50, 0]
        bounds_edge = [500, -500, 500, -300, 50, 0]
        bounds_out = [670, -200, 100, -850, 50, 0]
        self.robot1.bounds = bounds_normal
        assert self.robot1.outOfBoundsDetect(1000, 1000, test=True) == 'none'
        self.robot1.bounds = bounds_edge
        assert self.robot1.outOfBoundsDetect(1000, 1000, test=True) == 'none'
        self.robot1.bounds = bounds_out
        assert self.robot1.outOfBoundsDetect(1000, 1000, test=True) == LVector2f(170, -350)

    def test_collisionDetect(self):
        utils = RobotUtils('', '', '')
        robots = [self.robot1, self.robot2]
        bounds_normal = [[0, -160, 300, -300, 50, 0], [450, 100, -340, -440, -20, -40]]
        bounds_edge = [[0, -160, 300, -300, 50, 0], [50, -200, 250, -100, -20, -40]]
        bounds_coll = [[0, -160, 300, -300, 50, 0], [-50, -170, 250, -100, 20, 0]]

        self.robot1.bounds = bounds_normal[0]
        self.robot2.bounds = bounds_normal[1]
        assert utils.collisionDetect(robots) == []
        self.robot1.bounds = bounds_edge[0]
        self.robot2.bounds = bounds_edge[1]
        assert utils.collisionDetect(robots) == []
        self.robot1.bounds = bounds_coll[0]
        self.robot2.bounds = bounds_coll[1]
        print(utils.collisionDetect(robots))
        assert utils.collisionDetect(robots) == [[0, 1]]

###########################################################################################################################################################################
    # Test file operations

    utils = RobotUtils('config/config4.txt', 'positions/pos4.txt', 'json/robot1.json')
    positions = [[0, 0, 0], [-300, -300, 0], [300, 300, 0], [400, -200, 0]]
    config = [1000, 1000, 4]

    def test_configParse(self):
        assert self.utils.configParse() == self.config

    def test_posParse(self):
        assert self.utils.posParse() == self.positions

    def test_writeRobot(self):
        self.utils.writeRobot(self.robot1, 'robot1')
        robotIn = self.utils.robotParse(1, self.positions[0])[0]
        for i, _ in enumerate(robotIn.connections):
            r1 = robotIn.connections[i]
            r2 = self.robot1.connections[i]
            assert r1.src.id == r2.src.id
            assert r1.dst.id == r2.dst.id
            assert r1.src.type == r2.src.type
            assert r1.dst.type == r2.dst.type
            assert r1.src.root == r2.src.root
            assert r1.dst.root == r2.dst.root
            assert r1.src.orientation == r2.src.orientation
            assert r1.dst.orientation == r2.dst.orientation
            assert r1.src_slot == r2.src_slot
            assert r1.dst_slot == r2.dst_slot
        os.remove('json/robot1.json')

###########################################################################################################################################################################


"""Visual tests, invoke with 'python test_method.py'"""
if __name__ == '__main__':
    config_path = 'config/config4.txt'
    pos_path = 'positions/pos4.txt'
    robot_path = 'json/multipleRobots.json'

    window = RobotGUI(config_path=config_path, pos_path=pos_path, robot_path=robot_path, cli=True)
    window.runSim()
