import maya.cmds as cmds
import maya.mel as mel
import os, sys,	subprocess
from shutil import copyfile
from functools import partial

import chrlx_pipe.chrlxFuncs as cFuncs
reload(cFuncs)
import chrlx_pipe.chrlxClash as cClash
reload(cClash)
import chrlx_pipe.masterWin as mstWin
reload(mstWin)
import chrlx_pipe.cleanShaders as clnShd
reload(clnShd)
import chrlx_pipe.utils as utils

##############
# functions and such for the mastering process of assets
# some separate processes for geo and rigs
# uses chrlxFuncs to do general things 
##############

######### open separate window to promote past version to current master, (save ws version somewhere in scene? Scene info)
######### this woudl be ws version itself for ws's and ws version for masters

mWidget = {}
sWidget = {}
assOptions = {"note":"", "cam":1, "shd":1, "rig":1, "freeze":0, "light":1}
shotOptions = {"note":"", "cam":1, "shd":1, "rig":1, "freeze":0, "light":1}
######### all of masterAsset AFTER button click? this will allow us to push through
def masterAsset(asset, assFolder, fType, batch=False, *args):
    # print "++++++++++ i'm in masterAsset and vars are:\nasset:{0}\nassFolder:{1}\nftype:{2}".format(asset, assFolder, fType)
    """
    gets latest version of past_versions
    ARGS:
        assetName (string): i.e. "man"
        assFolder (string): i.e. rig folder [...JOB/3d_assets/CHARS/ASSET], etc
        fType (string): i.e. 'geo', 'rig', 'mtl'
        batch (bool): is for batch mode (no UI) and is a bool (True/False or 0/1)

    RETURN:
        string: to be used in the asset win to the kill the master process or to give users a message
    """

    mastered = False

    note = "mastering asset!"

    #clash check
    clash = cClash.clash(0)
    if clash:
        fix = cmds.confirmDialog(title="Clash Fix?", message = "Name clashes have been detected!\nSee script editor for details\nHow should we fix?", button = ("Fix Automatically", "Fix Manually"), defaultButton = "Fix Automatically", dismissString = "Fix Manually", cancelButton = "Fix Automatically")
        if fix == "Fix Manually":
            cClash.clash(0)
            return("clash")
        else:
            cClash.clash(1)

    # below UI has "dict" attr that will grab a dictionary from masterWin ("note":str, "cam":bool, "shd":bool, "rig":bool). use these vals to turn on funcs
    if not batch:
        options = mstWin.masterAssetUI()
        assOptions["note"] = options.dict["note"]
        assOptions["cam"] = options.dict["cam"]
        assOptions["shd"] = options.dict["shd"]
        assOptions["rig"] = options.dict["rig"]
        assOptions["light"] = options.dict["light"]
        assOptions["freeze"] = options.dict["freeze"]

        note = assOptions['note']
        if note == "__CANCEL__":
            return "__CANCEL__"

    masterFile = "{0}_{1}".format(asset, fType)

    latestMasterVersion = cFuncs.getLastAssetMasterVersion(asset, assFolder, fType, *args) #check if there's a master
    latestWorkshop = cFuncs.getLatestAssetWS(asset, assFolder, fType) #check the lastest workshop
    print "masterFuncs.masterAsset:\nlatestMasterVersion:{0}\nlatestAssetWS:{1}".format(latestMasterVersion, latestWorkshop)

    if latestMasterVersion and (latestMasterVersion != "Abort"): # if we get a good value from the latest master
        num = int(os.path.basename(latestMasterVersion).rstrip(".ma").rpartition("_v")[2]) # get the number from the file name
        incrNum = "{:0>3d}".format(num + 1)

    elif latestMasterVersion == "Abort":
        cmds.warning("masterFuncs.masterAsset: There was some kind of issue with the paths to get the latest master for backup")
        return
    
    elif latestMasterVersion == None: # if no num, set it to one
        incrNum = "001"
    
    #create file name and full path
    newPastVersion = "{0}/{1}/past_versions/{2}_v{3}.ma".format(assFolder, fType, masterFile, incrNum)

    # does this line up with the ws file structure? 	
    check = cFuncs.checkCurrentMasterMatch(asset, fType)

    if not check:
        #here we bail out if current scene isn't workshop of the scene you're trying to master (from window)
        cmds.confirmDialog(t="SCENE MISMATCH", m="Your current scene doesn't line up\nwith the asset you've selected\nin the asset window. . . \n\nMake sure you're in a workshop file\nfor the asset you want to master!")
        return "FILE MISMATCH - NO MASTER CREATED!"

    #copy current master to past masters and rename to new num 
    currentMaster = "{0}/{1}/{2}.ma".format(assFolder, fType, masterFile)
    destination = "{0}".format(newPastVersion)
    currentWS = cmds.file(q=True, sceneName = True)
    
