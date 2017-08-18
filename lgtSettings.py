import maya.cmds as cmds
import maya.mel as mel
import mtoa.aovs as aovs

def setCommon(*args):
    print "Setting Common Render Parameters:"

    mel.eval("RenderGlobalsWindow")
    cmds.setAttr("perspShape.renderable", 0)
    cmds.setAttr("perspShape.mask", 0)
    cmds.setAttr("perspShape.image", 0)

    cmds.setAttr("defaultRenderGlobals.animation", 1)
    cmds.setAttr("defaultRenderGlobals.animationRange", 1)
    cmds.setAttr("defaultRenderGlobals.startFrame", 1)
    cmds.setAttr("defaultRenderGlobals.endFrame", 10)
    cmds.setAttr("defaultRenderGlobals.byFrame", 1.25)
    cmds.setAttr("defaultRenderGlobals.byFrameStep", 1) #catch?

    cmds.setAttr("defaultRenderGlobals.modifyExtension", 0)
    cmds.setAttr("defaultRenderGlobals.startExtension", 1)
    cmds.setAttr("defaultRenderGlobals.byExtension", 1) #catch?
    cmds.setAttr("defaultRenderGlobals.extensionPadding", 4)
    cmds.setAttr("defaultRenderGlobals.useFrameExt", 0)
    cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
    cmds.setAttr("defaultRenderGlobals.outFormatControl", 0) #catch?
    cmds.setAttr("defaultRenderGlobals.enableDefaultLight", 0)
    cmds.setAttr("defaultRenderGlobals.imageFormat", 51)
    
    cmds.setAttr("defaultResolution.lockDeviceAspectRatio", 0)
    cmds.setAttr("defaultResolution.aspectLock", 1)
    cmds.setAttr("defaultResolution.width", 1920)
    cmds.setAttr("defaultResolution.height", 1080)
    cmds.setAttr("defaultResolution.deviceAspectRatio", 1.777)

    # for all but maxwell
    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", "<Scene>/<RenderPass>", type="string")


def setArnold(*args):
    print "Setting Arnold parameters:"

    if not cmds.pluginInfo("mtoa", q=True, loaded=True):
        if (cmds.confirmDialog(t="Arnold not loaded!", message="mtoa is not loaded, would you like to load now?", button=["yes", "no"], defaultButton="yes", cancelButton="no", dismissString="no")=="no"):
            cmds.error("Lighting setup cancelled! (arnold plug in)")
            return()
        else:
            cmds.warning("loading arnold plugin . . .")
            cmds.loadPlugin("mtoa") # try/catch here?
            cmds.warning("===== arnold has been loaded, please try again to create the light setup! ======")

    cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")

    cmds.setAttr("defaultArnoldDriver.ai_translator", "exr", type="string")

    cmds.setAttr("defaultArnoldRenderOptions.motion_blur_enable", 1)
    cmds.setAttr("defaultArnoldRenderOptions.ignoreMotionBlur", 1)
    cmds.setAttr("defaultArnoldRenderOptions.range_type", 3)
    cmds.setAttr("defaultArnoldRenderOptions.motion_start", 0)
    cmds.setAttr("defaultArnoldRenderOptions.motion_end", .5)
    cmds.setAttr("defaultArnoldRenderOptions.use_existing_tiled_textures", 1)                   

    # # Create AOV
    # aovs.AOVInterface().addAOV('beauty', aovType='float')
    # aovs.AOVInterface().addAOV('Z', aovType='float')
    # aovs.AOVInterface().addAOV('motionvector', aovType='float')

    # # List all AOVs with their names
    # print(aovs.AOVInterface().getAOVNodes(names=True))


