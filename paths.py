#----------------import chrlx
from collections import deque, namedtuple
from functools import wraps
import glob
import os
from pprint import pprint
import re
import shutil
import sys
import unittest
import subprocess

#----------------from enum import Enum


def fixPath(dir):
    if dir:
        return joinPath(splitPath(dir))
def splitPath(dir):
    if dir:
        return filter(None, re.split(r"[\\\/]",dir))
def joinPath(splits):
    if ":" in splits[0]:
        return os.sep.join(splits)
    return os.sep*2+os.sep.join(splits)

class Shottype(int): #---------------- this was Enum
    lgt=1
    anm=2

class ProxyClass(object):
    def __init__(self):
        self.dbhandle=None
    def __str__(self):
        return str(self.fullname)
    def __len__(self):
        return len(self.path)
    def __repr__(self):
        return self.shortname
class ProxyJob(ProxyClass):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.__dict__.update(kwargs)
        self.__dict__.update(locals())
    def __getattr__(self, name):
        if not self.dbhandle:
            #----------------from chrlx.model.jobs import Job, Spot, Shot
            #----------------from chrlx.model.meta import Session
            self.dbhandle = Session.query(Job).filter(Job.dir_name==self.dir_name).first()

            if not self.dbhandle:
                raise KeyError("Job does not exist in db.")
        return getattr(self.dbhandle, name)
class ProxySpot(ProxyClass):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.__dict__.update(kwargs)
        self.__dict__.update(locals())
    def __getattr__(self, name):
        if not self.dbhandle:
            #----------------from chrlx.model.jobs import Job, Spot, Shot
            #----------------from chrlx.model.meta import Session
            from sqlalchemy import or_, and_
            self.dbhandle=Session.query(Spot).filter(and_(Spot.dir_name==self.dir_name,
                                                          Spot.jobid==self.job.id)).first()
            if not self.dbhandle:
                raise KeyError("Spot {0} does not exist in job {1}.".format(self.dir_name, self.job.jobDirname))
        return getattr(self.dbhandle, name)
class ProxyShot(ProxyClass):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.__dict__.update(kwargs)
        self.__dict__.update(locals())
    def __getattr__(self, name):
        if "frames" in name or "plates" in name:
            if "restored" in name:
                return self.shotFrames(name,True)
            else:
                return self.shotFrames(name)

        if not self.dbhandle:
            from chrlx.model.jobs import Job, Spot, Shot
            from chrlx.model.meta import Session
            from sqlalchemy import or_, and_
            self.dbhandle=Session.query(Shot).filter(and_(Shot.spotid==self.spot.id,
                                         Shot.shot==self.shot,
                                         Shot.stage==self.stage)).first()
            if not self.dbhandle:
                raise KeyError("Shot {0} does not exist in spot {1}.".format(self.shotName, self.spot.id))
        return getattr(self.dbhandle, name)

class PathInterface(type):
    def __call__(cls, path, *args, **kwargs):
        source=kwargs.pop("source", None)

        if isinstance(path, PathManager) or isinstance(path, PathBase):
            pm = path
        else:
            pm=PathManager(path)

        if not source:
            source=pm
        obj=type.__call__(cls, path, *args, **kwargs)
        obj.source=source
        obj.pm=pm
        obj.setup()
        return obj
class PathBase(str):
    def __init__(self, path):
        self.path=path
    def __getattr__(self, name):
        if not self.pm:
            return getattr(self.source, name)
        return getattr(self.pm, name)
    def __str__(self):
        return str(self.path)
    def __repr__(self):
        return "<{0} {1}>".format(str(self.__class__)[8:-2], self.path)
    def __contains__(self, item):
        return item in self.path

    @staticmethod
    def checkWorkshop_decorator(f):
        @wraps(f)
        def checkWorkshop(self):
            if self.ws in self.splits:
                return f(self)
            raise AttributeError("Not a workshop file.")
        return checkWorkshop
class BasePath(PathBase):
    __metaclass__ = PathInterface
    def __init__(self, path):
        super(BasePath, self).__init__(path)
    def setup(self):
        pass
