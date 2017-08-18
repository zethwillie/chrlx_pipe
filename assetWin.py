#chrlxAssetWin
import maya.cmds as cmds
import maya.mel as mel

import os
import sys
from functools import partial
import datetime
import json

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
import buttonsToLayout as btl
reload(btl)
import chrlx_pipe.utils as utils
import assetFuncs as aFuncs
reload(aFuncs)

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
        self.assetFolder = ""
        self.charFolder = ""
        self.propFolder = ""
        self.setFolder = ""
        self.shotsFolder = ""
        self.currentAsset = ""
        self.currentAssetFolder = ""
        self.currentGeoFolder = ""
        self.currentRigFolder = ""
        self.currentMtlFolder = ""
        self.currentAssetLatestGeoWS = ""
        self.currentAssetLatestRigWS = ""
        self.currentAssetLatestMtlWS = ""
        self.currentAssetGeoMaster = ""
        self.currentAssetRigMaster = ""
        self.currentAssetMtlMaster = ""
        self.currentAssetGeoWS = ""
        self.currentAssetRigWS = ""
        self.currentAssetMtlWS = ""


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
"openAssWS":"opens the latest WS of the selected asset (rig or geo)",
"incrAssWS":"save the current scene as an incremented WS version of the selected asset (rig or geo)",
"prevAssWS":"opens window to browse prev WS's", 
"openAssMst":"will open the published master of this asset (rig or geo)",
"pubAssMst":"opens window to publish the current scene as the master for the selected asset(rig or geo)",
"prevAssMst":"opens folder to browse previous master versions of the selected asset", 
"WSInfo":"opens window with info about the latest workshop file", 
"MstInfo":"opens window with info about the latest master file", 
"crtIcon":"create an icon image for the current scene (based on current camera)",
"import":"import an external file into the current scene",
"reference":"reference an external file into the current scene",
"qkIncr":"brings up convenient window to increment the current workshop",
"crtAsset":"create a new asset folder structure",
"dupeAsset":"duplicate selected asset, either to the current job or to another",
"archive":"archive selected asset into the archive folder under the asset type folder. Does NOT delete the asset, simply removes it from view!",
"unarchive":"restore an archived asset from it's archive folder back into the main project structure",
"refGeo":"reference in the geometry master file from the selected asset (if it exists)", 
"assTab":"select the asset in these lists to bring up it's info on the right.\nDouble-click to open asset folder explorer window",
"jobIcon":"click to take a snapshot of the current scene to replace this pic", 
"dupeRef":"Duplicates the referenced geometry (from geo mstr) for the current scene and places the reffed origs in the 'deleteSet', if not already there",
"cpSkin":"Select 1) a bound geo and 2) unbound geo and this will bind second from binding jnts and copy the skin weights from first to second",
"xferUV":"opens window to transfer shaders and uv's from obj to other objs", 
"pushRig":"in a background process, will refresh the reference in rig workshop, then master the rig asset (NOTE: won't update any duplicated or imported geo files in rig)"
""
}


############
# UI creation
###########

