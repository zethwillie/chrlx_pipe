# createDirectories.py
import maya.cmds as cmds

import os, sys
from functools import partial
import chrlx_pipe.chrlxFuncs as cFuncs
reload(cFuncs)
import chrlx_pipe.utils as utils
#---------------- restore this and then the one in the body. . . 
# import chrlx_pipe.jobDirectoryCreator as jobDirectoryCreator

###########
# this module is used to create directories for new shots, assets, variants, etc
############

awidgets = {} #dict for asset win
swidgets = {} #dict for shot win
vwidgets = {} #dict for variant win

############################
# create asset directories
############################

def createAssetUI(assFolder, *args):

    if cmds.window("createAssWin", exists = True):
        cmds.deleteUI("createAssWin")

    awidgets["createAssWin"] = cmds.window("createAssWin", t="Create New Asset", s=False)
    awidgets["mainCLO"] = cmds.columnLayout()

    awidgets["mainFLO"] = cmds.formLayout(w = 300, h=120, bgc = (.3,.3,.3))

    awidgets["name"] = cmds.textFieldGrp(l="Asset Name: ", w=300, cw = [(1, 70), (2,220)], cal = [(1,"left"), (2, "left")])
    awidgets["type"] = cmds.radioButtonGrp(l="Type: ", labelArray3 = ("Char", "Prop", "Set"), numberOfRadioButtons = 3, sl=1, cal = [(1, "left"), (2,"left"), (3, "left"), (4, "left")], cw=[(1, 70), (2, 50), (3,50), (4,50)])
    awidgets["createBut"] = cmds.button(l="Create Asset!", w=300, h=50, bgc = (.5, .8, .5), c=partial(createWinAssetDirs, assFolder))

    cmds.formLayout(awidgets["mainFLO"], e=True, af = [
        (awidgets["name"], "left", 0), 
        (awidgets["name"], "top", 10),
        (awidgets["type"], "left", 0), 
        (awidgets["type"], "top", 40),
        (awidgets["createBut"], "left", 0), 
        (awidgets["createBut"], "top", 70)])

    cmds.window(awidgets["createAssWin"], e=True, w=300, h=120)
    cmds.showWindow(awidgets["createAssWin"])

def createWinAssetDirs(assFolder, *args):
    """assFolder is the "asset" folder. [...JOB/3D_assets/]"""

    name = cmds.textFieldGrp(awidgets["name"], q=True, tx=True)
    types = cmds.radioButtonGrp(awidgets["type"], q=True, sl=True)

    #here we compare that list of assets with our proposed name
    assets = cFuncs.getSpotAssetList(assFolder)
    if name in assets:
        cmds.confirmDialog(t="Name Exists!", m = "There is already an asset of this name\nin this project! Please enter another.")
        return()

    if types == 1:
        assType = "characters"
    elif types == 2:
        assType = "props"
    elif types == 3:
        assType = "sets"

    createAssDirs(assFolder, assType, name)
    
def createAssDirs(assetFolder, assType, name, *args):
    """creates asset directories from args
        -asset folder is path to asset folder [...JOB/3D_assets/]
        -assType is either "characters", "props", or "sets"
        -name is string name of the new character
    """

    cFuncs.createAssetDirectories(assetFolder, assType, name)

    if cmds.window("createAssWin", exists = True):
            cmds.deleteUI("createAssWin")

    # refresh teh asset win
    if cmds.window("assetWin", exists=True):
        #pth = utils.PathManager(assetFolder)
        import chrlx_pipe.assetWin as assWin
        assWin.populateAssets(assetFolder)

############################
# create shot directories
############################
def createShotUI(shotFolder, *args):
    if cmds.window("createShotWin", exists = True):
        cmds.deleteUI("createShotWin")

    swidgets["createShotWin"] = cmds.window("createShotWin", t="Create New Shot", s=False, rtf=True)
    swidgets["mainCLO"] = cmds.columnLayout()

    swidgets["mainFLO"] = cmds.formLayout(w = 300, h=120, bgc = (.3,.3,.3))


    #swidgets["shotName"] = cmds.textFieldGrp(l="Shot Name ", w=200, cw = [(1, 90), (2,110)], cal = [(1,"left"), (2, "left")], tx = "")
    swidgets["version"] = cmds.radioButtonGrp(l="Type of Shot: ", nrb=2, l1="Shot", l2="Previs", sl=1, cal=[(1, "left"),(2, "left"), (3,"left")], cw=[(1,110), (2,50),(3,50)])
    swidgets["num"] = cmds.textFieldGrp(l="Shot Number: ", cw = [(1, 110), (2,40)], cal = [(1,"left"), (2, "left")], tx = "000")
    swidgets["variant"] = cmds.textFieldGrp(l="Initial Anm Var Name:", cw = [(1, 110), (2,100)],  cal = [(1,"left"), (2, "left")], tx = "baseVariant")
    swidgets["createBut"] = cmds.button(l="Create Shot!", w=300, h=50, bgc = (.5, .8, .5), c=partial(createWinShotDirs, shotFolder))

    cmds.formLayout(swidgets["mainFLO"], e=True, af = [
        (swidgets["version"], "left", 0), 
        (swidgets["version"], "top", 0),
        (swidgets["num"], "left", 0), 
        (swidgets["num"], "top", 25),
        (swidgets["variant"], "left", 0), 
        (swidgets["variant"], "top", 50),
        (swidgets["createBut"], "left", 0), 
        (swidgets["createBut"], "top", 75),
        ])

    cmds.window(swidgets["createShotWin"], e=True, w=5, h=5)
    cmds.showWindow(swidgets["createShotWin"])