class ShotPath(PathBase):
    __metaclass__ = PathInterface
    v1lgtMasterMask   ="{spotShortname}_{shot:03d}_{variant}.ma"
    v1lgtWorkshopMask ="{spotShortname}_{shot:03d}_{variant}.{version}.ma"
    v1lgtVersionMask  ="{spotShortname}_{shot:03d}_{variant}.ma.v{version}"
    v1anmMasterMask   ="{shotName}_anm.ma"
    v1anmWorkshopMask ="{shotName}_anmRef.v{version}.ma"
    v1anmVersionMask  ="{shotName}_anm.ma.v{version}"
    v2MasterMask      ="{shotShortname}_{shotType}_{variant}.ma"
    v2WorkshopMask    ="{shotShortname}_{shotType}_{variant}_ws_v{version}.ma"
    v2VersionMask     ="{shotShortname}_{shotType}_{variant}_v{version}.ma"
    def checkVariant_decorator(f):
        @wraps(f)
        def checkVariant(self, variant=None, *args, **kwargs):
            if not variant and self.variant:
                variant=self.variant

            if self.spotSchema>1:
                if not variant:
                    raise AttributeError("Missing shot variant.",  self.getVariants())
                self.variantPath=os.path.join(self.shotTypePath, variant)
            else:
                if self.shotType==Shottype.lgt.name:
                    if not variant:
                        raise AttributeError("Missing shot variant.",  self.getVariants())
                elif self.shotType==Shottype.anm.name:
                    if "workshop" in f.__name__:
                        variant="anmRef"
                    else:
                        variant="anm"
            return f(self, variant, *args, **kwargs)
        return checkVariant

    def __call__(self, shottype=None, variant=None, version=None):
        if variant==None:
            variant=self.variant
        if version==None:
            version=self.version
        if shottype:
            return ShotPath(os.path.join(self.shotPath, shottype), variant, version)
        return ShotPath(self.shotTypePath, variant, version)
    def __new__(cls, path, *args, **kwargs):
        return str.__new__(cls, path)
    def __init__(self, path, variant=None, version=None):
        self.vari=variant
        self.vers=version
        super(ShotPath, self).__init__(path)
    def setup(self):
        self.isVersion=False
        self.isWorkshop=False
        self.isMaster=False

        if self.spotSchema<=1:
            typeIndex=self.jobRootIndex+5
        elif self.spotSchema>1:
            typeIndex=self.jobRootIndex+6
        if len(self.splits)<typeIndex+1:
            return
        self.shotType=self.splits[typeIndex]
        self.shotTypePath=os.path.join(self.shotPath, self.shotType)
        if self.spotSchema<=1:
            vers="{version}"
            if self.shotType=="lgt":
                self.wm = self.v1lgtWorkshopMask
                self.mm = self.v1lgtMasterMask
                self.vm = self.v1lgtVersionMask
            elif self.shotType=="anm":
                self.wm = self.v1anmWorkshopMask
                self.mm = self.v1anmMasterMask
                self.vm = self.v1anmVersionMask
            self.variantPath=self.shotTypePath
        elif self.spotSchema>1:
            self.wm = self.v2WorkshopMask
            self.mm = self.v2MasterMask
            self.vm = self.v2VersionMask
            vers="{version:03d}"

            if len(self.splits)>typeIndex+1:
                self.vari=self.splits[typeIndex+1]
                self.variantPath=os.path.join(self.shotTypePath, self.vari)
                self.variantIcon=os.path.join(self.variantPath, "icon", "{0}Icon.png".format(self.vari))

        if self.shotType not in ["anm", "lgt", "fx"]:
            return
        shotShortname=self.shotShortname
        spotShortname=self.spotShortname
        shotType=self.shotType
        shot=self.shot.shot
        shotName=self.shotName
        vari="{variant}"
        self.mm=self.mm.format(variant=vari, version=vers, **locals())
        self.wm=self.wm.format(variant=vari, version=vers, **locals())
        self.vm=self.vm.format(variant=vari, version=vers, **locals())
        self.MM=self.mm
        self.WM=self.wm
        self.VM=self.vm

        if self.ws==self.splits[-2]:
            self.isWorkshop=True
        elif self.vs==self.splits[-2]:
            self.isVersion=True
        elif re.search(self.mm.format(variant="\S+"), self.splits[-1]):
            self.isMaster=True

    @checkVariant_decorator
    def getWorkshops(self, variant=None):
        mask=os.path.join(self.variantPath, self.ws,self.wm.format(variant=variant,version=999).replace("999","*"))
        files = glob.glob(mask)
        files.sort()
        files = [ShotPath(f) for f in files]
        if self.spotSchema<=1:
            def vernum(f):
                try:
                    return int(f.split('.', 3)[1].lstrip('v'))
                except ValueError:
                    return 0
            files.sort(key=vernum)
        return files
    @checkVariant_decorator
    def getNextWorkshop(self, variant=None, version=None):
        if version==None:
            version=1
            current=self.getWorkshops(variant=variant)
            if current:
                version=current[-1].version+1
        wm=self.wm
        if self.spotSchema<=1 and self.shotType=="lgt":
            wm=self.wm.format(version="{version:02d}", variant="{variant}")
        return ShotPath(os.path.join(self.variantPath, self.ws, wm.format(variant=variant, version=version)))

    def filterMaster(self, variant="*"):
        masters=[]
        for f in glob.glob(os.path.join(self.variantPath,self.mm.format(variant=variant))):
            masters.append(ShotPath(f))
        return  map(lambda l : ShotPath(l), masters)
    @checkVariant_decorator
    def getMaster(self, variant=None):
        return ShotPath(os.path.join(self.variantPath,self.mm.format(variant=variant)))

    @checkVariant_decorator
    def getVersions(self, variant=None):
        mask=os.path.join(self.variantPath, self.vs, self.vm.format(variant=variant, version=999).replace("999","*"))
        files=glob.glob(mask)
        files.sort()
        files=[ShotPath(f) for f in files]
        if self.spotSchema<=1:
            def vernum(f):
                try:
                    return int(os.path.basename(f).split('.')[-1].lstrip('v'))
                except ValueError:
                    return 0
            files.sort(key=vernum)
        return files
    @checkVariant_decorator
    def getNextVersion(self, variant=None, version=None):
        if version==None:
            version=0
            current=self.getVersions(variant=variant)
            if current:
                version=current[-1].version+1
        return ShotPath(os.path.join(self.variantPath, self.vs, self.vm.format(variant=variant,
                                                                               version=version)))

    @property
    def version(self):
        if self.vers:
            return self.vers
        return self._getFileVersion()
    def _getFileVersion(self):
        if self.isVersion or self.isWorkshop:
            if self.spotSchema>1:
                return int(self.path[-6:-3])
            else:
                if self.isVersion:
                    return int(os.path.basename(self.path).split('.')[-1][1:])
                elif self.isWorkshop:
                    return int(os.path.basename(self.path).split(".")[1].replace("v", ""))
    @property
    def variant(self):
        if self.vari:
            return self.vari
        return self._getFileVariant()
    def _getFileVariant(self):
        if self.isMaster or self.isVersion:
            if self.spotSchema<=1 and self.shotType=="anm":
                return "anm"
            match=re.search(self.mm.format(variant="(\w*)"), self.splits[-1])
            if match:
                return match.group(1)
        elif self.isWorkshop:
            if self.spotSchema<=1 and self.shotType=="anm":
                return "anmRef"
            match=re.search(self.wm.format(variant="(\w*)",version=999).replace("999", "\d*"), self.splits[-1])
            if match:
                return match.group(1)
        elif self.spotSchema>1:
            return os.path.basename(self.variantPath)
    def getVariants(self):
        files = glob.glob(os.path.join(self.shotTypePath,self.mm.format(variant="*")))
        variants=set()
        for f in files:
            variants.add(os.path.splitext(os.path.basename(f))[0].split("_")[-1])
        return list(variants)

