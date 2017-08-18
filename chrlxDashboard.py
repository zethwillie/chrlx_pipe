## charlex dashboard

import maya.cmds as cmds

import chrlx_pipe.assetWin as ass
reload(ass)
import chrlx_pipe.shotWin as sht
reload(sht)
import chrlx_pipe.projectSetter as prj
reload(prj)

class Dashboard(object):
    def __init__(self):
        """make ui for dashboard"""
        width = 150
        height = 130
        if cmds.window("dashWin",exists = True):
            cmds.deleteUI("dashWin")
        self.win = cmds.window("dashWin", t="CHRLX_DASH", w=width, h=height, mxb=False, mnb=False, s=False, rtf=True)
        self.clo = cmds.columnLayout(w=width, h=height)
        self.assetBut = cmds.button(l="Asset Window", w=width, h=30, bgc = (.8, .6, .4), c=self.assetWin)
        cmds.separator(h=3)
        self.shotBut = cmds.button(l="Shot Window", w=width, h=30, bgc = (.5, .8, .5), c=self.shotWin)
        cmds.separator(h=3)
        self.prjBut = cmds.button(l="Project Setter", w=width, h=30, bgc = (.5, .6, .8), c=self.projectSetter)
        #cmds.separator(h=3)
        #self.blnk2But = cmds.button(l="-blank-", w=width, h=30, bgc = (.5, .5, .5))
        
        cmds.window(self.win, e=True, w=5, h=5)
        cmds.showWindow(self.win)

    # launch commands
    def assetWin(self, *args):
        """opens the asset window"""
        reload(ass)
        ass.assetWin()

    def shotWin(self, *args):
        """opens the shot window"""
        reload(sht)
        sht.shotWin()

    def projectSetter(self, *args):
        """opens the project setter window"""
        reload(prj)
        projectSet = prj.ProjectSetter(True)