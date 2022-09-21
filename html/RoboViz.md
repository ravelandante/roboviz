Module RoboViz
==============

Functions
---------

    
`formatCollisions(collisions)`
:   Formats List of collisions into displayable format
    Args:
        `collisions`: possible collisions between robots (int[][])
    Returns:
        `collision_text`: text format of robot collisions (String)

    
`formatOutOfBounds(out_of_bounds)`
:   Formats List of out of bounds robots into displayable format
    Args:
        `out_of_bounds`: robots that are out of bounds + units ([int, LVector3f])
    Returns:
        `out_of_bounds_text`: text format of out of bounds robots (String)

Classes
-------

`Brick(id, type, root, orientation)`
:   Represents a CoreComponent or FixedBrick component
    
    Constructor
    Args:
        `id`: ID of Brick (String)  
        `type`: type of brick component (String)  
        `root`: whether this brick is the core of the robot or not (boolean)  
        `orientation`: orientation (roll) of this component relative to its parent (int)

    ### Ancestors (in MRO)

    * RoboViz.RobotComp

`Connection(src, dst, src_slot, dst_slot)`
:   Represents a connection between 2 robot components
    
    Constructor
    Args:
        `src`: source ('parent') component (RobotComp)  
        `dst`: destination ('child') component (RobotComp)  
        `src_slot`: side of source component to attach dest. to (int)  
        `dst_slot`: side of dset. component to attach source to (int)

    ### Methods

    `standardiseSlots(self)`
    :   Converts RoboGen's funky slot system to a more reasonable one (sides numbered clockwise 0->3 starting from side closest to viewer)

`Environment(x_length, y_length, swarm_size)`
:   Renders environment terrain and robot components
    
    Constructor   
    Args:  
        `x_length`: the x size of the environment plane (int)  
        `y_length`: the y size of the environment plane (int)  
        `swarm_size`: the number of Robots in the swarm (int)

    ### Ancestors (in MRO)

    * direct.showbase.ShowBase.ShowBase
    * direct.showbase.DirectObject.DirectObject

    ### Methods

    `displayLabel(self, pos, text, parent)`
    :   Displays a text label in the scene
        Args:
            `pos`: position of label (LVector3f)  
            `text`: text of label (String)  
            `parent`: parent of label (NodePath)

    `enlargeLabel(self, pickedObj)`
    :   Enlarges component label when component is selected
        Args:
            `pickedObj`: newly selected component (PandaNode)

    `initialView(self)`
    :   Moves and zooms camera so that all robots are initially placed in the camera's view

    `moveCamera(self, pos, z_dist)`
    :   Moves camera to point above pos in scene (looking down)
        Args:
            `pos`: position of camera (LVector3f)  
            `z_dist`: distance above pos that camera is placed at (int)

    `moveRobot(self, direction)`
    :   Moves selected robot in the given direction for the given units relative to the camera view
        Args:
            `direction`: direction of robot movement (0:forward, 1:back, 2:left, 3:right, 4:up, 5:down) (int)  
            `units`: number of units to move robot by (int)

    `renderRobot(self, robot)`
    :   Renders 1 robot in the scene by iterating through its Connections
        Args:
            `robot`: robot object to render (Robot)

    `select(self)`
    :   Determines which robot is selected (by mouse click), updates self.selected_robot to represent this

    `switchFocus(self)`
    :   Switches camera focus (origin) between robots in scene

    `toggleBounding(self)`
    :   Toggles visibility of robot bounding box (selection box)

    `toggleLabels(self, first=False)`
    :   Toggles visibility of component labels
        Args:
            `first`: first display of labels or not (Boolean) **optional**

`Hinge(id, type, root, orientation)`
:   Represents an ActiveHinge or PassiveHinge component
    
    Constructor
    Args:
        `id`: ID of Brick (String)  
        `type`: type of brick component (String)  
        `root`: whether this brick is the core of the robot or not (boolean)  
        `orientation`: orientation (roll) of this component relative to its parent (int)

    ### Ancestors (in MRO)

    * RoboViz.RobotComp