class AssetPath(PathBase):
    __metaclass__ = PathInterface
    v1MasterMask      ="{name}_{stage}.ma"
    v1WorkshopMask    ="{name}_{stage}.ma.v{version}"
    v1VersionMask     ="{name}_{stage}.ma.v{version}"
    v2MasterMask      ="{name}_{stage}.ma"
    v2WorkshopMask    ="{name}_{stage}_ws_v{version}.ma"
    v2VersionMask     ="{name}_{stage}_v{version}.ma"

    @staticmethod
    def getType(path, typ):
        if PathManager.getSchema(path)==1:
            return "char"
        else:
            if typ=="char":
                return "characters"
        return typ

    def checkStage_decorator(func):
        @wraps(func)
        def checkStage(self, typ=None, name=None, stage=None, *args, **kwargs):
            if not typ:
                typ=self.typ
            if not name:
                name=self.name
            if not stage:
                stage=self.stage

            if stage:
                return func(AssetPath(os.path.join(self.assetPath, typ, name, stage)), *args, **kwargs)
            else:
                raise AttributeError("AssetStage and AssetName must be specified.")
        return checkStage

    def __call__(self, typ="", name="", stage=""):
        if typ=="":
            typ=self.typ
        if name=="":
            name=self.name
        if stage=="":
            stage=self.stage
        return AssetPath(os.path.join(self.assetPath, typ, name, stage))
    def __new__(cls, path, typ="", name="", stage=""):
        if typ or name or stage:
            typ=AssetPath.getType(path, typ)
            path=os.path.join(PathManager(path).assetPath, typ, name, stage)
        return str.__new__(cls, path)
    def __init__(self, path, typ='', name='', stage=''):
        self.typ=AssetPath.getType(path, typ)
        self.name=name
        self.stage=stage
        super(AssetPath, self).__init__(path)
    def setup(self):
        self.typePath=None
        self.namePath=None
        self.stagePath=None
        self.isVersion=False
        self.isWorkshop=False
        self.isMaster=False

        if self.spotSchema<=1:
            typeIndex=self.jobRootIndex+5
            nameIndex=typeIndex+1
            stageIndex=nameIndex+1

            self.wm = self.v1WorkshopMask
            self.mm = self.v1MasterMask
            self.vm = self.v1VersionMask
            version="{version:d}"
        if self.source.spotSchema>1:
            typeIndex=self.jobRootIndex+3
            nameIndex=typeIndex+1
            stageIndex=nameIndex+1

            self.wm = self.v2WorkshopMask
            self.mm = self.v2MasterMask
            self.vm = self.v2VersionMask
            version="{version:03d}"
        if len(self.splits)>=typeIndex+1 or self.typ:
            if not self.typ:
                self.typ=AssetPath.getType(self.path, self.splits[typeIndex])
            self.typePath=os.path.join(self.assetPath, self.typ)
            if len(self.splits)>=nameIndex+1 or self.name:
                if not self.name:
                    self.name=self.splits[nameIndex]
                self.namePath=os.path.join(self.typePath, self.name)
                name=self.name

                if self.spotSchema<=1:
                    self.assetIcon=os.path.join(self.namePath, "reference", "{0}Icon.png".format(self.name))
                else:
                    self.assetIcon=os.path.join(self.namePath, "icon", "{0}Icon.png".format(self.name))

                if len(self.splits)>=stageIndex+1 or self.stage:
                    if not self.stage:
                        self.stage=self.splits[stageIndex]
                    stage=self.stage
                    self.stagePath=os.path.join(self.namePath, self.stage)
                    self.MM=self.mm
                    self.WM=self.wm
                    self.VM=self.vm
                    self.mm=self.mm.format(**locals())
                    self.wm=self.wm.format(**locals())
                    self.vm=self.vm.format(**locals())
                    if self.spotSchema<=1 and self.stage=="geo":
                        self.mm=self.mm.replace("_geo","")
                        self.vm=self.vm.replace("_geo","")
                    elif self.spotSchema<=1 and self.stage=="rig":
                        self.wm=self.wm.replace("_rig", "_refRig")

                    if self.ws in self.splits and re.search(self.wm.format(variant="\S+", version=999).replace("999", "\S+"), self.splits[-1]):
                        self.isWorkshop=True
                    elif self.vs in self.splits and re.search(self.mm.format(variant="\S+"), self.splits[-1]):
                        self.isVersion=True
                    elif re.search(self.mm.format(variant="\S+"), self.splits[-1]):
                        self.isMaster=True



    @checkStage_decorator
    def getWorkshops(self):
        mask=os.path.join(self.stagePath, self.ws, self.wm.format(typ=self.typ,
                                                                  name=self.name,
                                                                  stage=self.stage,
                                                                  version=999).replace("999","*"))
        files = glob.glob(mask)
        files.sort()
        files = [AssetPath(f) for f in files]
        if self.spotSchema<=1:
            def vernum(f):
                try:
                    return int(os.path.basename(f).split('.')[-1].lstrip('v'))
                except ValueError:
                    return 0
            files.sort(key=vernum)
        return files
    @checkStage_decorator
    def getNextWorkshop(self, version=None):
        if version==None:
            versions=self.getWorkshops()
            if versions:
                version=self.getWorkshops()[-1].version+1
            else:
                version=1
        return AssetPath(os.path.join(self.stagePath, self.ws, self.wm.format(version=version)))

    def filterMaster(self, typ="*", name="*", stage="*"):
        masters=[]
        mask=os.path.join(self.assetPath,typ,name,stage,self.MM.format(name=name,stage=stage))
        for f in glob.glob(mask):
            masters.append(AssetPath(f))
        return masters
    @checkStage_decorator
    def getMaster(self):
        return AssetPath(os.path.join(self.assetPath, self.typ, self.name, self.stage,
                                      self.mm.format(typ=self.typ, name=self.name, stage=self.stage)))

    @checkStage_decorator
    def getVersions(self):
        if self.stage=="mtl" and self.spotSchema<=1:
            return

        mask=os.path.join(self.stagePath, self.vs, self.vm.format(version=999).replace("999","*"))
        files = glob.glob(mask)
        files.sort()
        files=[AssetPath(f) for f in files]
        if self.spotSchema<=1:
            def vernum(f):
                try:
                    return int(os.path.basename(f).split('.')[-1].lstrip('v'))
                except ValueError:
                    return 0
            files.sort(key=vernum)
        return files
    @checkStage_decorator
    def getNextVersion(self, version=None):
        if self.stage=="mtl" and self.spotSchema<=1:
            return
        if version==None:
            versions=self.getVersions()
            if versions:
                version=versions[-1].version+1
            else:
                version=0
        return AssetPath(os.path.join(self.stagePath, self.vs, self.vm.format(version=version)))

    @property
    def version(self):
        return self.getVersion()
    def getVersion(self):
        if self.spotSchema>1:
            return int(self.path[-6:-3])
        else:
            version=self.path.split(".")[-1]
            return int(re.findall("\d+", version)[0])
    def getAssets(self, typ=None):
        if typ:
            assets=[]
            for f in glob.glob(os.path.join(self.assetPath,typ,"*")):
                assets.append(os.path.basename(f))
        else:
            assets={}
            for f in glob.glob(os.path.join(self.assetPath,"*","*")):
                tpe, name = splitPath(f)[-2:]
                if tpe not in assets:
                    assets[tpe]=[]
                assets[tpe].append(name)
        return assets

    def createDirectories(self):
        createAssetDirectories(self.assetPath, self.typ, self.name)
