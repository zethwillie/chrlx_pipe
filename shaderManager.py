import os
import maya.cmds as cmds
import chrlx_pipe.chrlxFuncs as cFuncs


widgets = {}
def shaderManUI(*args):
	w = 400
	h = 600
	if cmds.window("shadermanWin", exists=True):
		cmds.deleteUI("shadermanWin")

	widgets["win"] = cmds.window("shadermanWin", w=w, h=h, s=True, rtf=True, t="chrlx Shader Manager")
	widgets["mainTLO"] = cmds.tabLayout(w=w, h=h)

	widgets["assetCLO"] = cmds.columnLayout("Assets", w=w, h=h)
	
	widgets["assetFrLO"] = cmds.frameLayout("Asset List", h=300)
	widgets["assetFLO"] = cmds.formLayout(w=w, h=h)
	widgets["assetTSL"] = cmds.textScrollList(w=250,h=295, bgc =(0,0,0))

	cmds.formLayout(widgets["assetFLO"], e=True, af=[
		(widgets["assetTSL"], "left", 0),
		(widgets["assetTSL"], "top", 5)
		])

	cmds.setParent(widgets["assetCLO"])
	widgets["assetRLFrLO"] = cmds.frameLayout("Render Layers")
	widgets["assetRLFLO"] = cmds.formLayout(w=w, h=h)
	widgets["assetRLTSL"] = cmds.textScrollList(w=250,h=195, bgc =(0,0,0))

	cmds.formLayout(widgets["assetRLFLO"], e=True, af=[
		(widgets["assetRLTSL"], "left", 0),
		(widgets["assetRLTSL"], "top", 5)
		])


	cmds.setParent(widgets["mainTLO"])
	widgets["shdrCLO"] = cmds.columnLayout("Shaders", w=w, h=h)

	widgets["shdrFrLO"] = cmds.frameLayout("Shader List")
	widgets["shdrFLO"] = cmds.formLayout(w=w, h=h)
	widgets["shdrTSL"] = cmds.textScrollList(w=250,h=300, bgc =(0,0,0))

	cmds.formLayout(widgets["shdrFLO"], e=True, af=[
		(widgets["shdrTSL"], "left", 0),
		(widgets["shdrTSL"], "top", 0)
		])


	cmds.window(widgets["win"], e=True, w=5, h=5)
	cmds.showWindow(widgets["win"])


def getShadingGroupListFromShader(shdr):
	"""given a shader, get the shading group"""

	cns = cmds.listConnections(shdr)
	sgs = []
	for s in cns:
		if cmds.objectType(s)=="shadingEngine":
			sgs.append(s)
	return sgs
	

def getGeoListFromShadingGroup(sg):
	"""given a shading group, get the attached geo"""

	cns = cmds.listConnections(sg)
	trns = []
	for obj in cns:
		if cmds.objectType(obj)=="transform":
			trns.append(obj)
	return trns	


def getAllRenderLayers():
	return(cmds.ls(type="renderLayer"))


def getRenderLayerListFromGeo(obj):
	"""gets renderlayers that are connected to given geo
		remember to get rid of 'defaultRenderLayer' in calling code
	"""
	rls = []
	shp = cmds.listRelatives(obj, s=True)
	if shp:
		for s in shp:
			layers = cmds.listConnections(s, type="renderLayer")
			if layers:
				for l in layers:
					if l not in rls:
						rls.append(l)
	return(rls)


def getShadingGroupListFromGeo(obj):
	"""given a piece of geo, return the shadergroup"""

	sgs = [x for x in cmds.listConnections(cmds.listRelatives(obj, s=True)[0]) if cmds.objectType(x)=="shadingEngine"]
	return sgs

# query current render layer
# cmds.editRenderLayerGlobals(q=True, crl=True)

# set current render layer
# cmds.editRenderLayerGlobals(crl="defaultRenderLayer")


def getObjectsFromRenderLayer(layer):
	# query objects in render layer - note this could return shapes AND transforms?
	objs = cmds.editRenderLayerMembers(layer, q=True)
	return(objs)