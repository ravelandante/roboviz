# ----------------------------------------------------------------------------
# Created By: GMLMOG016, FLDCLA001, YNGFYN001
# Created Date: 13/08/22
# ---------------------------------------------------------------------------
"""Runs application in either GUI or command line mode"""

from robotGUI import RobotGUI
import sys

CREATE_BRAIN = True

# Command line mode
if(len(sys.argv) > 1):
    window = RobotGUI(sys.argv[1], sys.argv[2], sys.argv[3])
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
