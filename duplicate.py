import os
import maya.cmds as cmds
from functools import partial

from shutil import copyfile
from chrlx_pipe.paths import PathManager
import copyFiles
import chrlx_pipe.utils as utils

import chrlx_pipe.projectSetter as projSet
from chrlx_pipe.createDirectories import createAssDirs
import chrlx_pipe.chrlxFuncs as cFuncs
reload(cFuncs)


widgets = {}
newProjPathSelect = ""
currentProj = cFuncs.getCurrentProject()

def duplicateAssetUI(oldAss = None, *args):
    newPath = ""
    if oldAss:
        newPath = os.path.dirname(os.path.dirname(os.path.dirname(oldAss)))

    if cmds.window("dupeWin", exists=True):
        cmds.deleteUI("dupeWin")
    widgets["win"] = cmds.window("dupeWin", w=400, h=200, t="Duplicate Asset")
    widgets["mainCLO"] = cmds.columnLayout(w=400, h=200)

    cmds.text(l="Asset Path to Duplicate", al="center")
    widgets["oldTFBG"] = cmds.textFieldButtonGrp(l="Asset To Duplicate:", fileName=oldAss, buttonLabel="<<<", cal =[(1, "left"), (2,"left"), (3, "left")], cw=[(1, 125), (2, 235), (3,40)])
    # cmds.text(l="Select either existing asset path OR asset file (asset win will autopopulate)")
    widgets["nameTFG"] = cmds.textFieldGrp(l="New Asset Name:", cal=[(1, "left"), (2, "left")], cw=[(1, 125), (2, 200)])
    widgets["assTypeRBG"] = cmds.radioButtonGrp(l="Asset Type:", labelArray3 = ("Char", "Prop", "Set"), numberOfRadioButtons = 3, sl=1, cal = [(1, "left"), (2,"left"), (3, "left"), (4, "left")], cw=[(1, 70), (2, 50), (3,50), (4,50)])
    cmds.separator(h=5)
    cmds.text(l="Select duplicate's job folder")
    widgets["newTFBG"] = cmds.textFieldButtonGrp(l="New Asset Job Path:", tx=newPath, bl="<<<", cal =[(1, "left"), (2,"left"), (3, "left")], cw=[(1, 125), (2, 235), (3,40)], bc = partial(getPath, "newTFBG"))
    cmds.separator(h=20)
    widgets["dupeBut"] = cmds.button(l="Duplicate Asset", w=400, h=50, bgc=(.5, .8, .5), c=readWinDupe)

    cmds.window(widgets["win"], e=True,rtf=True, w=5, h=5)
    cmds.showWindow(widgets["win"])	

def getPath(pathField, *args):
    """gets the path that will fill the field group"""
    path = cmds.fileDialog2(fm=2, dir= currentProj)
    cmds.textFieldButtonGrp(widgets[pathField], e=True, fi=path[0])
    val = cmds.textFieldButtonGrp(widgets["oldTFBG"], q=True, tx=True)

    if (pathField == "oldTFBG") and (not cmds.textFieldButtonGrp(widgets["newTFBG"], q=True, tx=True)):
        if val:
            sel = cmds.radioButtonGrp(widgets["assTypeRBG"], q=True, sl=True)
            oldPath = PathManager(path[0])
            if sel == 1:
                newDest = cFuncs.fixPath(os.path.join(oldPath.charPath))
            if sel == 2:
                newDest = cFuncs.fixPath(os.path.join(oldPath.propPath))
            if sel == 3:
                newDest = cFuncs.fixPath(os.path.join(os.path.join(oldPath.assetPath, "sets")))						
            
            cmds.textFieldButtonGrp(widgets["newTFBG"], e=True, fi=newDest)

def readWinDupe(*args):
    """gets the info from the win and passes it to dupe execute"""
    oldAss = cmds.textFieldButtonGrp(widgets["oldTFBG"], q=True, tx=True)
    newAssBase = cmds.textFieldButtonGrp(widgets["newTFBG"], q=True, tx=True)

    if cmds.window("dupeWin", exists=True):
        newType = cmds.radioButtonGrp(widgets["assTypeRBG"], q=True, sl=True)
        if newType ==1 :
            newType = "characters"
        if newType == 2:
            newType = "props"
        if newType == 3:
            newType = "sets"
    name = cmds.textFieldGrp(widgets["nameTFG"], q=True, tx=True)

#---------------- get the start job, end job and the asset name	
# ---------------- check here for info that Paul's dupe needs
    newAss = cFuncs.fixPath(os.path.join(newAssBase, "3D_assets", newType, name))
    
    if oldAss and newAssBase and name:
        print "duplicate.readWinDupe: passing\noldAss: {0}\nnewAss: {1}\nnewType: {2}".format(oldAss, newAss, newType)
# ---------------- pass Pauls script the correct info here		
        duplicateExecute(cFuncs.fixPath(oldAss), newAss, newType)
    else:
        cmds.warning("You have to fill in all of the fields!")