def setVray(*args):
    print "Setting V-Ray parameters:"

    if not cmds.pluginInfo("vray", q=True, loaded=True):
        if (cmds.confirmDialog(t="Vray not loaded!", message="Vray is not loaded, would you like to load now?", button=["yes", "no"], defaultButton="yes", cancelButton="no", dismissString="no")=="no"):
            cmds.error("Lighting setup cancelled! (vray plug in)")
            return()
        else:
            cmds.warning("loading vray plugin . . .")
            cmds.loadPlugin("vray") # try/catch here?
            cmds.warning("===== vray has been loaded, please try again to create the light setup! ======")
    
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "vray", type="string")

    cmds.setAttr("vraySettings.refractiveCaustics", 0)
    cmds.setAttr("vraySettings.secondaryEngine", 3)
    cmds.setAttr("vraySettings.samplerType", 1)
    cmds.setAttr("vraySettings.aaFilterSize", 2)
    cmds.setAttr("vraySettings.dmcLockThreshold", 1)
    cmds.setAttr("vraySettings.useForGlossy", 1)
    cmds.setAttr("vraySettings.imap_subdivs", 20)
    cmds.setAttr("vraySettings.dmcs_timeDependent", 1)
    cmds.setAttr("vraySettings.dmcs_adaptiveAmount", 0.5)
    cmds.setAttr("vraySettings.cmap_clampOutput", 1)
    cmds.setAttr("vraySettings.cmap_clampLevel", 1)
    cmds.setAttr("vraySettings.cmap_subpixelMapping", 1)
    cmds.setAttr("vraySettings.cmap_adaptationOnly", 1)
    cmds.setAttr("vraySettings.cmap_gamma", 2.2000000476837158)
    cmds.setAttr("vraySettings.cmap_affectSwatches", 1)
    cmds.setAttr("vraySettings.cam_overrideEnvtex", 1)
    cmds.setAttr("vraySettings.ddisplac_edgeLength", 0)
    cmds.setAttr("vraySettings.ddisplac_viewDependent", 0)
    cmds.setAttr("vraySettings.ddisplac_maxSubdivs", 4)
    cmds.setAttr("vraySettings.sys_rayc_dynMemLimit", 3000)
    cmds.setAttr("vraySettings.globopt_render_viewport_subdivision", 1)
    cmds.setAttr("vraySettings.globopt_light_doDefaultLights", 1)
    cmds.setAttr("vraySettings.width", 1920)
    cmds.setAttr("vraySettings.height", 1080)
    cmds.setAttr("vraySettings.aspectRatio", 1.7777777910232544)
    cmds.setAttr("vraySettings.aspectLock", 0)
    cmds.setAttr("vraySettings.animBatchOnly", 1)
    cmds.setAttr("vraySettings.imageFormatStr", "exr", type="string")
    cmds.setAttr("vraySettings.batchCamera", "anm_renderCam", type="string")
    cmds.setAttr("vraySettings.relements_separateFolders", 1)
    cmds.setAttr("vraySettings.fileNameRenderElementSeparator", "_", type="string")
    cmds.setAttr("vraySettings.vfbOn", 0)
    cmds.setAttr("vraySettings.vfbSettingsArr", (132, 521, 4, 35, 643, 688, 412, 1328, 394, 292, 394, 17985, 1, 0, 76, 150, 463, 147, 453, 1, 1, 1, 1066751316, 0, 0, 0, 1, 0, 5, 0, 1065353216, 1, 1, 2, 1065353216, 1065353216, 1065353216, 1065353216, 1, 0, 5, 0, 0, 0, 0, 1, 0, 5, 0, 1065353216, 1, 137531, 65536, 1, 1313131313, 65536, 944879383, 0, -525502228, 1065353216, 1621981420, 1034147584, 1053609165, 1065353216, 2, 0, 0, -1097805629, -1097805629, 1049678019, 1049678019, 0, 2, 1065353216, 1065353216, -1097805629, -1097805629, 1049678019, 1049678019, 0, 2, 1, 1, -1, 0, 0, 0, 1634300481, 108, 1288, 0, 609671680, 59, 1549966976, 32656, 102230656, 32656, 102230624, 32656, 1544389984, 32656, 606587400, 59, 1288, 0, 1288, 0, 1549966976, 32656, 604265889, 59, -1143802928, 16777215, 0, 70, 1, 32, 53, 1632775510, 1868963961, 1632444530, 622879097, 2036429430, 1936876918, 544108393, 1701978236, 1919247470, 1835627552, 1915035749, 1701080677, 1835627634, 101, 0),type="Int32Array")


