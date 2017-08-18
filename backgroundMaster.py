import sys, os, datetime, getpass
from maya.standalone import initialize, uninitialize
import maya.cmds as cmds

root = os.environ.get("chrlx_3d_root") 
#print root
mayascripts_raw = "{}/maya/maya2016/scripts".format(root)
mayascripts = mayascripts_raw.replace("\\", "/")
#print "the append path should be: {}".format(mayascripts)
sys.path.append(mayascripts)

import chrlx_pipe.masterFuncs as mFuncs

def backgroundMaster(fType, variant, variantFolder, newWSFile, destination, currentMaster, *args):
    """
    variant is var name []
    variantFolder is path to variant [. . .shots/SHOT/TYPE/VARIANT]
    newWSFile is the most recent ws of that variant
    destination is the full path to the proposed latest pastVersion of the master (incremented version of master in past_versions)
    currentMaster is the full path to the master we'll be creating
    """

    #set up the log file
    saveout = sys.stdout
    fsock = open("{0}/{1}_masterLog.log".format(variantFolder, variant), "w")
    sys.stdout = fsock
    sys.stderr = fsock
    # print getpass.getuser()
    # print datetime.datetime.now()

    print "backgroundMaster.newWSFile:", newWSFile
    print "backgroundMaster.destination:", destination
    print "backgroundMaster.currentMaster:", currentMaster
    
    print "-------starting mastering------"

    initialize("python")
    print "== initialized python"

 ##########################--------- fix below for mastering. . .. 
 	# get latest variant WS path (newWSFile)
 	# get past variant master path (destination)
 	# get variant master path (currentMaster)

    # open latest ws file, call clean(?), rename and save as currentMaster, DON"T INCREMENT WS AFTERWARDS. This will happen in masterFuncs
    cmds.file(newWSFile, open=True, force=True)
    mFuncs.cleanShotScene(fType, BG=False, importRefs=True)

    #load the refs

    cmds.file(rename=currentMaster)	
    if os.path.isfile(currentMaster): #check if there is a master file currently. If so, move it to the past versions
        os.rename(currentMaster, destination)
        print "masterFuncs.masterShot:\n------ moving: {0} \n------ to: {1}".format(currentMaster, destination)
    cmds.file(save=True, type="mayaAscii") # save as master
    cmds.file(newFile=True, force=True)

    print "== mastered variant file"

    uninitialize()
    return("completed")

    print "== closing socket"
    #close out the log file
    sys.stdout = saveout
    fsock.close()

backgroundMaster(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