########### save current scene as latest workshop - note: "MASTERING - ".format(currentWS)  is there a way to do this??? pass a note? maybe use an arg (bool) in to tell whether to use UI stuff
######### --- need to sort out fType for fileinfo mastering of rig file, right now it says "geo" in file info
    #increment ws file from current
    newWSFile = "{0}".format(cFuncs.incrementWS(asset, assFolder, fType))
    correctWSnum = "{:0>3d}".format(int(latestWorkshop[-6:-3]))

    cFuncs.putFileInfo(fType, correctWSnum, note)	

# *************** increment #1
    cmds.file(rename = newWSFile)
    cmds.file(save=True, type="mayaAscii")

    #do the mastering stuff to the current file, if we bail at any stage, reopen the ws and don't save master
    cmds.file(rename=currentMaster)
    if fType == "geo":
        masterTest = masterGeo(asset, assFolder)
        if masterTest == "AbortC":
            print "trying to get latest ws file: {0}".format(newWSFile)
            cmds.file(newWSFile, open=True, force=True )
            return("Failed mastering at geo cleanup phase. Try again after fixing problems")

    if fType == "rig":
        masterTest = masterRig(asset, assFolder)
        if masterTest == "AbortC":
            cmds.file(latestWorkshop, open=True, force=True )
            return("Failed mastering at rig cleanup phase. Try again after fixing problems")

    mastered = True

    if os.path.isfile(currentMaster): #check if there is a master file currently. If so, move it to the past versions
        os.rename(currentMaster, destination)
        print "masterAsset.masterAsset:\n------ moving: {0} \n------ to: {1}".format(currentMaster, destination)

    cmds.file(save=True, type="mayaAscii")

    if fType == "geo":
        #check if there's a rig workshop for this asset
        rigWS = cFuncs.getLatestAssetWS(asset, assFolder, "rig")
        print "workshop rig file is:", rigWS
        if not (rigWS and os.path.exists(rigWS)) and assOptions["rig"]:
            print "-------Starting creation of rig files-------"
            initializeRigWS(asset, assFolder, "rig")

        else:
            print "Not initializing rig!"

    if mastered:
        cmds.file(newFile=True, force=True)

    #refresh the asset info in the asset win
    if cmds.window("assetWin", exists=True):
        import chrlx_pipe.assetWin as assWin
        assWin.populateWindow()

    return "Master created successfully: {0}".format(currentMaster)

def masterGeo(asset, assetFolder, *args):
    #make sure to stick info about the relevant workshop into the file for the "promotePastVersion" function later (promote them both)

    # make saving a note mandatory, BUT make sure this DOESN"T require user input when in headless mode (maybe just an arg to pass)
    #bring up window
    print "\n-------------------\nDOING MASTER GEO STUFF HERE!\n-------------------"
    clean = cleanAssetScene("geo")
    if clean == "Abort":
        return("AbortC")

####### ------ tag this master with the workshop num to compare to latest?
###### ------ if not mastering through, option to either go to new scene or open master?

