# User Manual
****
## Installation
****
### Prerequisites:
- Python 3.10.2 or higher
- Pip
- RoboViz source  

### Installing Required Packages
To install the required Python packages, from the root project directory run:
`pip install -r requirements.txt`
****
## Usage

RoboViz can be run in both command line (CLI) mode and graphical (GUI) mode.
To load a **Robot** in the **Environment**, 3 files are required:
- Configuration file (.txt) - contains the environment and robot swarm size
- Positions file (.txt) - contains the <x, y, z> positions for each robot
- Robot file (.json) - contains specs for one or many robots

_Formats for these files are provided in the Appendix_
****
### Rendering a robot

### CLI

To use the CLI, simply run the script by providing the relevant file paths args:
`python robotHandler.py <config_path> <positions_path> <robot_json_path>`

The **Environment** will then be loaded and the **Robots** rendered, before the viewing window appears.
_Note: Collision and out of bounds detection is not supported for the CLI_

##### Example
`python robotHandler.py ./config/config.txt ./positions/pos.txt ./json/robot.json`

### GUI
To use the GUI, simply run the script without any args:
`python robotHandler.py`

Then:
1. Select the 3 required files by clicking the 'Browse' buttons
2. Click on the 'Submit' button

The **Environment** will then be loaded and the **Robots** rendered, before the viewing window appears.

****

### Navigating the viewing window

The Camera is automatically centered on the first **Robot** to be loaded

##### Camera Controls:
- Orbit: Hold **'middle mouse button'** and drag
- Shift: Hold **'left mouse button'** and drag 
- Zooming: Hold **'right mouse button'** and drag back and forth
- Switching Focus: **'C'** - cycle the camera's focus between **Robots**

##### Robot Movement Controls:

- Clicking on a **Robot** will select it and toggle its selection outline box
- Clicking on a **Component** will enlarge its label for easier viewing
(The selected **Robot** and **Component** are also shown in the menu near the top right)

With a **Robot** selected:
- Movement left/right: **'left/right arrows'**
- Movement forward/back: **'up/down arrows'**
- Movement up/down: **'ctrl + up/down arrows'**
- Rotation: **'ctrl + left/right arrows'**

##### Other Controls:
- Toggle Component Labels: **'L'**
- Hide Help Menu: **'H'**

****

### Building a robot

You can create your own **Robots** using the file formats specified in the Appendix. Alternatively, you can use the **Robot builder**, accessed by clicking on the 'Build' button on the initial GUI window.

To start creating a **Robot**, **DO STUFF HERE!!!!!!!!**

****

## Appendix

****

### File Formats

****

#### Configuration File

The **configuration file** contains the **x** and **y** dimensions of the environment plane and the robot **swarm size**. It should be a **text (.txt)** file.

The format should be as follows:

```
x_length
y_length
swarm_size
```

##### Example

```
1000
1500
10
```

****

#### Positions File

The **positions file** contains the **<x, y, z> positions** of each **Robot** in the swarm. It should be a **text (.txt)** file.

The format should be as follows:

```
x y z   # robot 1
x y z   # robot 2
x y z   # etc.
```

##### Example

```
0 0 0
100 0 0
-200 800 50
```

****

#### Robot File

The **robot file** contains the specifications for one or many **Robots**. It should be a **JSON (.json)** file.

The format should be as follows:
**Single Robot (Homogenous)**

```
{
    "id": 0,
    "body": {
        "part": [
            {
                "id": "Core",
                "type": "CoreComponent",
                "root": true,
                "orientation": 0
            },
            {
                "id": "Hip1",
                "type": "ActiveHinge",
                "root": false,
                "orientation": 1
            },
        ],
        "connection": [
            {
                "src": "Core",
                "dest": "Hip1",
                "srcSlot": 0,
                "destSlot": 0
            },
        ]
    },
    "brain": {
        "neuron": [
            {
                "id": "Core-0",
                "layer": "input",
                "type": "simple",
                "bodyPartId": "Core",
                "ioId": 0,
                "gain": 1.0
            },
        ],
        "connection": [
            {
                "src": "Core-0",
                "dest": "Hip1-0",
                "weight": -1.7611217498779297
            },
        ]
    }
}
```

**Multiple Robots (Heterogeneous)**

```
{
  "swarm": [
    {
        "id": 1,
        "body": {
            "part": [
            {
                "id": "Core",
                "type": "CoreComponent",
                "root": true,
                "orientation": 0
            },
            {
                "id": "Hip1",
                "type": "ActiveHinge",
                "root": false,
                "orientation": 1
            },
        ],
        "connection": [
        etc...
           ...
           ...
        ]
      }
    }
  ]
}
```

_Note: The "brain" section can be left out if CREATE_BRAIN is set to False in robotHandler.py._

##### Example

Two full example JSON files are given in the source code (homogenous + heterogeneous)

****