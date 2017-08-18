import maya.cmds as cmds

def copySkinning(*args):
    """
    select the orig bound mesh, then the new unbound target(s) mesh and run
    Args:
        None
    Return:
        None    
    """
    sel = cmds.ls(sl=True)
    if sel and len(sel)>1:
        orig = sel[0]
        targets = sel[1:]

        for target in targets:
            #get orig obj joints
            try:
                jnts = cmds.skinCluster(orig, q=True, influence = True)
            except Exception, e:
                cmds.warning("rigFuncs.copySkinning: --------Couldn't get skin weights from {0}\n{1}".format(orig, e))

            #bind the target with the jnts
            try:
                targetClus = cmds.skinCluster(jnts, target, bindMethod=0, skinMethod=0, normalizeWeights=1, maximumInfluences = 3, obeyMaxInfluences=False, tsb=True)[0]
                print targetClus
            except Exception, e:
                cmds.warning("rigFuncs.copySkinning: --------Couldn't bind to {0}\n{1}".format(target, e))
                    
            origClus = mel.eval("findRelatedSkinCluster " + orig)

            #copy skin weights from orig to target
            try:
                cmds.copySkinWeights(ss=origClus, ds=targetClus, noMirror=True, sa="closestPoint", ia="closestJoint")
            except Exception, e:
                cmds.warning("rigFuncs.copySkinning: --------Couldn't copy skin weights from {0} to {1}\n{2}".format(orig, target, e))
    else:
        cmds.warning("You need to select a skinned piece of geo and and geo to transfer the skin weights to. . .")

def dupeReffedGeo(referenceFile, *args):
    """
    gets the reference for the geo master file and duplicates the geo (in place where ref is)
    Args:
        referenceFile(string): the path to the reference file we're lookign at (geo master)
    Return: 
        string: the group the contains our new duped geo
    """

#---------------- NOTE: this isn't checking that the ref is our geo file. Should do that. . . maybe get ref file and then path manager to get geo master file and compare to that
    # get geo in reference as list
    ourGeo = []
    refGeo = cmds.referenceQuery(referenceFile, nodes=True)
    refXform = cmds.ls(refGeo, type="transform")
    for x in refXform:
        if cmds.listRelatives(x, s=True):
            if cmds.objectType(cmds.listRelatives(x,s=True)) == ("mesh" or "nurbsSurface" or "nurbsCurve"):
                ourGeo.append(x)
    print "Geo To Duplicate: {0}".format(ourGeo)

    newGeo = []
    # dupe geo (in place?) 
    for geo in ourGeo:
        newG = cmds.duplicate(geo)
        newGeo.append(newG)
    # if geo is in ref group, create new grp and put that geo here
    for geo in newGeo:
        if cmds.listRelatives(geo, p=True):
            if cmds.listRelatives(geo, p=True)[0] == "refGeo":
                if not cmds.objExists("dupedGeo"):
                    cmds.group(n="dupedGeo", empty=True)
                cmds.parent(geo, "dupedGeo")

    # put ref geo in deleteSet! put refgroup in there too
    cmds.sets(ourGeo, forceElement="deleteSet")
    if cmds.objExists("refGeo"):
        cmds.sets("refGeo", forceElement="deleteSet")

    return(newGeo)


def copyWithInputs(*args):
    """
    duplicate with the input connections. . . 
    """
    OBJS = []
    cmds.duplicate(OBJS, ic=True)
    pass