def initializeRigWS(asset, assetFolder, *args):
    """will use standalone maya to create the initial rig ws file"""	

    print "INITIALIZING RIG WORKSHOP"
    root = os.getenv("MAYA_ROOT")
    initRigFile = cFuncs.fixPath("{0}/scripts/chrlx_pipe/buildInitialRigFiles.py".format(root))
    if os.name=="nt":
        mayapy = cFuncs.fixPath(os.path.join(os.getenv("MAYA_LOCATION"), "bin", "mayapy.exe"))
    elif os.name!="nt":
        mayapy = cFuncs.fixPath(os.path.join(os.getenv("MAYA_LOCATION"), "bin", "mayapy"))

    try:	
        subprocess.call([mayapy, initRigFile, asset, assetFolder])
        print "FINISHED WITH RIG WS CREATION"
    except Exception, e:
        print "masterFuncs.InitializeRigWS - error:\n", e
        print "masterFuncs.InitializeRigWS: DID NOT CREATE RIG WS"

def masterRig(asset, assetFolder, *args):
    #make sure to stick info about the relevant workshop into the file for the "promotePastVersion" function later (promote them both)
    # Should group geo and put it group under the controller to start!!! (this will allow for auto-mastering)
    # need to check whether there already is a scene in the ws folder? If not then go through geo ref process (prefix, setup, etc)

    #make a copy from reffed geo, group it 
    # import geo file from reference. . . 
    print "\n-------------------\nDOING MASTER RIG STUFF HERE!\n-------------------"
    ######## - am I returning something below?
    clean = cleanAssetScene("rig") 
    if clean == "Abort":
        return("AbortC")

    # tag this master with the current rig ws to compare later. Also tag with latest geo ws? compare that too? 

def cleanAssetScene(fType, *args):	
    """cleans up the stuff in the scene (deletes unwanted stuff, etc)"""
#generically to geo and rig files
    #remove namespaces
    ns = cFuncs.removeNamespace()
    print "removed namespaces: {0}".format(ns)

###### ---------- clash fix should happen BEFORE master. . . 
    cfix = 1 #1 = fix the clashes, 0 = just report the clashes
    cClash.clash(cfix)

    # clean up the delete set
    if cmds.objExists("deleteSet"):
        delStuff = cmds.sets("deleteSet", q=True)
        cmds.delete(delStuff)
        try:
            cmds.delete("deleteSet")
        except:
            print "-Problem deleting the deleteSet"

    #import all refs
    refs =  cmds.file(q=True, r=True)
    for ref in refs:
        refNode = cmds.referenceQuery(ref, rfn=True)
        cmds.file(rfn=refNode, ir=True)

    #delete image planes
    ip = cmds.ls(type="imagePlane")
    print "deleting image planes: {0}".format(ip)
    if ip:
        cmds.delete(ip)
    
    #delete camera bookmarks
    bm = cmds.ls(type = "cameraView")
    print "deleting camera bookmarks: {0}".format(bm)
    if bm:
        cmds.delete(bm)

    #get all lights and delete
    if assOptions["light"]:
        lights = cFuncs.getLightList()
        print "deleting lights: {0}".format(lights)
        if lights:
            cmds.delete(lights)

    #get extra cameras and delete
    if assOptions["cam"]:
        cams = cFuncs.getCamList()
        print "deleting non-default cameras: {0}".format(cams)
        if cams:
            cmds.delete(cams)
    
    #delete all TIME BASED anim curves (not setdriven keys)
    anmsT = cmds.ls(type = ("animCurveTL", "animCurveTU", "animCurveTA", "animCurveTT"))
    if anmsT:
        print "deleting time-based anim curves: {0}".format(anmsT)
        cmds.delete(anmsT)

    #get rid of display layers, render layers, anm layers
    dl = cmds.ls(type="displayLayer")
    if dl:
        dl.remove("defaultLayer")
        print "deleting display layers: {0}".format(dl)
        cmds.delete(dl)

    rl = cmds.ls(type = "renderLayer")
    if rl:
        rl.remove("defaultRenderLayer")
        print "deleting render layers: {0}".format(rl)
        cmds.delete(rl)

    al = cmds.ls(type = "animLayer")
    if al:
        al.remove("BaseAnimation")
        print "deleting anim layers: {0}".format(al)
        cmds.delete(al)

    #delete unknown nodes
    uk = cmds.ls(type = "unknown")
    if uk:
        print "deleting unknown nodes: {0}".format(uk)
        for node in uk:
            cmds.lockNode(node, l=False)
        cmds.delete(uk)

    #check for shaders
    if assOptions["shd"]:
        clnShd.cleanShaders()

    #grab list of all transforms
    allGeo = cmds.listRelatives(cmds.ls(geometry = True), p=True)
    #remove lattices from list
    for g in allGeo:
        if cmds.listRelatives(g, shapes=True, type="lattice"):
            allGeo.remove(g)

    allTransforms = cmds.ls(type = "transform")

    #get rid of face assigments (select only the first shader assigned)
    for geo in allGeo:
        shps = cmds.listRelatives(geo, s=True)
        if shps:
            for shp in shps:
                sg = cmds.listConnections(shp, type="shadingEngine")
                if (sg and len(sg) > 1):
                    cmds.sets(geo, e=True, forceElement=sg[0]) 
                    print "Found more than one shader on {0}. Reassigning to {1}".format(geo, sg[0])		
    
