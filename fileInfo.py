import maya.cmds as cmds
import os
import chrlx_pipe.chrlxFuncs as cFuncs

###########
# getInfoDict(path) will return a dictionary of the scene's info 
# fileInfo(path) will call the funcs to show the window with all scene fileInfo
############

#info window on selected scene
widgets = {}

def fileInfoUI(filePath, *args):
    if cmds.window("fileInfoWin", exists=True):
        cmds.deleteUI("fileInfoWin")

    widgets["win"] = cmds.window("fileInfoWin", w=270, h=300, t="Charlex File Info", s=False)
    widgets["mainSLO"] = cmds.scrollLayout(w=450, h=300)
    widgets["mainCLO"] = cmds.columnLayout()

    cmds.window(widgets["win"], e=True, w=270, h=300)
    cmds.showWindow(widgets["win"])
    
    #populate the window here
    populateInfoWin(filePath, widgets["mainCLO"])

def populateInfoWin(filePath, parent, *args):
    """grabs only the relevant info from the file and creates text for the window"""

    cmds.text(l=os.path.basename(filePath), font = "boldLabelFont", align = "left")
    cmds.text(l="================================", align = "left", h=20)

    goodInfo = ['"FILETYPE"', '"DATE"', '"WORKSHOP"', '"USER"', '"CHRLX_NOTE"', '"version"', '"FPS"', '"FRAMERANGE"', '"RESOLUTION"']
    infoDict = cFuncs.getInfoDict(filePath)
    if infoDict:
        for key in infoDict.keys():
            if key in goodInfo:
                cmds.text(l=key.replace("\"",""), parent= parent, align="left", ww=True, font="boldLabelFont")
                cmds.text(l= infoDict[key], parent = parent, align = "left", ww=True)


def fileInfo(filePath):
    """calls the window, then populates it"""
    
    fileInfoUI(filePath)


# fileinfo keys in current scene:
# "FILETYPE" : "geo";
# "cutIdentifier" : "201511301000-979500";
# "product" : "Maya 2016";
# "NOTE" : "dinoBodyB and eyeblink shapes added";
# "USER" : "ekim";
# "osv" : "Microsoft Windows 7 Business Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
# "CHRLX_NOTE" : "dinoBodyB and eyeblink shapes added";
# "version" : "2016";
# "application" : "maya";
# "DATE" : "11:59:22 2016/05/10";
# "WORKSHOP" : "66";