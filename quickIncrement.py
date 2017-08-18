###########
# quick increment - just a little window to increment when you're in a workshop file
###########

import os
import maya.cmds as cmds
import chrlx_pipe.paths as paths
import chrlx_pipe.chrlxFuncs as cFuncs

widgets = {}

def quickInrementUI(*args):
    """win for quick increment"""
    if cmds.window("qiwin", exists=True):
        cmds.deleteUI("qiwin")

    widgets["win"] = cmds.window("qiwin", t="Increment WS", w=200, h=75, s=False)

    widgets["mainCLO"] = cmds.columnLayout()
    widgets["incrBut"] = cmds.button(l="Increment Current WS!", bgc = (.9, .5, .5), w=200, h=75, c=increment)

    cmds.window(widgets["win"], e=True, w=200, h=75)
    cmds.showWindow(widgets["win"])


def increment(*args):
    #get current scene
    curr = cFuncs.fixPath(cmds.file(q=True, sn=True))
    print curr
    pm = ""
    #check that we're in schema 2
    if curr:
        try:
            pm = paths.PathManager(curr)
        except:
            warning("Can't get file name or find the project path")

        if pm: #check that we're in a ws file in correct proj type
            if isinstance(pm, paths.AssetPath): # if asset
                asset = pm.name
                assetFolder = cFuncs.fixPath(os.path.join(pm.assetPath, pm.typ, asset))
                fType = pm.stage
                incrementFile = cFuncs.incrementWS(asset, assetFolder, fType)
                wsNum = "{0:0>3}".format(pm.version+1)
                cmds.file(rename = incrementFile + ".ma")
                cFuncs.putFileInfo(fType, wsNum, "quick increment")
                cmds.file(save=True, type="mayaAscii")

            elif isinstance(pm, paths.ShotPath): # if shot
                variant = pm.variant
                fType = pm.shotType
                varFolder = cFuncs.fixPath(os.path.join(pm.shotPath, fType, variant))
                print "quick increment:\nvariant: {0}\nvarFolder: {1}\nfType: {2}".format(variant, varFolder, fType)
                incrementFile = cFuncs.incrementWS(variant, varFolder, fType)
                wsNum = "{0:0>3}".format(pm.version+1)
                cmds.file(rename = incrementFile + ".ma")
                cFuncs.putFileInfo(fType, wsNum, "quick increment")
                cmds.file(save=True, type="mayaAscii")			

            else:
                cmds.warning("quickIncrement.increment: I'm not able to recognize the shot you've passed me")

            if cmds.window("assetWin", exists=True):
                import chrlx_pipe.assetWin as assWin
                assWin.populateWindow()

            if cmds.window("shotWin", exists = True):
                import chrlx_pipe.shotWin as shotWin
                shotWin.populateWindow()

        else:
            cmds.warning("You're not in a file I can increment (either wrong project schema or not in a workshop)")
    else:
        cmds.warning("You seem to be in an unsaved scene! No workshop to increment!")

def quickIncrement(*args):
    quickInrementUI()
