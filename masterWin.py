# mastering window class that will return the options needed

import maya.cmds as cmds

#callback dismiss function to get the values of the stuff inside
class masterAssetUI(object):
    def __init__(self, *args):
        self.dict = {}
        self.dialog = cmds.layoutDialog(ui=self.masterAssetWindow, t= "Mastering Options")

    def getValues(self):
        pass

    def dismissUI(self, *args):
        self.dict["note"] = cmds.scrollField(self.txt, q=True, tx=True)
        self.dict["cam"] = cmds.checkBoxGrp(self.cam, q=True, v1=True)
        self.dict["shd"] = cmds.checkBoxGrp(self.shd, q=True, v1=True)
        self.dict["rig"] = cmds.checkBoxGrp(self.rig, q=True, v1=True)
        self.dict["light"] = cmds.checkBoxGrp(self.light, q=True, v1=True)
        self.dict["freeze"] = cmds.checkBoxGrp(self.freeze, q=True, v1=True)
        cmds.layoutDialog(dismiss = "got it")

    def cancelUI(self, *args):
        self.dict["note"] = "__CANCEL__"
        self.dict["cam"] = cmds.checkBoxGrp(self.cam, q=True, v1=True)
        self.dict["shd"] = cmds.checkBoxGrp(self.shd, q=True, v1=True)
        self.dict["rig"] = cmds.checkBoxGrp(self.rig, q=True, v1=True)
        self.dict["light"] = cmds.checkBoxGrp(self.light, q=True, v1=True)
        self.dict["freeze"] = cmds.checkBoxGrp(self.freeze, q=True, v1=True)		
        cmds.layoutDialog(dismiss = "cancel")

    def masterAssetWindow(self):
        form = cmds.setParent(q=True)
        cmds.formLayout(form, e=True, w=310, h=270)
        t1 = cmds.text(l="Mastering Options:")
        
        self.cam = cmds.checkBoxGrp(l="Delete user cameras?", ncb = 1, cal=[(1, "left"), (2, "left")], cw = [(1, 200),(2, 100)], v1=True) #delete unused cameras?
        self.shd = cmds.checkBoxGrp(l="Delete unused shaders/textures?", ncb = 1, cal=[(1, "left"), (2, "left")], cw = [(1, 200),(2, 100)], v1=True) #delete unused shaders and textures
        self.rig = cmds.checkBoxGrp(l="Create initial rigs? (for first geo only)", ncb = 1, cal=[(1, "left"), (2, "left")], cw = [(1, 200),(2, 100)], v1=True) #create rig WS?
        self.light = cmds.checkBoxGrp(l="Delete lights?", ncb = 1, cal=[(1, "left"), (2, "left")], cw = [(1, 200),(2, 100)], v1=True) # delete any light in scene
        self.freeze = cmds.checkBoxGrp(l="Freeze Geometry", ncb = 1, cal=[(1, "left"), (2, "left")], cw = [(1, 200),(2, 100)], v1=False)

        t2 = cmds.text(l="Note:")
        self.txt = cmds.scrollField(h=40, tx = "note field", w=300, ww=True)
        #pum = cmds.popupMenu(b=3, p=widgets["noteSF"])
        #cmds.menuItem("yo", p=pum)
      
        self.but = cmds.button(l="Master Asset!", bgc = (.5, .7, .4), w=300, h=50, c= self.dismissUI)
        self.cancel = cmds.button(l="Cancel", bgc = (.7, .4, .4), w=300, h=30, c= self.cancelUI)

        cmds.formLayout(form, e=True,attachForm = [(t1, "top", 0), (t1, "left", 5), 
        (self.cam, "top", 25), (self.cam, "left", 5), 
        (self.shd, "top", 45), (self.shd, "left", 5),
        (self.rig, "top", 65), (self.rig, "left", 5),
        (self.freeze, "top", 85), (self.freeze, "left", 5),
        (self.light, "top", 105), (self.light, "left", 5),         	
        (t2, "top", 135), (t2, "left", 5), 
        (self.txt, "top", 150), (self.txt, "left", 5),
        (self.but, "top", 210), (self.but, "left", 5),
        (self.cancel, "top", 270), (self.cancel, "left", 5),
        ])
        
        cmds.formLayout(form, e=True, h=270)

class masterShotUI(masterAssetUI):
    def __init__(self, *args):
        self.dict = {}
        self.dialog = cmds.layoutDialog(ui=self.masterShotWindow, t= "Mastering Options" )

    def masterShotWindow(self):
        form = cmds.setParent(q=True)
        cmds.formLayout(form, e=True, w=300, h=200)
        t1 = cmds.text(l="Mastering Options:")
        
        self.cam = cmds.checkBoxGrp(l="Delete user cameras not named 'renderCam'?", ncb = 1, cal=[(1, "left"), (2, "left")], cw = [(1, 200),(2, 100)], v1=True)#delete unused cameras?
        self.shd = cmds.checkBoxGrp(l="Delete unused shaders/textures?", ncb = 1, cal=[(1, "left"), (2, "left")], cw = [(1, 200),(2, 100)], v1=True) #delete unused shaders and textures
        t2 = cmds.text(l="Note:")
        self.txt = cmds.scrollField(h=40, tx = "note field", w=300, ww=True)
        #pum = cmds.popupMenu(b=3, p=widgets["noteSF"])
        #cmds.menuItem("yo", p=pum)
      
        self.but = cmds.button(l="Master Shot!", bgc = (.5, .7, .4), w=300, h=50, c= self.dismissUI)
        self.cancel = cmds.button(l="Cancel", bgc = (.7, .4, .4), w=300, h=30, c= self.cancelUI)

        cmds.formLayout(form, e=True,attachForm = [(t1, "top", 0), (t1, "left", 5), 
        (self.cam, "top", 25), (self.cam, "left", 5), 
        (self.shd, "top", 45), (self.shd, "left", 5),
        #(self.rig, "top", 65), (self.rig, "left", 5),
        (t2, "top", 85), (t2, "left", 5), 
        (self.txt, "top", 105), (self.txt, "left", 5),
        (self.but, "top", 155), (self.but, "left", 5),
        (self.cancel, "top", 215), (self.cancel, "left", 5),
        ])
        
        cmds.formLayout(form, e=True, h=200)

    def dismissUI(self, *args):
        self.dict["note"] = cmds.scrollField(self.txt, q=True, tx=True)
        self.dict["cam"] = cmds.checkBoxGrp(self.cam, q=True, v1=True)
        self.dict["shd"] = cmds.checkBoxGrp(self.shd, q=True, v1=True)
        # self.dict["rig"] = cmds.checkBoxGrp(self.rig, q=True, v1=True)
        cmds.layoutDialog(dismiss = "got it")

    def cancelUI(self, *args):
        self.dict["note"] = "__CANCEL__"
        self.dict["cam"] = cmds.checkBoxGrp(self.cam, q=True, v1=True)
        self.dict["shd"] = cmds.checkBoxGrp(self.shd, q=True, v1=True)
        # self.dict["rig"] = cmds.checkBoxGrp(self.rig, q=True, v1=True)
        # self.dict["freeze"] = cmds.checkBoxGrp(self.freeze, q=True, v1=True)		
        cmds.layoutDialog(dismiss = "cancel")		