class CompPath(PathBase):
    __metaclass__ = PathInterface
    MM="{shotShortname}_{variant}_v{version}.nk"

    def __new__(cls, path, *args, **kwargs):
        return str.__new__(cls, path)
    def checkVariant_decorator(f):
        @wraps(f)
        def checkVariant(self, variant=None, *args, **kwargs):
            if not variant and self.variant:
                variant=self.variant
            if variant:
                return f(self, variant=variant, *args, **kwargs)
            else:
                raise AttributeError("Missing Variant or Version.")
        return checkVariant

    def __init__(self, path, variant=None, version=None):
        self.vari=variant
        self.vers=version
        super(CompPath, self).__init__(path)
    def setup(self):
        if self.spotSchema<=1:
             version="{version:02d}"
        elif self.spotSchema==2:
            version="{version:03d}"
        self.mm=self.MM.format(shotShortname=self.shotShortname, variant="{variant}", version=version)

    def getVariants(self):
        files = glob.glob(os.path.join(self.path,"*.nk"))
        variants=set()
        for f in files:
            variants.add(os.path.basename(f).split("_")[1])
        return list(variants)
    @property
    def version(self):
        return self._getVersion()
    def _getVersion(self):
        if self.vers:
            return self.vers
        if not self.path.endswith(".nk"):
            raise AttributeError("No Version Available")
        return int(os.path.splitext(os.path.basename(self.path))[0].split("_v")[1])
    @property
    def variant(self):
        return self._getVariant()
    def _getVariant(self):
        if self.vari:
            return self.vari
        if not self.path.endswith(".nk"):
            raise AttributeError("No Variant Available")
        return os.path.splitext(os.path.basename(self.path))[0].split("_")[1]

    def getVersions(self, variant=None):
        if variant==None:
            variant=self.variant
        files = glob.glob(os.path.join(self.compPath,self.mm.format(variant=variant,version=999).replace("999","*")))
        files.sort()
        files = [CompPath(f) for f in files]
        return files
    @checkVariant_decorator
    def getNextVersion(self, variant=None, version=None):
        if version==None:
            version=0
            versions=self.getVersions()
            if versions:
                version=self.getVersions()[-1].version+1
        return CompPath(os.path.join(self.compPath,self.mm.format(version=version, variant=variant)))
