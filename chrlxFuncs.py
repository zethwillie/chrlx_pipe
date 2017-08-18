import maya.cmds as cmds
import maya.mel as mel
import chrlx_pipe.utils as utils
import webbrowser as browser

import os, fnmatch, shutil, sys, fileinput

###################################################
# helper scripts that do little functions for the pipeline
# wherever possible, these should be generic (call/return from external scripts or manually)
#####################################################


def fixPath(path, *args):
    """
    cleans up the path for use in both win and linux. Remember to pass handmade paths as r'string'. 

    Args:
        path (string): the path to "correct". be careful of escape characters (use 'r' in front of handtyped paths, perhaps)

    Return:
        string/path
    """
    
    if path:
        cleanPath = path.replace("\\", "/")
        return cleanPath
    else:
        return None


def getCurrentProject(*args):
    """returns the current project path"""

    proj = cmds.workspace(q=True, act=True)
    if proj:
        cleanProj = fixPath(proj)
        return cleanProj
    else: 
        print "chrlxFuncs: couldn't find a valid project"
        return proj


def setProject(path, *args):
    """given a path, this will set the project to the path
    ---needs a bit more error checking and cleaner way to deal with win vs linux paths
    """
    #clean up the path for linux and win
    fixedPath = fixPath(path)
    #if the dir exists, then set the project to that
    ############
    #check where to set up the render directories, caches, files, etc bc they won't be in the default locations
    #maybe a separate script for that
    ############
    if os.path.isdir(fixedPath):
        mel.eval('setProject "{0}";'.format(fixedPath))
        ws = cmds.workspace(q=True, fn=True)
        cmds.warning("You've set the the current project to: %s"%(ws))
    else:
        cmds.warning("chrlxFuncs.setProject(): I can't find: {0}. talk to a TD!".format(fixedPath))


def getProjectAssetList(assetFolder, *args):
    """
    Args:
        assetFolder (string): the folder of assets (at the job level, not spot level)
    Return:
        list: returns a list of lists (chars, props, sets)
    """
    
    cAsset = fixPath(assetFolder)
    chars = []
    props = []
    sets = []

    charRoot = os.path.join(cAsset, "characters")
    propRoot = os.path.join(cAsset, "props")
    setRoot = os.path.join(cAsset, "sets")
    dirs = [charRoot, propRoot, setRoot]
    #check if the dir exists
    for dir in dirs:
        exists = os.path.isdir(dir)
        if exists:
            try:
                if dir==charRoot:
                    chars = os.listdir(dir)
                    chars.sort()
                    chars = [x for x in chars if (x[0] != "." and x != "archive")]
                elif dir==propRoot:
                    props = os.listdir(dir)
                    props.sort()
                    props = [x for x in props if (x[0] != "." and x != "archive")]
                elif dir==setRoot:
                    sets = os.listdir(dir)
                    sets.sort()
                    sets = [x for x in sets if (x[0] != "." and x != "archive")]					
            except:
                cmds.warning("chrlxFuncs.getProjectAssetList: couldn't access {0}".format(dir))		
        else:
            cmds.warning("chrlxFuncs.getProjectAssetList: Couldn't find the {0} path! Skipping.".format(dir))
    
    return chars, props, sets


def saveDialog(*args):
        save = cmds.confirmDialog(title="Save Confirmation", message = "Save current scene?", button = ("Save", "Don't Save", "Cancel"), defaultButton = "Save", cancelButton = "Cancel", dismissString = "Cancel")
        if save == "Save":
            return("save")
        elif save == "Don't Save":
            return("noSave")
        else:
            return("cancel")


def getShotVariantDict(shotPath, *args):
    """
    given the shot path [...SPOT/3d/shots/SHOT]
    -returns dict of the variants {"anm":VARS, "lgt":VARS, "fx":VARS}
    """

    shotVariants = {"anm":None, "lgt":None, "fx":None}
    exclude = ["import_export", "sourceImages", "reference", "houdini", "fx_data", "archive", "houdiniDev"]

    shotVariants["anm"] = [x for x in os.listdir(fixPath(os.path.join(shotPath, "anm"))) if x not in exclude]
    shotVariants["lgt"] = [x for x in os.listdir(fixPath(os.path.join(shotPath, "lgt"))) if x not in exclude]
    shotVariants["fx"] = [x for x in os.listdir(fixPath(os.path.join(shotPath, "fx"))) if x not in exclude]

    return shotVariants

# def getProjectAnm(spotPath, *args):
# 	"""given the spot path [...SPOT/3d]
# 		-returns the list of mastered animation names (not paths) in every shot
# 	"""
# 	exclude = ["import_export", "sourceImages", "reference"]
# 	shots = getProjectShotList(spotPath)
# 	for shot in shots:
# 		animPath = fixPath(os.path.join(spotPath, "shots", shot, "anm"))
# 		if animPath:
# 			vars = 


def getProjectShotList(spotPath, *args):
    """
    given a job(spot) path[...SPOT/3d], returns the list of folders in the shot path of that job
    """

    cJob = fixPath(spotPath)
    shotRoot = os.path.join(cJob, "shots")
    exclude = ["houdiniDev"]
    try:
        shots = os.listdir(shotRoot)
        #clear out files
        if shots:
            for item in exclude:
                if item in shots:
                    shots.remove(item)
            shots.sort()
            return shots
    except:
        cmds.warning("chrlxFuncs.getProjectShotList: No directory!!")


def referenceIn(scene, prefix, *args):
    """
    NOT USING!
    reference scenes, no namespace and will replace the obj name with the prefix arg
    -scene is the path to the scene
    -prefix is what we will use in the scene for the reference file
    """
    
    #############
    #---- need to check names in scene, increment if necessary
    #

    path = fixPath(scene)
    newPath = path.replace("\\", "/")
    ref = cmds.file(path, reference= True, uns = False, rpr = prefix)
    #maybe use parameter to push out a list of all the new nodes? 
    return ref