#if geo file . . . 
    if fType == "geo":

        #delete history on all geo objects
        cmds.delete(allGeo, ch=True)
        
        #delete deformers left over (should be none)
        # for geo in allGeo:
        # 	df = mel.eval("findRelatedDeformer {0}".format(geo))
        # 	if df:
        # 		print "deleting deformers: {0}".format(df)
        # 		cmds.delete(df)

        #parent all transforms to world
        for i in allGeo:
            print "------ {0}".format(i)
            if cmds.listRelatives(i, p=True):
                cmds.parent(i, world=True)
    
        #delete constraints
        cnstrs = cmds.ls(type="constraint")
        print "deleting constraints: {0}".format(cnstrs)
        if cnstrs:
            cmds.delete(cnstrs)
        
        #delete all sets
        removeSets = ["defaultLightSet", "defaultObjectSet"]
        setList = cmds.ls(et = "objectSet")
        for rmSt in removeSets:
            setList.remove(rmSt)
        if setList:
            cmds.delete(setList)

        #delete all expressions
        exprs = cmds.ls(type="expression")
        print "deleting expressions: {0}".format(exprs)
        if exprs:
            cmds.delete(exprs)

        #delete all UNIT BASED anim curves (sdks, etc)
        sdkAnms = cmds.ls(type = ("animCurveUL", "animCurveUU", "animCurveUA", "animCurveUT"))
        if sdkAnms:
            print "deleting unit-based anim curves: {0}".format(sdkAnms)
            cmds.delete(sdkAnms)
        
        allTransforms = cmds.ls(type = "transform")	

        #delete groups - because DAG should be flattened we can just delete a transform w/o children
        grps = [x for x in allTransforms if not cmds.listRelatives(x, shapes=True)]
        if grps:
            print "deleting empty groups: {0}".format(grps)
            cmds.delete(grps)
        
        allTransforms = cmds.ls(type = "transform")
        #delete connections(should be no more anim, constraints at this point, so these would be direct connections) 
        for trans in allTransforms:
            #disconnect all channelbox channels
            cons = cmds.listConnections(trans, plugs=True, s=True)

            if cons:
                for con in cons:
                    dest = cmds.connectionInfo(con, dfs=True)
                    if dest:
                        cmds.disconnectAttr(con, dest[0])
        
        #freeze transforms on geo
        if allGeo and assOptions["freeze"]:
            print "masterFuncs.cleanAssetScene: assOptions[freeze] = {0}\nallGeo = {1}".format(assOptions["freeze"], allGeo)
            cmds.makeIdentity(allGeo, apply=True)
        else:
            print "-- not freezing geo"

        #delete all namespaces
        cFuncs.removeNamespace()

        #check for "geo_" name - warn out of this
        geoName = cmds.ls("geo_*")
        if geoName:
            cmds.warning("the following objects have 'geo_' as their prefix!\n{0}".format(geoName))

        #set displaySmoothness to 3
        cmds.displaySmoothness(allGeo, polygonObject = 1)

        #set ctrl size node
        if cmds.objExists("*ctrlSizeTemplateCrv"):
            ctrl = cmds.ls("*ctrlSizeTemplateCrv")[0]
            #measure distance (10.421 is scale 1)
            pos6 = cmds.pointPosition("{0}.cv[6]".format(ctrl))
            pos18 = cmds.pointPosition("{0}.cv[18]".format(ctrl))
            dist = pos6[0]-pos18[0]
            factor = dist/10.421

            rigScale = cmds.shadingNode("multiplyDivide", asUtility=True, n="RIGDATA")
            cmds.addAttr(rigScale, ln="scaleCtrl", at="float", dv=1.0)
            cmds.setAttr("{0}.scaleCtrl".format(rigScale), factor)
            cmds.delete(ctrl)

