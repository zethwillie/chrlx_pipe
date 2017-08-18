#create rigWS setup

import maya.cmds as cmds

def rigSetup(*args):
    """builds the controls and sets for the chrlx rigs"""	
    #setup the sets
    rigList = ["MAIN", "ALLKEYABLE", "RES", "HIRES", "MEDRES", "LORES", "BNDJNTS", "RIGSETS", "deleteSet", "GOD", "DIRECTION", "BODY"]
    clear = "yes"
    clashList = []

    for s in rigList:
        if cmds.objExists(s):
            clear = "no"
            clashList.append(s)

    setList = rigList[:-3]

    if clear == "yes":
        for s in setList:		
            cmds.sets(name=s, empty=True)

        cmds.sets(("HIRES", "LORES", "MEDRES"), include="RES")
        cmds.sets(("ALLKEYABLE", "RES", "RIGSETS"), include = "MAIN")
        cmds.sets("BNDJNTS", include = "RIGSETS")

        #build the controls
        god = cmds.curve(n="GOD", d=1, p=[[0.0, 0.0, -6.88573], [-2.81689, 0.0, -5.633779], [-0.625975, 0.0, -5.633779], [-0.625975, 0.0, -5.007804], [-5.007804, 0.0, -5.007804], [-5.007804, 0.0, -0.625975], [-5.633779, 0.0, -0.625975], [-5.633779, 0.0, -2.81689], [-6.88573, 0.0, 0.0], [-5.633779, 0.0, 2.81689], [-5.633779, 0.0, 0.625975], [-5.007804, 0.0, 0.625975], [-5.007804, 0.0, 5.007804], [-0.625975, 0.0, 5.007804], [-0.625975, 0.0, 5.633779], [-2.81689, 0.0, 5.633779], [0.0, 0.0, 6.88573], [2.81689, 0.0, 5.633779], [0.625975, 0.0, 5.633779], [0.625975, 0.0, 5.007804], [5.007804, 0.0, 5.007804], [5.007804, 0.0, 0.625975], [5.633779, 0.0, 0.625975], [5.633779, 0.0, 2.81689], [6.88573, 0.0, 0.0], [5.633779, 0.0, -2.81689], [5.633779, 0.0, -0.625975], [5.007804, 0.0, -0.625975], [5.007804, 0.0, -5.007804], [0.625975, 0.0, -5.007804], [0.625975, 0.0, -5.633779], [2.81689, 0.0, -5.633779], [0.0, 0.0, -6.88573]])

        direction = cmds.curve(n="DIRECTION", d=1, p=[[-4.0, 0.0, -4.0], [4.0, 0.0, -4.0], [4.0, 0.0, 4.0], [-4.0, 0.0, 4.0], [-4.0, 0.0, -4.0]])

        body = cmds.curve(n="BODY", d=3, p=[[-0.001075669821, 0.0002350895934, 3.981101846], [-1.040596346, 0.0002350895934, 3.980804926], [-3.119786326, 0.0002350895934, 3.11927925], [-4.411834098, 0.0002350895934, -1.278439146e-15], [-3.119637807, 0.0002350895934, -3.119637807], [-5.03337518e-16, 0.0002350895934, -4.411834098], [3.119637807, 0.0002350895934, -3.119637807], [4.411834098, 0.0002350895934, 2.369604699e-15], [3.046183643, 0.0002350895934, 3.119637807], [0.7069376368, 0.0002350895934, 3.981250519], [-0.001075669821, 0.0002350895934, 3.981101846], [-0.001075669821, 0.0002350895934, 3.981101846], [-0.001075669821, 0.0002350895934, 3.981101846], [-0.001075669821, 0.0002350895934, 3.981101846], [-0.0007171132224, 0.03981102, 3.981101949], [-0.0007171132224, 0.03981102, 3.981101949], [-0.0007171132224, 0.03981102, 3.981101949], [-0.0007171132224, 0.03981102, 3.981101949], [-0.7080132704, 0.03981102, 3.980804926], [-3.046332162, 0.03981102, 3.11927925], [-4.411834098, 0.03981102, -1.278439146e-15], [-3.119637807, 0.03981102, -3.119637807], [-5.03337518e-16, 0.03981102, -4.411834098], [3.119637807, 0.03981102, -3.119637807], [4.411834098, 0.03981102, 2.369604699e-15], [3.046183643, 0.03981102, 3.119637807], [0.7069376368, 0.03981102, 3.981250519], [-0.001075669821, 0.03981102, 3.981101846], [-0.001075669821, 0.03981102, 3.981101846], [-0.001075669821, 0.03981102, 3.981101846], [-0.001075669821, 0.07938695041, 3.981101846], [-0.001075669821, 0.07938695041, 3.981101846], [-0.001075669821, 0.07938695041, 3.981101846], [-0.7080132704, 0.07938695041, 3.980804926], [-3.046332162, 0.07938695041, 3.11927925], [-4.411834098, 0.07938695041, -1.278439146e-15], [-3.119637807, 0.07938695041, -3.119637807], [-5.03337518e-16, 0.07938695041, -4.411834098], [3.119637807, 0.07938695041, -3.119637807], [4.411834098, 0.07938695041, 2.369604699e-15], [3.119637807, 0.07938695041, 3.119637807], [1.039520712, 0.07938695041, 3.981250519], [-0.001075669821, 0.07938695041, 3.981101846]])

        for a in [god, body, direction]:
            shp = cmds.listRelatives(a, s=True)[0]
            #print "got shape: {}".format(shp)
            cmds.rename(shp, "{}Shape".format(a))

        geo = cmds.group(n="GEO", em=True)
        rig = cmds.group(n="RIG", em=True)

        #connect the controls
        cmds.parent(body, direction)
        cmds.parent(direction, god)
        cmds.parent((geo, rig), god)

        for s in rigList:
            if s != "deleteSet":
                cmds.lockNode(s)

        cmds.setAttr("{}.inheritsTransform".format(geo), 0)
        cmds.setAttr("{}.inheritsTransform".format(rig), 0)

        cmds.sets([body, direction, god], fe="ALLKEYABLE")

    else:
        cmds.warning("You already have the following objects/sets in your scene:")
        for x in clashList:
            print x