def referenceInWithNamespace(filePath, *args):
    '''
    given a path, reference that file in, using namespaces
    '''
    fileName = os.path.basename(filePath).rstrip(".ma")
    refName = cmds.file(filePath, r=True, ns=fileName)
    return(refName)

def replaceReferenceAndNamespace(replacementFile, targetRefFile, namespace, *args):
    """
    replaces a reference and changes the ns to match the new file
    Args:
        replacementFile (string): the new file path that you want to bring in
        targetRefFile (string): the file path that currently is being referenced in the scene
                             NOTE: the target file should be what is returned from cmds.file(q=True, r=True) which may include some stuff at the end
        namespace (string): the new namespace of the reference
    Return:
        none
    """
    # get the reference node
    rfn = cmds.file(targetRefFile, q=True, rfn=True)
    cmds.file(replacementFile, loadReference=rfn, type="mayaAscii")
#---------------- this part is acting weird- maybe I should get all refs in scene, search for the name and number it larger than largest?
#---------------- I'm not sure about getting the namespace (in shot win), how do I get this properly?
    cmds.file(replacementFile, e=True, namespace=namespace)


def makeDirectory(path, *args):
    """just makes a directory in the path if one doesn't exists"""

    cPath = fixPath(path) #cleans the path if we're hand typing it
    #check if the dir exists already
    exists = os.path.isdir(path)
    if not exists:
        try:
            os.makedirs(cPath)
            cmds.warning("Just made directory: {0}".format(cPath))
        except:
            cmds.warning("chrlxFuncs.makeDirectory: Couldn't make: {0}. Error Type: {1}".format(sys.exc_info()[0]))


def getAssetMaster(asset, assetPath, fType, *args):
    """
    takes the asset name and path to the asset [...3d/assets/ASSET]
    returns the path the master, return None if not there
    """
    
    maya = "{0}_{1}.ma".format(asset, fType)
    if (maya in os.listdir("{0}/{1}".format(assetPath, fType))):
        return("{0}/{1}/{2}".format(assetPath, fType, maya))
    else:
        return None


def getLatestAssetWS(asset, assetPath, fType, *args):
    """
    given an asset base name, asset base directory, and type ("rig", "mtl" or "geo"), find the latest version of the WS in that dir, returns the full path to file
    Args:
        asset(string): the asset name (ie. "man")
        assetPath(string): the asset path (ie. ...JOB/3d_assets/chars/ASSET)
        fType(string): "geo", "rig", "mtl"
    Return: 
        None or path to latestWS file
    """
############- -- - - check if this is/has a directory (I'm getting an OS error)
    ws = fnmatch.filter(os.listdir("{0}/{1}/workshops".format(assetPath, fType)), "{0}_{1}_ws_v[0-9]*.ma".format(asset, fType))
    
    #find the highest number WS
    sortNum = 0
    sortWS = "" #the file name of the last workshop file
    try:
        for x in range(0, len(ws)):
            #strip off the .ma, then get things after "_v". note this breaks if not named correctly!
            num = int(ws[x].rpartition("_v")[2].rstrip(".ma"))
            if num > sortNum:
                sortNum = num
                sortWS = ws[x]
    except:
        pass
        
    if sortWS:
        return "{0}/{1}/workshops/{2}".format(assetPath, fType, sortWS)
    else: 
        return None
        print "found no workshop files for {0}".format(asset)


def getLatestVarWS(varPath,*args):
    """
        -varPath = the full path the variant folder (...3d/shots/SHOT/TYPE/VAR)
    """
    # file name = T#####<spotLetter>shot010_anm_variant1.ma

    pm = utils.PathManager(varPath)
    jobNum = pm.jobNumber
    jobLetter = pm.jobType
    #print "+++++++ cFuncs.getLatestVarWS: \nshotName={0}\npathManager={1}".format(shotName, pm)
    fType = pm.shotType
    shotLabel = os.path.basename(pm.shotPath)
    varName = os.path.basename(varPath)
    wsBasename = "{0}_{1}_{2}".format(shotLabel, fType, varName)

    ws = fnmatch.filter(os.listdir("{0}/workshops".format(varPath)), "*{0}_ws_v[0-9]*.ma".format(wsBasename))

    #find the highest number WS
    sortNum = 0
    sortWS = "" #the file name of the last workshop file
    try:
        for x in range(0, len(ws)):
            #strip off the .ma, then get things after "_v". note this breaks if not named correctly!
            num = int(ws[x].rpartition("_v")[2].rstrip(".ma"))
            if num > sortNum:
                sortNum = num
                sortWS = ws[x]
    except:
#---------------- throw up the exception here        
        pass
        
    if sortWS:
        return "{0}/workshops/{1}".format(varPath,sortWS)
    else:
        print "found no workshop files for {0}".format(wsBasename)
        return None


def checkCurrentWSMatch(selectedAsset, fType, *args):
    """checks that the selected asset is actually the asset of the open scene. Puts up confirm dialog telling user this and returns 'cancel' if person decides not to continue

    """
    result = ""

    #get asset from current open ws scene name
    current = os.path.basename(cmds.file(q=True, sceneName = True))
    test = "{0}_{1}_ws".format(selectedAsset, fType)
    #strip off "_v###.ma" from open scene
    if current[:-8] != test:
        result = cmds.confirmDialog(t="Workshop Name Mismatch!", m = "Current scene: {0}\n\nSelected asset: {1}\n\nYou are attempting to save this to the {2} {3} folder!".format(current, test, selectedAsset, fType), b = ("Continue", "Cancel"), db = "Continue", cb = "Cancel", ds = "Cancel", bgc = (.8, .6, .6))
    return result


