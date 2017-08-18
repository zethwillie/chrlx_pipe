#to use: call shotWin.shotWin()

#chrlxShotWin
import maya.cmds as cmds
import maya.mel as mel

import os
import sys
from functools import partial
import datetime
import time
import itertools
import json

import chrlx_pipe.paths as paths
import chrlx_pipe.chrlxFuncs as cFuncs
reload(cFuncs)
import chrlx_pipe.projectSetter as projectSetter
reload(projectSetter)
import chrlx_pipe.masterFuncs as cMaster
reload(cMaster)
import chrlx_pipe.createDirectories as createDir
reload(createDir)
import chrlx_pipe.unarchiveAssets as unarch
reload(unarch)
import chrlx_pipe.fileInfo as fileInfo
reload(fileInfo)
import chrlx_pipe.duplicate as dupe
reload(dupe)
import chrlx_pipe.quickIncrement as qincr
reload(qincr)
import chrlx_pipe.compareSceneInfo as csi
reload(csi)
import buttonsToLayout as btl
reload(btl)
import chrlx_pipe.utils as utils
import chrlx_pipe.lgtSettings as lgt
reload(lgt)
import chrlx_pipe.shotFuncs as sFuncs
reload(sFuncs)

#a class to store basic variables across functions
class ProjectVars(object):

    def __init__(self):
    #many of these are getting set in the populate window function or the poluateAsset, Shot and updateAssetInfo functions 

        self.root = cFuncs.fixPath(os.environ.get("CHRLX_3D_ROOT"))
        self.mayaRoot = cFuncs.fixPath(os.getenv("MAYA_ROOT"))
        self.images = cFuncs.fixPath("{0}/scripts/chrlx_pipe/images".format(self.mayaRoot))

        self.currentProject = ""
        self.job = ""
        self.spot = ""
        self.spotRefFolder = ""
        self.charFolder = ""
        self.propFolder = ""
        self.setFolder = ""
        self.shotsFolder = ""
        self.currentAsset = ""
        self.currentAssetFolder = ""
        self.currentGeoFolder = ""
        self.currentRigFolder = ""
        self.currentAssetLatestGeoWS = ""
        self.currentAssetLatestRigWS = ""
        self.currentAssetGeoMaster = ""
        self.currentAssetRigMaster = ""
        self.currentShot = ""
        self.currentShotNum = ""
        self.currentJobNumber = ""
        self.currentShotFolder = ""
        self.currentAnmFolder = ""
        self.currentLgtFolder = ""
        self.currentFxFolder = ""

        self.currentFrameRange = ""

        self.currentVariant = ""
        self.referenceDictionary = {}
        self.currentShotLatestAnmWS = ""
        self.currentShotLatestLgtWS = ""
        self.currentShotLatestFXWS = ""
        self.currentShotAnmMaster = ""
        self.currentShotLgtMaster = ""
        self.currentShotFXMaster = ""

        self.openSceneFullPath = ""
        self.openScene = ""
        self.user = mel.eval("getenv USER")
        self.date = ""
        self.time = ""

#dictionary of UI widgets
widgets = {}
pi = ProjectVars()
tooltips = cmds.help(q=True, popupMode=True)

ann = {"proj":"opens window to set your project - job/spot",
"refresh":"refresh this window",
"explore":"open explorer to the reference folder for the current spot",
"openWS":"opens the latest WS of the variant selected above",
"incrWS":"saves current scene as an incremented version of the variant selected above",
"prevWS":"opens window to browse prev anim WS's",
"openMst":"opens the published master of the variant selected above",
"pubRefMst":"to publish the currently open workshop variant. Does NOT IMPORT references in the master",
"pubBGMst":"opens a background process to master the open workshop variant. IMPORTS REFERENCES in the master.",
"prevMst":"opens expolorer to browse previous master versions of the selected variant",
"WSInfo":"opens window to see file info on the latest workshop", 
"MstInfo":"opens window to see file info on the latest master",
"crtIcon":"create an icon image for the current scene (based on current camera)",
"import":"import an external file into the current scene",
"refAsset":"references the asset rig master selected on the left into the current scene",
"reference":"reference an external file into the current scene",
"qkIncr":"brings up convenient window to increment the current workshop",
"crtShot":"create a new shot folder structure and a first anm variant to get started",
"dupeShot":"duplicate selected shot, either to the current job or to another",
"archive":"archive selected variant into the archive folder under the asset type folder. Does NOT delete the asset, simply removes it from view!",
"unarchive":"restore an archived asset from it's archive folder back into the main project structure", 
"crtVariant":"create a new variant folder for the selected shot (a variant is separate version of the same shot)",
"replace":"replace the selected reference on the right with the master selected on the left",
"reload":"reloads the selected reference",
"unload":"unloads the selected reference. Does NOT remove the reference",
"remove":"removes the selected reference from the scene (permanently removes)", 
"refMult":"imports multiple copies of the same asset (use integer field)", 
"expAnim":"export the animation from the selected reffed asset's 'ALLKEYABLE' set (in .atom format)",
"impAnim":"import animation (.atom format) to the selected reffed asset (from and to 'ALLKEYABLE' set)",
"refTo":"reference the selected from the list on the left to the location of the currently selected object\nNote: double clicking a reference on the right list will select the top nodes of that reference",
"rendGen":"set up the current scene with some default render global setttings, including loading the renderer chosen, if possible", 
"spotIcon":"click to take a snapshot of the current scene to replace this pic",
"mtlApply":"apply the material master on the left to the reffed asset on the right",
"ctrlMk":"takes selection and groups it, then makes a control based on the bounding box of that selection", 
"shotList":"A list of shots currently created in the spot. Double-click a shot to opens it in explorer", 
"reffedAssets":"list of referenced files in the current scene (usually this is the namespace). Double-click to select the top node(s) of the reffed file.", 
"varFile":"this section is for creating and working in shot 'variants'. These are sub-versions of shots and are independent from one another. Each shot must have a least one variant", 
"test":"testing yo buddy testing"
}



############
# UI creation
###########

def shotWinUI(*args):
    """create the UI for the shotWin"""
