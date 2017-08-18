import os
import getpass
import logging
import glob
from pprint import pprint
import re
import sys

import chrlx
from chrlx.utils import PathManager, CompPath, PathInterface, PathManagerInterface, ShotPath, PathBase, ConfigPath, AssetPath
import chrlx.utils as utils
import copyShot
from chrlx.model.jobs import QueuedShotCopy, Shot

def callOnce(func):
    def new_func(*args,**kwargs):
        if not new_func._called:
            new_func._called=True
            return func(*args, **kwargs)
    new_func._called=False
    return new_func

@callOnce
def setLog(logFile, loglevel="INFO"):
    if logFile:
        lineLog_handler = logging.FileHandler(filename=logFile, mode='w')
        lineLog_handler.setLevel(0)
        lineLog_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        copyShot.lineLog.addHandler(lineLog_handler)
        copyShot.log.addHandler(lineLog_handler)

    debug_handler = logging.StreamHandler()
    debug_handler.setLevel(getattr(logging, loglevel))
    debug_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    copyShot.log.addHandler(debug_handler)
    copyShot.lineLog.addHandler(debug_handler)
def getId(fromshot, toshot):
    fromshot=PathManager(fromshot)
    toshot=PathManager(toshot)
    if not toshot.shotNumber:
        toshot.shotNumber=0
    name="{fromshot}__{tospot}{toshotstage}{toshotnumber:03d}.log".format(
                                                        fromshot=str(fromshot.shot).replace("/", ""),
                                                        tospot=str(toshot.spot).replace("/",""),
                                                        toshotstage=toshot.shotStage,
                                                        toshotnumber=toshot.shotNumber)
    path=os.path.join(chrlx.PATHS['CHRLX_3D_LOG'],"copyshot")
    next = 5000
    currentCopies=glob.glob(os.path.join(path, "5???_"+name))
    if currentCopies:
        next = int(os.path.basename(max(currentCopies))[:4])+1
    return next, os.path.join(path, "{0:04d}_".format(next)+name)

def copy_assets(assetBundle, frompath, topath, user=getpass.getuser()):
    frompath=PathManager(frompath)
    topath=PathManager(topath)
    setLog(getId(frompath, topath)[1])
    copyShot.copy_assets(assetBundle, frompath, topath, user)
def copy_comps(nukefilenames, fromshot, toshot, change_reads=1):
    setLog(getId(fromfile, toshot)[1])
    fromshot.change_reads=change_reads
    fromshot.compfile=files
    fromshot.folder=0

    files = copyShot._find_compfiles(fromshot, toshot.shot)
    for comp in files:
        copyShot.copy_convert_compfile(comp, fromshot.shot, toshot.shot)
def copy_file(copyFile, toshot, settingsShotName=None, change_nuke_reads=False):
    fromfile = PathManager(copyFile)
    toshot = PathManager(toshot)
    if not fromfile:
        print "Error reading copyFile."
        return
    if not toshot:
        print "Error reading toshot."
        return
    setLog(getId(fromfile, toshot)[1], loglevel="DEBUG")

    attrs=dict(vars(fromfile.restored.pm))
    del attrs["path"]
    del attrs["obj"]
    filtered_attrs = dict((key, attrs[key]) for key,value in attrs.iteritems() if isinstance(value, str))
    dest, pathType=copyShot.updatePath(fromfile.restored, fromfile.restored, filtered_attrs, toshot)

    if isinstance(dest, AssetPath):
        toname=fromfile.name
        totype=fromfile.typ
        toasset=utils.AssetPath(toshot)
        if toasset.name:
            toname=toasset.name
        if toasset.typ:
            totype=toasset.typ
        copy_assets([fromfile.typ, fromfile.name, totype, toname], fromfile, toshot)
    else:
        #check if shot exists
        if toshot.shotName not in [shot.shotName for shot in toshot.spot.shots]:
            if settingsShotName==None:
                print "Destination {shotName} does not exist.  Provide a source shotName(ex. settingsShotName=shot010) to copy shot settings(fps,startframe,res...) from. [settingsShotName=0 for default shot settings]".format(shotName=toshot.shotName)
                return
            #immitate a queue copy shot object
            toshot.uid=getpass.getuser()
            toshot.shotnum=toshot.shotNumber
            toshot.toshotstage=toshot.shotStage
            toshot.overwrite=False
            if settingsShotName==0:
                fps=Shot.fps.default.arg
                start_frame=Shot.start_frame.default.arg
                end_frame=Shot.end_frame.default.arg
                camera=Shot.camera.default.arg
                resolution=Shot.resolution.default.arg
            else:
                fromshot=PathManager(os.path.join(fromfile.spotPath,settingsShotName))
                fps=fromshot.shot.fps
                start_frame=fromshot.shot.start_frame
                end_frame=fromshot.shot.end_frame
                camera=fromshot.shot.camera
                resolution=fromshot.shot.resolution
            toshot.shot.fps=fps
            toshot.shot.start_frame=start_frame
            toshot.shot.end_frame=end_frame
            toshot.shot.camera=camera
            toshot.shot.resolution=resolution

            newshot = copyShot.create_new_shot(toshot)

        copyShot.smartCopy(fromfile, dest, change_nuke_reads=change_nuke_reads)
def copy_shot(fromshot, tospot, shotname, uid=getpass.getuser(), compfiles="", change_reads=True, animcopy=True, force=False):
    fromshot = PathManager(fromshot)
    tospot = PathManager(tospot)
    toshot = tospot.override(shot=shotname)

    copyShot.copy_shot(QueuedShotCopy(
        uid = uid,
        compfile = ",".join(compfiles),  #comma seperated nuke file names
        change_reads = change_reads,     #change nuke's file read nodes (default is to change writes and version_control node only)
        animcopy = animcopy,             #copy the animworkshop, animmaster and chars (default is to skip if overwriting a shot)
        force = force,                   #allow overwriting files (chars never get overwritten)

        shot = fromshot.shot,            #add proxy shot to mimic db
        shotid = fromshot.shot.id,
        spot = toshot.spot,              #add proxy spot to mimic db
        spotid = toshot.spot.id,
        toshotstage = toshot.shot.stage,
        shotnum = toshot.shot.shot,

        folder = None,
        overwrite = os.path.exists(toshot.shot.path),
        id=getId(fromshot, toshot)[0],
    ))