class ConfigPath(PathBase):
    __metaclass__ = PathInterface
    def __new__(cls, path, *args, **kwargs):
        return str.__new__(cls, path)
    def __init__(self, path, shotName=None, variant=None):
        self._shotName = shotName
        self._variant  = variant
        super(ConfigPath, self).__init__(path)
    def setup(self):
        pass
    def list(self):
        return map(lambda name:ConfigPath(os.path.join(self.path, name)), os.listdir(self.configPath))
    def getConfig(self, shotName=None, variant=None):
        if shotName:
            self._shotName=shotName
        if not variant:
            variant = self.variant
        if self.shotName and variant:
            return ConfigPath(os.path.join(self.configPath, "{spotshort}{shot}_{variant}.xml".format(spotshort=self.spot.shortname,
                                                                                                 shot=self.shotName,
                                                                                                 variant=variant)))
        else:
            raise AttributeError( "Missing shot_name or variant.")

    @property
    def shotName(self):
        if self._shotName:
            if self.spotSchema>1:
                return self._shotName
            else:
                if re.findall("\d+", self._shotName):
                    return re.findall("\d+", self._shotName)[0]
                return self._shotName
        if self.path.endswith(".xml"):
            return os.path.basename(self.path)[7:].split("_")[0]
    @property
    def variant(self):
        if self._variant:
            return self._variant
        if self.path.endswith(".xml"):
            variant=os.path.basename(self.path)
            variant, ext=os.path.splitext(variant)
            return variant.split("_")[-1]
class FramesPath(PathBase):
    __metaclass__ = PathInterface
    def __init__(self, path):
        super(FramesPath, self).__init__(path)
    def setup(self):
        pass

class PathManagerInterface(type):
    cache={}
    def __call__(cls, path):
        #user passed in a pathmanager so don't make anything
        if isinstance(path, PathManager) or isinstance(path, PathBase):
            return path

        path=fixPath(path)
        if path in cls.cache:
            #path has already been made or is currently being made
            return cls.cache[path]
        else:
            cls.cache[path]=None
            pm=type.__call__(cls, path)
            if pm.obj:
                #if path is a shot, asset, comp, etc. return the concrete class
                cls.cache[path]=pm.obj
            else:
                #return the pathmanager
                cls.cache[path]=pm
                pm.pm=pm
            return cls.cache[path]
