import maya.cmds as cmds
import chrlx_pipe.chrlxFuncs as funcs
reload(funcs)
import maya.mel as mel
import os
from functools import partial

######## get proper env var for root of jobs folder(line 9)

class ProjectSetter(object):

    def __init__(self, doSet = True, *args):
        """ only arg to the class is: doSet(bool) to tell whether to actually set the project or just collect the info
            attribute to get project setting is VARIABLE.projectPath
        """


        self.widgets = {}

        self.jobsFolder = os.environ["CHRLX_JOBS"]
        self.exclude = [".DS_Store", ".TemporaryItems", ".directory", "Bluearc", "RESTORE", "Thumbs.db", "MAYA_CHOOSER"]
        self.set = doSet
        
        #THIS IS ATTR FOR FINAL PROJECT SETTING
        self.projectPath = ""

        if cmds.window("psWin", exists = True):
            cmds.deleteUI("psWin")

        self.widgets["mainWin"] = cmds.window("psWin", w=400, h=300, t="Set Project Window", s=True)
        #row layout for two scroll lists
        self.widgets["mainFLO"] = cmds.formLayout()
        self.widgets["jobTSL"] = cmds.textScrollList(w=250, h=200, sc=self.getSpots)
        self.widgets["spotTSL"] = cmds.textScrollList(w=250, h=200)
        self.widgets["setBut"] = cmds.button(l="Set Project", w=300, h=30, en=False, bgc = (.3, .3,.3), c=self.setProject)

        cmds.formLayout(self.widgets["mainFLO"], e=True, af = [
            (self.widgets["jobTSL"], "top", 0), 
            (self.widgets["jobTSL"], "left", 0), 
            (self.widgets["jobTSL"], "bottom", 50)])
        cmds.formLayout(self.widgets["mainFLO"], e=True, af = [
            (self.widgets["spotTSL"], "top", 0),
            (self.widgets["spotTSL"], "right", 0), 
            (self.widgets["spotTSL"], "bottom", 50)])
        cmds.formLayout(self.widgets["mainFLO"], e=True, af = [
            (self.widgets["setBut"], "bottom", 0), 
            (self.widgets["setBut"], "left", 0), 
            (self.widgets["setBut"], "bottom", 0), 
            (self.widgets["setBut"], "right", 0)])

        cmds.formLayout(self.widgets["mainFLO"], e=True, ac = [
            (self.widgets["jobTSL"], "right", 10, self.widgets["spotTSL"])
            ])
        cmds.window(self.widgets["mainWin"], e=True, w=400, h=300)
        cmds.showWindow(self.widgets["mainWin"])

        self.populateJobs()

    def populateJobs(self, *args):
        #get location of jobs folder
        dirs = os.listdir(self.jobsFolder)
        dirlist = []
        for dir in dirs:
            if (dir not in self.exclude) and (dir[0] != ".") and (dir[0] != "_"):
                dirlist.append(dir)	
        dirlist.sort()
        for dir in dirlist:
            cmds.textScrollList(self.widgets["jobTSL"], e=True, a=dir)

    def getSpots(self, *args):
        #clear spots list
        cmds.textScrollList(self.widgets["spotTSL"], e=True, ra=True)
        cmds.button(self.widgets["setBut"], e=True, en=False, bgc = (.3, .3, .3))
        #get spots for selected job
        sel = cmds.textScrollList(self.widgets["jobTSL"], q=True, si=True)[0]
        newDir = os.path.join(self.jobsFolder, sel)
        spots = os.listdir(newDir)
        spotlist = []
        for spot in spots:
            #create list of null folders and below say if not in list:
            if spot != "calendar" and (spot[0] != ".") and (spot[0] != "_") and spot != "3D_assets":
                spotlist.append(spot)
        spotlist.sort()
        for spot in spotlist:
                cmds.textScrollList(self.widgets["spotTSL"], e=True, a=spot, sc = self.enableButton)

    def enableButton(self, *args):
        cmds.button(self.widgets["setBut"], e=True, en=True, bgc = (.9, .6, .4))

    def setProject(self, *args):
        #set project to proper folder!!! project is 3D folder!!!
        self.job = cmds.textScrollList(self.widgets["jobTSL"], q=True, si=True)[0]
        self.spot = cmds.textScrollList(self.widgets["spotTSL"], q=True, si=True)[0]

        if self.job and self.spot:

            path = os.path.join(self.jobsFolder, self.job, self.spot, "3d")
            self.cleanPath = funcs.fixPath(path)

            # - FINAL OUTPUT ATTRIBUTE
            self.projectPath = self.cleanPath

            #sets project if arg is True
            if os.path.isdir(self.cleanPath) and self.set:
                funcs.setProject(self.cleanPath)
                cmds.deleteUI("psWin")

            elif os.path.isdir(self.cleanPath) and not self.set:
                cmds.warning("The project you've selected is:\n", self.projectPath)
                cmds.deleteUI("psWin")

            else:
                cmds.warning("I can't find the directory you've listed")

            #reset fileWin or do output thingy based on passed in info

            if cmds.window("assetWin", exists=True):
                import chrlx_pipe.assetWin as fileWin
                fileWin.populateWindow()

            if cmds.window("shotWin", exists=True):
                import chrlx_pipe.shotWin as fileWin
                fileWin.populateWindow()

        else:
            cmds.warning("You need to select a job and a spot first!")