### ---------- should check for current project
    if cmds.window("shotWin", exists = True):
        cmds.deleteUI("shotWin")

    widgets["win"] = cmds.window("shotWin", t= "Charlex Shot Manager", w=1000, h=560, s=False)
    widgets["mainCLO"] = cmds.columnLayout(w=1000, h=560)

    #######################
    #top bar layout
    #######################

    #rowlayout
    widgets["bannerFLO"] = cmds.formLayout(w=1000, h=50, bgc=(.300,.3,.300))
    widgets["bannerImage"] = cmds.image(image="{0}/banner_shotWin.png".format(pi.images))
    widgets["spotImage"] = cmds.iconTextButton(style="iconOnly", image = "{0}/defaultSpotImage.jpg".format(pi.images), w=50, h=50, ann=ann["spotIcon"], c=changeSpotIcon)
    widgets["projectText"] = cmds.text(l="Project Name: Spot Name", font = "boldLabelFont")
    widgets["sceneText"] = cmds.text(l="Current Scene") 
    widgets["projectButton"] = cmds.button(l="Change Job", w = 100, h= 40, bgc= (.5,.5,.5), ann = ann["proj"], c=setProject)
    widgets["refreshButton"] = cmds.button(l="Refresh", w = 60, h= 40, bgc= (.2,.2,.2), c = populateWindow)
    widgets["exploreButton"] = cmds.button(l="Explore\nReference", w = 60, h= 40, bgc= (.7,.5,.3), c=exploreReference)

    cmds.formLayout(widgets["bannerFLO"], e=True, af = [(widgets["bannerImage"], "top", 0),
        (widgets["bannerImage"], "left", 0),
        (widgets["projectText"], "left", 400),
        (widgets["projectText"], "top", 5),
        (widgets["sceneText"], "top", 25),
        (widgets["spotImage"], "left", 335),         
        (widgets["sceneText"], "left", 400),
        (widgets["projectButton"], "left", 740),
        (widgets["projectButton"], "top", 5),
        (widgets["refreshButton"], "left", 850),
        (widgets["refreshButton"], "top", 5),
        (widgets["exploreButton"], "left", 920),
        (widgets["exploreButton"], "top", 5),       
        ])

        ######################
        #bottom layout
        ########################
    cmds.setParent(widgets["mainCLO"])
    widgets["lowFLO"] = cmds.formLayout()
    widgets["lowTLO"] = cmds.tabLayout(bgc = (.2, .2, .2 ))

            ################
            #shots tab
            ################
    cmds.setParent(widgets["lowTLO"])
    widgets["shotsFLO"] = cmds.formLayout("Shots - Anim, Light and FX",w=1000, h=500, bgc = (.4,.4,.4))
    
                ##############
                #shot asset List layout
                ###############
    widgets["shotAssListCLO"] = cmds.columnLayout(w=240, bgc = (.5, .5,.5))
    widgets["shotAssListFLO"] = cmds.formLayout(w=240, h= 500)
    widgets["shotAssListTSL"] = cmds.textScrollList(w=240, h=465, ams=True) 

    widgets["shotAssListTitleText"] = cmds.text(l="Referenced Assets In Current Scene", font = "boldLabelFont", al="center", ann=ann["reffedAssets"])

    cmds.formLayout(widgets["shotAssListFLO"], e=True, af = [
        (widgets["shotAssListTSL"], "top", 35),
        (widgets["shotAssListTSL"], "left", 0),
        
        (widgets["shotAssListTitleText"], "top", 5),
        (widgets["shotAssListTitleText"], "left", 20),
        ])

                ##############
                #shot List layout
                ###############
    cmds.setParent(widgets["shotsFLO"])
    widgets["shotListCLO"] = cmds.columnLayout(w=130, bgc = (.5, .5, .5))
    widgets["shotListFLO"] = cmds.formLayout(w=130, h= 500)
    widgets["shotListTSL"] = cmds.textScrollList(w=130, h=460)
    widgets["shotListTitleText"] = cmds.text(l="Shot List", font = "boldLabelFont", ann=ann["shotList"])
    widgets["shotListCharText"] = cmds.text(l="Shots")

    cmds.formLayout(widgets["shotListFLO"], e=True, af = [
        (widgets["shotListTSL"], "top", 40), 
        (widgets["shotListTSL"], "left", 0),
        (widgets["shotListTitleText"], "top", 5),
        (widgets["shotListTitleText"], "left", 30),
        (widgets["shotListCharText"], "top", 25),
        (widgets["shotListCharText"], "left", 5),
        ])

                ##############
                #shot Status layout
                ############### 
    cmds.setParent(widgets["shotsFLO"])
    widgets["shotInfoAssListTLO"] = cmds.tabLayout(w=200, h=500)
    widgets["shotInfoFLO"] = cmds.formLayout("ShotInfo", w=200, h=500, bgc= (.5, .5, .5))
    widgets["shotInfoTitleText"] = cmds.text(l="Shot Information", font = "boldLabelFont")
    widgets["shotInfoNameText"] = cmds.text(l="<Shot Name>", font = "boldLabelFont", al="center", w=200)
    widgets["shotInfoVariantText"] = cmds.text(l="<Var Name>", font = "boldLabelFont", al="center", w=200)  
    widgets["shotInfoPic"] = cmds.image(image = "{0}/kitten-photo-632-3.jpg".format(pi.images), w= 154, h=154)
    widgets["shotAnnCB"] = cmds.checkBox(l="Tooltips popups?", value=tooltips, changeCommand=tooltipSet)

    cmds.formLayout(widgets["shotInfoFLO"], e=True, af =[
        (widgets["shotInfoNameText"], "top", 60),
        (widgets["shotInfoNameText"], "left", 0),
        (widgets["shotInfoVariantText"], "top", 80),
        (widgets["shotInfoVariantText"], "left", 0),        
        (widgets["shotInfoPic"], "top", 110),
        (widgets["shotInfoPic"], "left", 23),
        (widgets["shotInfoTitleText"], "top", 5),
        (widgets["shotInfoTitleText"], "left", 35),
        (widgets["shotAnnCB"], "top", 420),
        (widgets["shotAnnCB"], "left", 50),        
        ])

    cmds.setParent(widgets["shotInfoAssListTLO"])
    widgets["shotAssRigListTLO"] = cmds.tabLayout("ProjAssets", w=200, h=500)   
    widgets["shotAssRigCharListCLO"] = cmds.columnLayout("Chars", w=200, h=500)
    widgets["shotAssRigCharListTSL"] = cmds.textScrollList(w=200, h=450)    
    cmds.setParent(widgets["shotAssRigListTLO"])
    widgets["shotAssRigPropListCLO"] = cmds.columnLayout("Props", w=200, h=500)
    widgets["shotAssRigPropListTSL"] = cmds.textScrollList(w=200, h=450)    
    cmds.setParent(widgets["shotAssRigListTLO"])
    widgets["shotAssRigSetListCLO"] = cmds.columnLayout("Sets", w=200, h=500)
    widgets["shotAssRigSetListTSL"] = cmds.textScrollList(w=200, h=450) 
    cmds.setParent(widgets["shotAssRigListTLO"])
    widgets["shotAnmMstListCLO"] = cmds.columnLayout("Anm", w=200, h=500)
    widgets["shotAnmMstListTSL"] = cmds.textScrollList(w=200, h=450)    
                ###############
                #Shot Action layout
                ################
    cmds.setParent(widgets["shotsFLO"])
    widgets["shotActionFLO"] = cmds.formLayout(w=150, h=500, bgc =(.5, .5, .5))
    widgets["shotActionRefAssBut"] = cmds.button(l="-> Ref Asset In ->", w=130, h=20, bgc = (.7,.7,.7), c=referenceAsset, ann=ann["refAsset"])  
    widgets["shotActionReplaceBut"] = cmds.button(l="-> Replace Reference ->", w=130, h=20, en=True, bgc = (.7,.7,.7), ann=ann["replace"], c=replaceReference)
    widgets["shotActionRefMultBut"] = cmds.button(l="-> Ref Multiple ->", w=100, h=20, en=True, bgc = (.7,.7,.7), ann=ann["refMult"], c=referenceMultiple)
    widgets["shotActionRefMultIFG"] = cmds.intFieldGrp(w=20, v1=1)
    widgets["shotActionReloadBut"] = cmds.button(l="Reload Reference ->", w=130, h=20, bgc = (.7,.7,.7), c=reloadReference, ann=ann["reload"])
    widgets["shotActionUnloadBut"] = cmds.button(l="Unload Reference ->", w=130, h=20, bgc = (.7,.7,.7), c=unloadReference, ann=ann["unload"])
    widgets["shotActionRemoveBut"] = cmds.button(l="Remove Reference ->", w=130, h=20, bgc = (.7,.7,.7), c=removeReference, ann=ann["remove"])
    widgets["shotActionQIncrBut"] = cmds.button(l="Quick Increment", w=130, h=20, en=True, bgc = (.7,.7,.7), c=quickIncrement, ann=ann["qkIncr"])
    widgets["shotActionNewShotBut"] = cmds.button(l="Create new shot", en=True, w=130, h=20, bgc = (.7,.7,.7), c=createNewShot, ann=ann["crtShot"]) 
    widgets["shotActionTitle"] = cmds.text(l="Shot Actions", font = "boldLabelFont")

    # create an embedded tab layout for each type of button!
    widgets["shotActionTypeTLO"] = cmds.tabLayout("Specific Actions", w=150, h=180, bgc=(.2,.2,.2))

    widgets["shotActionTypeAnmSLO"] = cmds.scrollLayout("Anm", w=150, h=180, verticalScrollBarThickness=5)    
    widgets["shotActionTypeAnmFLO"] = cmds.formLayout(w=150,h=240, bgc=(.4, .45, .4))
    widgets["shotActionExpAnimBut"] = cmds.button(l="Export Anim ->", w=130, h=20, en=True, bgc=(.7,.7,.7), c=exportAnimation, ann=ann["expAnim"])
    widgets["shotActionImpAnimBut"] = cmds.button(l="Import Anim ->", w=130, h=20, en=True, bgc=(.7,.7,.7), c=importAnimation, ann=ann["impAnim"])
    widgets["shotActionRefToBut"] = cmds.button(l="-> Reference To", w=130, h=20, en=True, bgc=(.7,.7,.7), c=referenceTo, ann=ann["refTo"])
    widgets["shotActionCtrlMkBut"] = cmds.button(l="Ctrl On Selection", w=130, h=20, en=True, bgc=(.7,.7,.7), c=controlMaker, ann=ann["ctrlMk"])

    cmds.setParent(widgets["shotActionTypeTLO"])
    widgets["shotActionTypeLgtSLO"] = cmds.scrollLayout("Lgt", w=150, h=180, verticalScrollBarThickness=5)    
    widgets["shotActionTypeLgtFLO"] = cmds.formLayout(w=150,h=240, bgc=(.4, .4, .45))
    widgets["shotActionGenericBut"] = cmds.button(l="Render Setup", w=130, h=20, en=True, bgc = (.7,.7,.7), c=renderSetup, ann=ann["rendGen"])

    widgets["shotActionMtlBut"] = cmds.button(l="-> Apply Mtl To Sel ->", w=130, h=20, en=False, bgc = (.7,.7,.7), ann=ann["mtlApply"])

    cmds.setParent(widgets["shotActionTypeTLO"])
    widgets["shotActionTypeFxSLO"] = cmds.scrollLayout("Fx", w=150, h=240, verticalScrollBarThickness=5)      
    widgets["shotActionTypeFxFLO"] = cmds.formLayout(w=150,h=180, bgc=(.45, .4, .4))
  