#if rig file . . . 
    print "Doing rig cleanup stuff. . . "
    if fType == "rig":
        if cmds.objExists("*RIGDATA"):
            rigDataStuff = cmds.ls("*RIGDATA")
            cmds.delete("*RIGDATA")

        # put all ctrls into ALLKEYABLE
        cFuncs.crvsToAllkeyable()
        print "putting all crvs under god node into allkeyable set"

#again generically to both rig and geo
    #optimize scene

def masterShot(var, varFolder, fType, batch=False, BG = False, importRefs = True, *args):
    """
    gets latest version of past_versions
    Args: 
        varName (string): variantName (ie. "defaultVariant")
        varFolder (string): the folder for the variant (i.e. rig folder, lgt var folder, etc)
        fType (string): the type of shot abbreviation ('lgt', 'anm', 'fx'), 
        batch (bool): for batch mode (no UI)
        BG (bool): render in background?
        importRefs (bool): should we import the references when mastering?

    Return:
        string: returns message for the confirm dialog in shot win
    """

    note = "mastering shot!"

    #clash check
    clash = cClash.clash(0)
    if clash:
        fix = cmds.confirmDialog(title="Clash Fix?", message = "Name clashes have been detected!\nSee script editor for details\nHow should we fix?", button = ("Fix Automatically", "Fix Manually"), defaultButton = "Fix Automatically", dismissString = "Fix Manually", cancelButton = "Fix Automatically")
        if fix == "Fix Manually":
            cClash.clash(0)
            return("clash")
        else:
            cClash.clash(1)

    # below UI has "dict" attr that will grab a dictionary from masterWin ("note":str, "cam":bool, "shd":bool, "rig":bool). use these vals to turn on funcs
    if not batch:
        options = mstWin.masterShotUI()
        shotOptions["note"] = options.dict["note"]
        shotOptions["shd"] = options.dict["shd"]
# - -------  add frame range, resolution, FPS?

        note = shotOptions['note']
        if note == "__CANCEL__":
            return "__CANCEL__"


    pm = utils.PathManager(varFolder)
    shotmst = pm.getMaster()
    masterFile = os.path.basename(shotmst)[:-3]

    latestMasterVersion = cFuncs.getLatestVarMaster(var, varFolder, fType) #check if there's a master