def checkCurrentMasterMatch(asset, fType, *args):
    """just a boolean to check whether the current scene's name lines up with the workshop format for the selected asset (in order to master)
        - asset would be name of asset for assets (ie. "man")
        - asset ==> the full name of the shot for shots (ie. "60174Bshot020_lgt_variantName")
        fType(string): "anm", "lgt", "fx", "geo", "rig", "mtl"

    """
    check = False
    currentScenePath = cmds.file(q=True, sceneName=True) #gets the full path
    currentScene = os.path.basename(currentScenePath)[:-8]
# ---------- fix this for type of asset (asset or shot var)
    if fType == "geo" or fType=="rig" or fType == "mtl":
        wsFormat = "{0}_{1}_ws".format(asset, fType)
    if fType == "anm" or fType == "lgt" or fType == "fx":
        wsFormat = "{0}_ws".format(asset)

    print "chrlxFuncs.checkCurrentMasterMatch: \ncurrentScene = {0}\nwsFormat = {1}".format(currentScene, wsFormat)
    if currentScene == wsFormat:
        check = True
    return(check)

def incrementWS(name, namePath, fType, *args):

    """
        takes in some info from the window and returns the full path to the next increment
        
        Args:
        name (string): asset or var name (i.e. "man" or "variantA")
        namePath (string): main asset or var folder (ie. ". . .JOB/3d_assets/characters/NAME/" or "...3d/shots/SHOT/TYPE/VAR/")
        fType (string): "geo", "rig", "mtl", "anm", "lgt", "fx"
        
        Return:
        string: the full path to the new increment
    """

    if fType == "geo" or fType == "rig" or fType == "mtl":
        latestWsPath = getLatestAssetWS(name, namePath, fType)

    if fType == "lgt" or fType == "fx" or fType == "anm":
        latestWsPath = getLatestVarWS(namePath)
    
    #if latestWsPath = None, then create a first path for newFile
    if latestWsPath:
        folder, doc = os.path.split(latestWsPath)
        num = int(doc.rpartition("_v")[2].rstrip(".ma"))

        base = doc.rpartition("v")[0]
        incr = num + 1
        newDoc = base + "v{:0>3d}".format(incr)
        newFile = "{0}/{1}".format(folder, newDoc)

    else:
    #split this between shot and asset - get rid of fType join in newFile and prepend with job number for SHOT STUFF
        if fType == "geo" or fType == "rig" or fType == "mtl":
            wsFile = "{0}_{1}_ws_v001".format(name, fType)
            newFile = "{0}/{1}/workshops/{2}".format(namePath, fType, wsFile)
        if fType == "anm" or fType == "lgt" or fType == "fx":
            pm = utils.PathManager(namePath)
            # jobNumb = pm.jobNumber
            # jobType = pm.jobType
            # shotLabel = os.path.basename(pm.shotPath)
            # wsFile = "{0}{1}{2}_{3}_{4}_ws_v001".format(jobType, jobNumb, shotLabel, fType, name)
            # newFile = "{0}/workshops/{1}".format(namePath, wsFile)
            newFile = pm.getNextWorkshop()

    return newFile


def getLastAssetMasterVersion(asset, assetPath, fType, *args):
    """
    given an asset base name and the master version folder path, return the latest master version file path

    Args: 
        asset (string): the name of the asset (ie. "man")
        assetPath (string): the path to the asset folder (ie. .../JOB/3d_assets/)
        fType (string): the type of asset (ie. "geo", "rig", "mtl")
    Return:
        string (path): returns the full path to the last backup version of the mastered Asset
    """

    #print "++++++ cFuncs.getLastAssetmasterVersion: asset:{0}\nassetpath: {0}\nfType: {0}".format(asset, assetPath, fType)

    if asset and assetPath and fType:

        ws = fnmatch.filter(os.listdir("{0}/{1}/past_versions".format(assetPath, fType)), "{0}_{1}_v[0-9]*.ma".format(asset, fType))
        
        #find the highest number WS
        sortNum = 0
        sortWS = "" #the file name of the last workshop file
        try:
            for x in range(0, len(ws)):
                #strip off the .ma, then get things after "_v". note this breaks if not named correctly!
                num = int(ws[x].rpartition("_v")[2].rstrip(".ma"))
                if num > sortNum:
                    sortNum = num
                    sortWS = ws[x]
        except:
            pass
            
        if sortWS:
            return "{0}/past_versions/{1}".format(assetPath,sortWS)
        else: 
            return None

    else:
        cmds.warning("chrlxFuncs.getLastAssetMasterVersion: you haven't given me all the args I need")
        return "Abort"

def getLatestVarMaster(var, varPath, fType, *args):
    """
    returns path to latest PAST VERSION of master file for shot variant

    Args:
        var (string): variant name (ie. "carDriving2")
        varPath(string): the path to the variant folder (ie. ...3d/shots/SHOT/VARIANT)
        fType(string): the type of shot (ie. "anm", "lgt", "fx")
    Return:
        string (path): the full path to the latest variant master (ie. ..."3d/shots/myShot/tunaJumping/past_versions/myfilename_v001.ma)
    """
    pm = utils.PathManager(varPath)
    shot = pm.shot

    if var and varPath and fType:

        mst = fnmatch.filter(os.listdir("{0}/past_versions".format(varPath)), "{0}_{1}_{2}_v[0-9]*.ma".format(shot, fType, var))

        #find the highest number WS
        sortNum = 0
        sortMst = "" #the file name of the last workshop file
        try:
            for x in range(0, len(mst)):
                #strip off the .ma, then get things after "_v". note this breaks if not named correctly!
                num = int(mst[x].rpartition("_v")[2].rstrip(".ma"))
                if num > sortNum:
                    sortNum = num
                    sortMst = mst[x]
        except:
            pass
            
        if sortMst:
            return fixPath("{0}/past_versions/{1}".format(varPath,sortMst))
        else: 
            return None

    else:
        cmds.warning("chrlxFuncs.getLastAssetMasterVersion: you haven't given me all the args I need")
        return "Abort"