def createWinShotDirs(shotFolder, *args):
    """
    from the window, will create a shot folder structure 
    Args:
        shotFolder (string): the generic "shots" folder under the job [...SPOT/3d/shots]
    Return:
        None
    """

    num = cmds.textFieldGrp(swidgets["num"], q=True, tx=True)
    myChars = [int(s) for s in num if s.isdigit()] # get list of int digits in num

    if len(myChars) !=3 : # if we don't have 3 digits. . .
        cmds.warning("You need to enter a 3 digit number for the shot!!")
        return() 

    shotType = cmds.radioButtonGrp(swidgets["version"], q=True, sl=True)
    if shotType == 1:
        sname = "shot"
    if shotType == 2:
        sname = "previs"

    name = "{0}{1}".format(sname, num)

    #here we compare that list of assets with our proposed name
    shots = cFuncs.getSpotShotList(shotFolder)
    if name in shots:
        cmds.confirmDialog(t="Name Exists!", m = "There is already a shot of this name\nin this project! Please enter another.")
        return()
    
    shotFolderObj=utils.PathManager(shotFolder)
#---------------- restore this!!     
    # jobDirectoryCreator.createShot(shotFolderObj.jobDirname, shotFolderObj.spotDirname, name)

    varName = cmds.textFieldGrp(swidgets["variant"], q=True, tx=True)

    thisShotFolder = cFuncs.fixPath(os.path.join(shotFolder, name))
    createVariantDirs(thisShotFolder, "anm", varName, *args)

    if cmds.window("createShotWin", exists = True):
            cmds.deleteUI("createShotWin")

    # refresh the shot win
    if cmds.window("shotWin", exists=True):
        #pth = utils.PathManager(shotFolder)
        import chrlx_pipe.shotWin as shotWin
        shotWin.populateWindow()

    
def createShotDirs(shotFolder, shotName, *args):
    """creates shot directories from args
        -shot folder is path to the shots folder [../JOB/SPOT/3D/shots/]
        -name is string name of the new shot
    """
    cFuncs.createShotDirectories(shotFolder, shotName)

#########################
# create variant
#########################

def createVariantUI(shotFolder, varType, *args):
    if cmds.window("createVarWin", exists = True):
        cmds.deleteUI("createVarWin")

    vwidgets["createVarWin"] = cmds.window("createVarWin", t="Create New {0} Variant".format(varType), s=False)
    vwidgets["mainCLO"] = cmds.columnLayout()
    vwidgets["mainFLO"] = cmds.formLayout(w = 300, h=120, bgc = (.3,.3,.3))

    vwidgets["varText"] = cmds.text(l="Enter your variant identifier (ideally one word)")
    vwidgets["name"] = cmds.textFieldGrp(l="Variant Name: ", w=300, cw = [(1, 70), (2,220)], cal = [(1,"left"), (2, "left")])
    vwidgets["createBut"] = cmds.button(l="Create Variant!", w=300, h=50, bgc = (.5, .8, .5), c=partial(createWinVarDirs, shotFolder, varType))

    cmds.formLayout(vwidgets["mainFLO"], e=True, af = [
        (vwidgets["varText"], "left", 0), 
        (vwidgets["varText"], "top", 10),
        (vwidgets["name"], "left", 0), 
        (vwidgets["name"], "top", 30),
        (vwidgets["createBut"], "left", 0), 
        (vwidgets["createBut"], "top", 60)])

    cmds.window(vwidgets["createVarWin"], e=True, w=300, h=120)
    cmds.showWindow(vwidgets["createVarWin"])

def createWinVarDirs(shotFolder, varType, *args):
    """folder is the shot folder (shot folder). Proj is project folder"""

    name = cmds.textFieldGrp(vwidgets["name"], q=True, tx=True)

    varFold = cFuncs.fixPath(os.path.join(shotFolder, varType))
    variants = cFuncs.getShotVariantList(varFold)

    if variants and (name in variants):
        cmds.confirmDialog(t="Name Exists!", m = "There is already a shot of this name\nin this spot! Please enter another.")
        return()

    createVariantDirs(shotFolder, varType, name)
    if cmds.window("createVarWin", exists=True):
        cmds.delete("createVarWin")

    # refresh the shot win
    if cmds.window("shotWin", exists=True):
        #pth = utils.PathManager(shotFolder)
        import chrlx_pipe.shotWin as shotWin
        shotWin.populateWindow()    

def createVariantDirs(shotFolder, varType, name, *args):
    """creates variant directories from args
        -asset folder is path to asset folder under 3D
        -assType is either "characters", "props", or "sets"
        -name is string name of the new character
    """
    #do this again (like above) just to make sure we don't repeat a name if we're calling externally
    cFuncs.createVariantDirectories(shotFolder, varType, name)
    cmds.warning("Created variant: {0} in {1}".format(name, cFuncs.fixPath(os.path.join(shotFolder, varType))))
    if cmds.window("createVarWin", exists=True):
        cmds.deleteUI("createVarWin")

    #refresh the shot win
    if cmds.window("shotWin", exists=True):
        #pth = utils.PathManager(shotFolder)
        import chrlx_pipe.shotWin as shotWin
        shotWin.populateWindow()

##################
# calls to run UI's
##################

def createAsset(assFolder, *args):
    """assFolder - is the asset path [. . . JOB/3D_assets/TYPE/]"""
    createAssetUI(assFolder)

def createShot(shotFolder, *args):
    """shot folder is the "shots" path [. . . SPOT/3d/shots]"""
    createShotUI(shotFolder)

def createVariant(shotFolder, shotType, *args):
    """
        - shotFolder is the folder of the "shot" we're creating the var in [...3d/shots/SHOT]
        -varType is the type of file we're creating: "anm", "lgt", "fx"
    """
    createVariantUI(shotFolder, shotType)