def duplicateExecute(oldAss=None, newAss=None, newType=None, *args):
    """
    given an old asset name (full path, [. . ./3d/assets/TYPE/NAME]) and a new asset name 
    (...3d/assets/TYPE/NAME), newType is either [characters, props or sets]
    """
# oldAss: //Bluearc/GFX/jobs/charlex_testAreaB_T60174/3D_assets/characters/ipad2tablet
# newAss: //Bluearc/GFX/jobs/charlex_testAreaB_T60174/3D_assets/characters/test

    oldDir, oldName = os.path.split(oldAss)
    oldJob3D, oldType = os.path.split(oldDir)
    oldJob = os.path.dirname(oldJob3D)

    newDir, newName = os.path.split(newAss)
    newJob3D, newType = os.path.split(newDir)
    newJob = os.path.dirname(newJob3D)


    print "oldType: {0}\noldName: {1}\nnewType: {2}\nnewName: {3}\noldJob: {4}\nnewJob: {5}".format(oldType, oldName, newType, newName, oldJob, newJob)
    
    # for x in [oldName, oldType, oldJob, newName, newType, newJob]:
    # 	print x
    copyFiles.copy_assets([[oldType, oldName, newType, newName]], oldJob, newJob)

# 	return

# 	#create objs that we can get info from the utils function
# 	oldAss = cFuncs.fixPath(oldAss)
# 	newAssRaw = cFuncs.fixPath(newAss)
# 	#replace type with newType
# 	newAss = cFuncs.fixPath(os.path.join(os.path.join(os.path.dirname(os.path.dirname(newAssRaw)), newType), os.path.basename(newAss)))
# 	oldAssNew = cFuncs.fixPath(os.path.join(os.path.join(os.path.dirname(os.path.dirname(oldAss)), newType), os.path.basename(oldAss)))
# 	print "oldAssNew:", oldAssNew

# 	oldPath = PathManager(oldAss)
# 	newPath = PathManager(newAss)

# 	oldAssName = os.path.basename(oldAss)
# 	newAssName = os.path.basename(newAss)

# 	#create an asset structure for the new name
# 	createAssDirs(cFuncs.fixPath(newPath.assetPath), newType, newAssName)
    
# 	#geo latest ws - rename, replace references
# 	oldGeoWS = cFuncs.getLatestAssetWS(oldAssName, oldAss, "geo")
# 	newGeoWS = ""
# 	if oldGeoWS:
# 		newGeoWS = "{0}/geo/workshops/{1}".format(newAss, os.path.basename(oldGeoWS).replace(oldAssName.partition("_")[0], newAssName))
# 		print newGeoWS
# 		copyfile(oldGeoWS, newGeoWS)

# 	#geo master if exists - rename 
# 	oldGeoMst = cFuncs.getAssetMaster(oldAssName, oldAss, "geo")
# 	newGeoMst = ""
# 	if oldGeoMst:
# 		newGeoMst = "{0}/geo/{1}".format(newAss, os.path.basename(oldGeoMst).replace(oldAssName.partition("_")[0], newAssName))
# 		copyfile(oldGeoMst, newGeoMst)

# 	#rig latest ws if exists - rename, replace references
# 	oldRigWS = cFuncs.getLatestAssetWS(oldAssName, oldAss, "rig")
# 	newRigWS = ""
# 	if oldRigWS:
# 		newRigWS = "{0}/rig/workshops/{1}".format(newAss, os.path.basename(oldRigWS).replace(oldAssName.partition("_")[0], newAssName))
# 		copyfile(oldRigWS, newRigWS)
    
# 	#get rig master and copy
# 	oldRigMst = cFuncs.getAssetMaster(oldAssName, oldAss, "rig")
# 	newRigMst = ""
# 	if oldRigMst:
# 		newRigMst = "{0}/rig/{1}".format(newAss, os.path.basename(oldRigMst).replace(oldAssName.partition("_")[0], newAssName))
# 		copyfile(oldRigMst, newRigMst)

# ######## copy mtl and shader files. . . . 

# 	replaceFiles = []
# 	# copy contents of source images
# 	for fl in cFuncs.getFilesInPath(os.path.join(oldAss, "sourceImages")):
# 		if fl:
# 			copyfile(fl, "{0}/sourceImages/{1}".format(newAss, os.path.basename(fl).replace(oldAssName, newAssName)))

# ########## -- add mtl file to this . . .
# 	filesToSearch = [newRigWS]

# 	for doc in filesToSearch:
# 		cFuncs.replaceTextInFile(doc, oldGeoMst, newGeoMst)

    if cmds.window("dupeWin", exists=True):
        cmds.deleteUI("dupeWin")

# def projectSelect(*args):
# 	proj = cmds.fileDialog2(fm=2)


def duplicateAsset(oldAss, *args):
    """oldAss = the path the specific asset folder to be duplicated (ie. ...3d/assets/characters/CHARNAME)"""
    if oldAss:
        duplicateAssetUI(oldAss)
    else:
        cmds.warning("No asset selected to dupe!")