def getVarMaster(varPath, *args):
    """
    check whether theres an var master file and returns full path

    Args:
        varPath (string): the full path to the variant folder (.../3d/shots/VAR/TYPE/)
    Return:
        string: full path to the current master of the variant
    """
    varPath = fixPath(varPath)
    fType = os.path.basename(varPath.rpartition(r"/")[0])
    varName = os.path.basename(varPath)
    pm = utils.PathManager(varPath)
    if pm:
        shot = pm.shot
        masterFile = pm.getMaster()
        if os.path.isdir(varPath) and (os.path.basename(masterFile) in os.listdir(varPath)):
            return(masterFile)

    else: return(None)


def createJobSpotIcon(currentProjectPath, iconType, *args):
    """
    Args:
        currentProjectPath (string): the path for the project your'e creating icon for
        iconType (string): "spotIcon" or "jobIcon" - determines where to put the image
    Return:
        None
    """

    result = cmds.confirmDialog(title="Create Icon", message="This will create a new icon for the {0}\nfrom the current open scene/frame.\nDo you want to proceed?\nNOTE: the other option is just to create\na 50x50px image and put it in appropriate folder\nJOB/3d_assets/ for jobIcon\nJOB/SPOT/3d/ for spotIcon".format(iconType), button=["yes", "no"], defaultButton="no", cancelButton="no", dismissString="no")

    pm = utils.PathManager(currentProjectPath)
    if pm.spotSchema == 2:
        if iconType == "spotIcon":
            name = fixPath(os.path.join(pm.spotPath, "3d", "spotIcon"))
        if iconType == "jobIcon":
            name = fixPath(os.path.join(pm.jobPath, "3d_assets", "jobIcon"))

        if os.path.isfile(name+".jpg"):
            ow = cmds.confirmDialog(title="Overwrite Existing?", message="An icon already exists. Should we overwrite?", button=["yes", "no"], defaultButton="no", cancelButton="no", dismissString="no")
            if ow=="no":
                return
            if ow=="yes":
                os.remove(name+".jpg")

        if result == "yes":
            im = cmds.playblast(filename = name, forceOverwrite = 1, orn = 0, fmt = "image", frame = cmds.currentTime(q=True), fp=4, v=0, c="jpg", wh=(154,154), p=100)
            nums = im.replace(".####", ".0000")
            base = im.rpartition(".####")
            os.rename(nums, base[0]+base[2])

        if result == "no":
            return

        if cmds.window("assetWin", exists=True):
            import chrlx_pipe.assetWin as ass
            ass.populateWindow()

        if cmds.window("shotWin", exists=True):
            import chrlx_pipe.shotWin as shotWin
            shotWin.populateWindow()


def createAssetIcon(refPath, asset, *args):
    """takes the char reference folder path and asset name, playblasts a frame and renames it correctly (PNG format)"""
    #Get directory and asset name
    fname = "{0}/{1}".format(refPath, asset)
#---------------- turn off curves display?
    im = cmds.playblast(filename = fname, forceOverwrite = 1, orn = 0, fmt = "image", frame = cmds.currentTime(q=True), fp=4, v=0, c="png", wh=(154,154), p=100)
#---------------- turn on curves display?
    # # now strip the padding
    nums = im.replace(".####", ".0000")
    base = im.rpartition(".####")
    os.rename(nums, base[0] + "Icon" + base[2]) 

  
def openFolderInExplorer(path, *args):
    """takes in path and opens it in os folder"""
    if os.path.isdir(path):
        if sys.platform == "win32":
            winPath = path.replace("/", "\\")
            browser.open(winPath)
        elif sys.platform == "darwin":
            pass
        elif sys.platform == "linux" or sys.platform=="linux2":
            pass


def moveFolder(source, target, *args):
    """moves a folder and contents to new location"""
    #get asset folder 
    # use shutil.copytree(src, dst)
    if source and target:

        #####  test if the desitnation folder already exists, flash option to overwrite? 
        # shutil.copytree(source, target)
        shutil.move(source, target)

        return "Moved - asset: \n{0}\nTo - Destination:\n{1}".format(source, target)
    else: 
        return "chrlxFuncs.moveFolder: wasn't given two paths to move"

        if cmds.window("assetWin", exists=True):
            import chrlxPipe.assetWin as assWin
            assWin.populateWindow(asset)


def getLightList(*args):
    """
    returns all lights in the scene
    Args:
        none
    Return:
        list: a list of all lights in a scene
    """

    lgtShp = cmds.ls(type="light")
    lights = []

    if lgtShp:
        for shp in lgtShp:
            obj = cmds.listRelatives(shp, p=True)[0]
            lights.append(obj)

    return lights


def getCamList(*args):
    """
    returns all cams (not default) in scene
    Args:
        none
    Return:
        list: a list of all the cameras in the scene
    """

    camShps = cmds.ls(type="camera")
    cams = []
    camList = ["front", "persp", "side", "top"]
    
    if camShps:
        for cam in camShps:
            obj = cmds.listRelatives(cam, p=True)[0]
            if obj not in camList:
                cams.append(obj)
            
    return cams


def removeNamespace(*args):
    """looks in the current scene and removes namespaces"""
    defaults = ['UI', 'shared']

    def num_children(ns): #function to used as a sort key
        return ns.count(':')

    namespaces = [ns for ns in cmds.namespaceInfo(lon=True, r=True) if ns not in defaults]

    namespaces.sort(key=num_children, reverse=True) # reverse the list

    for ns in namespaces:
        try:
            #get contents of namespace and move to root namespace
            cmds.namespace(mv=[ns, ":"])
            
            cmds.namespace(rm=ns)
        except RuntimeError as e:
            # namespace isn't empty, so you might not want to kill it?
            pass
    return(namespaces)