#---------------- add any fx buttons here and then postion them below 

    cmds.formLayout(widgets["shotActionTypeLgtFLO"], e=True, af = [
        (widgets["shotActionGenericBut"], "top", 10),
        (widgets["shotActionGenericBut"], "left", 2),
        (widgets["shotActionMtlBut"], "top", 40),
        (widgets["shotActionMtlBut"], "left", 2)        
        ])

    cmds.formLayout(widgets["shotActionTypeAnmFLO"], e=True, af = [
        (widgets["shotActionExpAnimBut"], "top", 10),
        (widgets["shotActionExpAnimBut"], "left", 2),
        (widgets["shotActionImpAnimBut"], "top", 40),
        (widgets["shotActionImpAnimBut"], "left", 2),
        (widgets["shotActionRefToBut"], "top", 70),
        (widgets["shotActionRefToBut"], "left", 2),
        (widgets["shotActionCtrlMkBut"], "top", 100),
        (widgets["shotActionCtrlMkBut"], "left", 2)        
        ])

    cmds.formLayout(widgets["shotActionFLO"], e=True, af = [
        (widgets["shotActionTitle"], "top", 5),
        (widgets["shotActionTitle"], "left", 35),
        (widgets["shotActionRefAssBut"], "top", 30),
        (widgets["shotActionRefAssBut"], "left", 10),
        (widgets["shotActionRefMultBut"], "top", 60),
        (widgets["shotActionRefMultBut"], "left", 10),
        (widgets["shotActionRefMultIFG"], "top", 60),
        (widgets["shotActionRefMultIFG"], "left", 110),
        (widgets["shotActionReloadBut"], "top", 90),
        (widgets["shotActionReloadBut"], "left", 10),
        (widgets["shotActionUnloadBut"], "top", 120),
        (widgets["shotActionUnloadBut"], "left", 10),
        (widgets["shotActionRemoveBut"], "top", 150),
        (widgets["shotActionRemoveBut"], "left", 10),
        (widgets["shotActionReplaceBut"], "top", 180),
        (widgets["shotActionReplaceBut"], "left", 10),
        (widgets["shotActionQIncrBut"], "top", 210),
        (widgets["shotActionQIncrBut"], "left", 10),
        (widgets["shotActionTypeTLO"], "top", 270),
        (widgets["shotActionTypeTLO"], "left", 0),        
        (widgets["shotActionNewShotBut"], "top", 470),
        (widgets["shotActionNewShotBut"], "left", 10),      
        ])

                ###############
                #Shot anmLgt tab layout
                ################
    cmds.setParent(widgets["shotsFLO"])
    widgets["anmLgtFLO"] = cmds.formLayout(w=250, h=500, bgc = (.4, .4, .4))
    widgets["anmLgtTLO"] = cmds.tabLayout(w=250, h=500, bgc = (.4,.4,.4), changeCommand = varTabChange)
                    ###############
                    #shot anm tab layout
                    ###############
    widgets["anmTabCLO"] = cmds.columnLayout("ANM", w=250, bgc = (.4, .45, .4))
                        #################
                        #anm info frame and column layouts
                        #################                       
    cmds.separator(h=5)
    widgets["anmVariationsTSL"] = cmds.textScrollList(w=250, h=90)
    widgets["anmLastWSTFG"] = cmds.textFieldGrp(l="Latest WS: ", w=250, cw = [(1, 70), (2,170)], cal = [(1,"left"), (2, "left")],ed=False)
    widgets["anmLastMasterTFG"] = cmds.textFieldGrp(l="Master: ", w=250, cw = [(1, 70), (2,170)], cal = [(1,"left"), (2, "left")],ed=False)
    cmds.separator(h=5)

                        #################
                        #anm 'workshop' frame and column layouts
                        #################
    cmds.setParent(widgets["anmTabCLO"])
    widgets["anmWSFLO"] = cmds.frameLayout("Animation Workshop", w=250, h=165, bgc= (.3, .3, .3))
    widgets["anmWSFoLO"] = cmds.formLayout(w=250, h=165, bgc = (.4,.45,.4))

    widgets["anmWSOpenBut"] = cmds.button(l="Open Latest\nAnim\nWorkshop", w=70, h=50, en=False, bgc = (.4,.5,.8), ann=ann["openWS"])
    widgets["anmWSIncrBut"] = cmds.button(l="Increment Anim Workshop", w=160, h=50, en=True, bgc = (.7,.6,.4), ann=ann["incrWS"], c = partial(incrementWorkshop, "anm"))
    widgets["anmWSPrevBut"] = cmds.button(l="Previous Anim Workshops", w=160, bgc = (.7,.7,.7), en=False, ann=ann["prevWS"])
    widgets["anmWSInfoBut"] = cmds.button(l="WS Info", w=70, bgc = (.7, .7, .7), en=False, ann=ann["WSInfo"])   
    widgets["anmWSNewVarBut"] = cmds.button(l="Create New Variant", w=160, h=30, bgc = (.2,.2,.2), c=partial(createVariant, "anm"), ann=ann["crtVariant"])
    widgets["anmVarIconBut"] = cmds.button(l="Create Var\nIcon", w=70, h=30, bgc = (.7,.7,.7), en=False, c=createShotIcon, ann=ann["crtIcon"])  

    cmds.formLayout(widgets["anmWSFoLO"], e=True, af = [
        (widgets["anmWSOpenBut"], "left", 5),
        (widgets["anmWSOpenBut"], "top", 10),
        (widgets["anmWSIncrBut"], "left", 80),
        (widgets["anmWSIncrBut"], "top", 10),
        (widgets["anmWSInfoBut"], "left", 5),
        (widgets["anmWSInfoBut"], "top", 65),
        (widgets["anmWSPrevBut"], "left", 80),
        (widgets["anmWSPrevBut"], "top", 65),
        (widgets["anmWSNewVarBut"], "left", 5),
        (widgets["anmWSNewVarBut"], "top", 105),
        (widgets["anmVarIconBut"], "left", 170),
        (widgets["anmVarIconBut"], "top", 105),         
        ])
                        #################
                        #anm 'master' frame and column layouts
                        #################
    cmds.setParent(widgets["anmTabCLO"])
    widgets["anmMstFLO"] = cmds.frameLayout("Animation Master", w=250, h=200, bgc= (.3, .3, .3))
    widgets["anmMstFoLO"] = cmds.formLayout(w=250, h=200, bgc = (.4,.45,.4))
    widgets["anmMstOpenBut"] = cmds.button(l="Open Anim\nMaster", w=70, h=50, en=False, bgc = (.5,.7,.5), ann=ann["openMst"])
    widgets["anmMstIncrBut"] = cmds.button(l="Publish Anim Master\n(Import Refs)", w=160, h=50, en=False, bgc = (.7,.5,.5), ann=ann["pubRefMst"])
    widgets["anmMstBgIncrBut"] = cmds.button(l="BG Publish Anim Master (Import Refs)", w=235, en=False, bgc = (.3,.3,.3), ann=ann["pubBGMst"])
    widgets["anmMstPrevBut"] = cmds.button(l="Previous Anim Masters", w=160, en=False, bgc = (.7,.7,.7), ann=ann["prevMst"])
    widgets["anmMstInfoBut"] = cmds.button(l="Mst Info", w=70, bgc = (.7, .7, .7), en=False, ann=ann["MstInfo"])


        
    cmds.formLayout(widgets["anmMstFoLO"], e=True, af = [
        (widgets["anmMstOpenBut"], "left", 5),
        (widgets["anmMstOpenBut"], "top", 10),
        (widgets["anmMstIncrBut"], "left", 80),
        (widgets["anmMstIncrBut"], "top", 10),
        (widgets["anmMstBgIncrBut"], "left", 5),
        (widgets["anmMstBgIncrBut"], "top", 65),        
        (widgets["anmMstInfoBut"], "left", 5),
        (widgets["anmMstInfoBut"], "top", 95),          
        (widgets["anmMstPrevBut"], "left", 80),
        (widgets["anmMstPrevBut"], "top", 95), 
        
        ])
                    ###############
                    #shot Lgt tab layout
                    ################    
    cmds.setParent(widgets["anmLgtTLO"])                
    widgets["lgtTabCLO"] = cmds.columnLayout("LGT", w=250, bgc = (.4,.4,.45))
                        #################
                        #lgt info frame and column layouts
                        #################                       
    cmds.separator(h=5)
    widgets["lgtVariationsTSL"] = cmds.textScrollList(w=250, h=90)
    widgets["lgtLastWSTFG"] = cmds.textFieldGrp(l="Latest WS: ", w=250, cw = [(1, 70), (2,170)], cal = [(1,"left"), (2, "left")],ed=False)
    widgets["lgtLastMasterTFG"] = cmds.textFieldGrp(l="Master: ", w=250, cw = [(1, 70), (2,170)], cal = [(1,"left"), (2, "left")],ed=False) 
    cmds.separator(h=5)
                        #################
                        #lgt 'workshop' frame and column layouts
                        #################
    cmds.setParent(widgets["lgtTabCLO"])
    widgets["lgtWSFLO"] = cmds.frameLayout("Lighting Workshop", w=250, h=165, bgc= (.3, .3, .3))
    widgets["lgtWSFoLO"] = cmds.formLayout(w=250, h=165, bgc = (.4,.4,.45))

    widgets["lgtWSOpenBut"] = cmds.button(l="Open Latest\nLight\nWorkshop", w=70, h=50, en=False, bgc = (.4,.5,.8), ann=ann["openWS"])
    widgets["lgtWSIncrBut"] = cmds.button(l="Increment Light Workshop", w=160, h=50, en=True, bgc = (.7,.6,.4), c = partial(incrementWorkshop, "lgt"), ann=ann["incrWS"])
    widgets["lgtWSInfoBut"] = cmds.button(l="WS Info", w=70, bgc = (.7, .7, .7), en=False, ann=ann["WSInfo"])
    widgets["lgtWSPrevBut"] = cmds.button(l="Previous Light Workshops", w=160, en=False, bgc = (.7,.7,.7), ann=ann["prevWS"])
    widgets["lgtWSNewVarBut"] = cmds.button(l="Create New Variant", w=160, h=30, bgc = (.2,.2,.2), c=partial(createVariant, "lgt"), ann=ann["crtVariant"])  
    widgets["lgtVarIconBut"] = cmds.button(l="Create Var\nIcon", w=70, h=30, en=False, bgc = (.7,.7,.7), c=createShotIcon, ann=ann["crtIcon"])

    cmds.formLayout(widgets["lgtWSFoLO"], e=True, af = [
        (widgets["lgtWSOpenBut"], "left", 5),
        (widgets["lgtWSOpenBut"], "top", 10),
        (widgets["lgtWSIncrBut"], "left", 80),
        (widgets["lgtWSIncrBut"], "top", 10),
        (widgets["lgtWSInfoBut"], "left", 5),
        (widgets["lgtWSInfoBut"], "top", 65),
        (widgets["lgtWSPrevBut"], "left", 80),
        (widgets["lgtWSPrevBut"], "top", 65),
        (widgets["lgtWSNewVarBut"], "left", 5),
        (widgets["lgtWSNewVarBut"], "top", 105),
        (widgets["lgtVarIconBut"], "left", 170),
        (widgets["lgtVarIconBut"], "top", 105),                     
        ])  
                        #################
                        #lgt 'master' frame and column layouts
                        #################
    cmds.setParent(widgets["lgtTabCLO"])
    widgets["lgtMstFLO"] = cmds.frameLayout("Lighting Master", w=250, h=200, bgc= (.3, .3, .3))
    widgets["lgtMstFoLO"] = cmds.formLayout(w=250, h=200, bgc = (.4,.4,.45))
    widgets["lgtMstOpenBut"] = cmds.button(l="Open\nLight Master", w=70, h=50, en=True, bgc = (.5,.7,.5), c=partial(openShotMaster, "lgt"), ann=ann["openMst"])
    widgets["lgtMstIncrBut"] = cmds.button(l="Publish Light Master\n(Keep Refs)", w=160, h=50, en=False, bgc = (.7,.5,.5), ann=ann["pubRefMst"])
    widgets["lgtMstInfoBut"] = cmds.button(l="Mst Info", w=70, bgc = (.7, .7, .7), en=False, ann=ann["MstInfo"])        
    widgets["lgtMstPrevBut"] = cmds.button(l="Previous Light Masters", w=160, en=False, bgc = (.7,.7,.7), ann=ann["prevMst"])
    widgets["lgtMstBgIncrBut"] = cmds.button(l=" BG Publish Light Master (Import Refs)", w=235, en=False, bgc = (.3,.3,.3), ann=ann["pubBGMst"])    

    cmds.formLayout(widgets["lgtMstFoLO"], e=True, af = [
        (widgets["lgtMstOpenBut"], "left", 5),
        (widgets["lgtMstOpenBut"], "top", 10),
        (widgets["lgtMstIncrBut"], "left", 80),
        (widgets["lgtMstIncrBut"], "top", 10),
        (widgets["lgtMstBgIncrBut"], "left", 5),
        (widgets["lgtMstBgIncrBut"], "top", 65),    
        (widgets["lgtMstInfoBut"], "left", 5),
        (widgets["lgtMstInfoBut"], "top", 95),
        (widgets["lgtMstPrevBut"], "left", 80),
        (widgets["lgtMstPrevBut"], "top", 95),
    
        ])  

                    ###############
                    #shot anm tab layout
                    ###############
    cmds.setParent(widgets["anmLgtTLO"])
    widgets["fxTabCLO"] = cmds.columnLayout("FX", w=250, bgc = (.45, .4, .4))
                        #################
                        #fx info frame and column layouts
                        #################                       
    cmds.separator(h=5)
    widgets["fxVariationsTSL"] = cmds.textScrollList(w=250, h=90)
    widgets["fxLastWSTFG"] = cmds.textFieldGrp(l="Latest WS: ", w=250, cw = [(1, 70), (2,170)], cal = [(1,"left"), (2, "left")],ed=False)
    widgets["fxLastMasterTFG"] = cmds.textFieldGrp(l="Master: ", w=250, cw = [(1, 70), (2,170)], cal = [(1,"left"), (2, "left")],ed=False)  
    cmds.separator(h=5)
                        #################
                        #lgt 'workshop' frame and column layouts
                        #################
    cmds.setParent(widgets["fxTabCLO"])
    widgets["fxWSFLO"] = cmds.frameLayout("FX Workshop", w=250, h=165, bgc= (.3, .3, .3))
    widgets["fxWSFoLO"] = cmds.formLayout(w=250, h=165, bgc = (.45,.4,.4))

    widgets["fxWSOpenBut"] = cmds.button(l="Open Latest\nFX\nWorkshop", w=70, h=50, en=False, bgc = (.4,.5,.8), ann=ann["openWS"])
    widgets["fxWSIncrBut"] = cmds.button(l="Increment FX Workshop", w=160, h=50, en=True, bgc = (.7,.6,.4), c = partial(incrementWorkshop, "fx"), ann=ann["incrWS"])
    widgets["fxWSInfoBut"] = cmds.button(l="WS Info", w=70, bgc = (.7, .7, .7), en=False, ann=ann["WSInfo"])        
    widgets["fxWSPrevBut"] = cmds.button(l="Previous FX Workshops", w=160, en=False, bgc = (.7,.7,.7), ann=ann["prevWS"])
    widgets["fxWSNewVarBut"] = cmds.button(l="Create New Variant", w=160, h=30, bgc = (.2,.2,.2), c=partial(createVariant, "fx"), ann=ann["crtVariant"])
    widgets["fxVarIconBut"] = cmds.button(l="Create Var\nIcon", w=70, h=30, en=False, bgc = (.7,.7,.7), c=createShotIcon, ann=ann["crtIcon"])   
    
    cmds.formLayout(widgets["fxWSFoLO"], e=True, af = [
        (widgets["fxWSOpenBut"], "left", 5),
        (widgets["fxWSOpenBut"], "top", 10),
        (widgets["fxWSIncrBut"], "left", 80),
        (widgets["fxWSIncrBut"], "top", 10),
        (widgets["fxWSInfoBut"], "left", 5),
        (widgets["fxWSInfoBut"], "top", 65),
        (widgets["fxWSPrevBut"], "left", 80),
        (widgets["fxWSPrevBut"], "top", 65),
        (widgets["fxWSNewVarBut"], "left", 5),
        (widgets["fxWSNewVarBut"], "top", 105),
        (widgets["fxVarIconBut"], "left", 170),
        (widgets["fxVarIconBut"], "top", 105),                          
        ])  
                        #################
                        #lgt 'master' frame and column layouts
                        #################
    cmds.setParent(widgets["fxTabCLO"])
    widgets["fxMstFLO"] = cmds.frameLayout("FX Master", w=250, h=200, bgc= (.3, .3, .3))
    widgets["fxMstFoLO"] = cmds.formLayout(w=250, h=200, bgc = (.45,.4,.4))
    widgets["fxMstOpenBut"] = cmds.button(l="Open\nFX Master", w=70, h=50, en=False, bgc = (.5,.7,.5), ann=ann["openMst"])
    widgets["fxMstIncrBut"] = cmds.button(l="Publish FX Master\n(Import Refs)", w=160, h=50, en=False, bgc = (.7,.5,.5), ann=ann["pubRefMst"])
    widgets["fxMstInfoBut"] = cmds.button(l="Mst Info", w=70, bgc = (.7, .7, .7), en=False, ann=ann["MstInfo"])     
    widgets["fxMstPrevBut"] = cmds.button(l="Previous FX Masters", w=160, en=False, bgc = (.7,.7,.7), ann=ann["prevMst"])
    widgets["fxMstBgIncrBut"] = cmds.button(l=" BG Publish FX Master (Import Refs)", w=235, en=False, bgc = (.3,.3,.3), ann=ann["pubBGMst"])        

    cmds.formLayout(widgets["fxMstFoLO"], e=True, af = [
        (widgets["fxMstOpenBut"], "left", 5),
        (widgets["fxMstOpenBut"], "top", 10),
        (widgets["fxMstIncrBut"], "left", 80),
        (widgets["fxMstIncrBut"], "top", 10),
        (widgets["fxMstBgIncrBut"], "left", 5),
        (widgets["fxMstBgIncrBut"], "top", 65),     
        (widgets["fxMstInfoBut"], "left", 5),
        (widgets["fxMstInfoBut"], "top", 95),
        (widgets["fxMstPrevBut"], "left", 80),
        (widgets["fxMstPrevBut"], "top", 95),
            
        ])  


    cmds.setParent(widgets["anmLgtFLO"])
    widgets["anmLgtTitleText"] = cmds.text(l="Variant Files", font = "boldLabelFont", ann=ann["varFile"])   

    cmds.formLayout(widgets["anmLgtFLO"], e=True, af = [(widgets["anmLgtTitleText"], "top", 5), (widgets["anmLgtTitleText"], "left", 135)])

            ###################
            # - -- Shot Tab form setup
            ##################
    cmds.formLayout(widgets["shotsFLO"], e=True, af = [
        (widgets["shotListCLO"], "left", 0),
        (widgets["shotListCLO"], "top", 0),
        (widgets["anmLgtFLO"], "left", 134),
        (widgets["anmLgtFLO"], "top", 0),   
        (widgets["shotInfoAssListTLO"], "left", 387),
        (widgets["shotInfoAssListTLO"], "top", 0),
        (widgets["shotActionFLO"], "top", 0),
        (widgets["shotActionFLO"], "left", 594),
        (widgets["shotAssListCLO"], "top", 0),
        (widgets["shotAssListCLO"], "left", 752)
        ])

            ################
            #Misc tab
            ################
    cmds.setParent(widgets["lowTLO"])
    widgets["miscFLO"] = cmds.formLayout("Other Shot Tools",width=1000, height=500, backgroundColor = (.4,.4,.4))

    widgets["animationTLO"] = cmds.tabLayout(width=500, height=250, backgroundColor = (.3, .35, .3))
    widgets["animationRCLO"] = cmds.rowColumnLayout("animation", numberOfColumns = 4, columnSpacing=[(1, 0), (2,5), (3,5), (4,5)], rowSpacing=[1,5])

    cmds.setParent(widgets["miscFLO"])
    widgets["lightingTLO"] = cmds.tabLayout(width=500, height=250, backgroundColor = (.3, .32, .35))
    widgets["lightingRCLO"] = cmds.rowColumnLayout("lighting", numberOfColumns = 4, columnSpacing=[(1, 0), (2,5), (3,5), (4,5)], rowSpacing=[1,5])    

    cmds.setParent(widgets["miscFLO"])
    widgets["fxTLO"] = cmds.tabLayout(width=500, height=250, backgroundColor = (.35, .3, .3))
    widgets["fxRCLO"] = cmds.rowColumnLayout("fx", numberOfColumns = 4, columnSpacing=[(1, 0), (2,5), (3,5), (4,5)], rowSpacing=[1,5])

    cmds.setParent(widgets["miscFLO"])
    widgets["charlexTLO"] = cmds.tabLayout(width=500, height=250, backgroundColor = (.55, .55, .55))
    widgets["charlexRCLO"] = cmds.rowColumnLayout("charlex_general", numberOfColumns = 4, columnSpacing=[(1, 0), (2,5), (3,5), (4,5)], rowSpacing=[1,5])

    cmds.formLayout(widgets["miscFLO"], e=True, af=[
        (widgets["charlexTLO"], "top", 0),
        (widgets["charlexTLO"], "left", 0),
        (widgets["animationTLO"], "top", 0),
        (widgets["animationTLO"], "left", 500),
        (widgets["lightingTLO"], "top", 250),
        (widgets["lightingTLO"], "left", 0),
        (widgets["fxTLO"], "top", 250),
        (widgets["fxTLO"], "left", 500)          
        ])

    # get the dictionary of scripts, calls and annotations from the database
    dbPath =os.path.join(os.getenv("MAYA_ROOT"), "scripts", "chrlx_pipe", "chrlxScriptList.json")
    with open(dbPath, "r") as f:
        scriptList = json.load(f)

    # populate the row column layouts with buttons and funcs from the database
    btl.buttonsToLayout(widgets["animationRCLO"], scriptList["shot"]["animation"], width=117, height=40, color=(.38, .3, .38))
    btl.buttonsToLayout(widgets["lightingRCLO"], scriptList["shot"]["lighting"], width=117, height=40, color=(.37,.34, .3))
    btl.buttonsToLayout(widgets["fxRCLO"], scriptList["shot"]["fx"], width=117, height=40, color=(.35, .3, .3))
    btl.buttonsToLayout(widgets["charlexRCLO"], scriptList["shot"]["charlex"], width=117, height=40, color=(.3, .3, .3))

    # widgets["miscCLO"] = cmds.columnLayout("Other Pipeline Tools",w=1000, h=500, bgc = (.4,.4,.4))
    # cmds.text(l="------ANIM STUFF-------")
    # cmds.text(l="TODO - export cam(s) for nuke, etc")
    # cmds.text(l="TODO - create a new prop from selected geo (propify)")   
    # cmds.text(l="TODO - blasting, rendering stuff?")
    # cmds.text(l="TODO - export data (text file of scene locations?)")
    # cmds.text(l="TODO - create render cam? Should this be in the main anim increment? (probably both)")

    # cmds.text(l="------LGT STUFF--------")
    # cmds.text(l="TODO - set up current scene for maxwell, arnold")
    # cmds.text(l="TODO - convert an external image to icon (char or project)")
    # cmds.text(l="TODO - revert ['ROLL BACK'] to master version? (replaces master and grabs that workshop")
    # cmds.text(l="TODO - function to add your folder to the WIP folder in this project - save current to WIP folder")
    # cmds.text(l="TODO - explore various frame (render) folders in explorer")
    # cmds.text(l="TODO - various preset light setups/rigs? ")


    ######################
    #show window
    ######################
    cmds.window(widgets["win"], e=True, w=1000, h=580)
    cmds.showWindow(widgets["win"])

    #start us off
    populateWindow()


