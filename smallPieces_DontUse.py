"""
setting frame rates
"""

import maya.cmds as cmds

fps=24
secs = 1/24
# currentUnit --> "ntsc"(30), "film"(24), "ntscf" (60), "sec"(sec/fps)
cmds.currentUnit(time="film")
cmds.playbackOptions(playbackSpeed = 1)

"""
setting up for lighting
"""
# check for arnold (then do vray and maxwell)
# list plugins
pi = cmds.pluginInfo(listPlugins=True, query=True)
print pi

# load arnnold plug in
cmds.loadPlugin("mtoa", quiet=True)

# set renderer to Arnold
cmds.setAttr("defaultRenderGlobals.ren", "arnold", type="string")
#settings
# example on render settings change
#Change samples
cmds.setAttr('miDefaultOptions.maxSamples', 2);