def assetWinUI(*args):
    """create the UI for the assetWin"""

    if cmds.window("assetWin", exists = True):
        cmds.deleteUI("assetWin")

    widgets["win"] = cmds.window("assetWin", t= "Charlex Asset Manager", w=1000, h=560, s=False)
    widgets["mainCLO"] = cmds.columnLayout(w=1000, h=560)

    #######################
    #top bar layout
    #######################

    #rowlayout
    widgets["bannerFLO"] = cmds.formLayout(w=1000, h=50, bgc=(.300,.3,.300))
    widgets["bannerImage"] = cmds.image(image="{0}/banner_assetWin.png".format(pi.images))
    widgets["jobImage"] = cmds.iconTextButton(image = "{0}/defaultJobImage.jpg".format(pi.images), w=50, h=50, c=changeJobIcon, ann=ann["jobIcon"])
    widgets["projectText"] = cmds.text(l="Project Name: Spot Name", font = "boldLabelFont")
    widgets["sceneText"] = cmds.text(l="Current Scene") 
    widgets["projectButton"] = cmds.button(l="Change Job", w = 100, h= 40, bgc= (.5,.5,.5), ann = ann["proj"], c=setProject)
    widgets["refreshButton"] = cmds.button(l="Refresh", w = 60, h= 40, bgc= (.2,.2,.2), c = populateWindow, ann=ann["refresh"])
    widgets["exploreButton"] = cmds.button(l="Explore\nReference", w = 60, h= 40, bgc= (.7,.5,.3), c=exploreReference, ann=ann["explore"])

    cmds.formLayout(widgets["bannerFLO"], e=True, af = [(widgets["bannerImage"], "top", 0),
        (widgets["bannerImage"], "left", 0),
        (widgets["projectText"], "left", 400),
        (widgets["jobImage"], "left", 335), 
        (widgets["projectText"], "top", 5),
        (widgets["sceneText"], "top", 25),
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
            #asset tab
            ################
    widgets["assetFLO"] = cmds.formLayout("Assets - Geo, Rig, Lgt",w=1000, h=500,bgc = (.4,.4,.4))
                ##############
                #assetList layout
                ###############
    widgets["assListCLO"] = cmds.columnLayout(w=240, bgc = (.5, .5, .5))
    widgets["assListFLO"] = cmds.formLayout(w=240, h= 500)
    widgets["assListTypeTLO"] = cmds.tabLayout(w=240, h=500, bgc = (.3, .3, .3), ann=ann["assTab"])
    widgets["assCharListCLO"] = cmds.columnLayout("Chars", w=240, h=500)
    widgets["assCharListTSL"] = cmds.textScrollList(w=240, h=470)
    cmds.setParent(widgets["assListTypeTLO"])
    widgets["assPropListCLO"] = cmds.columnLayout("Props", w=240, h=500)
    widgets["assPropListTSL"] = cmds.textScrollList(w=240, h=470)
    cmds.setParent(widgets["assListTypeTLO"])
    widgets["assSetListCLO"] = cmds.columnLayout("Sets", w=240, h=500)
    widgets["assSetListTSL"] = cmds.textScrollList(w=240, h=470)
    #widgets["assListTitleText"] = cmds.text(l="Asset Lists", font = "boldLabelFont")

    cmds.formLayout(widgets["assListFLO"], e=True, af = [
        (widgets["assListTypeTLO"], "top", 0), 
        (widgets["assListTypeTLO"], "left", 0),
        ])
                
                ##############
                #charStatus layout
                ############### 
    cmds.setParent(widgets["assetFLO"])
    widgets["assetInfoFLO"] = cmds.formLayout("Asset Information", w=270, h=500, bgc= (.5, .5, .5))
    widgets["assetInfoTitleText"] = cmds.text(l="Asset Information", font = "boldLabelFont")
    widgets["assetInfoNameText"] = cmds.text(l="<Asset Name>", font = "boldLabelFont")
    widgets["assetInfoPic"] = cmds.image(image = "{0}/defaultAssetImage.jpg".format(pi.images), w= 154, h=154)
    widgets["assetGeoStatusTF"] = cmds.textFieldGrp(l="GEO STATUS: ", ed=False, cw = [(1, 70), (2, 100)])
    widgets["assetRigStatusTF"] = cmds.textFieldGrp(l="RIG STATUS: ", ed=False, cw = [(1, 70), (2, 100)])
    widgets["assetMtlStatusTF"] = cmds.textFieldGrp(l="MTL STATUS: ", ed=False, cw = [(1, 70), (2, 100)])
    widgets["assetAnnCB"] = cmds.checkBox(l="Tooltips popups?", value=tooltips, changeCommand=tooltipSet)

    cmds.formLayout(widgets["assetInfoFLO"], e=True, af =[
        (widgets["assetInfoNameText"], "top", 60),
        (widgets["assetInfoNameText"], "left", 10),
        (widgets["assetInfoPic"], "top", 100),
        (widgets["assetInfoPic"], "left", 58),
        (widgets["assetGeoStatusTF"], "top", 264),
        (widgets["assetGeoStatusTF"], "left", 10),
        (widgets["assetRigStatusTF"], "top", 284),
        (widgets["assetRigStatusTF"], "left", 10),
        (widgets["assetMtlStatusTF"], "top", 304),
        (widgets["assetMtlStatusTF"], "left", 10),      
        (widgets["assetInfoTitleText"], "top", 5),
        (widgets["assetInfoTitleText"], "left", 80),
        (widgets["assetAnnCB"], "top", 470),
        (widgets["assetAnnCB"], "left", 80),
        ])

                ###############
                #asset geoRig tab layout
                ################
    cmds.setParent(widgets["assetFLO"])
    widgets["geoRigFLO"] = cmds.formLayout(w=300, h=500, bgc = (.4, .4, .4))
    widgets["geoRigTLO"] = cmds.tabLayout(w=300, h=500, bgc = (.3,.3,.3), changeCommand=typeTabChange)
                    ###############
                    #asset geo tab layout
                    ###############
    widgets["geoTabCLO"] = cmds.columnLayout("GEO", w=300, bgc = (.42, .42, .4))
                        #################
                        #geo info frame and column layouts
                        #################                       
    cmds.separator(h=10)
    widgets["geoLastWSTFG"] = cmds.textFieldGrp(l="Latest WS: ", w=300, cw = [(1, 60), (2,230)], cal = [(1,"left"), (2, "left")],ed=False)
    widgets["geoLastMasterTFG"] = cmds.textFieldGrp(l="Master: ", w=300, cw = [(1, 60), (2,230)], cal = [(1,"left"), (2, "left")],ed=False)

    cmds.separator(h=20)
                        #################
                        #geo 'workshop' frame and column layouts
                        #################
    cmds.setParent(widgets["geoTabCLO"])
    widgets["geoWSFLO"] = cmds.frameLayout("Geo Workshop", w=300, h=200, bgc= (.55, .55, .4))
    widgets["geoWSFoLO"] = cmds.formLayout(w=300, h=200, bgc = (.45,.45,.4))

    widgets["geoWSOpenBut"] = cmds.button(l="Open Latest\nGeo Workshop", w=95, h=65, bgc = (.4,.5,.8), en=False, ann=ann["openAssWS"], c=partial(openAssetWorkshop,"geo"))
    widgets["geoWSIncrBut"] = cmds.button(l="Increment Geo Workshop", w=175, h=65, bgc = (.7,.6,.4), ann=ann["incrAssWS"], c=partial(incrementWorkshop, "geo"))
    widgets["geoWSPrevBut"] = cmds.button(l="Previous Geo Workshops", w=175, bgc = (.4,.4,.4), en=False, ann=ann["prevAssWS"])
    widgets["geoWSInfoBut"] = cmds.button(l="WS Info", w=95, bgc = (.7,.7,.7), en=False, ann=ann["WSInfo"]) 

    cmds.formLayout(widgets["geoWSFoLO"], e=True, af = [
        (widgets["geoWSOpenBut"], "left", 5),
        (widgets["geoWSOpenBut"], "top", 10),
        (widgets["geoWSIncrBut"], "left", 110),
        (widgets["geoWSIncrBut"], "top", 10),
        (widgets["geoWSPrevBut"], "left", 110),
        (widgets["geoWSPrevBut"], "top", 85),
        (widgets["geoWSInfoBut"], "left", 5), 
        (widgets["geoWSInfoBut"], "top", 85),  
        ])      
                        #################
                        #geo 'master' frame and column layouts
                        #################
    cmds.setParent(widgets["geoTabCLO"])
    widgets["geoMstFLO"] = cmds.frameLayout("Geo Master", w=300, h=200, bgc= (.55, .55, .4))
    widgets["geoMstFoLO"] = cmds.formLayout(w=300, h=200, bgc = (.45,.45,.4))

    widgets["geoMstOpenBut"] = cmds.button(l="Open\nGeo Master", w=95, h=65, bgc = (.5,.7,.5), en=False, ann=ann["openAssMst"], c=partial(openAssetMaster, "geo"))
    widgets["geoMstIncrBut"] = cmds.button(l="Publish Geo Master", w=175, h=65, bgc = (.7,.5,.5), en=False, ann=ann["pubAssMst"], c=partial(masterAsset, "geo"))
    widgets["geoMstPrevBut"] = cmds.button(l="Previous Geo Masters", w=175, bgc = (.4,.4,.4), en=False, ann=ann["prevAssMst"])
    widgets["geoMstInfoBut"] = cmds.button(l="Mst Info", w=95, bgc = (.7, .7, .7), en=False, ann=ann["MstInfo"])    
    cmds.formLayout(widgets["geoMstFoLO"], e=True, af = [
        (widgets["geoMstOpenBut"], "left", 5),
        (widgets["geoMstOpenBut"], "top", 10),
        (widgets["geoMstIncrBut"], "left", 110),
        (widgets["geoMstIncrBut"], "top", 10),
        (widgets["geoMstPrevBut"], "left", 110),
        (widgets["geoMstPrevBut"], "top", 85),
        (widgets["geoMstInfoBut"], "left", 5), 
        (widgets["geoMstInfoBut"], "top", 85),          
        ])      
                    ################
                    #asset rig tab layout
                    ################    
    cmds.setParent(widgets["geoRigTLO"])                
    widgets["rigTabCLO"] = cmds.columnLayout("RIG", w=300, bgc = (.38,.4,.42))
                        #################
                        #rig info frame and column layouts
                        #################                       
    cmds.separator(h=10)
    widgets["rigLastWSTFG"] = cmds.textFieldGrp(l="Latest WS: ", w=300, cw = [(1, 60), (2,230)], cal = [(1,"left"), (2, "left")],ed=False)
    widgets["rigLastMasterTFG"] = cmds.textFieldGrp(l="Master: ", w=300, cw = [(1, 60), (2,230)], cal = [(1,"left"), (2, "left")],ed=False)
    cmds.separator(h=20)
                        #################
                        #rig 'workshop' frame and column layouts
                        #################
    cmds.setParent(widgets["rigTabCLO"])
    widgets["rigWSFLO"] = cmds.frameLayout("Rig Workshop", w=300, h=200, bgc= (.3, .35, .5))
    widgets["rigWSFoLO"] = cmds.formLayout(w=300, h=200, bgc = (.35,.4,.45))

    widgets["rigWSOpenBut"] = cmds.button(l="Open Latest\nRig Workshop", w=95, h=65, bgc = (.7,.5,.7), en=False, ann=ann["openAssWS"], c=partial(openAssetWorkshop, "rig"))
    widgets["rigWSIncrBut"] = cmds.button(l="Increment Rig Workshop", w=175, h=65, bgc = (.5,.7,.5), en=False, ann=ann["incrAssWS"], c=partial(incrementWorkshop, "rig"))
    widgets["rigWSPrevBut"] = cmds.button(l="Previous Rig Workshops", w=175, bgc = (.7,.7,.7), en=False, ann=ann["prevAssWS"])  
    widgets["rigWSInfoBut"] = cmds.button(l="WS Info", w=95, bgc = (.5,.5,.5), en=False, ann=ann["WSInfo"]) 

    cmds.formLayout(widgets["rigWSFoLO"], e=True, af = [
        (widgets["rigWSOpenBut"], "left", 5),
        (widgets["rigWSOpenBut"], "top", 10),
        (widgets["rigWSIncrBut"], "left", 110),
        (widgets["rigWSIncrBut"], "top", 10),
        (widgets["rigWSPrevBut"], "left", 110),
        (widgets["rigWSPrevBut"], "top", 85),
        (widgets["rigWSInfoBut"], "left", 5), 
        (widgets["rigWSInfoBut"], "top", 85),       
        ])  
                        #################
                        #rig 'master' frame and column layouts
                        #################
    cmds.setParent(widgets["rigTabCLO"])
    widgets["rigMstFLO"] = cmds.frameLayout("Rig Master", w=300, h=200, bgc= (.3, .35, .5))
    widgets["rigMstFoLO"] = cmds.formLayout(w=300, h=200, bgc = (.35,.4,.45))

    widgets["rigMstOpenBut"] = cmds.button(l="Open\nRig Master", w=95, h=65, bgc = (.7,.7,.4), en=False, ann=ann["openAssMst"], c=partial(openAssetMaster, "rig"))
    widgets["rigMstIncrBut"] = cmds.button(l="Publish Rig Master", w=175, h=65, bgc = (.7,.5,.5), en=False, ann=ann["pubAssMst"], c=partial(masterAsset, "rig"))
    widgets["rigMstPrevBut"] = cmds.button(l="Previous Rig Masters", w=175, bgc = (.4,.4,.4), en=False, ann=ann["prevAssMst"])
    widgets["rigMstInfoBut"] = cmds.button(l="Mst Info", w=95, bgc = (.5,.5,.5), en=False, ann=ann["MstInfo"])          
    cmds.formLayout(widgets["rigMstFoLO"], e=True, af = [
        (widgets["rigMstOpenBut"], "left", 5),
        (widgets["rigMstOpenBut"], "top", 10),
        (widgets["rigMstIncrBut"], "left", 110),
        (widgets["rigMstIncrBut"], "top", 10),
        (widgets["rigMstPrevBut"], "left", 110),
        (widgets["rigMstPrevBut"], "top", 85), 
        (widgets["rigMstInfoBut"], "left", 5), 
        (widgets["rigMstInfoBut"], "top", 85)       
        ])  

    cmds.setParent(widgets["geoRigFLO"])
    widgets["geoRigTitleText"] = cmds.text(l="Asset Files", font = "boldLabelFont") 

    cmds.formLayout(widgets["geoRigFLO"], e=True, af = [(widgets["geoRigTitleText"], "top", 5), (widgets["geoRigTitleText"], "left", 150)])

            #########
            # mtl tab
            ##########
    cmds.setParent(widgets["geoRigTLO"])                
    widgets["mtlTabCLO"] = cmds.columnLayout("MTL", w=300, bgc = (.45,.48,.45))
    # open shaderman - what do we have to change to make this work in the new framework
                        #################
                        # mtl info frame and column layouts
                        #################                       
    cmds.separator(h=10)
    widgets["mtlLastWSTFG"] = cmds.textFieldGrp(l="Latest WS: ", w=300, cw = [(1, 60), (2,230)], cal = [(1,"left"), (2, "left")],ed=False)
    widgets["mtlLastMasterTFG"] = cmds.textFieldGrp(l="Master: ", w=300, cw = [(1, 60), (2,230)], cal = [(1,"left"), (2, "left")],ed=False)

    cmds.separator(h=20)

    cmds.setParent(widgets["mtlTabCLO"])
    widgets["mtlWSFLO"] = cmds.frameLayout("mtl Workshop", w=300, h=220, bgc= (.3, .5, .3))
    widgets["mtlWSFoLO"] = cmds.formLayout(w=300, h=250, bgc = (.45,.5,.45))

    widgets["mtlCreateBut"] = cmds.button(l="Create new mtl Workshop", w=280, h=25, bgc = (.8,.8,.5), en=False) 
    widgets["mtlWSOpenBut"] = cmds.button(l="Open Latest\nmtl Workshop", w=95, h=65, bgc = (.4,.5,.8), en=False, ann=ann["openAssWS"], c=partial(openAssetWorkshop, "mtl"))
    widgets["mtlWSIncrBut"] = cmds.button(l="Increment mtl Workshop", w=175, h=65, bgc = (.7,.6,.9), en=False, ann=ann["incrAssWS"], c=partial(incrementWorkshop, "mtl"))
    widgets["mtlWSPrevBut"] = cmds.button(l="Previous mtl Workshops", w=175, bgc = (.7,.7,.7), en=False, ann=ann["prevAssWS"])  
    widgets["mtlWSInfoBut"] = cmds.button(l="WS Info", w=95, bgc = (.5,.5,.5), en=False, ann=ann["WSInfo"])
    widgets["mtlInfoBut"] = cmds.button(l="Material info panel", w=280, h=25, bgc = (.5,.5,.5), en=False)   


    cmds.formLayout(widgets["mtlWSFoLO"], e=True, af = [
        (widgets["mtlCreateBut"], "left", 5),
        (widgets["mtlCreateBut"], "top", 10),
        (widgets["mtlWSOpenBut"], "left", 5),
        (widgets["mtlWSOpenBut"], "top", 45),
        (widgets["mtlWSIncrBut"], "left", 110),
        (widgets["mtlWSIncrBut"], "top", 45),
        (widgets["mtlWSPrevBut"], "left", 110),
        (widgets["mtlWSPrevBut"], "top", 120),
        (widgets["mtlWSInfoBut"], "left", 5), 
        (widgets["mtlWSInfoBut"], "top", 120),
        (widgets["mtlInfoBut"], "left", 5), 
        (widgets["mtlInfoBut"], "top", 160),                
        ])  

                        #################
                        #mtl 'master' frame and column layouts
                        #################
    cmds.setParent(widgets["mtlTabCLO"])
    widgets["mtlMstFLO"] = cmds.frameLayout("mtl Master", w=300, h=200, bgc= (.3, .5, .3))
    widgets["mtlMstFoLO"] = cmds.formLayout(w=300, h=200, bgc = (.45,.5,.45))

    widgets["mtlMstOpenBut"] = cmds.button(l="Open\nmtl Master", w=95, h=65, bgc = (.5,.7,.5), en=False, ann=ann["openAssMst"], c=partial(openAssetMaster, "mtl"))
    widgets["mtlMstIncrBut"] = cmds.button(l="Publish mtl Master", w=175, h=65, bgc = (.7,.5,.5), en=False, ann=ann["pubAssMst"], c=partial(masterAsset, "mtl"))
    widgets["mtlMstPrevBut"] = cmds.button(l="Previous mtl Masters", w=175, bgc = (.4,.4,.4), en=False, ann=ann["prevAssMst"])
    widgets["mtlMstInfoBut"] = cmds.button(l="Mst Info", w=95, bgc = (.5,.5,.5), en=False, ann=ann["MstInfo"])          
    cmds.formLayout(widgets["mtlMstFoLO"], e=True, af = [
        (widgets["mtlMstOpenBut"], "left", 5),
        (widgets["mtlMstOpenBut"], "top", 10),
        (widgets["mtlMstIncrBut"], "left", 110),
        (widgets["mtlMstIncrBut"], "top", 10),
        (widgets["mtlMstPrevBut"], "left", 110),
        (widgets["mtlMstPrevBut"], "top", 85), 
        (widgets["mtlMstInfoBut"], "left", 5), 
        (widgets["mtlMstInfoBut"], "top", 85)       
        ])  

########################################### 
                ###############
                #asset Action layout
                ################
    cmds.setParent(widgets["assetFLO"])
    widgets["assActionFLO"] = cmds.formLayout(w=150, h=500, bgc =(.5, .5, .5))
    widgets["assActionIconBut"] = cmds.button(l="Create Asset Icon", w=130, h=20, bgc = (.7,.7,.7), c=createAssetIcon, ann=ann["crtIcon"])
    widgets["assActionImpBut"] = cmds.button(l="Import External", w=130, h=20, bgc = (.7,.7,.7), c=importExternal, ann=ann["import"])
    widgets["assActionRefInBut"] = cmds.button(l="Reference External", w=130, h=20, bgc = (.7,.7,.7), c=refExternal, ann=ann["reference"])
    # widgets["assActionRefGeoBut"] = cmds.button(l="Reference Geo Master", w=130, h=20, bgc = (.7,.7,.7), c=refGeo, ann=ann["refGeo"])
    widgets["assActionQuickIncr"] = cmds.button(l="Quick Increment", w=130, h=20, bgc = (.7, .7, .7), c=quickIncrement, ann=ann["qkIncr"])  

    widgets["assActionNewAsset"] = cmds.button(l="Create New Asset", w=130, h=20, bgc = (.7, .7, .7), c=createAsset, ann=ann["crtAsset"])
    widgets["assActionDuplBut"] = cmds.button(l="Duplicate Asset", en=True, w=130, h=20, bgc = (.7,.7,.7), c=duplicateAsset, ann=ann["dupeAsset"])
    widgets["assActionArchBut"] = cmds.button(l="Archive Asset", w=130, h=20, bgc = (.7,.7,.7), c=archiveAsset, ann=ann["archive"])
    widgets["assActionUnArchBut"] = cmds.button(l="Unarchive Asset", w=130, h=20, bgc = (.7,.7,.7), c = unarchiveAssets, ann=ann["unarchive"])
    widgets["assActionTitle"] = cmds.text(l="Asset Actions", font = "boldLabelFont")

    widgets["assActionTypeTLO"] = cmds.tabLayout(w=150, h=200, bgc=(.2, .2, .2))

    widgets["assActionGeoSLO"] = cmds.scrollLayout("GEO", w=150, h=240, verticalScrollBarThickness=5)    
    widgets["assActionGeoFLO"] = cmds.formLayout("GEO", w=150, h=240, bgc= (.45,.45,.4))
    widgets["assActionGeoXferBut"] = cmds.button(l="transferShadersAndUV", w=130, h=20, en=True, bgc = (.7, .7,.7), c=shaderUVTransfer, ann=ann["xferUV"])
    widgets["assActionGeoPushBut"] = cmds.button(l="Push rig master", w=130, h=20, en=False, bgc = (.7, .7,.7), c=pushGeoRig, ann=ann["pushRig"])    

    cmds.formLayout(widgets["assActionGeoFLO"], e=True, af=[
        (widgets["assActionGeoXferBut"], "top", 5),
        (widgets["assActionGeoXferBut"], "left", 2),
        (widgets["assActionGeoPushBut"], "top", 35),
        (widgets["assActionGeoPushBut"], "left", 2)        
        ]) 

    cmds.setParent(widgets["assActionTypeTLO"])
    widgets["assActionRigSLO"] = cmds.scrollLayout("RIG", w=150, h=240, verticalScrollBarThickness=5)    
    widgets["assActionRigFLO"] = cmds.formLayout(w=150, h=240, bgc = (.35,.4,.45))
    widgets["assActionRigRefGeoBut"] = cmds.button(l="Reference Geo Master", w=130, h=20, bgc = (.7,.7,.7), c=refGeo, ann=ann["refGeo"])
    widgets["assActionRigDupeGeoBut"] = cmds.button(l="Duplicate Ref Geo", w=130, h=20, en=True, bgc = (.7,.7,.7), c=dupeReffed, ann=ann["dupeRef"])
    widgets["assActionRigCpSkBut"] = cmds.button(l="Copy skin weights", w=130, h=20, en=True, bgc = (.7,.7,.7), c=copySkin, ann=ann["cpSkin"])
    widgets["assActionRigXferBut"] = cmds.button(l="transferShadersAndUV", w=130, h=20, en=True, bgc = (.7, .7,.7), c=shaderUVTransfer, ann=ann["xferUV"])
    
    cmds.formLayout(widgets["assActionRigFLO"], e=True, af=[
        (widgets["assActionRigRefGeoBut"], "top", 5),
        (widgets["assActionRigRefGeoBut"], "left", 2),
        (widgets["assActionRigDupeGeoBut"], "top", 35),
        (widgets["assActionRigDupeGeoBut"], "left", 2),
        (widgets["assActionRigCpSkBut"], "top", 65),
        (widgets["assActionRigCpSkBut"], "left", 2),
        (widgets["assActionRigXferBut"], "top", 95),
        (widgets["assActionRigXferBut"], "left", 2),        
        ]) 

    cmds.setParent(widgets["assActionTypeTLO"])
    widgets["assActionMtlSLO"] = cmds.scrollLayout("MTL", w=150, h=240, verticalScrollBarThickness=5)    
    widgets["assActionMtlFLO"] = cmds.formLayout(w=150, h=240, bgc = (.45,.5,.45))
    widgets["assActionMtlXferUVBut"] = cmds.button(l="transferShadersAndUV", w=130, h=20, en=True, bgc=(.7, .7,.7), c=shaderUVTransfer, ann=ann["xferUV"])
    
    cmds.formLayout(widgets["assActionMtlFLO"], e=True, af=[
        (widgets["assActionMtlXferUVBut"], "top", 5),
        (widgets["assActionMtlXferUVBut"], "left", 2)
        ]) 

    cmds.formLayout(widgets["assActionFLO"], e=True, af = [
        (widgets["assActionIconBut"], "top", 40),
        (widgets["assActionIconBut"], "left", 10),
        (widgets["assActionRefInBut"], "top", 70),
        (widgets["assActionRefInBut"], "left", 10),
        (widgets["assActionImpBut"], "top", 100),
        (widgets["assActionImpBut"], "left", 10),
        (widgets["assActionQuickIncr"], "top", 130),
        (widgets["assActionTypeTLO"], "top", 160),
        (widgets["assActionTypeTLO"], "left", 0),
        (widgets["assActionQuickIncr"], "left", 10),        
        (widgets["assActionNewAsset"], "top", 370),
        (widgets["assActionNewAsset"], "left", 10),
        (widgets["assActionDuplBut"], "top", 400),
        (widgets["assActionDuplBut"], "left", 10),
        (widgets["assActionArchBut"], "top", 430),
        (widgets["assActionArchBut"], "left", 10),
        (widgets["assActionUnArchBut"], "top", 460),
        (widgets["assActionUnArchBut"], "left", 10),
        (widgets["assActionTitle"], "top", 5),
        (widgets["assActionTitle"], "left", 35)
        ])

            ###################
            # asset Tab form setup
            ##################
    cmds.formLayout(widgets["assetFLO"], e=True, af = [
        (widgets["assListCLO"], "left", 0),
        (widgets["assListCLO"], "top", 0),
        (widgets["assetInfoFLO"], "top", 0),
        (widgets["assetInfoFLO"], "left", 730),
        (widgets["geoRigFLO"], "top", 0),
        (widgets["geoRigFLO"], "left", 250),
        (widgets["assActionFLO"], "top", 0),
        (widgets["assActionFLO"], "left", 563),
        ])


            ################
            #Misc tab
            ################
    cmds.setParent(widgets["lowTLO"])
    widgets["miscFLO"] = cmds.formLayout("Other Asset Tools",width=1000, height=500, backgroundColor = (.4,.4,.4))

    widgets["modelingTLO"] = cmds.tabLayout(width=500, height=250, backgroundColor = (.35, .35, .3))
    widgets["modelingSLO"] = cmds.scrollLayout("modeling", w=500, h=250)
    widgets["modelingRCLO"] = cmds.rowColumnLayout("modeling", numberOfColumns=3, columnSpacing=[(1, 0), (2,5), (3,5)], rowSpacing=[1,5])

    cmds.setParent(widgets["miscFLO"])
    widgets["riggingTLO"] = cmds.tabLayout(width=500, height=250, backgroundColor = (.3, .32, .35))
    widgets["riggingSLO"] = cmds.scrollLayout("rigging", w=500, h=250)    
    widgets["riggingRCLO"] = cmds.rowColumnLayout("rigging", numberOfColumns=3, columnSpacing=[(1, 0), (2,5), (3,5)], rowSpacing=[1,5])    

    cmds.setParent(widgets["miscFLO"])
    widgets["shadingTLO"] = cmds.tabLayout(width=500, height=250, backgroundColor = (.3, .35, .3))
    widgets["shadingSLO"] = cmds.scrollLayout("shading", w=500, h=250)    
    widgets["shadingRCLO"] = cmds.rowColumnLayout("shading", numberOfColumns=3, columnSpacing=[(1, 0), (2,5), (3,5)], rowSpacing=[1,5])

    cmds.setParent(widgets["miscFLO"])
    widgets["charlexTLO"] = cmds.tabLayout(width=500, height=250, backgroundColor = (.55, .55, .55))
    widgets["charlexSLO"] = cmds.scrollLayout("charlex", w=500, h=250)    
    widgets["charlexRCLO"] = cmds.rowColumnLayout("charlex_general", numberOfColumns=3, columnSpacing=[(1, 0), (2,5), (3,5)], rowSpacing=[1,5])

    cmds.formLayout(widgets["miscFLO"], e=True, af=[
        (widgets["charlexTLO"], "top", 0),
        (widgets["charlexTLO"], "left", 0),
        (widgets["modelingTLO"], "top", 0),
        (widgets["modelingTLO"], "left", 500),
        (widgets["riggingTLO"], "top", 250),
        (widgets["riggingTLO"], "left", 0),
        (widgets["shadingTLO"], "top", 250),
        (widgets["shadingTLO"], "left", 500)          
        ])

    # get the dictionary of scripts, calls and annotations from the database
    dbPath =os.path.join(os.getenv("MAYA_ROOT"), "scripts", "chrlx_pipe", "chrlxScriptList.json")
    with open(dbPath, "r") as f:
        scriptList = json.load(f)

    # populate the row column layouts with buttons and funcs from the database
    btl.buttonsToLayout(widgets["modelingRCLO"], scriptList["asset"]["modeling"], width=158, height=40, color=(.38, .3, .38))
    btl.buttonsToLayout(widgets["riggingRCLO"], scriptList["asset"]["rigging"], width=158, height=40, color=(.37,.34, .3))
    btl.buttonsToLayout(widgets["shadingRCLO"], scriptList["asset"]["shading"], width=158, height=40, color=(.35, .3, .3))
    btl.buttonsToLayout(widgets["charlexRCLO"], scriptList["asset"]["charlex"], width=158, height=40, color=(.3, .3, .3))

#---------------- scripts to add. . . extractDeltas, 

    #widgets["modelFLO"] = cmds.formLayout(w=1000, h=500, bgc=(.4, 4.,.4))
    # cmds.text(l="TODO - export data (text file of scene locations?)")
    # cmds.text(l="TODO - backup (backlot) assets in job to another location (latest ws, mst and images)")
    # cmds.text(l="TODO - import asset from backlot (paul's 'move char')")
    # cmds.text(l="-------model stuff --------")
    # cmds.text(l="TODO - modeling toolkit")    
    # cmds.text(l="TODO - convert an external image to icon (char or project)")
    # cmds.text(l="------rig stuff-----------")
    # cmds.text(l="TODO - rig toolkit")
    # cmds.text(l="TODO - revert ['ROLL BACK'] to master version? (replaces master and grabs that workshop")
    # cmds.text(l="TODO - function to add your folder to the WIP folder in this project - save current to WIP folder")
    # cmds.text(l="TODO - some kind of shader assignment export?")
    # cmds.text(l="TODO - reference in geo button (should pull latest rig master only)")
    # cmds.text(l="TODO - dupe reffed geo for skinning. . . ")
    # cmds.text(l="TODO - PHOTO OF JOB/SPOT")

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
    updateSceneName()
    clearAll()

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
        print "loading proj into AssetWin UI!"
        # print "pi.currentProject = {0}".format(pi.currentProject)
        # print "pi.openScene = {0}".format(pi.openScene)
        # print "pi.job = {0}".format(pi.job)
        # print "pi.spot = {0}".format(pi.spot)
        # print "pi.assetFolder = {0}".format(pi.assetFolder)
        # print "pi.charFold = {0}".format(pi.charFolder)
        # print "pi.propFold = {0}".format(pi.propFolder)
        # print "pi.setFold = {0}".format(pi.setFolder)
        # print "pi.shotsFold = {0}".format(pi.shotsFolder)
        print "--------------------------"

        #get assets and populate list
        if projJob:
            populateAssets(pi.assetFolder)

    else: 
        cmds.warning("Doesn't seem like you're in project")

    pm = utils.PathManager(pi.currentProject)
    if pm.spotSchema == 2:
        jobImage = cFuncs.fixPath(os.path.join(pm.jobPath, "3D_assets", "jobIcon.jpg"))
        if os.path.isfile(jobImage):
            cmds.iconTextButton(widgets["jobImage"], e=True, image=jobImage)

def populateAssets(assetFolder, *args):
    """
    assetFolder is current assetFolder path (at the job level, not the spot level)
    searches out the char, prop and set asset folders and populates the asset lists
    """
    #projectCheck()
    assExclude = ["geo", "rig", "_NotInUse"]

    clearAll()

    charList, propList, setList = cFuncs.getProjectAssetList(assetFolder) #this should return (chars, props, sets)
    lists = [charList, propList, setList]
    TSLs = [widgets["assCharListTSL"], widgets["assPropListTSL"], widgets["assSetListTSL"]]
    
    for x in range(0, 3):
        if lists[x]:
            for ass in lists[x]:
                #only use if not in exclude list or doesn't start with a dot
                if (ass not in assExclude) and (ass[0] != "."):
                    cmds.textScrollList(TSLs[x], e=True, a=ass, sc=updateAssetInfo, dcc=openAssetFolder)

    #if current open scene lines up with asset that exists, select that asset in the list and go to appr tab
    f=cmds.file(q=True, sn=True)
    a = os.path.basename(f)
    aname = a.partition("_")[0]
    typeTab = "GEO"
    if "_geo" in a:
        typeTab = "GEO"
    elif "_rig" in a:
        typeTab = "RIG"
    elif "_mtl" in a:
        typeTab = "MTL"

    found = False
    tabSl = 0
    for y in range(0,3):
        if aname in lists[y]:
            cmds.textScrollList(TSLs[y], e=True, selectItem=aname)
            found = True
            tabSl = y
    if tabSl ==0:
        tab = "Chars"
    elif tabSl == 1:
        tab = "Props"
    elif tabSl == 2:
        tab = "Sets"

    cmds.tabLayout(widgets["assListTypeTLO"], e=True, st=tab)
    cmds.tabLayout(widgets["geoRigTLO"], e=True, st=typeTab)
    if found:
        updateAssetInfo()


def openAssetFolder(*args):
    # get open tab
    openTab = cmds.tabLayout(widgets["assListTypeTLO"], q=True, st=True)
    tsl=""
    typ=""
    if openTab == "Chars":
        tsl = "assCharListTSL"
        typ = "characters"
    if openTab == "Props":
        tsl = "assPropListTSL"
        typ = "props"
    if openTab == "Sets":
        tsl = "assSetListTSL"
        typ = "sets"
    # get selected item in that TSL
    print tsl, typ
    assetList = cmds.textScrollList(widgets[tsl], q=True, si=True)
    asset = assetList[0]
    # get the path to that asset folder
    path = cFuncs.fixPath(os.path.join(pi.assetFolder, typ, asset))
    cFuncs.openFolderInExplorer(path)


def exploreReference(*args):
    #just open the file browser to this folder
    if pi.spotRefFolder:
        cFuncs.openFolderInExplorer(pi.spotRefFolder)
    else:
        cmds.warning("I can't tell what project we're in right now!")


def updateAssetInfo(asset = "", *args):
    """updates information in the window based on selected asset from the list"""
    #get selected tab
    sTab = cmds.tabLayout(widgets['assListTypeTLO'], q=True, st=True) #st = selected tab
    tabs = ["Chars", "Props", "Sets"]
    lists = [widgets["assCharListTSL"], widgets["assPropListTSL"], widgets["assSetListTSL"]]
    # deselect all (from other two lists (tabs))
    for x in range(0, len(tabs)):
        if tabs[x] != sTab:
            cmds.textScrollList(lists[x], e=True, deselectAll=True) 
    
    # if no asset passed in (this would be from an external call?)
    if not asset:
        try:
            if sTab == "Chars":
                asset = cmds.textScrollList(widgets["assCharListTSL"], q=True, si=True)[0]
                pi.currentAssetFolder = "{0}/{1}".format(pi.charFolder, asset)
            elif sTab == "Props":
                asset = cmds.textScrollList(widgets["assPropListTSL"], q=True, si=True)[0]
                pi.currentAssetFolder = "{0}/{1}".format(pi.propFolder, asset)
            elif sTab == "Sets":
                asset = cmds.textScrollList(widgets["assSetListTSL"], q=True, si=True)[0]
                pi.currentAssetFolder = "{0}/{1}".format(pi.setFolder, asset)

            pi.currentAsset = asset
            pi.currentGeoFolder = "{0}/geo".format(pi.currentAssetFolder)
            pi.currentRigFolder = "{0}/rig".format(pi.currentAssetFolder)
            pi.currentMtlFolder = "{0}/mtl".format(pi.currentAssetFolder)

        except:
            cmds.warning("chrlxassetWin.updateAssetInfo: Couldn't access the list information. Possibly nothing selected. . .")

    if asset:
        #update statuses: pass getLatestWS last arg---> "geo", "rig" ,gets full path to these ws, master files
        cmds.text(widgets["assetInfoNameText"], e=True, l=asset)

        #geo
        geoWS = cFuncs.getLatestAssetWS(asset, pi.currentAssetFolder, "geo")

        if geoWS:
            cmds.textFieldGrp(widgets["assetGeoStatusTF"], e=True, tx = "WORKSHOPPED")
            cmds.textFieldGrp(widgets["geoLastWSTFG"], e=True, tx = os.path.basename(geoWS))
            pi.currentAssetGeoWS = geoWS
            cmds.button(widgets["geoWSPrevBut"], e=True, en=True, c=partial(explorePreviousWS, "geo"))
            cmds.button(widgets["geoWSInfoBut"], e=True, en=True, c=partial(fileInfoWin, pi.currentAssetGeoWS))
            cmds.button(widgets["geoWSOpenBut"], e=True, en=True)
            cmds.button(widgets["geoWSIncrBut"], e=True, en=True)
            cmds.button(widgets["geoMstIncrBut"], e=True, en=True)              
        else:
            cmds.textFieldGrp(widgets["assetGeoStatusTF"], e=True, tx = "-")
            cmds.textFieldGrp(widgets["geoLastWSTFG"], e=True, tx= "-")
            pi.currentAssetGeoWS = ""           
            cmds.button(widgets["geoWSPrevBut"], e=True, en=False)
            cmds.button(widgets["geoWSInfoBut"], e=True, en=False)
            cmds.button(widgets["geoWSOpenBut"], e=True, en=False)
            cmds.button(widgets["geoWSIncrBut"], e=True, en=True)
            cmds.button(widgets["geoMstIncrBut"], e=True, en=False)         

        geoMaster = cFuncs.getAssetMaster(asset, pi.currentAssetFolder, "geo")
        if geoMaster:
            cmds.textFieldGrp(widgets["assetGeoStatusTF"], e=True, tx = "MASTERED")
            cmds.textFieldGrp(widgets["geoLastMasterTFG"], e=True, tx = os.path.basename(geoMaster))
            pi.currentAssetGeoMaster = geoMaster
            cmds.button(widgets["geoMstPrevBut"], e=True, en=True, c=partial(explorePreviousMstr, "geo"))
            cmds.button(widgets["geoMstInfoBut"], e=True, en=True, c=partial(fileInfoWin, pi.currentAssetGeoMaster) )
            cmds.button(widgets["geoMstOpenBut"], e=True, en=True)
            cmds.button(widgets["geoMstIncrBut"], e=True, en=True)              
        else:
            cmds.textFieldGrp(widgets["assetGeoStatusTF"], e=True, tx = "-")
            cmds.textFieldGrp(widgets["geoLastMasterTFG"], e=True, tx = "-")
            pi.currentAssetGeoMaster = ""
            cmds.button(widgets["geoMstPrevBut"], e=True, en=False)
            cmds.button(widgets["geoMstInfoBut"], e=True, en=False)
            cmds.button(widgets["geoMstOpenBut"], e=True, en=False)

        #rig
        rigWS = cFuncs.getLatestAssetWS((asset), pi.currentAssetFolder, "rig")
        if rigWS:
            cmds.textFieldGrp(widgets["assetRigStatusTF"], e=True, tx = "WORKSHOPPED")
            cmds.textFieldGrp(widgets["rigLastWSTFG"], e=True, tx = os.path.basename(rigWS))
            pi.currentAssetRigWS = rigWS
            cmds.button(widgets["rigWSOpenBut"], e=True, en=True)
            cmds.button(widgets["rigWSIncrBut"], e=True, en=True)
            cmds.button(widgets["rigWSPrevBut"], e=True, en=True, c=partial(explorePreviousWS, "rig"))
            cmds.button(widgets["rigWSInfoBut"], e=True, en=True, c=partial(fileInfoWin, pi.currentAssetRigWS))
            cmds.button(widgets["rigMstIncrBut"], e=True, en=True)              
        else:
            cmds.textFieldGrp(widgets["assetRigStatusTF"], e=True, tx = "-")
            cmds.textFieldGrp(widgets["rigLastWSTFG"], e=True, tx= "-")
            pi.currentAssetRigWS = ""
            cmds.button(widgets["rigWSOpenBut"], e=True, en=False)
            cmds.button(widgets["rigWSIncrBut"], e=True, en=False)          
            cmds.button(widgets["rigWSPrevBut"], e=True, en=False)
            cmds.button(widgets["rigWSInfoBut"], e=True, en=False)
            cmds.button(widgets["rigMstIncrBut"], e=True, en=False)

        rigMaster = cFuncs.getAssetMaster(asset, pi.currentAssetFolder, "rig")
        if rigMaster:
            cmds.textFieldGrp(widgets["assetRigStatusTF"], e=True, tx = "MASTERED")
            cmds.textFieldGrp(widgets["rigLastMasterTFG"], e=True, tx = os.path.basename(rigMaster))
            pi.currentAssetRigMaster = rigMaster
            cmds.button(widgets["rigMstPrevBut"], e=True, en=True, c=partial(explorePreviousMstr, "rig"))
            cmds.button(widgets["rigMstInfoBut"], e=True, en=True, c=partial(fileInfoWin, pi.currentAssetGeoMaster))
            cmds.button(widgets["rigMstOpenBut"], e=True, en=True)
            cmds.button(widgets["rigMstIncrBut"], e=True, en=True)          
        else:
            cmds.textFieldGrp(widgets["assetRigStatusTF"], e=True, tx = "-")
            cmds.textFieldGrp(widgets["rigLastMasterTFG"], e=True, tx = "-")
            pi.currentAssetRigMaster = ""
            cmds.button(widgets["rigMstPrevBut"], e=True, en=False) 
            cmds.button(widgets["rigMstInfoBut"], e=True, en=False)
            cmds.button(widgets["rigMstOpenBut"], e=True, en=False)

        mtlWS = cFuncs.getLatestAssetWS(asset, pi.currentAssetFolder, "mtl")
        if mtlWS:
            cmds.textFieldGrp(widgets["assetMtlStatusTF"], e=True, tx = "WORKSHOPPED")
            cmds.textFieldGrp(widgets["mtlLastWSTFG"], e=True, tx = os.path.basename(rigWS))
            pi.currentAssetMtlWS = mtlWS
            cmds.button(widgets["mtlWSOpenBut"], e=True, en=True)
            cmds.button(widgets["mtlWSIncrBut"], e=True, en=True)
            cmds.button(widgets["mtlWSPrevBut"], e=True, en=True, c=partial(explorePreviousWS, "mtl"))
            cmds.button(widgets["mtlWSInfoBut"], e=True, en=True, c=partial(fileInfoWin, pi.currentAssetMtlWS))
            cmds.button(widgets["mtlMstIncrBut"], e=True, en=True)              
        else:
            cmds.textFieldGrp(widgets["assetMtlStatusTF"], e=True, tx = "-")
            cmds.textFieldGrp(widgets["mtlLastWSTFG"], e=True, tx= "-")
            pi.currentAssetMtlWS = ""
            cmds.button(widgets["mtlWSOpenBut"], e=True, en=False)
            cmds.button(widgets["mtlWSIncrBut"], e=True, en=False)          
            cmds.button(widgets["mtlWSPrevBut"], e=True, en=False)
            cmds.button(widgets["mtlWSInfoBut"], e=True, en=False)
            cmds.button(widgets["mtlMstIncrBut"], e=True, en=False)

        #upate pic
        iconDir = "{0}/icon".format(pi.currentAssetFolder)
        pic1 = "{0}Icon.png".format(asset)
        pic2 = "{0}Icon.xpm".format(asset)

        if pic1 in (os.listdir(iconDir)):
            cmds.image(widgets["assetInfoPic"], e=True, image = "{0}/{1}".format(iconDir, pic1))
        elif pic2 in (os.listdir(iconDir)):
            cmds.image(widgets["assetInfoPic"], e=True, image = "{0}/{1}".format(iconDir, pic2))
        else:
            cmds.image(widgets["assetInfoPic"], e=True, image = "{0}/defaultAssetImage.jpg".format(pi.images))
    else: #if there was no asset
        cmds.warning("chrlxassetWin.updateAssetInfo: There is no asset name passed to me")

def explorePreviousWS(fType, *args):
    """just pushes the path for the folder to the funcs to open that"""
    path = ""
    if fType == "geo":
        path = pi.currentGeoFolder + "/workshops"
    elif fType == "rig":
        path = pi.currentRigFolder + "/workshops"
    elif fType == "mtl":
        path = pi.currentMtlFolder + "/workshops"
    if path:
        cFuncs.openFolderInExplorer(path)


def typeTabChange(*args):
    """
    just changes the action button tab to match the shot type tab selection
    """
    tab = cmds.tabLayout(widgets["geoRigTLO"], q=True, st=True)
    if tab == "GEO":
        cmds.tabLayout(widgets["assActionTypeTLO"], e=True, st="GEO")
    if tab == "RIG":
        cmds.tabLayout(widgets["assActionTypeTLO"], e=True, st="RIG")
    if tab == "MTL":
        cmds.tabLayout(widgets["assActionTypeTLO"], e=True, st="MTL")

def fileInfoWin(filePath, *args):
    """calls module to bring up file win for filePath arg"""
    fileInfo.fileInfo(filePath)


def explorePreviousMstr(fType, *args):
    """just pushes the path for the folder to the funcs to open that"""
    path = ""
    if fType == "geo":
        path = pi.currentGeoFolder + "/past_versions"
    elif fType == "rig":
        path = pi.currentRigFolder + "/past_versions"
    elif fType == "mtl":
        path = pi.currentMtlFolder + "/past_versions"   
    if path:
        cFuncs.openFolderInExplorer(path)


############
# Set Project in Win
############    

def setProject(*args):
    setProj = ""
    setProj = projectSetter.ProjectSetter(True)
    populateWindow()


############
# Open Workshop and master files
############
def openAssetWorkshop(ftype, *args):
    if pi.currentAsset:
        if ftype == "geo":
            wsFile = pi.currentAssetGeoWS
        elif ftype == "rig":
            wsFile = pi.currentAssetRigWS
        elif ftype == "mtl":
            wsFile = pi.currentAssetMtlWS

        #if there's a file in the variable
        if wsFile:
            # #check if it's changed (need to save)
            # changed = cmds.file(q=True, modified = True)
            # if changed:
            #     save = cmds.confirmDialog(t="Save Scene", m="Save the current scene?", b=("Yes", "No", "Cancel"), cb="Yes", db="Cancel", ds="Cancel")
            #     if save=="Yes":
            #         #save
            #         cmds.file(save=True)
            #         print "saving current. . . "
            #         #then open
            #         cFuncs.chrlxFileOpen(wsFile)
            #         updateSceneName()
            #     elif save=="No":
            #         cFuncs.chrlxFileOpen(wsFile)
            #         updateSceneName()
            #     elif save=="cancel":
            #         cmds.warning("Cancelling open operation")
            #if it's not changed, just open
            # else:
            cFuncs.chrlxFileOpen(wsFile)
            updateSceneName()
        #if there's no file in the variable, but the asset is selected, then GO TO CREATE FILE PATH
        else:
            print "assetWin.openAssetWorkshop: THERE IS NO FILE!"
    else:
        cmds.warning("assetWin.openAssetWorkshop: No asset selected!")  


def openAssetMaster(ftype, *args):
    """gets the master we've listed in the textfield and opens it. takes in ftype ("geo or rig")"""
    master = ""
    
    if ftype == "geo":
        #get master file name from text field based on file type
        if pi.currentAsset:
            master = cFuncs.getAssetMaster(pi.currentAsset, pi.currentAssetFolder, "geo")
        else:
            cmds.warning("assetWin.openAssetMaster: There is no asset selected in the window!")
    elif ftype == "rig":
        if pi.currentAsset:
            master = cFuncs.getAssetMaster(pi.currentAsset, pi.currentAssetFolder, "rig")
        else:
            cmds.warning("assetWin.openAssetMaster: There is no asset selected in the window!")
    elif ftype == "mtl":
        if pi.currentAsset:
            master = cFuncs.getAssetmaster(pi.currentAsset, pi.currentAssetFolder, "mtl")
    if master:  
        cFuncs.chrlxFileOpen(master)

    populateWindow()


def updateSceneName(*args):
    """gets the open scene name, updates the window text and the class variable"""
    openScene = os.path.basename(cmds.file(q=True, sn=True))
    if openScene == "":
        openScene = "UNSAVED SCENE!"
    cmds.text(widgets["sceneText"], e=True, l=openScene)    
    pi.openScene = openScene


def duplicateAsset(*args):
    dupe.duplicateAsset(pi.currentAssetFolder)


#############
# increment Workshops
#############

def incrementWorkshop(fType, *args):
    """checks that we're matching current open scene with selected asset and then increments the number on the workshop file and saves"""
    
    incr = ""
    mismatch = ""

    # if there's not a selected asset, bail out, otherwise continue
    if not pi.currentAsset:
        cmds.warning("You don't have an asset selected!")

    else: 
        if fType in ["geo", "rig", "mtl"]:
            incr = cFuncs.incrementWS(pi.currentAsset, pi.currentAssetFolder, fType)
        else:
            pass
        
        #test to see if the current file matches the selected
        mismatch = cFuncs.checkCurrentWSMatch(pi.currentAsset, fType)

        if mismatch != "Cancel":

            pi.date = cmds.about(cd=True)
            pi.time = cmds.about(ct=True)
            #pi.user

            #pull up prompt dialogue for notes - ---- PASS THE NOTE TO THE CFUNCS
            note = cmds.promptDialog(title="Increment Workshop", message = os.path.basename(incr), scrollableField = True, button = ("Add and Save", "Cancel"), defaultButton = "Add and Save", cancelButton = "Cancel", dismissString = "Cancel")
            if note == "Add and Save":
                chrlxNote = cmds.promptDialog(q=True, text=True)
                cmds.file(rename = "{0}.ma".format(incr))
                # add some stuff into the initial geo workshop
                if fType == "geo":
                    print incr.rpartition("_ws_v")[2].rstrip(".ma")
                    if incr.rpartition("_ws_v")[2].rstrip(".ma") == "001":
                        print "-------Adding the delete set--------"
                        cmds.sets(name = "deleteSet", empty=True)
                        print "-------Adding master control template-------"
                        cFuncs.mstCtrlTemplate()

                # add fileInfo stuff to scene before we save. . .
                cFuncs.putFileInfo(fType, incr.rpartition("_ws_v")[2].rstrip(".ma"), chrlxNote)

                #save the incremented scene
                cmds.file(save=True, type="mayaAscii")

                cmds.warning("------Increment finished!--------\n{0}".format(incr))

                updateAssetInfo(pi.currentAsset)
                updateSceneName()


def refGeo(*args):

    sTab = cmds.tabLayout(widgets['assListTypeTLO'], q=True, st=True) #st = selected tab
    tabs = ["Chars", "Props", "Sets"]
    lists = [widgets["assCharListTSL"], widgets["assPropListTSL"], widgets["assSetListTSL"]]
    assFile = ""

    if sTab == "Chars":
        asset = cmds.textScrollList(widgets["assCharListTSL"], q=True, si=True)
        if asset:
            ass = asset[0]
            assFile = cFuncs.fixPath(os.path.join(pi.charFolder, ass, "geo", "{0}_geo.ma".format(ass)))
    elif sTab == "Props":
        asset = cmds.textScrollList(widgets["assPropListTSL"], q=True, si=True)
        if asset:
            ass = asset[0]
            assFile = cFuncs.fixPath(os.path.join(pi.propFolder, ass, "geo", "{0}_geo.ma".format(ass)))
    elif sTab == "Sets":
        asset = cmds.textScrollList(widgets["assSetListTSL"], q=True, si=True)
        if asset:
            ass = asset[0]
            assFile = cFuncs.fixPath(os.path.join(pi.setFolder, ass, "geo", "{0}_geo.ma".format(ass)))

    geoFile = cFuncs.fixPath(assFile)
    if assFile:
        # reference in the assFile
        if os.path.isfile(assFile):
            cmds.file(assFile, r=True)
        else:
            cmds.warning("I can't find the geo master for the selected asset! {0}".format(assFile))

    else:
        cmds.warning("You need to select the asset on the left side!")

def refExternal(*args):
    """reference external file into scene"""
    
    goTo = pi.currentProject
    if pi.currentGeoFolder:
        goTo = pi.currentGeoFolder
    fileFilter = "All Files (*.*);; Maya ASCII (.ma);; Maya Binary (.mb);; OBJ (.obj);; Maya Files (.ma, .mb)"
    refFile = cmds.fileDialog2(fm=1, dir = goTo, fileFilter = fileFilter)[0]
    if refFile:
        cmds.file(refFile, r=True)


def importExternal(*args):
    """import external file into scene"""
    
    goTo = pi.currentProject
    if pi.currentGeoFolder:
        goTo = pi.currentGeoFolder
    fileFilter = "All Files (*.*);; Maya ASCII (.ma);; Maya Binary (.mb);; OBJ (.obj);; Maya Files (.ma, .mb)"      
    impFile = cmds.fileDialog2(fm=1, dir = goTo, fileFilter = fileFilter)[0]
    if impFile:
        cmds.file(impFile, i=True)


def quickIncrement(*args):
    qincr.quickIncrement()


############
# master stuff
###########

def masterAsset(fType, *args):
    """
    takes in the type ("geo" or "rig") and passes info to the masterAsset.py module, which handles it's business and passes back a message in the dialog
    """
    test = ""

    if fType == "geo": 
        test = cMaster.masterAsset(pi.currentAsset, pi.currentAssetFolder, "geo", False)
        if test == "clash":
            return()
        cmds.confirmDialog(t="Mastered File", m=test, b="OK")

    elif fType == "rig":
        test = cMaster.masterAsset(pi.currentAsset, pi.currentAssetFolder, "rig", False)
        if test == "clash":
            return()
        cmds.confirmDialog(t="Mastering File", m=test, b="OK")

    if test != "__CANCEL__":
        # cmds.file(force = True, new = True)
        cmds.warning("Master created!")
        populateWindow()

######## option to continue in master, revert to latest ws or open blank scene

def pushGeoRig(*args):
    """
    should open background process to open (refresh refs in) rig workshop, then master rig ws
    """
    pass

    
#############
# create icon script
############

def changeJobIcon(*args):
    path = pi.currentProject
    cFuncs.createJobSpotIcon(path, "jobIcon")


def createAssetIcon(*args):
    #call to external to create icons
    #check if user is in the same scene file as the selected asset!!
    sceneName = cFuncs.fixPath(cmds.file(q=True, sn = True))
    snameChar = os.path.commonprefix([sceneName, pi.currentAssetFolder])
    #print "the common prefix is ", snameChar

    sceneCont = "Yes"
    if snameChar != pi.currentAssetFolder:
        sceneCont = cmds.confirmDialog(t="Mismatching Chars", m="Your scene doesn't match that asset!\nWrite icon to {0} anyways?".format(pi.currentAsset), b=("Yes","No"), db="No", cb="No", ds="No")
##### HERE above ==== > create a confirm dialog with the actual names of the assets/folders
    #check that something is selected in asset list
    if sceneCont == "Yes":
        sel = ""
        
        #go up a few levels to find what asset type we are . . . 
        tab = cmds.tabLayout(widgets["assListTypeTLO"], q=True, st=True)
        if tab == "Props":
            tabL = "assPropListTSL"
        elif tab == "Chars":
            tabL = "assCharListTSL"
        elif tab == "Sets":
            tabL = "assSetListTSL"
        try:
            sel = cmds.textScrollList(widgets[tabL], q=True, si=True)[0]
        except: 
            cmds.warning("Doesn't seem like you've selected an asset to create an image for!")

        if sel:
            go = "Yes"
            iconFile = "{0}/icon/{1}Icon.png".format(pi.currentAssetFolder, pi.currentAsset)
            if os.path.isfile(iconFile):
                go = cmds.confirmDialog(t="Overwrite Confirm", m="There is already an icon for this!\nShould I overwrite it?", b=("Yes", "No"), db="Yes", cb ="No", ds = "No")
            if go=="Yes":
                #at this pt we can delete the orig file
                if os.path.isfile(iconFile):
                    os.remove(iconFile)
                #deselect objects in scene, PB, then reselect
                sl = cmds.ls(sl=True)
                cmds.select(clear = True)
                cFuncs.createAssetIcon("{0}/icon".format(pi.currentAssetFolder), pi.currentAsset)
                cmds.select(sl, r=True)

                updateAssetInfo(pi.currentAsset)
            else:
                cmds.warning("Icon creation cancelled")
    else:
        cmds.warning("Cancelling Icon Creation")



def clearAll(*args):
    cmds.textScrollList(widgets["assCharListTSL"], e=True, ra =True)
    cmds.textScrollList(widgets["assPropListTSL"], e=True, ra =True)
    cmds.textScrollList(widgets["assSetListTSL"], e=True, ra =True)

    #clear asset info
    #geo
    # cmds.textField(widgets["geoMstLogTF"], e=True, tx="")
    # cmds.textField(widgets["geoWSLogTF"], e=True, tx = "")
    cmds.textFieldGrp(widgets["geoLastWSTFG"], e=True, tx="")
    cmds.textFieldGrp(widgets["geoLastMasterTFG"], e=True, tx="")

    #rig
    cmds.textFieldGrp(widgets["rigLastWSTFG"],e=True, tx="")
    cmds.textFieldGrp(widgets["rigLastMasterTFG"], e=True, tx = "")
    # cmds.textField(widgets["rigMstLogTF"], e=True, tx="") 
    # cmds.textField(widgets["rigWSLogTF"], e=True, tx="")

    #asset info
    cmds.text(widgets["assetInfoNameText"], e=True, l="")
    cmds.image(widgets["assetInfoPic"], e=True, image = "{0}/noImage.jpg".format(pi.images))
    cmds.textFieldGrp(widgets["assetGeoStatusTF"], e=True, tx ="")
    cmds.textFieldGrp(widgets["assetRigStatusTF"], e=True, tx="")

#############
# asset Action stuff
############

def createAsset(*args):
######## for database, pass "asset_jobNum" to get unique name
    pc = cFuncs.projectCheck()
    if pc:
        createDir.createAsset(pi.assetFolder)
    else:
        cmds.warning("You're not in an appropriate project setup!")

def archiveAsset(*args):
    """ moves the selected asset into the asset type archive folder (chars, props, sets)"""
    #get the current asset and the asset type folder (char, prop, set folder)
    #pass these to function in chrlx funcs, get return value
    tabType = cmds.tabLayout(widgets["assListTypeTLO"], q=True, selectTab=True)
    if tabType == "Chars":
        assType = "characters"
    elif tabType == "Props":
        assType = "props"
    elif tabType == "Sets":
        assType = "sets"

    archiveCont = cmds.confirmDialog(t="Archive Asset", m="Are you sure you want to archive: \n\n{0} ?\n\nThis will affect any scenes referencing it!".format(pi.currentAsset), b=("Yes","No"), db="No", cb="No", ds="No")
    if archiveCont == "Yes":
        assArchiveFolder =  "{0}/{1}/archive/{2}".format(pi.assetFolder, assType, pi.currentAsset)
        archive = cFuncs.moveFolder(pi.currentAssetFolder, assArchiveFolder)

        # used return values to put up confirm dialog
        cmds.confirmDialog(t="Archived Asset Confirmation!", m = archive)

        populateWindow()
    else: 
        cmds.warning("Archiving Cancelled!")

def unarchiveAssets(*args):
    """calls the unarchive module, which will restore assets from their archive folders back to activel lists"""
    unarch.unarchiveAssets(pi.assetFolder)


def copySkin(*args):
    aFuncs.copySkinning()


def dupeReffed(*args):
    """
    duplicates the referenced geo, as long as the ref is the 'geo' master of the current scene's asset
    Args:
        None
    Return:
        None
    """
    currentScene = cmds.file(q=True, sn=True)
    path = utils.PathManager(currentScene)
    # print cFuncs.checkCurrentWSMatch(path.name, "rig", *args)
    try:
        testRef = cFuncs.fixPath(path(stage="geo").getMaster())
        # get ref master file, check against list of references
        currentRefs = cmds.file(q=True, reference=True)
        if testRef in currentRefs:
            aFuncs.dupeReffedGeo(testRef)
        else: 
            cmds.warning("assetWin.dupReffed: I can't find the geo reference in this scene: {0}".format(testRef))
        return()
    except Exception, e:
        cmds.warning("assetWin.dupeReffed: Trouble getting the geo path\n{0}".format(e))


def shaderUVTransfer(*args):
    import zTools.zbw_shadingTransfer as shdXfer
    shdXfer.shadingTransfer()
 

def tooltipSet(*args):
    status = cmds.checkBox(widgets["assetAnnCB"], q=True, v=True)

    cmds.help(popupMode=status)
    cmds.savePrefs()

#############
# Call to start UI
############

def assetWin(*args):
    assetWinUI()