#######################################################################################################
# Functionality
#######################################################################################################

#############
# Get current Project
#############
def projectCheck(*args):
    cFuncs.projectCheck()

def populateWindow(*args):
########### - -- empty values if we're in the wrong schema

    #call out to chrlxFuncs to get current project
    current = cFuncs.getCurrentProject()
    project = ""
    job = ""
    clearAll()
    updateSceneName()

    if current:
        #projectCheck(current)
        projJob = os.path.split(current.rpartition("/jobs/")[2])[0]

        job = projJob.partition("/")[0]
        spot = projJob.partition("/")[2]

        #set some global variables to use later
        pi.currentProject = current
        pi.job = job
        pi.spot = spot

        pi.assetFolder = cFuncs.fixPath(os.path.abspath(os.path.join(pi.currentProject,  "..", "..", "3D_assets"))) 
        pi.charFolder = pi.assetFolder + "/characters"
        pi.propFolder = pi.assetFolder + "/props"
        pi.setFolder = pi.assetFolder + "/sets"                     
        pi.shotsFolder = pi.currentProject + "/shots"

        pi.spotRefFolder =  current.rpartition("/jobs")[0] + "/jobs/{0}/{1}/reference".format(job, spot)

        cmds.text(widgets["projectText"], e=True, l=projJob)
        cmds.text(widgets["sceneText"], e=True, l= pi.openScene)

        print "---------------------------"
        print "loading proj into ShotWin UI!"
        # print "currentProject = {0}".format(pi.currentProject)
        # print "openScene = {0}".format(pi.openScene)
        # print "job = {0}".format(pi.job)
        # print "spot = {0}".format(pi.spot)
        # print "assetFolder = {0}".format(pi.assetFolder)
        # print "charFold = {0}".format(pi.charFolder)
        # print "propFold = {0}".format(pi.propFolder)
        # print "setFold = {0}".format(pi.setFolder)
        # print "shotsFold = {0}".format(pi.shotsFolder)
        print "--------------------------"

        #get assets and populate list
        if projJob:
            populateShots(pi.currentProject)

    else: 
        cmds.warning("shotWin.populateWindow: Doesn't seem like you're in project")

    # #if current open scene lines up with var that exists, select that var in the list and go to appr tab

    f = cmds.file(q=True, sn=True)
    p=""
    if f:
        p = utils.PathManager(f)
    
        if p and isinstance(p, paths.ShotPath): # is file and is a shot path
            pVar = p.variant
            pSP = p.shotPath
            pShot = os.path.basename(pSP)
            pST = p.shotType

            if pST == "anm":
                typeTab = "ANM"
            elif pST == "lgt":
                typeTab = "LGT"
            elif pST == "fx":
                typeTab = "FX"

            shotVars = cFuncs.getShotVariantDict(pSP)
            anmVars = shotVars["anm"]
            lgtVars = shotVars["lgt"]
            fxVars = shotVars["fx"]
            lists = [anmVars, lgtVars, fxVars]
            TSLs = [widgets["anmVariationsTSL"], widgets["lgtVariationsTSL"], widgets["fxVariationsTSL"]]

            cmds.textScrollList(widgets["shotListTSL"], e=True, selectItem=pShot) # select the shot
            updateShotInfo()

            cmds.tabLayout(widgets["anmLgtTLO"], e=True, st=typeTab)            

            # select the var [pVar] in that list
            tabSl = 0
            for y in range(0,3):
                if pVar in lists[y]:
                    cmds.textScrollList(TSLs[y], e=True, selectItem=pVar)
                    updateVariantInfo(pVar, p.variantPath)
    else:
        print "shotWin.populateWindow: couldn't get a current scene name"

    pm = utils.PathManager(current)
    if pm.spotSchema == 2:
        spotImage = cFuncs.fixPath(os.path.join(pm.spotPath, "3d", "spotIcon.jpg"))
        if os.path.isfile(spotImage):
            cmds.iconTextButton(widgets["spotImage"], e=True, image=spotImage)
    
    # select the tab we want to be showing . . . 
    cmds.tabLayout(widgets["shotInfoAssListTLO"], e=True, st="ProjAssets")