#---------------- HERE: GET two WS FILES. THE SECOND WILL BE THE ONE WE SAVE, THEN EXTERNALLY COPY AND MASTER THE FIRST    
    latestWorkshop = cFuncs.getLatestVarWS(varFolder) #check the lastest workshop

    # get the number on the end of te 
    if latestMasterVersion and (latestMasterVersion != "Abort"):
        num = int(os.path.basename(latestMasterVersion).rstrip(".ma").rpartition("_v")[2])
        incrNum = "{:0>3d}".format(num + 1)

    elif latestMasterVersion == "Abort":
        cmds.warning("masterFuncs.masterShot: There was some kind of issue with the paths to get the latest master for backup")
        return
    
    elif latestMasterVersion == None:
        incrNum = "001"
    
    #create file name and full path
    # newPastVersion = "{0}/past_versions/{1}_v{2}.ma".format(varFolder, masterFile, incrNum)
    newPastVersion = cFuncs.fixPath(pm.getNextVersion())

    # does this line up with the ws file structure? 
    check = cFuncs.checkCurrentMasterMatch(masterFile, fType)

    if not check:
        #here we bail out if current scene isn't workshop of the scene you're trying to master (from window)
        cmds.confirmDialog(t="SCENE MISMATCH", m="Your current scene doesn't line up\nwith the asset you've selected\nin the asset window. . . \n\nMake sure you're in a workshop file\nfor the asset you want to master!")
        return "FILE MISMATCH - NO MASTER CREATED!"

    #copy current master to past masters and rename to new num
    currentMaster = "{0}/{1}.ma".format(varFolder, masterFile)
    destination = "{0}".format(newPastVersion)
    currentWS = cmds.file(q=True, sceneName = True)
    
    #increment ws file from current
    newWSFile = "{0}.ma".format(cFuncs.incrementWS(var, varFolder, fType))
    correctWSnum = "{:0>3d}".format(int(latestWorkshop[-6:-3]))

# -------------- add more data to the shot master fileInfo
    cFuncs.putFileInfo(fType, correctWSnum, note)

    # increment ws 
    cmds.file(rename = newWSFile)
    cmds.file(save=True, type="mayaAscii")

    #do the mastering stuff to the current file, if we bail at any stage, reopen the ws and don't save master	
    # depending on type of master we want to do, finish up the mastering process. . . .
    if BG == False and importRefs == True: # regular master

        print "\n-------------------\nDOING IMPORT MASTER SHOT STUFF HERE!\n-------------------"
        clean = cleanShotScene(fType, BG, importRefs)
        if clean == "Abort":
            print "trying to return you to latest workshop file: {0}".format(newWSFile)
            cmds.file(newWSFile, open=True, force=True )
            return("Failed mastering at cleanup phase. Try again after fixing problems")

        cmds.file(rename=currentMaster)	
        if os.path.isfile(currentMaster): #check if there is a master file currently. If so, move it to the past versions
            os.rename(currentMaster, destination)
            print "masterFuncs.masterShot:\n------ moving: {0} \n------ to: {1}".format(currentMaster, destination)
        cmds.file(save=True, type="mayaAscii") # save as master
        cmds.file(newFile=True, force=True)


    if BG == False and importRefs == False:  # referenced master
        print "\n-------------------\nDOING REFERENCE MASTER SHOT STUFF HERE!\n-------------------"
        clean = cleanShotScene(fType, BG, importRefs)
        if clean == "Abort":
            print "trying to return you to latest ws file: {0}".format(newWSFile)
            cmds.file(newWSFile, open=True, force=True )
            return("Failed mastering at cleanup phase. Try again after fixing problems")

        cmds.file(rename=currentMaster)	
        if os.path.isfile(currentMaster): #check if there is a master file currently. If so, move it to the past versions
            os.rename(currentMaster, destination)
            print "masterFuncs.masterShot:\n------ moving: {0} \n------ to: {1}".format(currentMaster, destination)
        cmds.file(save=True, type="mayaAscii") # save as master

        #rename to increment ws
        secondWSFile = "{0}".format(cFuncs.incrementWS(var, varFolder, fType))
        cmds.file(rename=secondWSFile)

        cmds.file(save=True, type="mayaAscii")


    if BG == True and importRefs == True:  # BG master
        # call to function to master shot on current ws
        print "---------- kicking out to BG Master function ------------"
        bgMasterShot(fType, var, varFolder, newWSFile, destination, currentMaster)
        # increment again and open variant ws
#---------------- maybe DON'T re-increment this here? Just open old ws?         
        reincr = "{0}".format(cFuncs.incrementWS(var, varFolder, fType))
        cmds.file(rename=reincr)
        cmds.file(save=True, type="mayaAscii")

    #refresh the info in the shot win
    if cmds.window("shotWin", exists=True):
        import chrlx_pipe.shotWin as shotWin
        shotWin.populateWindow()

    if BG == True:
        return "Mastering in background process: {0}".format(currentMaster)
    if BG == False:
        return "Master created successfully: {0}".format(currentMaster)


