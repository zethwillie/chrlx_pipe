#create the directories for a new character

import maya.cmds as cmds
import os
import charlexProj.chrlxFuncs as func

# make this whole thing able to accept mulitple inputs so you can batch the process (at least the functional parts)

#get current project
proj = cmds.workspace(q=True, act=True)
#is the current project a job/shot? Then you should be in "scenes" under job
#if not, flash a dialogue asking if they want to continue

#the result goes here
#get the character name, check for existing character names and no numbers first or last
name = ""

#from project create the character folders

#ask what kind of asset (char, prop, set). Might not matter for now
#create folders for 2015 setup. . .
#pull name from dialogue

#function to create list of directories from the basic info, clean them here or later
###############
#charRoot = PROJECT/scenes/master/char/
#under that we have "geo" and "rig" folders, as well as "shaders", "mtl", and "sourceImage" folders
################
charRoot = os.path.join(proj, "scenes/master/char", name)
charGeo = os.path.join(charRoot, "geo")
charRig = os.path.join(charRoot, "rig")
charRef = os.path.join(charRoot, "reference")
shaders = os.path.join(charRoot,"shaders")
sIm = os.path.join(charRoot,"sourceImages")
mtl = os.path.join(charRoot,"mtl")
gversions = os.path.join(charGeo, "versions")
rversions = os.path.join(charRig, "versions")
rws = os.path.join(charRig, "workshop")	
gws = os.path.join(charGeo, "workshop")


dirs = [charRoot, charGeo, charRef, charRig, shaders, sIm, mtl, gversions, rversions, rws, gws]

#######confirm dialogue, check project!
for path in dirs:
	#clean each name
	clean = func.fixpath(path)
	#create folders from charFolders keys
	os.makedirs(clean)
	print "Just created folder: %s"%clean