def exploreReference(*args):
    #just open the file browser to this folder
    if pi.spotRefFolder:
        cFuncs.openFolderInExplorer(pi.spotRefFolder)
    else:
        cmds.warning("I can't tell what project/spot we're supposed to be in! Are you in a pipeline-project?")


def explorePreviousWS(fType, *args):
    """just pushes the path for the folder to the funcs to open that"""
    path = ""
    if fType == "anm":
        path = pi.currentAnmFolder + "/workshops"
    elif fType == "lgt":
        path = pi.currentLgtFolder + "/workshops"
    elif fType == "fx":
        path = pi.currentFxFolder + "/workshops"
    if path:
        cFuncs.openFolderInExplorer(path)

def populateShots(current, *args):
    """populates the leftmost shot list
        -current is the current project (...3d)

    """
    cmds.textScrollList(widgets["shotListTSL"], e=True, ra=True)
    clearAll()

    shotList = cFuncs.getProjectShotList(current)
    shotExclude = ["master", "prepro", "launchExample", ".mayaSwatches", ".directory", "houdiniDev"]

    if shotList:
        shotList.sort()
        for shot in shotList:
            if shot not in shotExclude:
                shotFolder = cFuncs.fixPath(os.path.join(current, "shots", shot))
                cmds.textScrollList(widgets["shotListTSL"], e=True, a=shot, sc = updateShotInfo, dcc=openShotFolder)

    populateMasteredAssets()

def updateShotInfo(*args):
    """
    populates the variant lists within the selected shot (updates anm, lgt, fx)
    """
    shot = cmds.textScrollList(widgets["shotListTSL"], q=True, si=True)[0]

    #clear all text fields
    clearFields()

    pi.currentShotFolder = cFuncs.fixPath(os.path.join(pi.currentProject, "shots", shot))
    pi.currentVariant = ""  
######---------reset the pi variables for the shot stuff

    lists = ["anmVariationsTSL", "lgtVariationsTSL", "fxVariationsTSL"]
    types = ["anm", "lgt", "fx"]

    #loop through types of files in shot - anm, lgt, fx
    for x in range(3):
        shotTypeFolder = "{0}/{1}".format(pi.currentShotFolder, types[x])
        #clear the list
        cmds.textScrollList(widgets[lists[x]], e=True, ra=True)
        cmds.image(widgets["shotInfoPic"], e=True, image = "{0}/defaultAssetImage.jpg".format(pi.images))
        vars = cFuncs.getShotVariantList(shotTypeFolder)
        if vars:
            for var in vars:
                cmds.textScrollList(widgets[lists[x]], e=True, a=var, sc=partial(updateVariantInfo, var, shotTypeFolder))


def openShotFolder(*args):
    """when a shot is double clicked in the left most textScrollList, then run this to open folder in explorer"""
    shot = cmds.textScrollList(widgets["shotListTSL"], q=True, selectItem=True)[0]
    shotPath = cFuncs.fixPath(os.path.join(pi.shotsFolder, shot))
    cFuncs.openFolderInExplorer(shotPath)


# def openVariantFolder(*args):
#     """when a variant is double clicked , then run this to open folder in explorer"""
#     shot = cmds.textScrollList(widgets["shotListTSL"], q=True, selectItem=True)[0]
#     shotPath = cFuncs.fixPath(os.path.join(pi.shotsFolder, shot))
#     cFuncs.openFolderInExplorer(shotPath)



def clearFields(*args):
    """clears the text fields in the window"""

    cmds.text(widgets["shotInfoNameText"], e=True, l="")
    cmds.text(widgets["shotInfoVariantText"], e=True, l="")

    cmds.textFieldGrp(widgets["anmLastWSTFG"], e=True, tx= "-")
    cmds.textFieldGrp(widgets["anmLastMasterTFG"], e=True, tx = "-")

    cmds.textFieldGrp(widgets["lgtLastWSTFG"], e=True, tx= "-")
    cmds.textFieldGrp(widgets["lgtLastMasterTFG"], e=True, tx = "-")                                

    cmds.textFieldGrp(widgets["fxLastWSTFG"], e=True, tx= "-")
    cmds.textFieldGrp(widgets["fxLastMasterTFG"], e=True, tx = "-") 

#---------------- clear variable to get the image. . .
    cmds.image(widgets["shotInfoPic"], e=True, image = "{0}/noImage.jpg".format(pi.images))
    # cmds.textScrollList(widgets["shotAssListTSL"], e=True, ra=True)

def updateVariantInfo(var='', shotTypeFolder='', *args):
    """update the info for the variant
        DON'T NEED ARGS, WILL PULL FROM THE LIST SELECTION
        -var = name of variant ("varA")
        -shotTypeFolder = folder for the shot (.../3d/shots/SHOT/TYPE)
    """

## =------------- pass in info when I increment ws

    fType = ""
    tsl = ""
    selTab = cmds.tabLayout(widgets["anmLgtTLO"], q=True, st=True)
    if selTab == "ANM":
        fType = "anm"
        tsl = widgets["anmVariationsTSL"]
    if selTab == "LGT":
        fType = "lgt"
        tsl = widgets["lgtVariationsTSL"]
    if selTab == "FX":
        fType = "fx"
        tsl = widgets["fxVariationsTSL"]

    varA = cmds.textScrollList(tsl, q=True, si=True)
    if varA:
        var = varA[0]

    pi.currentShot = os.path.basename(pi.currentShotFolder)
    pi.currentVariant = cFuncs.fixPath(os.path.join(pi.currentShotFolder, fType, var))
    
    #clear all text fields
    clearFields()

    if shotTypeFolder:
        #set text in window
        cmds.text(widgets["shotInfoNameText"], e=True, l="{0}--{1}".format(pi.currentShot, fType))
        cmds.text(widgets["shotInfoVariantText"], e=True, l=var)

        #set some class variables and enable/disable relevant buttons
        #anm
        if fType == "anm":
            anmWS = cFuncs.getLatestVarWS(pi.currentVariant)
            if anmWS:
                cmds.textFieldGrp(widgets["anmLastWSTFG"], e=True, tx = os.path.basename(anmWS))
                pi.currentShotLatestAnmWS = anmWS
                cmds.button(widgets["anmWSOpenBut"], e=True, en=True,c= partial(openShotWS, "anm"))
                cmds.button(widgets["anmWSInfoBut"], e=True, en=True, c=partial(fileInfoWin, pi.currentShotLatestAnmWS))
                cmds.button(widgets["anmWSPrevBut"], e=True, en=True, c=partial(explorePreviousWS, "anm"))
                cmds.button(widgets["anmMstIncrBut"], e=True, en=True, c=partial(masterShot, "anm"))
                cmds.button(widgets["anmMstBgIncrBut"], e=True, en=True, c=partial(bgMasterShot, "anm"))
                cmds.button(widgets["anmVarIconBut"], e=True, en=True)          
            else:
                cmds.textFieldGrp(widgets["anmLastWSTFG"], e=True, tx= "-")
                pi.currentShotLatestAnmWS = ""          
                cmds.button(widgets["anmWSOpenBut"], e=True, en=False)
                cmds.button(widgets["anmWSInfoBut"], e=True, en=False)
                cmds.button(widgets["anmWSPrevBut"], e=True, en=False)
                cmds.button(widgets["anmMstIncrBut"], e=True, en=False)
                cmds.button(widgets["anmMstBgIncrBut"], e=True, en=False)
                cmds.button(widgets["anmVarIconBut"], e=True, en=False)          


            anmMaster = cFuncs.getVarMaster(pi.currentVariant)
            if anmMaster:
                cmds.textFieldGrp(widgets["anmLastMasterTFG"], e=True, tx = os.path.basename(anmMaster))
                pi.currentShotAnmMaster = anmMaster
                cmds.button(widgets["anmMstOpenBut"], e=True, en=True, c=partial(openShotMaster, "anm"))
                cmds.button(widgets["anmMstInfoBut"], e=True, en=True, c=partial(fileInfoWin, pi.currentShotAnmMaster))
                cmds.button(widgets["anmMstPrevBut"], e=True, en=True, c=partial(explorePreviousMstr, "anm"))

            else:
                cmds.textFieldGrp(widgets["anmLastMasterTFG"], e=True, tx = "-")
                pi.currentShotAnmMaster = ""
                cmds.button(widgets["anmMstOpenBut"], e=True, en=False)
                cmds.button(widgets["anmMstInfoBut"], e=True, en=False)
                cmds.button(widgets["anmMstPrevBut"], e=True, en=False)

        #lgt
        if fType == "lgt":
            lgtWS = cFuncs.getLatestVarWS(pi.currentVariant)
            if lgtWS:
                cmds.textFieldGrp(widgets["lgtLastWSTFG"], e=True, tx = os.path.basename(lgtWS))
                pi.currentShotLatestLgtWS = lgtWS
                cmds.button(widgets["lgtWSOpenBut"], e=True, en=True,c= partial(openShotWS, "lgt"))
                cmds.button(widgets["lgtWSInfoBut"], e=True, en=True, c=partial(fileInfoWin, pi.currentShotLatestAnmWS))
                cmds.button(widgets["lgtWSPrevBut"], e=True, en=True, c=partial(explorePreviousWS, "lgt"))
                cmds.button(widgets["lgtMstIncrBut"], e=True, en=True, c=partial(refMasterShot, "lgt"))
                cmds.button(widgets["lgtMstBgIncrBut"], e=True, en=True, c=partial(bgMasterShot, "lgt"))
                cmds.button(widgets["lgtVarIconBut"], e=True, en=True)                                  

            else:
                cmds.textFieldGrp(widgets["lgtLastWSTFG"], e=True, tx= "-")
                pi.currentShotLatestLgtWS = ""          
                cmds.button(widgets["lgtWSOpenBut"], e=True, en=False)
                cmds.button(widgets["lgtWSInfoBut"], e=True, en=False)
                cmds.button(widgets["lgtWSPrevBut"], e=True, en=False)
                cmds.button(widgets["lgtMstIncrBut"], e=True, en=False)
                cmds.button(widgets["lgtMstBgIncrBut"], e=True, en=False)
                cmds.button(widgets["lgtVarIconBut"], e=True, en=False)

            lgtMaster = cFuncs.getVarMaster(pi.currentVariant)
            if lgtMaster:
                cmds.textFieldGrp(widgets["lgtLastMasterTFG"], e=True, tx = os.path.basename(lgtMaster))
                pi.currentShotLgtMaster = lgtMaster
                cmds.button(widgets["lgtMstOpenBut"], e=True, en=True,c= partial(openShotMaster, "lgt"))
                cmds.button(widgets["lgtMstInfoBut"], e=True, en=True, c=partial(fileInfoWin, pi.currentShotLgtMaster))
                cmds.button(widgets["lgtMstPrevBut"], e=True, en=True, c=partial(explorePreviousMstr, "lgt"))

            else:
                cmds.textFieldGrp(widgets["lgtLastMasterTFG"], e=True, tx = "-")
                pi.currentShotLgtMaster = ""    
                cmds.button(widgets["lgtMstOpenBut"], e=True, en=False)
                cmds.button(widgets["lgtMstPrevBut"], e=True, en=False)

        #fx
        if fType == "fx":
            fxWS = cFuncs.getLatestVarWS(pi.currentVariant)
            if fxWS:
                cmds.textFieldGrp(widgets["fxLastWSTFG"], e=True, tx = os.path.basename(fxWS))
                pi.currentShotLatestFxWS = fxWS
                cmds.button(widgets["fxWSOpenBut"], e=True, en=True,c= partial(openShotWS, "fx"))
                cmds.button(widgets["fxWSInfoBut"], e=True, en=True, c=partial(fileInfoWin, pi.currentShotLatestFxWS))
                cmds.button(widgets["fxWSPrevBut"], e=True, en=True, c=partial(explorePreviousWS, "fx"))                
                cmds.button(widgets["fxMstIncrBut"], e=True, en=True, c=partial(masterShot, "fx"))
                cmds.button(widgets["fxMstBgIncrBut"], e=True, en=True, c=partial(bgMasterShot, "fx"))
                cmds.button(widgets["fxVarIconBut"], e=True, en=True)


            else:
                cmds.textFieldGrp(widgets["fxLastWSTFG"], e=True, tx= "-")
                pi.currentShotLatestFxWS = ""
                cmds.button(widgets["fxWSOpenBut"], e=True, en=False)
                cmds.button(widgets["fxWSInfoBut"], e=True, en=False)
                cmds.button(widgets["fxWSPrevBut"], e=True, en=False)               
                cmds.button(widgets["fxMstIncrBut"], e=True, en=False)
                cmds.button(widgets["fxMstBgIncrBut"], e=True, en=False)                        
                cmds.button(widgets["fxVarIconBut"], e=True, en=False)

            fxMaster = cFuncs.getVarMaster(pi.currentVariant)

            if fxMaster:
                cmds.textFieldGrp(widgets["fxLastMasterTFG"], e=True, tx = os.path.basename(fxMaster))
                pi.currentShotFxMaster = fxMaster
                cmds.button(widgets["fxMstOpenBut"], e=True, en=True, c= partial(openShotMaster, "fx"))             
            else:
                cmds.textFieldGrp(widgets["fxLastMasterTFG"], e=True, tx = "-")
                pi.currentShotFxMaster = ""
                cmds.button(widgets["fxMstOpenBut"], e=False, en=True)              

        #upate pic
        if pi.currentVariant:
            iconDir = "{0}/icon".format(pi.currentVariant)
        else:
            iconDir = pi.image

        pic1 = "{0}Icon.png".format(var)
        pic2 = "{0}Icon.xpm".format(var)

        if pic1 in (os.listdir(iconDir)):
            cmds.image(widgets["shotInfoPic"], e=True, image = "{0}/{1}".format(iconDir, pic1))
        elif pic2 in (os.listdir(iconDir)):
            cmds.image(widgets["shotInfoPic"], e=True, image = "{0}/{1}".format(iconDir, pic2))
        else:
            cmds.image(widgets["shotInfoPic"], e=True, image = "{0}/defaultAssetImage.jpg".format(pi.images))
    else:
        cmds.warning("chrlxshotWin.updateShotInfo: There is no shot name passed to me")


