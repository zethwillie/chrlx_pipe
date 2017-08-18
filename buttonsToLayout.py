import maya.cmds as cmds
import maya.mel as mel
import chrlx_pipe.chrlxFuncs as cFuncs
import os

def buttonsToLayout(layout="", dictionary={}, width=50, height=20, color=(.5, .5, .5), *args):
    """
    takes info from the given dictionary and creates buttons in the given layout to execute and display scripts

    Args:
        dict (dictionary): dictionary of button attrs (list) in the form --> key(which is used as label): [type ("py" or "mel"), command, annotation]
        width (int): the width of each button created
        height (int): the height of each button created
        color (float array3): a 3-array of 0-1 floats
        layout (string): the layout widget that is the parent widget of the buttons we will create

        example dictionary: example = {"buttonLabel_1":["py", "from myFolder import myModule; reload myModule; myModule.myFunc()", "this function does something"]
                                        "buttonLabel_2":["mel", "myMelScript.mel", "this function does something else"]}

        note: this assumes the call will correctly place the button in the layout
    Return:
        None
    """
    iconPath = cFuncs.fixPath(os.path.join(os.getenv("MAYA_ROOT"), "scripts", "chrlx_icons"))

    font = "tinyBoldLabelFont"

    melIconDefault = "commandButton.png"
    pyIconDefault = "pythonFamily.png"

    if layout and dictionary:
        rKeys = dictionary.keys()
        sKeys = []
        for sk in rKeys:
            strKey = str(sk)
            sKeys.append(strKey)
        keys = sorted(sKeys, key= lambda s: s.lower())

        for key in keys:
            if dictionary[key][0] == "py":
                c = dictionary[key][1]
                icon = pyIconDefault
            if dictionary[key][0] == "mel":
                c = "mel.eval('{0}')".format(dictionary[key][1])
                icon = melIconDefault

            a = dictionary[key][2]
            
            if len(dictionary[key]) > 3:
                icon = cFuncs.fixPath(os.path.join(iconPath, dictionary[key][3]))

            # change style to iconAndTextVertical, if you want
            thisButton = cmds.iconTextButton(label=key, parent=layout, w=width, h=height, backgroundColor=color, command=c, annotation=a, image=icon, style="iconAndTextHorizontal", font=font)
