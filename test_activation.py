import unittest

from roboviz.robotGUI import *
from roboviz.robotUtils import *
from roboviz.environment import *
from roboviz.robotComp import *
from roboviz.connection import *
from roboviz.robot import *
from roboviz.brain import *

fakeGUI = RobotGUI()
fakeUtil = RobotUtils('', '', '')
fakeEnv = Environment(0, 0, 0)


class TestGUI(unittest.TestCase):

    def test_gui_activation(self):
        self.assertEqual(fakeGUI.cli, False)
        self.assertEqual(fakeGUI.config_path, '')
        self.assertEqual(fakeGUI.pos_path, '')
        self.assertEqual(fakeGUI.robot_path, '')
        self.assertEqual(fakeGUI.ANN, True)
        print("\nGUI passed all tests")


class TestUtil(unittest.TestCase):

    def test_util_activation(self):
        self.assertEqual(fakeUtil.config_path, '')
        self.assertEqual(fakeUtil.pos_path, '')
        self.assertEqual(fakeUtil.robot_path, '')
        print("\nUtil passed all tests")


class TestEnv(unittest.TestCase):

    def test_env_activation(self):
        self.assertEqual(fakeEnv.x_length, 0)
        self.assertEqual(fakeEnv.y_length, 0)
        self.assertEqual(fakeEnv.swarm_size, 0)
        self.assertEqual(fakeEnv.label_toggle, False)
        self.assertEqual(fakeEnv.focus_switch_counter, 0)
        fakeEnv.toggleLabels()
        self.assertEqual(fakeEnv.label_toggle, True)
        print("\nEnv passed all tests")


class testComp(unittest.TestCase):
    def test_comp_activation(self):
        fakeComp = RobotComp(0, 'Fake', True, 0)
        self.assertEqual(fakeComp.id, 0)
        self.assertEqual(fakeComp.type, 'Fake')
        self.assertTrue(fakeComp.root)
        self.assertEqual(fakeComp.orientation, 0)
        self.assertEqual(fakeComp.direction, 0)
        self.assertEqual(fakeComp.dst_pos, 0)
        self.assertEqual(fakeComp.deltaX, 0)
        self.assertEqual(fakeComp.mass, 20)
        self.assertEqual(fakeComp.calcAccelaration(), 196)
        print("\nComp passed all tests")

    def test_hinge_activation(self):
        fakeHinge = Hinge(0, 'Fake', True, 0)
        self.assertEqual(fakeHinge.id, 0)
        self.assertEqual(fakeHinge.type, 'Fake')
        self.assertTrue(fakeHinge.root)
        self.assertEqual(fakeHinge.orientation, 0)
        self.assertEqual(fakeHinge.direction, 0)
        self.assertEqual(fakeHinge.dst_pos, 0)
        self.assertEqual(fakeHinge.deltaX, 0)
        self.assertEqual(fakeHinge.mass, 20)
        self.assertEqual(fakeHinge.calcAccelaration(), 196)
        self.assertEqual(fakeHinge.colour, (0, 1, 0, 1))
        print("\nHinge passed all tests")

    def test_brick_activation(self):
        fakeBrick = Brick(0, 'Fake', True, 0)
        self.assertEqual(fakeBrick.id, 0)
        self.assertEqual(fakeBrick.type, 'Fake')
        self.assertTrue(fakeBrick.root)
        self.assertEqual(fakeBrick.orientation, 0)
        self.assertEqual(fakeBrick.direction, 0)
        self.assertEqual(fakeBrick.dst_pos, 0)
        self.assertEqual(fakeBrick.deltaX, 0)
        self.assertEqual(fakeBrick.mass, 50)
        self.assertAlmostEqual(fakeBrick.calcAccelaration(), 490)
        self.assertEqual(fakeBrick.colour, (1, 0, 0, 1))
        print("\nBrick passed all tests")


class testConnect(unittest.TestCase):

    def test_con_activation(self):
        fakeComp1 = Brick(1, 'FakeBrick', True, 0)
        fakeComp2 = Hinge(2, 'FakeHinge', False, 1)
        fakeConnection = Connection(fakeComp1, fakeComp2, 0, 1)
        self.assertEqual(fakeConnection.src, fakeComp1)
        self.assertEqual(fakeConnection.dst, fakeComp2)
        self.assertEqual(fakeConnection.src_slot, 0)
        self.assertEqual(fakeConnection.dst_slot, 1)
        fakeConnection.standardiseSlots()
        self.assertEqual(fakeConnection.dst_slot, 2)
        print("\nConnection passed all tests")


class testRobot(unittest.TestCase):

    def test_con_activation(self):
        fakeComp1 = Brick(1, 'FakeBrick', True, 0)
        fakeComp2 = Hinge(2, 'FakeHinge', False, 0)
        fakeConnection = Connection(fakeComp1, fakeComp2, 0, 1)

        compArr = []
        compArr.append(fakeComp1)
        compArr.append(fakeComp2)

        fakeRobot = Robot(0, fakeConnection, compArr, (0, 0, 0))
        self.assertEqual(fakeRobot.id, 0)
        self.assertEqual(fakeRobot.connections, fakeConnection)
        self.assertEqual(fakeRobot.components, compArr)
        self.assertEqual(fakeRobot.core_pos, (0, 0, 0))
        print("\nRobot passed all tests")


class testBrain(unittest.TestCase):

    def test_brain_activation(self):
        fakeComp1 = Brick(1, 'FakeBrick', True, 0)
        fakeComp2 = Hinge(2, 'FakeHinge', False, 0)
        fakeComp3 = RobotComp(3, 'FakeHinge', False, 0)
        weights = [1, 2, 3]
        params = [1.1, 1.2, 2.1, 2.2, 2.3]
        type = ['input', 'sigmoid', 'oscillator']

        compArr = []
        compArr.append(fakeComp1)
        compArr.append(fakeComp2)
        compArr.append(fakeComp3)

        fakeBrain = ann(compArr, 1, 2, weights, params, type)
        self.assertEqual(fakeBrain.MAX_PARAMS, 3)
        self.assertEqual(fakeBrain.outputPorts, compArr)
        self.assertEqual(fakeBrain.INPUTS, 1)
        self.assertEqual(fakeBrain.OUTPUTS, 2)
        self.assertEqual(fakeBrain.Weights, weights)
        self.assertEqual(fakeBrain.Params, params)
        self.assertEqual(fakeBrain.Types, type)
        self.assertEqual(fakeBrain.state, [0.0, 0.0, 0.0])
        fakeBrain.feed([0.0])
        self.assertEqual(fakeBrain.input, [0.0])
        fakeBrain.step(0.01)
        self.assertEqual(fakeBrain.fetch(), [0.0, 0.0])
        print("\nANN passed all tests")


if __name__ == '__main__':
    unittest.main()