`Robot(id, connections, core_pos)`
:   Represents a robot and its connections
    
    Constructor
    Args:
        `id`: ID of robot (int)  
        `connections`: connections between components that make up the robot (Connection[])  
        `core_pos`: positions of the core component of the robot (int[])

    ### Methods

    `drawBounds(self)`
    :   Draws LineSegs between all points of the robot bounding box

    `outOfBoundsDetect(self, x_length, y_length)`
    :   Determines if robot exceeds the dimensions of the environment
        Args:
            `x_length`: x length of the environment (int)  
            `y_length`: y length of the environment (int)
        Returns:
            `out_of_bounds`: x and y values of how far the robot is out of bounds (LVector3f), returns `'none'` if not out of bounds

    `setBounds(self)`
    :   Calculates and sets the bounds (bounding box) of the robot

`RobotComp(id, type, root, orientation)`
:   Represents a component of a robot
    
    Constructor
    Args:
        `id`: ID of Brick (String)  
        `type`: type of brick component (String)  
        `root`: whether this brick is the core of the robot or not (boolean)  
        `orientation`: orientation (roll) of this component relative to its parent (int)

    ### Descendants

    * RoboViz.Brick
    * RoboViz.Hinge

    ### Methods

    `calcPos(self, src, dst, connection)`
    :   Calculates the position that the component should be placed at in the scene based on the source's position
        Args:
            `src`: source Panda3D node in connection (PandaNode)  
            `dst`: destination Panda3D node in connection (PandaNode)  
            `connection`: the Connection in question (Connection)
        Returns:
            `(dst_pos, heading)`: position and heading that component should be placed at in the scene (LVector3f, int)

`RobotGUI(config_path='', pos_path='', robot_path='')`
:   Initialises the GUI for inputting files, building robots and reporting errors
    
    Constructor
    Args:
        `config_path`: file path of configuration text file (String) **optional**, only used when building a robot  
        `pos_path`: file path of robot positions text file (String) **optional**, only used when building a robot  
        `robot_path`: file path of robot JSON file (String) **optional**, only used when building a robot

    ### Methods

    `build_window(self)`
    :   Displays the Robot building window

    `connection_window(self)`
    :   Displays the component connection window for specifying specific connection parameters
        Returns:
            `(src_slot, dst_slot, orientation)`: source, dest slots + orientation of component ((int, int, int)) (returns (-1, -1, -1) if window closed)

    `error_window(self)`
    :   Displays the error reporting window

    `runSim(self, config=0, robots=0, file=True)`
    :   Creates the Environment and runs the simulation
        Args:
            `config`: configuration parameters (int[]) **optional**, only used when building a robot  
            `robots`: array of Robots (Robot[]) **optional**, only used when building a robot

    `startGUI(self)`
    :   Displays the file input GUI window

`RobotUtils(config_path, pos_path, robot_path)`
:   Constructor
    Args:
        `config_path`: file path of configuration text file (String)  
        `pos_path`: file path of robot positions text file (String)  
        `robot_path`: file path of robot JSON file (String)

    ### Methods

    `collisionDetect(self, robots)`
    :   Determines if there are any possible collisions between robots in the scene
            Args:
                `robots`: list of all robots in the scene (Robot[])
            Returns
                `collisions`: possible collisions between robots (int[][])

    `configParse(self)`
    :   Parses environment and swarm size from configuration file
        Returns:
            `configuration`: environment and swarm size (int[])

    `createBrain(self, neurons, brain, compArr)`
    :   Creates list of neurons based on JSON file ANN inputs
        Args:
            `neurons`: list of neurons and their info from JSON file (Neurons[])  
            `brain`: list of connections between neurons from JSON file (List)  
            `compArr`: list of components that neurons are connected to (RobotComp[])

    `posParse(self)`
    :   Parses robot positions from positions file
        Returns:
            `positions`: positions of Robots in scene (int[])

    `robotParse(self, swarm_size, positions)`
    :   Parses robot(s) from robot JSON file
        Returns:
            `robotArr`: all robots to be rendered in the scene (Robot[])

    `writeRobot(self, robot, name)`
    :   Writes built Robot out to relevant files
        Args:
            `robot`: Robot to be written out (Robot)  
            `name`: name of Robot JSON file (String)