from robotComp import RobotComp


class Brick(RobotComp):
    def __init__(self, id, type, root, orientation):
        super().__init__(id, type, root, orientation)
        self.colour = (1, 0, 0, 1)