def setMaxwell(*args):
    print "Setting Maxwell parameters:"

    if not cmds.pluginInfo("maxwell", q=True, loaded=True):
        if (cmds.confirmDialog(t="Maxwell not loaded!", message="Maxwell is not loaded, would you like to load now?", button=["yes", "no"], defaultButton="yes", cancelButton="no", dismissString="no")=="no"):
            cmds.error("Lighting setup cancelled! (maxwell plug in)")
            return()
        else:
            cmds.warning("loading maxwell plugin . . .")
            cmds.loadPlugin("maxwell") # try/catch here?
            cmds.warning("===== maxwell has been loaded, please try again to create the light setup! ======")

    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", "", type="string")
   
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "maxwell", type="string")
    
    if not cmds.objExists("maxwellRenderOptions"):
        cmds.createNode("maxwellRenderOptions", shared=True, name="maxwellRenderOptions")

    cmds.setAttr("maxwellRenderOptions.outputImgDepth", 1) # set the image depth to 16 bit
    cmds.setAttr("maxwellRenderOptions.motionBlur", 0) # make sure motion blur is off
    cmds.setAttr("maxwellRenderOptions.multiLight", 2) # turn multi light on, this is something I want to test more
    cmds.setAttr("maxwellRenderOptions.skyType", 2) # turn the sky options off
    # create an alpha channel
    cmds.setAttr("maxwellRenderOptions.alphaChannel", 1)
    cmds.setAttr("maxwellRenderOptions.alphaChannelFormat", 5)
    cmds.setAttr("maxwellRenderOptions.alphaChannelDepth", 2)
    # set alpha to opaque
    cmds.setAttr("maxwellRenderOptions.opaqueChannel", 1)
    # set other channels bit depths higher, we will let the lighter enable the layers manually
    cmds.setAttr("maxwellRenderOptions.depthChannelFormat", 5)
    cmds.setAttr("maxwellRenderOptions.depthChannelDepth", 2)

    cmds.setAttr("maxwellRenderOptions.objIDChannelFormat", 5)
    cmds.setAttr("maxwellRenderOptions.objIDChannelDepth", 1)

    cmds.setAttr("maxwellRenderOptions.matIDChannelFormat", 5)
    cmds.setAttr("maxwellRenderOptions.matIDChannelDepth", 1)

    cmds.setAttr("maxwellRenderOptions.motionVectorChannelFormat", 5)
    cmds.setAttr("maxwellRenderOptions.motionVectorChannelDepth", 2)

    cmds.setAttr("maxwellRenderOptions.roughnessChannelFormat", 5)
    cmds.setAttr("maxwellRenderOptions.roughnessChannelDepth", 1)

    cmds.setAttr("maxwellRenderOptions.fresnelChannelFormat", 5)
    cmds.setAttr("maxwellRenderOptions.fresnelChannelDepth", 1)

    cmds.setAttr("maxwellRenderOptions.normalsChannelFormat", 5)
    cmds.setAttr("maxwellRenderOptions.normalsChannelDepth", 2)

    cmds.setAttr("maxwellRenderOptions.positionChannelFormat", 5)
    cmds.setAttr("maxwellRenderOptions.positionChannelDepth", 2)
    cmds.setAttr("maxwellRenderOptions.positionChannelSpace", 1)

    cmds.setAttr("maxwellRenderOptions.uvChannelFormat", 5)
    cmds.setAttr("maxwellRenderOptions.uvChannelDepth", 2)

    cmds.setAttr("maxwellRenderOptions.customAlphaChannelFormat", 5)
    cmds.setAttr("maxwellRenderOptions.customAlphaChannelDepth", 1)

    camShapes = cmds.ls("*renderCamShape", ap=True)
    for cam in camShapes:
        try:
            cmds.setAttr("{0}.mxLensType".format(cam), 1)
            cmds.setAttr("{0}.mxExpMode".format(cam), 2)
            cmds.setAttr("{0}.mxShutterSpeed".format(cam), 100)
            cmds.setAttr("{0}.mxFstop".format(cam), 11)
            cmds.setAttr("{0}.mxEV".format(cam), 19)
            cmds.setAttr("{0}.mxIso".format(cam), 100)
            cmds.setAttr("{0}.mxExportCamAnim".format(cam), 1)
            cmds.color(cam, ud=7)
        except RuntimeError as e:
            cmds.warning("lgtSettings.setMaxwell: Runtime error setting maxwell camera attributes:\n{0}".format(e))

def setMentalRay(*args):
    pass