class PathManager(str):
    __metaclass__ = PathManagerInterface
    schema2Assets=["characters", "layouts", "light_rigs", "mtl", "props", "sets", "shaders"]
    @staticmethod
    def getRoot(path):
        splits = splitPath(fixPath(path))
        spotSchema=None
        spotPath=None
        jobRootIndex=0
        if "restore" in [x.lower() for x in splits]:
            for i, split in enumerate(splits):
                if re.match("^\D[\D\d]+_[PN]\d{5}$", split):
                    jobRootIndex=i-1
                    break
            else:
                print "Cannot read path from restore"
        else:
            if "jobs" in splits:
                jobRootIndex=splits.index("jobs")
        jobPath=joinPath(splits[:jobRootIndex+2])
        spotFolders1=["artwork","assets","audio","autosave","bin","boards","comp","configs","confirmationDelivery","data","designAssets","edl","farmBlastFiles","frames","houdini","lights","mayaData","mentalRay","notes","objs","renderData","roughCuts","scenes","scripts","shaders","shootData","shotgrid","slates","sourceImages","workspace.mel","xsi"]
        spotFolders2=["2d","3d","digital","elements","renders","roughcuts"]
        #find based on given path
        if len(splits)>=jobRootIndex+3 and splits[jobRootIndex+2]=="3D_assets":
            return 2, spotPath, jobRootIndex
        if len(splits)>=jobRootIndex+4 and splits[jobRootIndex+3]=="master":
            return 1, spotPath, jobRootIndex
        if len(splits)>=jobRootIndex+3:
            spotPath=joinPath(splits[:jobRootIndex+3])
            if len(splits)>=jobRootIndex+4:
                if splits[jobRootIndex+3] in spotFolders1:
                    return 1, spotPath, jobRootIndex
                elif splits[jobRootIndex+3] in spotFolders2:
                    return 2, spotPath, jobRootIndex
        #find based of listdir
        #last resort since schema is suppose to be spot level
        if len(splits)>=jobRootIndex+2:
            jobPath=joinPath(splits[:jobRootIndex+2])
            if os.path.exists(jobPath):
                files = set(os.listdir(jobPath))
                if "3D_assets" in files:
                    return 2, spotPath, jobRootIndex
                else:
                    return 1, spotPath, jobRootIndex
        return None, spotPath, jobRootIndex
    @staticmethod
    def getSchema(path):
        return PathManager.getRoot(path)[0]
    def makeFolderClass(self, folderPath, cls=BasePath):
        if folderPath not in PathManagerInterface.cache:
            out=cls(folderPath, source=self)
        elif str(self.path) != str(folderPath):
            out=cls(folderPath, source=self)
        else:
            out=folderPath
        return out
    def __str__(self):
        return str(self.path)
    def __repr__(self):
        return "<{0} {1}>".format(str(self.__class__)[7:-1], self.path)
    def __len__(self):
        if self.path:
            return len(self.path)
        else:
            return 0
    def __init__(self, path=None):
        self.obj=None
        self.path=None

        self.jobNumber=None
        self.jobDirname=None
        self.jobShortname=None
        self.jobType=None
        self.jobPath=None

        self.spot=None
        self.spotLetter=None
        self.spotDirname=None
        self.spotFullname=None
        self.spotShortname=None
        self.spotSchema=None
        self.spotPath=None
        self.projectPath=None
        self.configPath=None
        self.assetPath=None
        self.charPath=None
        self.propPath=None
        self.framesPath=None
        self.shotsPath=None
        self.spotReferencePath=None
        self.spotImagesPath=None

        self.shot=None
        self.shotPath=None
        self.shotNumber=None
        self.shotName=None
        self.shotType=None
        self.shotFullname=None
        self.shotShortname=None
        self.shotStage=None
        self.compPath=None
        self.anmPath=None
        self.lgtPath=None
        self.shotImagesPath=None
        self.shotReferencePath=None
        self.renderFolders=[]
        if not path:
            return
        self.path = fixPath(path)
        self.splits = splitPath(self.path)
        self.spotSchema, self.spotPath, self.jobRootIndex = PathManager.getRoot(self.path)
        if not self.jobRootIndex:
            self.path=None
            return
        if len(self.splits)>=self.jobRootIndex+2:
            self.setJobProperties()
            if self.jobNumber and len(self.splits)>=self.jobRootIndex+3:
                if self.splits[self.jobRootIndex+2]=="3D_assets":
                    self.obj=AssetPath(self)
                else:
                    self.setSpotProperties()
                    if len(self.splits)>self.jobRootIndex+4:
                        self.setShot()
    def setJobProperties(self):
        self.jobDirname = self.splits[self.jobRootIndex+1]
        self.jobPath = joinPath(self.splits[:self.jobRootIndex+2])
        if not re.search("\d",self.jobDirname):
            return
        self.jobNumber = int(self.jobDirname[-5:])
        self.jobType = self.jobDirname[-6]
        self.jobShortname = self.jobType+str(self.jobNumber)
        if self.spotSchema>1:
            self.assetPath=self.makeFolderClass(os.path.join(self.jobPath,   "3D_assets"))
            self.charPath =self.makeFolderClass(os.path.join(self.assetPath, "characters"), AssetPath)
            for path in self.schema2Assets:
                setattr(self, path+"Path", self.makeFolderClass(os.path.join(self.assetPath, path), AssetPath))
            self.ws="workshops"
            self.vs="past_versions"
        else:
            self.vs="versions"
            self.ws="workshop"
        path = self.path
        passthrough = self.__dict__
        del passthrough["path"]
        self.job  = ProxyJob(jobtype=self.jobType,
                             id=self.jobNumber,
                             dir_name=self.jobDirname,
                             path=self.jobPath,
                             shortname=self.jobShortname,
                             **passthrough)
        self.path=path
    def setSpotProperties(self):
        self.spotDirname   = self.splits[self.jobRootIndex+2]
        self.spotPath      = joinPath(self.splits[:self.jobRootIndex+3])
        self.spotLetter    = self.spotDirname[0]
        self.spotShortname = self.jobType+str(self.jobNumber)+self.spotLetter
        self.spotFullname  = "%s/%s"%(self.jobDirname, self.spotDirname)
        self.spotReferencePath = self.makeFolderClass(os.path.join(self.spotPath,"reference"))

        if self.spotSchema==1:
            self.projectPath   =self.spotPath
            self.configPath    =self.makeFolderClass(os.path.join(self.spotPath,   "configs"), ConfigPath)
            self.framesPath    =self.makeFolderClass(os.path.join(self.spotPath,   "frames"), FramesPath)
            self.shotsPath     =self.makeFolderClass(os.path.join(self.projectPath,"scenes"))
            self.spotImagesPath=self.makeFolderClass(os.path.join(self.projectPath,"sourceImages"))

            self.assetPath     =self.makeFolderClass(os.path.join(self.shotsPath, "master"))
            self.charPath      =self.makeFolderClass(os.path.join(self.assetPath, "char"), AssetPath)
            for path in self.schema2Assets:
                setattr(self, path+"Path", self.charPath)
        elif self.spotSchema==2:
            self.projectPath   =os.path.join(self.spotPath, "3d")
            self.configPath    =self.makeFolderClass(os.path.join(self.projectPath, "configs"), ConfigPath)
            self.framesPath    =self.makeFolderClass(os.path.join(self.spotPath, "renders"), FramesPath)
            self.shotsPath     =self.makeFolderClass(os.path.join(self.projectPath,"shots"))
            self.spotImagesPath=self.makeFolderClass(os.path.join(self.spotPath,"reference", "stills"))
        else:
            return

        path = self.path
        passthrough = self.__dict__
        del passthrough["path"]
        self.spot = ProxySpot(dir_name=self.spotDirname,
                              schema=self.spotSchema,
                              fullname=self.spotFullname,
                              shortname=self.spotShortname,
                              path=self.spotPath,
                              letter=self.spotLetter,
                              **passthrough)
        self.path=path
    def setShot(self):
        '''determine which object to make'''
        if "comp" in self.splits:
            if self.spotSchema<=1:
                self.setShotSchema1(self.splits.index("comp")+1)
            elif self.spotSchema==2:
                self.setShotSchema2(self.splits.index("comp")-1)
            self.obj=CompPath(self)

        elif "master" in self.splits:
            self.obj=AssetPath(self)

        elif ("frames" in self.splits or "renders" in self.splits) and ("shoot_frames" not in self.splits and "precomp" not in self.splits):
            if self.spotSchema<=1 and "frames" in self.splits:
                self.setShotSchema1(self.splits.index("frames")+2)
            elif self.spotSchema==2 and "shots" in self.splits:
                self.setShotSchema2(self.splits.index("shots")+1)
            self.obj=FramesPath(self)

        elif self.contains(self.shotsPath):
            if self.spotSchema<=1:
                shot=self.setShotSchema1(self.splits.index("scenes")+1)
            elif self.spotSchema==2:
                shot=self.setShotSchema2(self.splits.index("shots")+1)
            if shot:
                self.obj=ShotPath(self)

        elif "configs" in self.splits:
            shotname=None
            if self.path.endswith(".xml"):
                shotname=os.path.basename(self.path)
                shotname=shotname.split("_")[0]
                shotname=shotname[7:]
            if shotname and shotname!="master":
                if self.spotSchema<=1:
                    shot=self.setShotSchema1(shotName="shot"+shotname)
                elif self.spotSchema==2:
                    shot=self.setShotSchema2(shotName=shotname)
            self.obj=ConfigPath(self)
    def setShotAccessor(self):
        path = self.path
        shot = self.shot
        passthrough = self.__dict__
        del passthrough["path"]
        del passthrough["shot"]
        self.shot = ProxyShot(stage=self.shotStage,
                              shortname=self.shotShortname,
                              path=self.shotPath,
                              name=self.shotName,
                              shot=shot,
                              **passthrough)
        self.path=path

        self.anmPath = self.makeFolderClass(os.path.join(self.shotPath, "anm"), ShotPath)
        self.lgtPath = self.makeFolderClass(os.path.join(self.shotPath, "lgt"), ShotPath)
        self.shotFullname  = "%s/%s/%s"%(self.jobDirname, self.spotDirname, self.shotName)
        self.shot.anmPath=self.anmPath
        self.shot.lgtPath=self.lgtPath
        self.shot.fullname=self.shotFullname
    def setShotSchema1(self, shotIndex=None, shotName=None):
        self.shotName=shotName
        self.shotIndex=shotIndex
        if shotIndex:
            if len(self.splits)<=shotIndex:
                return
            self.shotName = self.splits[shotIndex]
        match = re.search("\d+$", self.shotName)
        if match:
            self.shot=int(match.group())
        else:
            return
        self.shotNumber = self.shot
        self.shotStage = re.match("\D+", self.shotName).group()
        self.shotShortname = "%s%d%s%03d"%(self.jobType,self.jobNumber,self.spotLetter,self.shot)

        self.shotImagesPath    = self.spotImagesPath
        self.shotPath          = self.makeFolderClass(os.path.join(self.shotsPath, self.shotName))
        self.shotReferencePath = self.makeFolderClass(os.path.join(self.shotPath, "reference"))
        self.compPath          = self.makeFolderClass(os.path.join(self.spotPath, "comp", self.shotName), CompPath)
        self.shotIcon          = os.path.join(self.shotReferencePath, "{shot}Icon.png".format(shot=self.shotName))
        self.renderFolders=["anm_frames", "back_plates", "comp_frames", "design_frames", "fx_frames", "render_frames", "ship_frames", "shoot_frames", "test_frames", "track_plates"]
        for path in self.renderFolders:
             setattr(self,
                     path,
                     self.makeFolderClass(os.path.join(self.framesPath,path,self.shotName),
                                          FramesPath))
        self.render_precomp      = self.makeFolderClass(os.path.join(self.framesPath, "render_frames", "precomp"), FramesPath)
        self.render_shot_precomp = self.makeFolderClass(os.path.join(self.render_frames, "precomp"), FramesPath)

        self.setShotAccessor()

        return self.shot
    def setShotSchema2(self, shotIndex=None, shotName=None):
        self.shotName=shotName
        if not self.shotName:
            if not shotIndex or len(self.splits)<=shotIndex:
                return
            self.shotIndex = shotIndex
            self.shotName = self.splits[shotIndex]
        if self.shotName=="master":
            self.shot, self.shotNumber, self.shotStage, self.shotShortname=["master"]*4
            return
        self.shot = int(re.search("\d+$", self.shotName).group())
        self.shotNumber = self.shot
        self.shotStage = re.match("\D+", self.shotName).group()
        self.shotShortname = "%s%d%s%s"%(self.jobType, self.jobNumber,self.spotLetter,self.shotName)
        self.shotPath          = self.makeFolderClass(os.path.join(self.shotsPath, self.shotName))

        self.shotImagesPath    = self.makeFolderClass(os.path.join(self.shotPath, "images"))
        self.compPath          = self.makeFolderClass(os.path.join(self.shotPath, "comp", "nuke"), CompPath)
        self.shotReferencePath = self.shotImagesPath

        self.renderFolders = ["anim_frames", "backplates", "comp_frames", "design_frames", "fx_frames", "render_frames", "wip_frames"]
        for path in self.renderFolders:
            setattr(self,
                    path,
                    self.makeFolderClass(os.path.join(os.path.join(self.framesPath, "shots", self.shotName),path),
                                         FramesPath))
        self.render_precomp      = self.makeFolderClass(os.path.join(self.render_frames, "precomp"), FramesPath)
        self.render_shot_precomp = self.render_precomp

        self.setShotAccessor()
        return self.shot
    def override(self, job=None, spot=None, shot=None):
        if job and self.job:
            self.splits[self.jobRootIndex+1]=job
        if spot and self.spot:
            self.splits[self.jobRootIndex+2]=spot
        if shot and self.shot:
            self.splits[self.shotIndex]=shot

        if shot and self.spot and not self.shot:
            return PathManager(os.path.join(self.shotsPath, shot))

        return PathManager(joinPath(self.splits))
    def contains(self, path):
        if not path:
            return
        return path in self.path and len(self.splits)>len(splitPath(path))
    @property
    def restored(self):
        return PathManager(self.path.replace(self.jobPath, os.path.join(chrlx.PATHS['CHRLX_JOBS'], self.jobDirname)))
    @property
    def repair(self):
        print "repairing", self.path
        path=find_sensitive_path(self.path)
        if path:
            return PathManager(path)