def mstCtrlTemplate(*args):
    """creates a master control template object for geo scenes"""
    mstCtrl = cmds.curve(n="ctrlSizeTemplateCrv", d=1, p=[[0.045038530330620184, 0.25951525008201387, -5.210460506620644], [1.3936049431985766, 0.2595152500820137, -5.032918370204105], [2.650268783640949, 0.2595152500820139, -4.512391164149015], [3.7293904876667763, 0.25951525008201365, -3.684351957336151], [4.557429694479641, 0.25951525008201354, -2.60523025331032], [5.077956900534729, 0.25951525008201354, -1.3485664128679486], [5.255499036951263, 0.25951525008201354, 3.832412260469572e-15], [5.077956900534727, 0.2595152500820132, 1.348566412867956], [4.5574296944796355, 0.25951525008201354, 2.605230253310326], [3.729390487666771, 0.25951525008201337, 3.6843519573361547], [2.650268783640938, 0.2595152500820134, 4.512391164149018], [1.3936049431985678, 0.2595152500820136, 5.032918370204106], [0.04503853033061642, 0.2595152500820139, 5.210460506620647], [-1.3035278825373362, 0.259515250082014, 5.032918370204104], [-2.560191722979707, 0.2595152500820138, 4.512391164149014], [-3.639313427005534, 0.2595152500820142, 3.684351957336151], [-4.467352633818398, 0.2595152500820135, 2.6052302533103218], [-4.987879839873487, 0.2595152500820144, 1.3485664128679502], [-5.165421976290027, 0.25951525008201404, -1.5546578037753924e-15], [-4.987879839873485, 0.2595152500820145, -1.3485664128679529], [-4.467352633818397, 0.25951525008201376, -2.6052302533103235], [-3.6393134270055336, 0.25951525008201437, -3.6843519573361525], [-2.5601917229797033, 0.25951525008201387, -4.512391164149015], [-1.3035278825373326, 0.259515250082014, -5.032918370204103], [0.045038530330620184, 0.25951525008201387, -5.210460506620644], [0.04503853033061907, -0.25951525008201276, -5.210460506620644], [1.3936049431985753, -0.2595152500820128, -5.032918370204105], [2.6502687836409473, -0.2595152500820128, -4.512391164149015], [3.7293904876667785, -0.2595152500820133, -3.684351957336151], [4.55742969447964, -0.25951525008201276, -2.60523025331032], [5.07795690053473, -0.2595152500820132, -1.3485664128679486], [5.255499036951268, -0.2595152500820131, 3.832412260469572e-15], [5.255499036951263, 0.25951525008201354, 3.832412260469572e-15], [5.255499036951268, -0.2595152500820131, 3.832412260469572e-15], [5.077956900534729, -0.25951525008201354, 1.348566412867956], [4.5574296944796355, -0.259515250082013, 2.605230253310326], [3.7293904876667727, -0.25951525008201326, 3.6843519573361547], [2.6502687836409393, -0.2595152500820128, 4.512391164149018], [1.3936049431985689, -0.25951525008201337, 5.032918370204106], [0.04503853033061624, -0.25951525008201304, 5.210460506620647], [0.04503853033061642, 0.2595152500820139, 5.210460506620647], [0.04503853033061624, -0.25951525008201304, 5.210460506620647], [-1.3035278825373373, -0.259515250082013, 5.032918370204104], [-2.560191722979707, -0.25951525008201276, 4.512391164149014], [-3.639313427005533, -0.2595152500820126, 3.684351957336151], [-4.467352633818397, -0.2595152500820125, 2.6052302533103218], [-4.987879839873487, -0.2595152500820122, 1.3485664128679502], [-5.165421976290028, -0.25951525008201276, -1.5546578037753924e-15], [-5.165421976290027, 0.25951525008201404, -1.5546578037753924e-15], [-5.165421976290028, -0.25951525008201276, -1.5546578037753924e-15], [-4.987879839873485, -0.25951525008201226, -1.3485664128679529], [-4.467352633818397, -0.2595152500820125, -2.6052302533103235], [-3.639313427005532, -0.2595152500820127, -3.6843519573361525], [-2.560191722979703, -0.25951525008201204, -4.512391164149015], [-1.303527882537332, -0.2595152500820125, -5.032918370204103], [0.04503853033061907, -0.25951525008201276, -5.210460506620644]])
    cmds.rename(cmds.listRelatives(mstCtrl, s=True)[0], "{0}Shape".format(mstCtrl))
    cmds.select(clear=True)
    
    for a in ["tx", "ty", "tz", "rx", "ry", "rz"]:
        cmds.setAttr("{0}.{1}".format(mstCtrl, a), k=False)
    cmds.setAttr("{0}.overrideEnabled".format(mstCtrl), 1)
    cmds.setAttr("{0}.overrideColor".format(mstCtrl), 13)

def putFileInfo(fType = "", wsNum = 000, note = "", *args):
    """
    modifies the open scene's file info:
        info keys that will change: 'FILETYPE', 'USER', 'WORKSHOP', 'DATE', 'CHARLX_NOTE'
    Args:
        fType (string): "geo", "rig", "lgt", "anm", "fx", ["mtl"?]
        [user will get info from open scene]
        wsNum (int, 3pad): workshop num (###)
        [date will get from open scene]
        note (string): some text string
    Return: 
        none
    """
    user = mel.eval("getenv USER")
    date = cmds.date()

    cmds.fileInfo("FILETYPE", fType)
    cmds.fileInfo("USER", user)
    cmds.fileInfo("WORKSHOP", wsNum)
    cmds.fileInfo("DATE", date)
    cmds.fileInfo("CHRLX_NOTE", note)

    FPS = ""
    RESW = 1920
    RESH = 1080
    FRANGE = "1-200"

    if fType == "anm" or fType == "lgt" or fType== "fx":
        FPS = cmds.currentUnit(q=True, time=True)
        cmds.fileInfo("FPS", FPS)

        RESW = cmds.getAttr("defaultResolution.width")
        RESH = cmds.getAttr("defaultResolution.height")
        cmds.fileInfo("RESOLUTION", "{0}-{1}".format(RESW, RESH))

        FRANGEMIN = cmds.playbackOptions(q=True, min=True)
        FRANGEMAX = cmds.playbackOptions(q=True, max=True)
        cmds.fileInfo("FRAMERANGE", "{0}-{1}".format(FRANGEMIN, FRANGEMAX))