def bgMasterShot(fType, variant, variantFolder, newWSFile, destination, currentMaster):
    """
    will use standalone maya to master the ws passed in 
    Args:
        fType = "anm", "lgt", or "fx"
        variant = name of the variant
        variantFolder = full path the variant folder [...shots/SHOT/TYPE/VARIANT]
        newWSFile = from masterShot func, the full path to latest WS file
        destination = full path to the proposed incremented past version of the master
        currentMaster = full path to the name of the master file
    """	

    print "MASTERING SHOT IN BACKGROUND"
    root = os.getenv("MAYA_ROOT")
    backgroundMaster = cFuncs.fixPath("{0}/scripts/chrlx_pipe/backgroundMaster.py".format(root))
    if os.name=="nt":
        mayapy = cFuncs.fixPath(os.path.join(os.getenv("MAYA_LOCATION"), "bin", "mayapy.exe"))

    if os.name!="nt":
        mayapy = cFuncs.fixPath(os.path.join(os.getenv("MAYA_LOCATION"), "bin", "mayapy"))

    try:
        subprocess.Popen([mayapy, backgroundMaster, fType, variant, variantFolder, newWSFile, destination, currentMaster])
        print "Mastering in BG: {0}".format(variant)
    except:
        print "COULD NOT MASTER IN BACKGROUND: {0}\n Please check the 'master log' in the variant folder".format(variant)

def cleanShotScene(fType, BG = True, importRefs = True):
    """
    does stuff to clean the current open scene. . .
    BG 1 = clean for background import(import the refs, BG 0 = don't do the import reffed stuff)
    """
    #make sure to stick info about the relevant workshop into the file for the "promotePastVersion" function later (promote them both)
    # make saving a note mandatory, BUT make sure this DOESN"T require user input when in headless mode (maybe just an arg to pass)
    #bring up window
    #this is where we do the stuff in the mastering process depeneding on which fType we have
    
    # clean up the delete set
    if importRefs == True:
        if cmds.objExists("deleteSet"):
            delStuff = cmds.sets("deleteSet", q=True)
            cmds.delete(delStuff)
            try:
                cmds.delete("deleteSet")
            except:
                print "-Problem deleting the deleteSet"
#---------------- shoudl this be an "if" thing? ie. if deleteImage: and if deleteDisplay. . . 
        #delete image planes
        ip = cmds.ls(type="imagePlane")
        print "deleting image planes: {0}".format(ip)
        if ip:
            cmds.delete(ip)

        #get rid of display layers, render layers, anm layers
        dl = cmds.ls(type="displayLayer")
        if dl:
            dl.remove("defaultLayer")
            print "deleting display layers: {0}".format(dl)
            cmds.delete(dl)

    # lgt 
    if fType == "lgt":
        # - set frame to 000
        cmds.currentTime(0)
        # - do it in the bg ??
        # - delete "delete set" 

        # if we're importing the refs (in all BG masters or regular masters (not ref master process))
        if importRefs:
            refs =  cmds.file(q=True, r=True)
            # =========== DON"T REMOVE NAMESPACES from refs!!!!	
            for ref in refs:
                refNode = cmds.referenceQuery(ref, rfn=True)
                cmds.file(rfn=refNode, importReference=True)

    # anm 
    if fType == "anm":
        # - set frame to 000
        cmds.currentTime(0)

        # - get all lights and delete
        lights = cFuncs.getLightList()
        print "deleting lights: {0}".format(lights)
        if lights:
            cmds.delete(lights)

        refs =  cmds.file(q=True, r=True)
        # =========== DON"T REMOVE NAMESPACES from refs!!!!	
        for ref in refs:
            refNode = cmds.referenceQuery(ref, rfn=True)
            cmds.file(rfn=refNode, importReference=True)

        # rl = cmds.ls(type = "renderLayer")
        # if rl:
        # 	rl.remove("defaultRenderLayer")
        # 	print "deleting render layers: {0}".format(rl)
        # 	cmds.delete(rl)

        ######## --------- maybe look into baking down anim layers