def populateMasteredAssets(*args):
    """
    for asset types ("geo", "rig", "mtl", "anm"), populate the list of published assets in shot win (these are the assets/anm that the animators can use. . . ie. they have mastered rigs)
    """
    #clear the lists first
    cmds.textScrollList(widgets["shotAssRigCharListTSL"], e=True, ra=True)
    cmds.textScrollList(widgets["shotAssRigPropListTSL"], e=True, ra=True)
    cmds.textScrollList(widgets["shotAssRigSetListTSL"], e=True, ra=True)
    cmds.textScrollList(widgets["shotAnmMstListTSL"], e=True, ra=True)

    chars, props, sets = cFuncs.getProjectAssetList(pi.assetFolder)

    #check for rig masters
    for char in chars:
        cMstr = cFuncs.getAssetMaster(char, cFuncs.fixPath(os.path.join(pi.assetFolder, "characters", char)), "rig")
        if cMstr:
            cmds.textScrollList(widgets["shotAssRigCharListTSL"], e=True, a=char, dcc=showAssetImage)
    for prop in props:
        pMstr = cFuncs.getAssetMaster(prop, cFuncs.fixPath(os.path.join(pi.assetFolder, "props", prop)), "rig")     
        if pMstr:
            cmds.textScrollList(widgets["shotAssRigPropListTSL"], e=True, a=prop, dcc=showAssetImage)
    for sett in sets:
        sMstr = cFuncs.getAssetMaster(sett, cFuncs.fixPath(os.path.join(pi.assetFolder, "sets", sett)), "rig")      
        if sMstr:
            cmds.textScrollList(widgets["shotAssRigSetListTSL"], e=True, a=sett, dcc=showAssetImage)

    #check for anim variants and masters
    varAnm = []
    shots = cFuncs.getProjectShotList(pi.currentProject)
    # print "shotWin.populateMasteredAssets (line 937): shots =", shots
    if shots:
        for shot in shots:
            shotVars = cFuncs.getShotVariantDict(os.path.join(pi.currentProject, "shots", shot))
            if shotVars["anm"]:
                for anm in shotVars["anm"]:
                    aMstr = cFuncs.getVarMaster(cFuncs.fixPath(os.path.join(pi.currentProject, "shots", shot, "anm", anm)))
                    #print cFuncs.fixPath(os.path.join(pi.currentProject, "shots", shot, "anm", anm))
                    if aMstr:           
                        varAnm.append("{0}.{1}".format(anm, shot))

    for av in varAnm:
        cmds.textScrollList(widgets["shotAnmMstListTSL"], e=True, a=av)

    populateSceneRefs()     


def showAssetImage(*args):
    """ will get the selected asset from the open tab and call the assetImageUI func from cFuncs """

    selTab = cmds.tabLayout(widgets["shotAssRigListTLO"], q=True, st=True)

    fType = ""
    asset = ""
    assetPath = ""
    path = ""
    imagePath = ""

    if selTab == "Chars":
        asset = cmds.textScrollList(widgets["shotAssRigCharListTSL"], q=True, si=True)
        if asset:
            imagePath = cFuncs.fixPath(os.path.join(pi.assetFolder, "characters", asset[0], "icon","{0}Icon.png".format(asset[0])))
            if os.path.isfile(imagePath):
                cFuncs.assetImageUI(imagePath)
            else:
                cmds.warning("Can't find an image for {0}".format(asset[0]))

    if selTab == "Props":
        asset = cmds.textScrollList(widgets["shotAssRigPropListTSL"], q=True, si=True)
        if asset:
            imagePath = cFuncs.fixPath(os.path.join(pi.assetFolder, "props", asset[0], "icon","{0}Icon.png".format(asset[0])))
            if os.path.isfile(imagePath):
                cFuncs.assetImageUI(imagePath)
            else:
                cmds.warning("Can't find an image for {0}".format(asset[0]))
    
    if selTab == "Sets":
        asset = cmds.textScrollList(widgets["shotAssRigSetListTSL"], q=True, si=True)
        if asset:
            imagePath = cFuncs.fixPath(os.path.join(pi.assetFolder, "sets", asset[0], "icon","{0}Icon.png".format(asset[0])))
            if os.path.isfile(imagePath):
                cFuncs.assetImageUI(imagePath)
            else:
                cmds.warning("Can't find an image for {0}".format(asset[0]))
    
    # if selTab == "Anm":
    #   #need to split this up
    #   var_shot = cmds.textScrollList(widgets["shotAnmMstListTSL"], q=True, si=True)
    #   if var_shot:
    #       var, buf, shot = var_shot[0].partition(".")
    #       path = cFuncs.getVarMaster(cFuncs.fixPath(os.path.join(pi.shotsFolder, shot, "anm", var)))


def populateSceneRefs(*args):
    """ 
        populate the list with the ref node names
    """
    pi.referenceDictionary = {}
    cmds.textScrollList(widgets["shotAssListTSL"], e=True, ra=True)

    #get reference paths
    refs = cmds.file(q=True, r=True)

    buff = []
    # loaded = []
    for ref in refs:
        #get the associated namespace
        ns = cmds.file(ref, q=True, ns=True)
        pi.referenceDictionary[ns] = ref

    # put files in buffer list to sort
    for g in pi.referenceDictionary.keys():
        buff.append(g)
    buff.sort()

    # now put the sorted namespaces in the list
    for b in buff:
        cmds.textScrollList(widgets["shotAssListTSL"], e=True, append=b, dcc = selectRefs)

    # if ref is deferred(not loaded), change it's font
    for ref in refs:
        if cmds.file(ref, q=True, deferReference=True):
            ns = cmds.file(ref, q=True, ns=True) # get the namespace in order to get the item name
            cmds.textScrollList(widgets["shotAssListTSL"], e=True, selectItem=ns) # sel the item in order to query it
            index = cmds.textScrollList(widgets["shotAssListTSL"], q=True, selectIndexedItem=True)[0] # query the index of sel
            cmds.textScrollList(widgets["shotAssListTSL"], e=True, lineFont = [index, "obliqueLabelFont"])
            cmds.textScrollList(widgets["shotAssListTSL"], e=True, deselectAll=True)

    # if we're in a lgt file, look through current refs and for each one of type "anm", check the frame rates, etc. and give option to change
    curr = paths.PathManager(cmds.file(q=True, sn=True))
    if curr.shotType == "lgt":
        for ref in refs:
            p=paths.PathManager(ref)
            if p.shotType == "anm":
                dict = cFuncs.getFileFrameInfo(cFuncs.fixPath(ref))
                csi.compareSceneInfo(dict)


def renderSetup(style, *args):
    """
    sets up the current scene to render in given renderer. See chrlx_pipe.lgtSettings.py for the details
    """
    # set up confirm dialog to pop up window to do these things (replace the orig buttons and partial command)
    dial = cmds.confirmDialog(t="Render Setup", message="Choose how you'd like to initially setup the current scene:", button=["Generic", "Arnold", "Maxwell", "VRay", "Cancel"])

    if dial != "Cancel":
        # sets the common setting regarless
        lgt.setCommon()

        if dial == "Arnold":
            lgt.setArnold()
        if dial == "Vay":
            lgt.setVray()
        if dial == "Maxwell":
            lgt.setMaxwell()

def reloadReference(*args):
    """gets the scene refs from the list on the right, gets the paths from the dict and reloads them"""
    
    sel = cmds.textScrollList(widgets["shotAssListTSL"], q=True, si=True)
    if sel:
        for s in sel:
            path = pi.referenceDictionary[s]
            cmds.file(path, loadReference=True)

        populateSceneRefs()             


