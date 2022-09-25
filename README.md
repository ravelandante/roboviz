# User Manual
****

## Table of Contents

1. [**Installation**](/docs/User_Manual##Installation)
2. [**Usage**](/docs/User_Manual##Usage)
    a. [Rendering a robot](/docs/User_Manual###Rendering-a-robot)
    b. [Collisions and out of bounds](/docs/User_Manual###Collisions-and-out-of-bounds)
    c. [Navigating the viewing window](/docs/User_Manual###Navigating-the-viewing-window)
    d. [Building a robot](/docs/User_Manual###Building-a-robot)
3. [**Appendix**](/docs/User_Manual##Appendix)
    a. [File Formats](/docs/User_Manual###File-Formats)

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
- **Configuration file (.txt)** - contains the environment and robot swarm size
- **Positions file (.txt)** - contains the <x, y, z> positions for each robot
- **Robot file (.json)** - contains specs for one or many robots

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
1. Select the 3 required files by clicking the **'Browse'** buttons
2. Click on the **'Submit'** button

The **Environment** will then be loaded and the **Robots** rendered, before the viewing window appears.

##### Auto-packing

If you do not want to specify the positions for each **Robot** in the scene (e.g. if you have a great many **Robots** in your swarm), you can enable the **auto-pack** option from the bottom left of the main GUI window (This means you will _not_ have to specify a **positions file**).

This will attempt to fit all of the **Robots** into the environment of dimensions specified in the **configuration file**.

If it cannot fit all the **Robots** into the specified environment, it will attempt to incrementally enlarge the environment until it can (this increment can be changed by editing the _INCT_AMT_ constant in the _robotUtils.py_ file).
The buffer or spacing between these packed **Robots** can also be changed by editing the _BUFFER_ constant in the _robotUtils.py_ file.

****

### Collisions and out of bounds

RoboViz has a system for detecting _possible_ collisions between **Robots** and any **Robots** that are out of the bounds of the **Environment**. If collisions or bound violations are detected, a window will appear after clicking the **'Submit'** button. This will list _possible_ collisions between **Robots** in the scene and any **Robots** that are out of bounds and the units by which they are.

_Note: Collisions are reported as possible as the collision detection system simply uses the rectangular bounding boxes of the **Robots** and not their actual shapes. There may not be a collision after all as the actual components of 2 'colliding' **Robots** may not actually collide while there bounding boxes do._
_This method was chosen as it hardly introduces any overhead with regards to load times and was deemed all right for the application._

****

### Navigating the viewing window

The camera is automatically centered on the first **Robot** to be loaded

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

_Note: The Robot Builder currently only supports the building and loading of single Robots._

You can create your own **Robots** using the file formats specified in the Appendix. Alternatively, you can use the **Robot builder**, accessed by clicking on the **'Build'** button on the initial GUI window.

A _CoreComponent_ will be pre-loaded into the **Robot** tree.
To add additional components:
- select a 'parent' component by clicking on it (at first this will only be the _CoreComponent_)
- select a component type from the **dropdown**
- give it a name in the **text box**
- click on the **'+'** button in the top left

A new dialog will then appear, requiring you to select a **source slot**, **destination slot**, and **orientation** for the component. 
Clicking on **'Submit'** will then add the component to the tree.

To render the **Robot**, simply click on the **'Submit'** button and the viewing window will appear. If you would like to save your custom **Robot** to a JSON file, make sure the **'Write to file'** box is checked to the right of the lower buttons (and name your custom **Robot** file using the text box to the right of that).

You can also load and edit a pre-existing **Robot** from a file by clicking on the **'Load'** button and selecting a **Robot JSON** file.

##### A note on orientation and slots

[RoboGen's](https://robogen.org/docs/guidelines-for-writing-a-robot-text-file/) system for orientation and slot naming is slightly confusing at first, so here's how it works:
- **slot numbers** for components are labelled as follows:
    - 0 - front (side closest to viewer)
    - 1 - back (side furthest from viewer)
    - 2 - right (side to right of viewer)
    - 3 - left (side to left of viewer)
```
 BRICK          HINGE
   1              1         Note that hinges only have
3 |B| 2          |H|        slots 0 and 1 available
   0              0
 viewer         viewer
```

- **orientation** refers to the roll of a component and is based on the orientation of the component it is connected to (its 'parent' component). Orientation is visually applied to hinges, but not to bricks.

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

### Panda Versioning

****

For this project, Panda3D version 1.10.11 was used. This is not currently the latest version but it is recommended for two reasons:
- To keep current Panda3D code from breaking with potential new additions
- To keep the BAM model files for each component compatible
    -  Panda can use 2 types of model files, .egg or .bam files. BAM files are optimised versions of EGG files and are faster to load. However, they are often version-specific.
    -  To update Panda3D one would have to use [YABEE](https://github.com/09th/YABEE) to export the Blender models to EGG files and then use [egg2bam](https://docs.panda3d.org/1.10/python/tools/model-export/converting-egg-to-bam) to convert those EGG files into BAM files if desired.









