import copyFiles
from chrlx import utils

#copy chars specifically ([[fromtype, fromname, totype, toname]], frompath, topath)
copyFiles.copy_assets(["characters", "ipad2tablet", "characters", "dupe2Test"],
                     "/Bluearc/GFX/jobs/charlex_testAreaB_T60174",
                     "/Bluearc/GFX/jobs/charlex_testAreaB_T60174")

#copy arbitrary files (recognizes chars)
# copyFiles.copy_file("/Bluearc/GFX/jobs/advil_P12918/A_fastFacts/scenes/master/char/advilBoxC",
#                    "/Bluearc/GFX/jobs/charlex_testAreaB_T60174/3D_assets/props/banana")

#copy entire shots (chars, anm, lgt, configs, etc) schema 1 -> 2
#copyFiles.copy_shot(r"//Bluearc/GFX/jobs/harman_P12954/B_connectedGenericStill/scenes/shot010",
#                    r"//Bluearc/GFX/jobs/charlex_testAreaB_T60174/B_restructure/3d/shots/shot050",
#                    force=1) #force overwriting files (excluding assets)

#copy entire shots (chars, anm, lgt, configs) schema 2 -> 2
#copyFiles.copy_shot(r"//Bluearc/GFX/jobs/charlex_testAreaB_T60174/B_restructure/3d/shots/shot050",
#                    r"//Bluearc/GFX/jobs/charlex_testAreaB_T60174/C_newStyle/3d/shots/shot070",
#                    force=1)