def replaceReference(*args):

#---------------- FOR MULTIPLE SELECTION!
    # get the reference in the right side
    nspace = cmds.textScrollList(widgets["shotAssListTSL"], q=True, si=True)
    refs = cmds.file(q=True, r=True)

    if nspace:
        for ns in nspace:
            targetFile = pi.referenceDictionary[ns]

            path = ""
            path = getSelectMasteredAsset()

            if path:
                print "shotWin.replaceRef: replacing ref {0} with - - -".format(targetFile), path
                newNS = os.path.basename(path).rstrip(".ma")
                cFuncs.replaceReferenceAndNamespace(path, targetFile, newNS)

            else:
                cmds.warning("You must select an asset from the lists on the left (available refs) to reference in!")

        populateMasteredAssets()

    else:
        cmds.warning("You need to select an asset from the right side (current refs) to replace!")


def getSelectMasteredAsset(*args):
    """returns the selected asset path from the list on the left"""
    path = ""
    #check that we have the correct tab open
    topTab = cmds.tabLayout(widgets["shotInfoAssListTLO"], q=True, st=True)
    if topTab == "ShotInfo":
        cmds.warning("You must have the 'ProjAssets' tab open and select an asset or animation file")
        return()
    if topTab == "ProjAssets":
        # determine which tab is open and get selected from that
        selTab = cmds.tabLayout(widgets["shotAssRigListTLO"], q=True, st=True)
        assetRaw = ""
        asset = ""
        if selTab == "Chars":
            assetRaw = cmds.textScrollList(widgets["shotAssRigCharListTSL"], q=True, si=True)
            if assetRaw:
                asset = assetRaw[0]
                assetPath = cFuncs.fixPath(os.path.join(pi.assetFolder, "characters", asset))
                path = cFuncs.getAssetMaster(asset, assetPath, "rig")

        if selTab == "Props":
            assetRaw = cmds.textScrollList(widgets["shotAssRigPropListTSL"], q=True, si=True)
            if assetRaw:
                asset = assetRaw[0]
                assetPath = cFuncs.fixPath(os.path.join(pi.assetFolder, "props", asset))
                path = cFuncs.getAssetMaster(asset, assetPath, "rig")
        
        if selTab == "Sets":
            assetRaw = cmds.textScrollList(widgets["shotAssRigSetListTSL"], q=True, si=True)
            if assetRaw:
                asset = assetRaw[0]
                assetPath = cFuncs.fixPath(os.path.join(pi.assetFolder, "sets", asset))
                path = cFuncs.getAssetMaster(asset, assetPath, "rig")
            
        if selTab == "Anm":
            #need to split this up
            var_shot = cmds.textScrollList(widgets["shotAnmMstListTSL"], q=True, si=True)
            if var_shot:
                asset, buf, shot = var_shot[0].partition(".")
                path = cFuncs.getVarMaster(cFuncs.fixPath(os.path.join(pi.shotsFolder, shot, "anm", asset)))

    return(path) 


def refExternal(*args):
    """reference external file into scene"""
    goTo = pi.currentProject
    refFile = cmds.fileDialog2(fm=1, dir = goTo)[0]
    if refFile:
        cmds.file(refFile, r=True)


def importExternal(*args):
    """import external file into scene"""
    goTo = pi.currentProject
    impFile = cmds.fileDialog2(fm=1, dir = goTo)[0]
    if impFile:
        cmds.file(impFile, i=True)


def referenceMultiple(*args):
    """references multiple copies of the asset master chosen on the left"""
    num = cmds.intFieldGrp(widgets["shotActionRefMultIFG"], q=True, v1=True)
    path = ""
    path = getSelectMasteredAsset()

    if path:    
        for x in range(num):
            print "shotWin.referenceAsset: referencing in - - -", path
            cFuncs.referenceInWithNamespace(path)
            # now refresh. . .
            populateMasteredAssets()
    else:
        cmds.warning("You must select an asset from the lists to reference in!")


def removeReference(*args): 
    sel = cmds.textScrollList(widgets["shotAssListTSL"], q=True, si=True)

    if sel:
        for s in sel:
            path = pi.referenceDictionary[s]
            cmds.file(path, removeReference=True)

        populateSceneRefs() 


def unloadReference(*args):
    sel = cmds.textScrollList(widgets["shotAssListTSL"], q=True, si=True)

    if sel:
        for s in sel:
            path = pi.referenceDictionary[s]
            cmds.file(path, unloadReference=True)

        populateSceneRefs() 


def createNewShot(*args):
    """
    calls create new shot window - will pass the spot "shots" folder
    """
    createDir.createShot(pi.shotsFolder)


def exportAnimation(shot="", var="", *args):
    # store current selection
    prevSel = cmds.ls(sl=True)
    # get sel on right
    ass = cmds.textScrollList(widgets["shotAssListTSL"], q=True, si=True)
    if ass:
        if len(ass)>1:
            cmds.warning("Must select only one reffed asset to export!")
            return()
        else:
            assKey = "{0}:ALLKEYABLE".format(ass[0])
            if cmds.objExists(assKey):
                cmds.select(assKey)

                sn = cmds.file(q=True, sn=True)
                if sn:
                    p = utils.PathManager(sn)
                    if isinstance(p, utils.ShotPath):
                        name = "{0}_{1}_{2}_anim.atom".format(p.shotName, p.variant, ass[0])
                        path = cFuncs.fixPath(os.path.join(p.shotPath, "data", "anm", name)) # get the shot data anm path
                else:
                    if pi.currentProject:
                        name = "{0}_anim.atom".format(ass[0])
                        path = cFuncs.fixPath(os.path.join(pi.currentProject, "shots", name)) # get the generic shots path
                    else:
                        cmds.warning("You need to be in a project for me to know what to do")
                        cmds.select(prevSel, r=True)
                        return()                

                cFuncs.exportAnimation(path)
            else:
                cmds.warning("I can't find the 'ALLKEYABLE' set to export anim from!")
    else:
        cmds.warning("You need to select an asset on the right side to export anim from!")

    cmds.select(prevSel, r=True)


def importAnimation(*args):
    ass = cmds.textScrollList(widgets["shotAssListTSL"], q=True, si=True)

    if ass:
        if len(ass)>1:
            cmds.warning("Must select only one reffed asset to import anim to!")
            return()
        else:
            assKey = "{0}:ALLKEYABLE".format(ass[0])
            if cmds.objExists(assKey):
                cmds.select(assKey, r=True)

        # try to get a starting path
        sn=cmds.file(q=True, sn=True)
        if sn:
            p = utils.PathManager(sn)
            if isinstance(p, utils.ShotPath):
                path = cFuncs.fixPath(os.path.join(p.shotPath, "data", "anm"))
            else:
                path = cFuncs.getCurrentProject()
        else:
            path = cFuncs.getCurrentProject()

        cFuncs.importAnimation(path)

    else:
        cmds.warning("You need to a target asset on the right!")


def quickIncrement(*args):
    qincr.quickIncrement()


def varTabChange(*args):
    """
    just changes the action button tab to match the shot type tab selection
    """
    tab = cmds.tabLayout(widgets["anmLgtTLO"], q=True, st=True)
    if tab == "ANM":
        cmds.tabLayout(widgets["shotActionTypeTLO"], e=True, st="Anm")
    if tab == "LGT":
        cmds.tabLayout(widgets["shotActionTypeTLO"], e=True, st="Lgt")
    if tab == "FX":
        cmds.tabLayout(widgets["shotActionTypeTLO"], e=True, st="Fx")

def controlMaker(*args):
    sFuncs.createControl()


############
# Set Project in Win
############    
def setProject(*args):
    prj = projectSetter.ProjectSetter(True)

############
# Open Workshop and master files
############

def createVariant(fType, *args):
    """
    creates a variant of the selected shot base on the fType (anm, lgt, fx)
    calls out to createDirectories to create a variant within a shot (var of type ftype)
    ARGS:
        fType (string): 'anm','lgt','fx'
    RETURN:
        None
    """
    # pass the shotFolder and fType to chrlx_pipe.createDirectories.createVariant(shotFolder, fType)
    shot = cmds.textScrollList(widgets["shotListTSL"], q=True, si=True)
    if shot:
        createDir.createVariant(pi.currentShotFolder, fType)
    else:
        cmds.warning("You need to select a shot in which to create a new variant!")


def openShotWS(fType, *args):
    if pi.currentShot:
        if fType == "anm":
            wsFile = pi.currentShotLatestAnmWS
        elif fType == "lgt":
            wsFile = pi.currentShotLatestLgtWS
        elif fType == "fx":
            wsFile = pi.currentShotLatestFxWS

        #if there's a file in the variable
        if wsFile:
            cFuncs.chrlxFileOpen(wsFile)
            updateSceneName()
            populateShots(pi.currentProject)
        #if there's no file in the variable, but the asset is selected, then GO TO CREATE FILE PATH
        else:
            print "shotWin.openShotWorkshop: THERE IS NO FILE!"
    else:
        cmds.warning("shotWin.openShotWorkshop: No asset selected!")

    populateWindow()


def openShotMaster(fType, *args):
    """
    """
    if pi.currentVariant:
        if fType == "anm":
            # here get the selected variant from list
            varName = cmds.textScrollList(widgets["anmVariationsTSL"], q=True, si=True)[0]
            master = cFuncs.getVarMaster(pi.currentVariant)
        if fType == "lgt":
            varName = cmds.textScrollList(widgets["lgtVariationsTSL"], q=True, si=True)[0]
            master = cFuncs.getVarMaster(pi.currentVariant)
        if fType == "fx":
            varName = cmds.textScrollList(widgets["fxVariationsTSL"], q=True, si=True)[0]
            master = cFuncs.getVarMaster(pi.currentVariant)

        if master:
            cFuncs.chrlxFileOpen(master)

        else:
            print "This is no master file for the variant:", pi.currentVariant
    else:
        print "showWin.opeShotMaster: I can't find a selected variant"


def updateSceneName(*args):
    """gets the open scene name, updates the window text and the class variable"""
    pi.openSceneFullPath = cmds.file(q=True, sn=True)
    pi.openScene = os.path.basename(pi.openSceneFullPath)

    if pi.openScene == "":
        pi.openScene = "UNSAVED SCENE!"
    cmds.text(widgets["sceneText"], e=True, l=pi.openScene) 


def referenceAsset(*args):
    """
    get file from asset list - clean up name and path and ref in (do something with NAMESPACE. . .)
    """

    #check that we have the correct tab open
    path = ""
    path = getSelectMasteredAsset()

    if path:
        print "shotWin.referenceAsset: referencing in - - -", path
        cFuncs.referenceInWithNamespace(path)
        # now refresh. . .
        populateMasteredAssets()
    else:
        cmds.warning("You must select an asset from the lists to reference in!")


def explorePreviousWS(fType, *args):
    """just pushes the path for the folder to the funcs to open that"""
    path = ""
    if fType == "anm":
        path = pi.currentVariant + "/workshops"
    elif fType == "lgt":
        path = pi.currentVariant + "/workshops"
    elif fType == "fx":
        path = pi.currentVariant + "/workshops"
    if path:
        cFuncs.openFolderInExplorer(path)