def getFileFrameInfo(refFilePath, *args):
    """
    this creates a dictionary of both the passed scene and the current scene's frame related info
     -to be used primarily in updating lighting shots to conform to anim
     -when the values match, they are excluded from the return
     Args:
     	refFilePath (string): the path to (presumably) the referenced file to compare to our current one
     Return:
     	dictionary: returns a dict of ONLY the attributes(key)["RESOLUTION", "FPS", "FRAMERANGE"] and list (values)
     	of the 1. passed file and 2. current scene, only when values differ
    """
    # get this from the imported file (should read file instead)
    refDict = getInfoDict(refFilePath)

    currRes = ""
    currFps = ""
    currRng = ""

    min = float(cmds.playbackOptions(q=True, min=True))
    max = float(cmds.playbackOptions(q=True, max=True))
    w = cmds.getAttr("defaultResolution.width")
    h = cmds.getAttr("defaultResolution.height")

    currRes = "{0}-{1}".format(w, h)
    currRng = "{0}-{1}".format(min, max)
    currFps = cmds.currentUnit(q=True, time=True)

    # compare the two
    refResR = refDict['"RESOLUTION"']
    refFpsR = refDict['"FPS"']
    refRngR = refDict['"FRAMERANGE"']
    refRes = refResR.strip(";\n").strip('"')
    refFps = refFpsR.strip(";\n").strip('"')
    refRng = refRngR.strip(";\n").strip('"')

    fieldsToPass = {}
    if currRes != refRes:
        fieldsToPass["RESOLUTION"] = [refRes, currRes]

    if currFps != refFps:
        fieldsToPass["FPS"] = [refFps, currFps]
    
    if currRng != refRng:
        fieldsToPass["FRAMERANGE"] = [refRng, currRng]

    return fieldsToPass


def getInfoDict(filePath, *args):
    """
    given a full path, will get the file info for a maya file and return the info as a dictionary
    Args:
        filePath (string): the path to the file we're checking . . . 
    Return:
        dictionary: a dict of the fileInfo parameters and their values ("name":"value")
    """

    infoDict = {}
    
    with open(filePath) as x:
        for line in x:
            found = False
            if "fileInfo" in line:
                lineList = []
                lineList = line.split(" ") 
                info = " ".join(lineList[2:])
                infoDict[lineList[1]] = info
                found = True
            else:
                if found:
                    break
        if infoDict:
            return infoDict
        else:
            return None


def projectCheck():
    """
    if project is the correct schema (via chrlx.utils), then return "good", else return 'None'
    Args:
        none
    Return:
        string: "good" or None
    """
    proj = getCurrentProject()
    pm = utils.PathManager(proj)
    check = pm.spotSchema

    if check == 2:
        return("good")
    else:
        return(None)


def crvsToAllkeyable(mst=None):
    """
    for rig mastering. This will put all crvs under the master into all keyable set
    mst -> the node we're assuming is the top node to look under
    Args:
        mst (string): the node we want to look under for all crvs to be put into the scene
    Return:
        none
    """
    if not mst:
        mst = "GOD"
    if cmds.objExists(mst):
        children = cmds.listRelatives(mst, ad=True, s=False)
        crvs = []
        if children:
            for chld in children:
                if cmds.objectType(chld) == "transform":
                    shp = cmds.listRelatives(chld, s=True)
                    if shp and cmds.objectType(shp[0]) == "nurbsCurve":
                        crvs.append(chld)

        for crv in crvs:   
            cmds.sets(crv, e=True, fe="ALLKEYABLE" )


def getSpotAssetList(assFolder):
    """return list of all assets in a spot folder (incl arched assets). NOT paths, just asset names
        -assFolder is the assetFolder under 3D in a spot folder
    """
    #print "cfuncs.getSpotAssetList (568): assFolder = {0}".format(assFolder)
    if assFolder:
        assets = []
        types = ["characters", "props", "sets"]
        for assType in types:
            assTypeFolder = "{0}/{1}".format(assFolder, assType)
            comps = os.listdir(assTypeFolder)
            comps.remove("archive")
            for comp in comps:
                assets.append(comp)
            archiveFolder = "{0}/archive".format(assTypeFolder)
            archs = os.listdir(archiveFolder)
            for arch in archs:
                assets.append(arch)
        return(assets)
    else:
        return(None)


def getSpotShotList(shotsFolder, *args):
    """return list of all shots in the given folder. NOT paths, just shot names
        -shotsFolder arg is the ".../SPOT/3d/shots" folder under 3D in a spot folder 
    """
    shots = []
    if shotsFolder and os.path.isdir(shotsFolder):
        exclude = ["archive"] # any folders we should skip in search
        shots = [x for x in (os.listdir(shotsFolder)) if (x not in exclude)]
    return shots


def getShotVariantList(shotFolder, *args):
    """
    return list of all variant names in a given shot
    Args:
        shotFolder (string): the ".../SPOT/3d/shots/SHOT/TYPE" folder (ie. a specific shot anm/lgt/fx folder)
    Return:
        list: list of all variant names in a given shot
    """
    variants = []
    if shotFolder:
        exclude = ["reference", "sourceImages", "import_export", "archive", "fx_data", "houdini"] # any folders we should skip in search
        variants = [x for x in os.listdir(shotFolder)]
        if variants:
            variants = list(set(variants)-set(exclude))
            variants.sort()
    return variants


