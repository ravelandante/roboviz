from direct.showbase.ShowBase import ShowBase


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.core = self.loader.loadModel("./models/BAM/Core_FDM.bam")              # load static model of core component
        self.hinge = self.loader.loadModel("./models/BAM/ActiveHinge_Frame.bam")    # load static model of active hinge
        # self.hinge.setScale(0.005, 0.005, 0.005)                                  # make hinge smol
        self.hinge.setPos(20.5, 0, -5)                                              # change position of hinge to fit to core

        self.core.reparentTo(self.render)                           # make the render node the parent of our core
        self.hinge.reparentTo(self.core)                            # make the core node/component the parent of our frame


app = MyApp()
app.run()
