# mastering window class that will return the options needed

import maya.cmds as cmds


widgets = {}
attrs = {}

def compareSceneInfoUI(attrs, *args):
    if cmds.window("csiWin", exists=True):
        cmds.deleteUI("csiWin")

    widgets["win"] = cmds.window("csiWin", w=300, h=200, rtf=True, t="Compare Scene Info")

    widgets["mainCLO"] = cmds.columnLayout()
    widgets["instrText"] = cmds.text("The following attrs are mismatched:")
    cmds.separator(h=20)
    cmds.text("                                   anim ref:                 current:")
    for key in attrs:
        widgets[key] = cmds.radioButtonGrp(l=key, nrb=2, l1=attrs[key][0], l2=attrs[key][1], cw=[(1, 100),(2, 90),(3, 90)], sl=2, cal=[(1, "left"), (2, "left"), (3,"left")])
    cmds.separator(h=20)
    widgets["endText"] = cmds.text("Select the values you'd like to assign to current scene.")
    cmds.separator(h=10)
    widgets["but"] = cmds.button(l="Set Values", w=300, h=30, bgc = (.7, .7, .4), c=setValues)

    cmds.window(widgets["win"], e=True, w=5, h=5)
    cmds.showWindow(widgets["win"])


def setValues(*args):
    for key in attrs:
        sl = cmds.radioButtonGrp(widgets[key], q=True, sl=True)
        #print sl
        val = attrs[key][sl-1]

        if key == "FRAMERANGE":
            rngMin = int(float(attrs["FRAMERANGE"][sl-1].partition("-")[0]))
            rngMax = int(float(attrs["FRAMERANGE"][sl-1].partition("-")[2]))

            cmds.playbackOptions(max=rngMax, min=rngMin)
            print rngMin, rngMax

        if key == "RESOLUTION":
            resW = int(float(attrs["RESOLUTION"][sl-1].partition("-")[0]))
            resH = int(float(attrs["RESOLUTION"][sl-1].partition("-")[2]))

            cmds.setAttr("defaultResolution.width", resW)
            cmds.setAttr("defaultResolution.height", resH)

            print resW, resH

        if key == "FPS":
            fps = attrs["FPS"][sl-1]
            cmds.currentUnit(time=fps)

            print fps

    cmds.deleteUI(widgets["win"])

def compareSceneInfo(fields, *args):
    # check fields and pass to compare scene info
    keys = fields.keys()
    for key in keys:
        attrs[key] = fields[key]
    if attrs:
        compareSceneInfoUI(attrs)