def getSpotVariantList(spotShotPath, *args):
    """
    returns names of all created variants for a particular spot (anm, lgt and fx)
    Args:
        spotShotPath (string): spot path - "...SPOT/3D/shots"
    RETURNS:
        list: a list of all variants in the given shot path. includes anm, lgt, fx
    """
    variants = []
    types = ["anm", "lgt", "fx"]
    shots = getSpotShotList(spotShotPath)
    for shot in shots:
        shotFolder = fixPath(os.path.join(spotShotPath, shot))
        print "cFuncs.getSPotVariantList.shotFolder:", shotFolder
        for t in types:
            vs = getShotVariantList(fixPath(os.path.join(shotFolder, t)))

            if vs:
                for v in vs:
                    variants.append(v)
    return(variants)


def getFilesInPath(path):
    """
    returns a list of files only in a path
    Args:
        path (string): a directory
    Return:
        list: list of files in that directory

    """
    files = []
    for obj in os.listdir(path):
        if os.path.isfile(os.path.join(path, obj)):
            files.append(fixPath(os.path.join(path, obj)))

    return files


def replaceTextInFile(filePath, searchTxt, replaceTxt):
    """opens the file and replaces [searchTxt] with [replaceTxt] in place in the file"""

    fileData = None
    with open(filePath, "r") as file:
        # fileData = file.read()
        fileData = fileData.replace(searchTxt, replaceTxt)
    
    with open(filePath, "w") as file:
        file.write(fileData)


def getTopNodes(objects = [], *args):
    """
    from given list of objects return a list of the top nodes in DAG hierarchy
    Args:
        objects (list): list of scene objects
    Return:
        list: any top nodes of the given objects 
    """	
    roots = []
    
    for objs in objects:
        obj = ""
        if cmds.objectType(objs)=="transform":
            obj = cmds.ls(objs, l=True, dag=True)[0]
        if obj:
            root = (obj.split("|")[:2])
        if root:
            if len(root) > 1 and root[1] not in roots:
                roots.append(root[1])

    return(roots)


def assetImageUI(imagePath, *args):
    """
    passed a 154x154 image, this will show it in a small win
    Args:
        imagePath (string): path to the image
    Return:
        none
    """

    if cmds.window("assetImageWin", exists=True):
        cmds.deleteUI("assetImageWin")
        
    imageWin = cmds.window("assetImageWin", wh=(154, 154))
    cmds.columnLayout(w=154, h=154)
    cmds.image(image=imagePath)
    
    cmds.showWindow(imageWin)
    
    # ----------- position the window on the screen? ? 
    #cmds.window(imageWin, e=True, tlc = (480, 800))	
    #assetImageUI(r"//Bluearc/GFX/jobs/charlex_testAreaB_T60174/3D_assets/characters/raspberryA/icon/raspberryAIcon.png")


def createAssetDirectories(assetFolder, assType, name, *args):
    """creates asset directories from args
    Args:
        asset folder (string): path to asset folder [...JOB/3D_assets/]
        assType (string): either "characters", "props", or "sets"
        name (string): string name of the new character
    Return:
        none
    """

    assetFolder = fixPath("{0}/{1}/{2}".format(assetFolder, assType, name))
    if not os.path.isdir(assetFolder):
        print "------making {0}".format(assetFolder)
        os.makedirs(assetFolder)
        assetContents = ["geo", "rig", "mtl", "sourceImages", "reference", "icon"]
        for direct in assetContents:
            assDirect = "{0}/{1}".format(assetFolder, direct)
            print "------making {0}".format(assDirect)
            os.makedirs(assDirect)
        geoContents = ["import_export", "past_versions", "workshops"]
        for direct in geoContents:
            geoDirect = "{0}/geo/{1}".format(assetFolder, direct)
            print "------making {0}".format(geoDirect)
            os.makedirs(geoDirect)
        geoWSContents = ["max", "mudbox", "zbrush"]
        for direct in geoWSContents:
            WSDirect = "{0}/geo/workshops/{1}".format(assetFolder, direct)
            print "------making {0}".format(WSDirect)
            os.makedirs(WSDirect)
        rigContents = ["import_export", "past_versions", "workshops"]
        for direct in rigContents:
            rigDirect = "{0}/rig/{1}".format(assetFolder, direct)
            print "------making {0}".format(rigDirect)
            os.makedirs(rigDirect)
        mtlContents = ["import_export", "past_versions", "workshops"]
        for direct in mtlContents:
            mtlDirect = "{0}/mtl/{1}".format(assetFolder, direct)
            os.makedirs(mtlDirect)

    else:
        print "The directory already exists: {0}".format(assetFolder)

def createVariantDirectories(shotFolder, varType, name, *args):
    """
    creates variant directories from args
    Args:
        shotFolder (string): shot folder is path to the shot folder under 3D [JOB/3D/Shots/SHOT]
        assType (string): either "characters", "props", or "sets"
        name (string): name of the new character
    Return:
        none
    """
    variantFolder = fixPath("{0}/{1}/{2}".format(shotFolder, varType, name))
    if not os.path.isdir(variantFolder):
        print "------making {0}".format(variantFolder)
        os.makedirs(variantFolder)
        variantContents = ["workshops", "past_versions", "icon"]
        for direct in variantContents:
            varDirect = "{0}/{1}".format(variantFolder, direct)
            print "------making {0}".format(varDirect)
            os.makedirs(varDirect)
    else:
        print "This directory already exists: {0}".format(variantFolder)