def createAssetDirectories(assetFolder, assType, name):
    """creates asset directories from args
        -asset folder is path to asset folder [...JOB/3D_assets/]
        -assType is either "characters", "props", or "sets"
        -name is string name of the new character
    """
    assetFolder = fixPath("{0}/{1}/{2}".format(assetFolder, assType, name))
    if not os.path.isdir(assetFolder):
        print "------making {0}".format(assetFolder)
        os.makedirs(assetFolder)
        assetContents = ["geo", "rig", "mtl", "sourceImages", "reference", "icon"]
        for direct in assetContents:
            assDirect = "{0}/{1}".format(assetFolder, direct)
            print "------making {0}".format(assDirect)
            os.makedirs(assDirect)
        geoContents = ["import_export", "past_versions", "workshops"]
        for direct in geoContents:
            geoDirect = "{0}/geo/{1}".format(assetFolder, direct)
            print "------making {0}".format(geoDirect)
            os.makedirs(geoDirect)
        geoWSContents = ["max", "mudbox", "zbrush"]
        for direct in geoWSContents:
            WSDirect = "{0}/geo/workshops/{1}".format(assetFolder, direct)
            print "------making {0}".format(WSDirect)
            os.makedirs(WSDirect)
        rigContents = ["import_export", "past_versions", "workshops"]
        for direct in rigContents:
            rigDirect = "{0}/rig/{1}".format(assetFolder, direct)
            print "------making {0}".format(rigDirect)
            os.makedirs(rigDirect)
        mtlContents = ["import_export", "past_versions", "workshops"]
        for direct in mtlContents:
            mtlDirect = "{0}/mtl/{1}".format(assetFolder, direct)
            os.makedirs(mtlDirect)

    else:
        print "The directory already exists: {0}".format(assetFolder)