def explorePreviousMstr(fType, *args):
    """just pushes the path for the folder to the funcs to open that"""
    path = ""
    if fType == "anm":
        path = pi.currentVariant + "/past_versions"
    elif fType == "lgt":
        path = pi.currentVariant + "/past_versions"
    elif fType == "fx":
        path = pi.currentVariant + "/past_versions" 
    if path:
        cFuncs.openFolderInExplorer(path)

#############
# increment Workshops
#############

def incrementWorkshop(fType, *args):
    #get info from window about what KIND of WS file it is (geo, rig, anm, lgt or fx)
    #call out to chrlxFuncs to increment file num   

    incr = ""

    if pi.currentVariant:
        name = os.path.basename(pi.currentVariant)

        if fType == "anm":
            incr = cFuncs.incrementWS(name, pi.currentVariant, fType)
        elif fType == "lgt":
            incr = cFuncs.incrementWS(name, pi.currentVariant, fType)
        elif fType == "fx":
            incr = cFuncs.incrementWS(name, pi.currentVariant, fType)
        else:
            pass

    else:
        print "No variant is selected in the variant window!"

    pi.date = cmds.about(cd=True)
    pi.time = cmds.about(ct=True)
    #pi.user

    #pull up prompt dialogue for notes - ---- PASS THE NOTE TO THE CFUNCS
    note = cmds.promptDialog(title="Add Note", message = os.path.basename(incr), scrollableField = True, button = ("Add and Save", "Cancel"), defaultButton = "Add and Save", cancelButton = "Cancel", dismissString = "Cancel")
    if note == "Add and Save":
        chrlxNote = cmds.promptDialog(q=True, text=True)
        cmds.file(rename = "{0}".format(incr))
        # add some stuff into the initial geo workshop
        if incr.rpartition("_ws_v")[2].rstrip(".ma") == "001":
            print "-------Adding the delete set--------"
            if not cmds.objExists("deleteSet"):
                cmds.sets(name = "deleteSet", empty=True)

        # add fileInfo stuff to scene before we save. . .
        cFuncs.putFileInfo(fType, incr.rpartition("_ws_v")[2].rstrip(".ma"), chrlxNote)

        #save the incremented scene
        cmds.file(save=True, type="mayaAscii")

        cmds.warning("------Increment finished!--------\n{0}".format(incr))

        updateSceneName()
        #updateVariantInfo()
        updateVariantInfo(os.path.basename(pi.currentVariant), pi.currentVariant)

    else:
        pass


def masterShot(fType, *args):
    """
    masters the shot in the current open maya, so slow. . . , imports references and cleans stuff
    fType is "anm", "lgt", "fx"
    """
    # seperate in case we need to do thing indiv for each type
    if fType == "anm":
        test = cMaster.masterShot(os.path.basename(pi.currentVariant), pi.currentVariant, fType, BG = False, importRefs = True)
        if test == "clash":
            return()
        cmds.confirmDialog(t="Mastered File", m=test, b="OK")

    if fType == "lgt":
        test = cMaster.masterShot(os.path.basename(pi.currentVariant), pi.currentVariant, fType, BG = False, importRefs = True)
        if test == "clash":
            return()
        cmds.confirmDialog(t="Mastered File", m=test, b="OK")

    if fType == "fx":
        test = cMaster.masterShot(os.path.basename(pi.currentVariant), pi.currentVariant, fType, BG = False, importRefs = True)
        if test == "clash":
            return()
        cmds.confirmDialog(t="Mastered File", m=test, b="OK")


def refMasterShot(fType, *args):
    """
        masters the shot without importing any references or doing much else. Is faster and returns you back to your scene (incremented)
        fType is "anm", "lgt", "fx"
    """
    # seperate in case we need to do thing indiv for each type
    if fType == "anm":
        test = cMaster.masterShot(os.path.basename(pi.currentVariant), pi.currentVariant, fType, BG = False, importRefs = False)
        if test == "clash":
            return()
        cmds.confirmDialog(t="Mastered File", m=test, b="OK")

    if fType == "lgt":
        test = cMaster.masterShot(os.path.basename(pi.currentVariant), pi.currentVariant, fType, BG = False, importRefs = False)
        if test == "clash":
            return()
        cmds.confirmDialog(t="Mastered File", m=test, b="OK")

    if fType == "fx":
        test = cMaster.masterShot(os.path.basename(pi.currentVariant), pi.currentVariant, fType, BG = False, importRefs = False)
        if test == "clash":
            return()
        cmds.confirmDialog(t="Mastered File", m=test, b="OK")


def bgMasterShot(fType, *args):
    """
        masters the shot in a background process, while incrementing the scene you are currently in. Standard master process(import refs, etc)
        fType is "anm", "lgt", "fx"
    """
    # seperate in case we need to do thing indiv for each type
    if fType == "anm":
        test = cMaster.masterShot(os.path.basename(pi.currentVariant), pi.currentVariant, fType, BG = True, importRefs = True)
        if test == "clash":
            return()
        cmds.confirmDialog(t="Mastered File", m=test, b="OK")

    if fType == "lgt":
        test = cMaster.masterShot(os.path.basename(pi.currentVariant), pi.currentVariant, fType, BG = True, importRefs = True)
        if test == "clash":
            return()
        cmds.confirmDialog(t="Mastered File", m=test, b="OK")

    if fType == "fx":
        test = cMaster.masterShot(os.path.basename(pi.currentVariant), pi.currentVariant, fType, BG = True, importRefs = True)
        if test == "clash":
            return()
        cmds.confirmDialog(t="Mastered File", m=test, b="OK")


def fileInfoWin(filePath, *args):
    """calls module to bring up file win for filePath arg"""
    fileInfo.fileInfo(filePath)


def referenceTo(*args):
    # pi.referenceDictionary to get refPath
    refPath = getSelectMasteredAsset()
    node = ""
    sel = cmds.ls(sl=True, transforms=True)
    if not sel or (len(sel)!=1):
        cmds.warning("You must only have one object selected!")
    else: 
        node = sel[0]
    
        if refPath and node:
            cFuncs.refToLocation(refPath, node)
        else:
            cmds.warning("I didn't get a selection on the left list and one object selected in the scene to RefereceTo")


def selectRefs(*args):
    """
    gets the selected ref asset (on the right side) and on double click, selects the top node of that asset in the maya scene
    """
    sel = cmds.textScrollList(widgets["shotAssListTSL"], q=True, si=True)
    roots = []
    nodes = []
    if sel:
        for s in sel:
            path = pi.referenceDictionary[s]
            nodes.append(cmds.referenceQuery(path, nodes=True))
    roots = cFuncs.getTopNodes(nodes[0])
    cmds.select(cl=True)
    for x in roots:
        cmds.select(x, add=True)


def tooltipSet(*args):
    status = cmds.checkBox(widgets["shotAnnCB"], q=True, v=True)

    cmds.help(popupMode=status)
    cmds.savePrefs()


#############
# create icon script
############

def changeSpotIcon(*args):
    path = pi.currentProject
    cFuncs.createJobSpotIcon(path, "spotIcon")


def createShotIcon(*args):
    #check if user is in the same scene file as the selected asset!!
    sceneName = cFuncs.fixPath(cmds.file(q=True, sn = True))
    if sceneName == None:
        sceneName = "UNSAVED"
    snameChar = os.path.commonprefix([sceneName, pi.currentVariant])

    sceneCont = "Yes"
    if snameChar != pi.currentVariant:
        sceneCont = cmds.confirmDialog(t="Mismatching Chars", m="Your scene doesn't match that asset!\nWrite icon to {0} anyways?".format(pi.currentAsset), b=("Yes","No"), db="No", cb="No", ds="No")

    #check that something is selected in asset list
    if sceneCont == "Yes":
        sel = ""
        
        #go up a few levels to find what asset type we are . . . 
        tab = cmds.tabLayout(widgets["anmLgtTLO"], q=True, st=True)
        if tab == "ANM":
            tabL = "anmVariationsTSL"
        elif tab == "LGT":
            tabL = "lgtVariationsTSL"
        elif tab == "FX":
            tabL = "fxVariationsTSL"
        try:
            sel = cmds.textScrollList(widgets[tabL], q=True, si=True)[0]
        except: 
            cmds.warning("Doesn't seem like you've selected a shot to create an image for!")

        if sel:
            go = "Yes"
            iconFile = "{0}/icon/{1}Icon.png".format(pi.currentVariant, sel)
            if os.path.isfile(iconFile):
                go = cmds.confirmDialog(t="Overwrite Confirm", m="There is already an icon for this!\nShould I overwrite it?", b=("Yes", "No"), db="Yes", cb ="No", ds = "No")
            if go=="Yes":
                #at this pt we can delete the orig file
                if os.path.isfile(iconFile):
                    os.remove(iconFile)
                #deselect objects in scene, PB, then reselect
                sl = cmds.ls(sl=True)
                cmds.select(clear = True)
                cFuncs.createAssetIcon("{0}/icon".format(pi.currentVariant), sel)
                cmds.select(sl, r=True)

                updateShotInfo()
            else:
                cmds.warning("Icon creation cancelled")
    else:
        cmds.warning("Cancelling Icon Creation")

    populateWindow()


def clearAll(*args):
    """clears text fields and lists"""

    pi.openScene = ""
    pi.openSceneFullPath = ""

    #shot lists and variants
    cmds.textScrollList(widgets["shotListTSL"], e=True, ra =True)
    cmds.textScrollList(widgets["anmVariationsTSL"], e=True, ra =True)
    cmds.textScrollList(widgets["lgtVariationsTSL"], e=True, ra =True)
    cmds.textScrollList(widgets["fxVariationsTSL"], e=True, ra =True)   
    cmds.text(widgets["shotInfoNameText"], e=True, l="")
    cmds.text(widgets["shotInfoVariantText"], e=True, l="") 
    #anm
    cmds.textFieldGrp(widgets["anmLastWSTFG"], e=True, tx = "")
    cmds.textFieldGrp(widgets["anmLastMasterTFG"], e=True, tx="")
    #lgt
    cmds.textFieldGrp(widgets["lgtLastWSTFG"], e=True, tx = "")
    cmds.textFieldGrp(widgets["lgtLastMasterTFG"], e=True, tx="")
    #fx
    cmds.textFieldGrp(widgets["fxLastWSTFG"], e=True, tx = "")
    cmds.textFieldGrp(widgets["fxLastMasterTFG"], e=True, tx="")
    cmds.textScrollList(widgets["shotAssListTSL"], e=True, ra=True)
    cmds.textScrollList(widgets["shotAssRigCharListTSL"], e=True, ra=True)  
    cmds.textScrollList(widgets["shotAssRigPropListTSL"], e=True, ra=True)  
    cmds.textScrollList(widgets["shotAssRigSetListTSL"], e=True, ra=True)   
    cmds.textScrollList(widgets["shotAnmMstListTSL"], e=True, ra=True)  
    #shot info
    cmds.image(widgets["shotInfoPic"], e=True, image = "{0}/noImage.jpg".format(pi.images))
    cmds.textScrollList(widgets["shotAssListTSL"], e=True, ra=True)    
    
#############
# Call to start UI
############

def shotWin(*args):
    shotWinUI()