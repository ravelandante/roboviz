from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight


class Environment(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.set_background_color(0.6, 0.6, 0.6, 1)                     # set background colour to a lighter grey

        # this is where the read config file code would be (maybe even in a separate method)
        self.x_length = 1000
        self.y_length = 1000
        self.swarm_size = 1

        self.plane = self.loader.loadModel('./models/BAM/plane.bam')    # load 'terrain' plane
        self.plane.setScale(1, self.x_length, self.y_length)            # scale up to specified dimensions
        self.plane.reparentTo(self.render)

        #self.comp = self.loader.loadModel('./models/BAM/Core_FDM.bam')
        # self.comp.reparentTo(self.render)

        alight = AmbientLight('alight')                                 # create ambient light
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        # self.useDrive()                                 # enable use of arrow keys

    def traverseTree(self, robot):
        pass
        # for connection in robot.connections:
        # src_path = "./models/BAM/" + connection.src.id
        # self.src = self.loader.loadModel(src_path)
        # if connection.src.root:
        # connection.src.pos = robot.corePos

        # self.src.setPos(connection.src.pos)
        # self.src.reparentTo(self.render)

        # dst_path = "./models/BAM/" + connection.dst.id
        # self.dst = self.loader.loadModel(dst_path)
        # connection.dst.pos = new pos calculated from connection.src.pos
        # self.dst.setPos(connection.dst.pos)
        # self.dst.reparentTo(self.src)
