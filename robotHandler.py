# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------
"""Runs application in either GUI or command line mode"""

from robotGUI import RobotGUI
import sys

# Command line mode
if(len(sys.argv) > 1):
    config_path = sys.argv[1]
    pos_path = sys.argv[2]
    robot_path = sys.argv[3]

    if len(sys.argv) < 4:
        print('[ERROR] Not all files have been entered: python robotHandler.py <config.txt> <positions.txt> <robot.json>')
        quit()
    if not config_path.endswith('.txt'):
        print('[ERROR] Incorrect file type for configuration file, should be .txt')
        quit()
    if not pos_path.endswith('.txt'):
        print('[ERROR] Incorrect file type for positions file, should be .txt')
        quit()
    if not robot_path.endswith('.json'):
        print('[ERROR] Incorrect file type for robot file, should be .json')
        quit()

    window = RobotGUI(config_path=config_path, pos_path=pos_path, robot_path=robot_path, cli=True)
    window.runSim()

# GUI mode
else:
    window = RobotGUI()
    window.startGUI()

    """if((len(robotArr) == len(positions)) and (len(robotArr) == configuration[2])):
            else:
                print("Contradicting swarm sizes!")
                if os.path.isfile('LastRender.txt'):
                    os.remove('LastRender.txt')
                quit()

            if(len(positions) == configuration[2]):
            else:
                print("Contradicting swarm sizes!")
                if os.path.isfile('LastRender.txt'):
                    os.remove('LastRender.txt')
                quit()
    except IOError:
        print("Couldn't find Robot JSON file:", JSONPath)
        quit()"""