def find_sensitive_path(path, partial=False):
    '''
    find case sensitive path give a case insensitive path
    find linux path given windows path
    partial: return longest match if full path does not exist
    '''
    splits=deque(splitPath(fixPath(path)))
    currentPath=[os.sep]
    if os.name=="nt":
        if ":" in path:
            currentPath=[splits[0]]
            splits.popleft()
        else:
            machines=getShares(splits[0])
            for share in machines:
                if splits[1].lower() == share.lower():
                    #cannot find a way of getting case sensitive machine name so manually lower+capitalize it (Bluearc/Blackgate)
                    currentPath=[splits[0].lower().capitalize(), share]
                    splits.popleft()
                    splits.popleft()
                    break
            if not currentPath:
                return

    def find_in_folder():
        if splits:
            item=None
            if os.path.exists(joinPath(currentPath)):
                for test in os.listdir(joinPath(currentPath)):
                    if test.lower() == splits[0].lower():
                        item=test
                if item:
                    splits.popleft()
                    currentPath.append(item)
                    find_in_folder()
    find_in_folder()
    if partial or not splits:
        return fixPath(joinPath(currentPath))

def getShares(machine=None, flat=False):
    '''get a dictionary of letter mapped unc paths'''
    map={"unmapped":[]}
    args = ['net', 'view']
    if machine:
        net_view = subprocess.Popen(args+[machine], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in net_view.stdout.readlines():
            if "Disk" in line:
                map["unmapped"].append(line.split()[0])
        return map["unmapped"]
    else:
        net_view = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in net_view.stdout.readlines():
            if line.startswith("\\"):
                map["unmapped"].append(line.split()[0])
    net_use = subprocess.Popen(['net','use'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in net_use.stdout.readlines():
        if "Microsoft Windows Network" in line:
            if len(line.split())>4:
                line=line.split()[0:-3]
                if line[0]=="OK":
                    line=line[1:]
                if len(line)>1:
                    map[line[0]]=line[1]
                else:
                    map["unmapped"].append(line[0])
    if flat:
        unmapped=map["unmapped"]
        del map["unmapped"]
        return unmapped+[map[letter] for letter in map]
    return map


if __name__=="__main__":
    pass
