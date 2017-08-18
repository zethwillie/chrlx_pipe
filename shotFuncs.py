import maya.cmds as cmds
import zTools.zbw_rigTools as rTools

# ------------------------------------------------------------------------
# below three funcs are for creating in-scene controls on selected objects
cwidgets = {}
def ctrlUI(*args):
    if cmds.window("nWin", exists=True):
        cmds.deleteUI("nWin")
    cwidgets["win"] = cmds.window("nWin", w=200, h=80, t="Create Control", rtf=True)
    cwidgets["clo"] = cmds.columnLayout()
    cwidgets["nm"] = cmds.textFieldGrp(l="Name:", cw=[(1, 50),(2, 150)], cal=[(1, "left"),(2,"left")], tx="newCtrl")
    cmds.separator(h=10)
    cmds.button(l="Create Control!", w=200, h=30, bgc=(.5, .7, .5), c=makeControl)
    cmds.window(cwidgets["win"], e=True, w=5, h=5)
    cmds.showWindow(cwidgets["win"])
    
def makeControl(*args):
    name = cmds.textFieldGrp(cwidgets["nm"], q=True, tx=True)

    nameList = ["{0}Grp".format(name), "{0}Ctrl".format(name), "{0}CtrlGrp".format(name)]
    for nm in nameList:
        if cmds.objExists(nm):
            cmds.warning("An object by the name {0} already exists! Please type in a new name".format(nm))
            return()
    
    sel = cmds.ls(sl=True, type="transform")
    if sel:
        grp = cmds.group(sel, n="{0}Grp".format(name))
        cmds.move(0,0,0, grp, rpr=True)
        t_orig = cmds.getAttr("{0}.t".format(grp))[0]
        t = (t_orig[0]*-1, t_orig[1]*-1, t_orig[2]*-1)
        
        ctrl = rTools.bBox()
        newCtrl = cmds.rename(ctrl, "{0}Ctrl".format(name))
        ctrlGrp = cmds.group(newCtrl, n="{0}CtrlGrp".format(name))
        
        cmds.parent(grp, newCtrl)
        cmds.xform(ctrlGrp, a=True, ws=True, t=t)
        cmds.select(newCtrl, r=True)

        cmds.deleteUI(cwidgets["win"])
    else:
        cmds.warning("You haven't selected any transforms!")

    
def createControl(*args):
    ctrlUI()
    
# ------------------------------------------------------------------------