def chrlxFileOpen(filePath, *args):
    """
    opens the given file path with check whether the scene isn't being read properly because of the absence of the arnold plugin. 
    Looks whether the scene recognizes itself and if it doesn't, then offer option to resave the scene over itself 
    (with whatever options are in the current scene)
    if asset: workshops will increment,masters will overwrite, both will then open
    if shot: workshops will increment and open, master will NOT open
    Args:
        filePath (string): the full patht to the file we're trying to open
    Return:
        none

    """

    changed = cmds.file(q=True, modified = True)
    if changed:
        save = saveDialog()
        if save=="save":
            #save
            cmds.file(save=True)
            print "saving current. . . "
            
        elif save == "noSave":
            print "not saving current. . ."

        elif save=="cancel":
                cmds.warning("Cancelling open operation")
                return
    try:
        cmds.file(filePath, open=True, f=True)

    except Exception, e:
        print "this is the error", e
        # look for ""
        if fnmatch.filter(e, "*ai*"):
            # check if the file recognizes itself
            fileCheck = cmds.file(q=True, sceneName=True)
            # if not, call up the confirm dialog(?) and give option to save over or abort 
            if not fileCheck:
                result = cmds.confirmDialog(title="Arnold Plug-in Issue!", message="Do you want to increment (ws) or overwrite (mst)\n the scene WITHOUT the arnold elements?\nNOTE: You CANNOT work on shot master files!\n", button=["yes", "no"], defaultButton="no", cancelButton="no", dismissString="no")
                # if we say yes, determine type of shot and whether ws or master and act accordingly
                if result == "yes":
                    path = utils.PathManager(filePath)
                    if type(path)==utils.AssetPath:
                        # print "this is an asset"
                        if path.isWorkshop:
                            next = path.getNextWorkshop()
                            # rename scene to next and save
                            cmds.file(rename=next)
                            cmds.file(save=True, type="mayaAscii")
                        if path.isMaster:
                            # print "and we're in a master"
                            cmds.file(rename=filePath)
                            cmds.file(save=True, type="mayaAscii")
                    elif type(path)==utils.shotPath:
                        # print "this is a shot"
                        if path.isWorkshop:
                            # print "and we're in a workshop"
                            next = path.getNextWorkshop()
                            cmds.file(rename=next)
                            cmds.file(save=True, type="mayaAscii")
                        if path.isMaster:
                            print "and we're in a master"
                            cmds.confirmDialog(title="Sorry!", message="You need to get to a computer with Arnold!\n You're not allowed to mess with shot masters!")
                            cmds.file(new=True, f=True)
                    else:
                        # print "we're not in the pipeline"
                        cmds.file(rename=filePath)
                        cmds.file(save=True, type="mayaAscii")

                if result == "no":
                    cmds.file(new=True, force=True)

    if cmds.window("assetWin", exists=True):
        import chrlx_pipe.assetWin as ass
        ass.populateWindow()
    
    if cmds.window("shotWin", exists=True):
        import chrlx_pipe.shotWin as shotWin
        shotWin.populateWindow()


def exportAnimation(fullPath, *args):
    """
    exports the selected objects as an .atom file to the given path
    Args:
        fullPath (string): this is the path where we will save the atom file. This CAN include the default filename by just appending it to end of dirpath
    Return:
        string: the file path we've created or None
    """
    if not (cmds.pluginInfo("atomImportExport", q=True, loaded=True)):
        print "===== trying to load atom plugin. . . ====="
        cmds.loadPlugin("atomImportExport.mll", quiet=True)
        print "===== atom plugin loaded! ====="
        
    sel = cmds.ls(sl=True) # just get transforms?
    destinationRaw = cmds.fileDialog2(fm=0, dir=fullPath)
    if destinationRaw:
        destination = destinationRaw[0]
#---------------- try/except here
        options = "precision=8;selected=selectedOnly;sdk=0;statics=1;whichRange=1; useChannelBox=1;hierarchy=none;animLayers=1;whichRange=1;options=keys;baked=0"
        cmds.file(destination, type="atomExport", exportSelected=True, options=options)


def importAnimation(dataPath, *args):
    """
    Args:
        dataPath (string): the full path of the anim atom file
    Return:
        None
    """
    if not (cmds.pluginInfo("atomImportExport", q=True, loaded=True)):
        print "===== trying to load atom plugin. . . ====="
        cmds.loadPlugin("atomImportExport.mll", quiet=True)
        print "===== atom plugin loaded! ====="

    sel = cmds.ls(sl=True)

    impPathRaw = cmds.fileDialog2(fm=1, dir=dataPath)
    
    if impPathRaw:
        impPath = impPathRaw[0]

        options="targetTime=3;option=insert;match=hierarchy;selected=selectedOnly"
        cmds.file(impPath, i=True, renameAll=True, type="atomImport", options=options)    

def refToLocation(refPath, node, *args):
    """
    references in a file and sticks it's top node at the location of the given node
    Args:
        refPath (string): the path to the reference file we want to import
        node (string): the name of the node whose position, rotation(?) we're matching to
    Return:
        none
    """
    # get loc and pos of the node
    pos = cmds.xform(node, q=True, ws=True, rp=True)
    rot = cmds.xform(node, q=True, ws=True, ro=True)

    # ref in the file
    if not os.path.isfile(refPath):
        cmds.warning("cFuncs.refToLocation: Can't find a file at path:", refPath)    
    
    refName = referenceInWithNamespace(refPath)
    ns = cmds.file(refName, q=True, ns=True)

    # get the top node of the ref file
    cmds.select(cl=True)
    cmds.select("{0}:ALLKEYABLE".format(ns))
    selList = cmds.ls(sl=True)

    # move the top to the node
    if selList:
        top = getTopNodes(selList)

        if len(top)==1:
            cmds.xform(top, ws=True, t=pos)
            cmds.xform(top, ws=True, ro=rot)
        else:
            cmds.warning("There is more than one top node in this reference rig! Make sure things are under the god node in the rig file!")
        if cmds.window("shotWin", exists=True):
            import chrlx_pipe.shotWin as shotWin
            shotWin.populateWindow()
    else:
        cmds.warning("I couldn't find an ALLKEYABLE set in this file! Make sure the rig is set up properly!")