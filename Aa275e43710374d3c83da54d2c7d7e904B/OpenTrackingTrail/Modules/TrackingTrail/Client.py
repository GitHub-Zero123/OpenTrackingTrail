# -*- coding: utf-8 -*-
from ...QuModLibs.Client import *
from ...QuModLibs.Util import TRY_EXEC_FUN
from ...QuModLibs.Modules.EntityComps.Client import QBaseEntityComp
from ...QuModLibs.Modules.ModelRender.Client import QFreeModelPool, QNativeEntityModel
from ...QuModLibs.Modules.EventsPool.Client import POOL_ListenForEvent, POOL_UnListenForEvent
from copy import copy
import math
import time
lambda: "By 棱花 && KID团队 请在遵循协议的前提下使用"

clientComp = clientApi.GetEngineCompFactory()

class BaseKnifeLightEffect:
    """ 刀光效果组件 绘制刀光(N例模式) """

    def __init__(self):
        self._modelPool = QFreeModelPool("open_knife_light")
        self.binderArgs = {}
        self.customArgs = {}
        self.entityId = None
        self.boneObj = BaseKnifeLightEffectRenderer.BoneBinder("", "")
        self.knifeList = list()
        self.length = 30
        self.default_length = 30
        self.free = False
        self.fps = 120.0
        self.tickTime = 1.0 / self.fps
        self.lastTick = 0

    def getLength(self, value1, value2):
        pix = 0
        end_value = 0
        for v1 in value1:
            v2 = value2[pix]
            end_value += pow(v2 - v1, 2)
            pix += 1
        return math.sqrt(end_value)

    def mix(self, value1, value2, t):
        pix = 0
        newValue = []
        for v1 in value1:
            v2 = value2[pix]
            newValue.append((v2 - v1) * t + v1)
            pix += 1
        return tuple(newValue)

    def renderUpdate(self, moveTime=0.033):
        if self.lastTick and time.time() - self.lastTick <= self.tickTime:
            return
        self.lastTick = time.time()
        self.createKnifeFrag()
        for index in range(0, len(self.knifeList)):
            if index >= len(self.knifeList) - 1: continue
            nowKnifeFrag = self.knifeList[index]
            lastKnifeFrag = self.knifeList[index + 1]
            fragModel = nowKnifeFrag[0]
            mix_end_pos = self.mix(lastKnifeFrag[2], nowKnifeFrag[2], 0.5)
            if index >= 1:
                nextKnifeFrag = self.knifeList[index - 1]
                next_direction = clientApi.GetDirFromRot(clientApi.GetRotFromDir((nowKnifeFrag[2][0] - nextKnifeFrag[2][0], nowKnifeFrag[2][1] - nextKnifeFrag[2][1], nowKnifeFrag[2][2] - nextKnifeFrag[2][2])))
                now_direction = clientApi.GetDirFromRot(clientApi.GetRotFromDir((lastKnifeFrag[2][0] - nowKnifeFrag[2][0], lastKnifeFrag[2][1] - nowKnifeFrag[2][1], lastKnifeFrag[2][2] - nowKnifeFrag[2][2])))
                mix_end_direction = self.mix(next_direction, now_direction, 0.4)
                length = self.getLength(nowKnifeFrag[2], lastKnifeFrag[2])
                mix_end_pos = nowKnifeFrag[2][0] + mix_end_direction[0] * length, nowKnifeFrag[2][1] + mix_end_direction[1] * length, nowKnifeFrag[2][2] + mix_end_direction[2] * length
            elif index <= len(self.knifeList) - 3:
                nextKnifeFrag = self.knifeList[index + 2]
                next_direction = clientApi.GetDirFromRot(clientApi.GetRotFromDir((nextKnifeFrag[2][0] - lastKnifeFrag[2][0],nextKnifeFrag[2][1] - lastKnifeFrag[2][1],nextKnifeFrag[2][2] - lastKnifeFrag[2][2])))
                now_direction = clientApi.GetDirFromRot(clientApi.GetRotFromDir((lastKnifeFrag[2][0] - nowKnifeFrag[2][0], lastKnifeFrag[2][1] - nowKnifeFrag[2][1], lastKnifeFrag[2][2] - nowKnifeFrag[2][2])))
                mix_end_direction = self.mix(next_direction, now_direction, 1.5)
                length = self.getLength(nowKnifeFrag[2], lastKnifeFrag[2])
                mix_end_pos = nowKnifeFrag[2][0] + mix_end_direction[0] * length, nowKnifeFrag[2][1] + mix_end_direction[1] * length, nowKnifeFrag[2][2] + mix_end_direction[2] * length
            self.renderKnifeModel(fragModel, nowKnifeFrag, lastKnifeFrag, index, mix_end_pos)

    def onCreate(self):
        self.length = self.binderArgs["length"] * 15
        self.default_length = self.binderArgs["length"] * 15
        pass

    def FreeModel(self):
        if not clientApi.GetEngineCompFactory().CreateGame(levelId).HasEntity(self.entityId):
            self._modelPool.freeAllModel()
            self.knifeList = []
        if len(self.knifeList) > 1:
            self.length -= max(1, self.default_length * 0.01)
            self.default_length -= max(1, self.default_length * 0.01)
        else:
            POOL_UnListenForEvent("OnScriptTickClient", self.FreeModel)
            POOL_UnListenForEvent("OnScriptTickNonChaseFrameClient", self.renderUpdate)
            self._modelPool.freeAllModel()

    def onFree(self):
        self.free = True
        POOL_ListenForEvent("OnScriptTickNonChaseFrameClient", self.renderUpdate)
        POOL_ListenForEvent("OnScriptTickClient", self.FreeModel)
        pass

    def createKnifeFrag(self):
        if not clientApi.GetEngineCompFactory().CreateGame(levelId).HasEntity(self.entityId):
            self._modelPool.freeAllModel()
            self.knifeList = []
            return
        self.length = int(
            self.default_length * min(clientApi.GetEngineCompFactory().CreateGame(levelId).GetFps(), 120.0) * 0.015)
        Mx, My, Mz = (0, 0, 0)
        length = 0
        if self.binderArgs["motion"] != (0, 0, 0):
            length = self.getLength((0, 0, 0), self.binderArgs["motion"])
            Mx, My, Mz = self.binderArgs["motion"]
            Rx, Ry = clientApi.GetEngineCompFactory().CreateRot(self.entityId).GetRot()
            rx, ry = clientApi.GetRotFromDir((Mx, My, Mz))[0], clientApi.GetRotFromDir((Mx, My, Mz))[1] + Ry
            Mx, My, Mz = clientApi.GetDirFromRot((rx, ry))
        for knife_data in self.knifeList:
            knife_data[1] = knife_data[1][0] + Mx * length, knife_data[1][1] + My * length, knife_data[1][
                2] + Mz * length
            knife_data[2] = knife_data[2][0] + Mx * length, knife_data[2][1] + My * length, knife_data[2][
                2] + Mz * length
        oldList = copy(self.knifeList)
        newList = list()
        locator_pos_begin = self.boneObj.getBonePos(self.boneObj.locators[0])
        locator_pos_end = self.boneObj.getBonePos(self.boneObj.locators[1])
        rx, ry = self.binderArgs["rotate"]
        mx, my, mz = locator_pos_end[0] - locator_pos_begin[0], locator_pos_end[1] - locator_pos_begin[1], locator_pos_end[2] - locator_pos_begin[2]
        Orx, Ory = clientApi.GetRotFromDir((mx, my, mz))
        nmx = mx * math.cos(math.radians(-Ory)) - mz * math.sin(math.radians(-Ory))
        nmz = mx * math.sin(math.radians(-Ory)) + mz * math.cos(math.radians(-Ory))
        mx, my, mz = nmx, my, nmz
        nmz = mz * math.cos(math.radians(Orx)) - my * math.sin(math.radians(Orx))
        nmy = mz * math.sin(math.radians(Orx)) + my * math.cos(math.radians(Orx))
        mx, my, mz = mx, nmy, nmz
        nmz = mz * math.cos(math.radians(rx)) - my * math.sin(math.radians(rx))
        nmy = mz * math.sin(math.radians(rx)) + my * math.cos(math.radians(rx))
        mx, my, mz = mx, nmy, nmz
        nmx = mx * math.cos(math.radians(ry)) - mz * math.sin(math.radians(ry))
        nmz = mx * math.sin(math.radians(ry)) + mz * math.cos(math.radians(ry))
        mx, my, mz = nmx, my, nmz
        nmz = mz * math.cos(math.radians(-Orx)) - my * math.sin(math.radians(-Orx))
        nmy = mz * math.sin(math.radians(-Orx)) + my * math.cos(math.radians(-Orx))
        mx, my, mz = mx, nmy, nmz
        nmx = mx * math.cos(math.radians(Ory)) - mz * math.sin(math.radians(Ory))
        nmz = mx * math.sin(math.radians(Ory)) + mz * math.cos(math.radians(Ory))
        mx, my, mz = nmx, my, nmz
        locator_pos_end = locator_pos_begin[0] + mx, locator_pos_begin[1] + my, locator_pos_begin[2] + mz
        length = self.getLength(locator_pos_begin, locator_pos_end)
        width = copy(self.binderArgs["width"])
        offset = copy(self.binderArgs["offset"])
        if length < 0.1:
            self.length = 0
        if self.free:
            width = 0.001
        self_width = self.getLength(self.boneObj.getBonePos(self.boneObj.locators[1]),
                                    self.boneObj.getBonePos(self.boneObj.locators[0])) * 2.9
        direction = clientApi.GetDirFromRot(clientApi.GetRotFromDir((locator_pos_end[0] - locator_pos_begin[0],
                                                                     locator_pos_end[1] - locator_pos_begin[1],
                                                                     locator_pos_end[2] - locator_pos_begin[2])))
        bone_pos = locator_pos_begin[0] + direction[0] * offset, locator_pos_begin[1] + direction[1] * offset, locator_pos_begin[2] + direction[2] * offset
        target_bone_pos = bone_pos[0] + direction[0] * width * self_width, bone_pos[1] + direction[
            1] * width * self_width, bone_pos[2] + direction[2] * width * self_width
        modelId = self._modelPool.malloc(True)
        clientApi.GetEngineCompFactory().CreateModel(levelId).SetTexture(self.binderArgs["texture"], modelId)
        if self.binderArgs["bloom"]:
            clientApi.GetEngineCompFactory().CreateModel(levelId).SetModelMaterial(modelId, "knife_light_bloom")
        newList.append([modelId, bone_pos, target_bone_pos])
        for i in oldList:
            newList.append(i)
        self.knifeList = newList
        if self.knifeList and len(self.knifeList) > self.length:
            for i in range(int(max((len(self.knifeList) - self.length) / 5.0, 1) + 1)):
                if not self.destroyKnifeFrag():
                    break

    def destroyKnifeFrag(self):
        if self.knifeList:
            endFrag = self.knifeList[-1]
            self._modelPool.free(endFrag[0], True)
            self.knifeList.pop()
            return True
        return False

    def renderKnifeModel(self, fragModel, nowKnifeFrag, lastKnifeFrag, index, mix_end_pos):
        startColor = self.binderArgs["startColor"]
        endColor = self.binderArgs["endColor"]
        now_begin_x, now_begin_y, now_begin_z = nowKnifeFrag[1]
        now_end_x, now_end_y, now_end_z = nowKnifeFrag[2]
        last_begin_x, last_begin_y, last_begin_z = lastKnifeFrag[1]
        last_end_x, last_end_y, last_end_z = lastKnifeFrag[2]
        mix_end_x, mix_end_y, mix_end_z = mix_end_pos
        clientComp.CreateModel(levelId).SetFreeModelPos(fragModel, now_begin_x, now_begin_y, now_begin_z)
        clientComp.CreateModel(levelId).SetFreeModelScale(fragModel, 1, 1, 1)
        clientComp.CreateModel(levelId).SetFreeModelRot(fragModel, 0, 0, 0)

        last_progress = round(1.0 - (index + 2) / max(float(len(self.knifeList) - 2), 1), 2)

        target_progress = round(1.0 - (index + 1) / max(float(len(self.knifeList) - 2), 1), 2)

        start_r, start_g, start_b, start_a = startColor

        start_r = min(max(round(start_r, 2), 0.01), 0.99)
        start_g = min(max(round(start_g, 2), 0.01), 0.99)
        start_b = min(max(round(start_b, 2), 0.01), 0.99)
        start_a = min(max(round(start_a, 2), 0.01), 0.99)

        end_r, end_g, end_b, end_a = endColor

        end_r = min(max(round(end_r, 2), 0.01), 0.99)
        end_g = min(max(round(end_g, 2), 0.01), 0.99)
        end_b = min(max(round(end_b, 2), 0.01), 0.99)
        end_a = min(max(round(end_a, 2), 0.01), 0.99)

        clientComp.CreateModel(levelId).SetExtraUniformValue(fragModel, 1, (
        now_end_x - now_begin_x, now_end_y - now_begin_y, now_end_z - now_begin_z,
        last_progress * 100.0 + target_progress))
        clientComp.CreateModel(levelId).SetExtraUniformValue(fragModel, 2, (
        last_begin_x - now_begin_x, last_begin_y - now_begin_y, last_begin_z - now_begin_z,
        start_r * 1000.0 + start_g * 10.0 + start_b * 0.1))
        clientComp.CreateModel(levelId).SetExtraUniformValue(fragModel, 3, (
        last_end_x - now_begin_x, last_end_y - now_begin_y, last_end_z - now_begin_z,
        end_r * 1000.0 + end_g * 10.0 + end_b * 0.1))
        clientComp.CreateModel(levelId).SetExtraUniformValue(fragModel, 4, (
        mix_end_x - now_begin_x, mix_end_y - now_begin_y, mix_end_z - now_begin_z, start_a * 100.0 + end_a))
        pass

class BaseKnifeLightEffectRenderer(QBaseEntityComp):
    """ 刀光特效渲染器通用组件类 管理目标实体持有N个刀光 """
    _USE_TICK = 0
    _USE_FPS = 1

    class BoneBinder:
        """ 骨骼绑定器 """

        def __init__(self, entityId, boneName, locators=[]):
            # type: (str, str, list[str]) -> None
            self.entityId = entityId
            """ 绑定的实体 """
            self.boneName = boneName
            """ 绑定的Bone """
            self.locators = locators
            """ locators定位器表 用于计算自有坐标系 """
            self.customArgs = {}
            """ 自定义参数表 """
            self._effectSet = set()  # type: set[BaseKnifeLightEffect]
            """ 刀光效果集合 """
            self._boneObjMap = {}  # type: dict[str, QNativeEntityModel.MinecraftBone]

        def getBoneObject(self, boneName=""):
            # type: (str) -> QNativeEntityModel.MinecraftBone
            if not boneName in self._boneObjMap:
                self._boneObjMap[boneName] = QNativeEntityModel.MinecraftBone(self.entityId, boneName)
            return self._boneObjMap[boneName]

        def getBonePos(self, boneName=""):
            # 默认使用Par粒子方案获取Pos
            #self.getBoneObject(boneName).getTestWorldPos()
            return self.getBoneObject(boneName).getParWorldPos()

        def getRelativeSpaceCoordinates(self):
            """ 计算相对空间坐标系(自有坐标系) """
            return (0, 0, 0)

        def getEffectCls(self):
            """ 匹配刀光效果类(适用于高度自定义场合) """
            return BaseKnifeLightEffect

        def getBoneRot(self, right_begin, right_end):
            begin_pos = right_begin
            end_pos = right_end
            z_x2 = pow(end_pos[0]-begin_pos[0], 2)
            z_z2 = pow(end_pos[2]-begin_pos[2], 2)
            z_y = end_pos[1]-begin_pos[1]
            motion_y = (end_pos[0]-begin_pos[0], 0, end_pos[2]-begin_pos[2])
            motion_z = math.sqrt(z_x2+z_z2)
            try:
                rotate_z = math.degrees(math.atan(z_y/motion_z))
            except:
                rotate_z = 0
            rotate_y = clientApi.GetRotFromDir(motion_y)[1]
            knife_rot = [rotate_y, rotate_z]
            return knife_rot

        def createEffect(self, customArgs={}):
            """ 创建刀光效果 """
            effectObj = self.getEffectCls()()
            effectObj.binderArgs = self.customArgs
            effectObj.customArgs = customArgs
            effectObj.entityId = self.entityId
            effectObj.boneObj = self
            self._effectSet.add(effectObj)
            TRY_EXEC_FUN(effectObj.onCreate)
            return effectObj

        def freeEffect(self, obj):
            # type: (BaseKnifeLightEffect) -> None
            """ 释放刀光效果 """
            if obj in self._effectSet:
                self._effectSet.remove(obj)
                obj.onFree()

        def freeAllEffects(self):
            # type: () -> None
            """ 释放所有刀光效果 """
            for obj in copy(self._effectSet):
                TRY_EXEC_FUN(obj.onFree)
            self._effectSet.clear()

        def onCreate(self):
            self.createEffect()

        def onFree(self):
            self.freeAllEffects()

        def renderUpdate(self, moveTime=0.033):
            """ 渲染更新方法 不一定是Tick 也可能是FPS事件驱动 """
            for obj in copy(self._effectSet):
                TRY_EXEC_FUN(obj.renderUpdate, moveTime)

    def __init__(self):
        QBaseEntityComp.__init__(self)
        self._binderMap = {}  # type: dict[str, BaseKnifeLightEffectRenderer.BoneBinder]
        self._fpsListenState = False

    def listenFPSEvent(self):
        if not self._fpsListenState:
            self._fpsListenState = True
            POOL_ListenForEvent("OnScriptTickNonChaseFrameClient", self.onFPSEvent)
            self.onFPSEvent()

    def unListenFPSEvent(self):
        if self._fpsListenState:
            self._fpsListenState = False
            POOL_UnListenForEvent("OnScriptTickNonChaseFrameClient", self.onFPSEvent)

    def getRenderUpdateMode(self):
        """ 获取渲染更新模式 0.Tick 1.FPS """
        return BaseKnifeLightEffectRenderer._USE_FPS

    def createBinder(self, boneName, locators=[], customArgs={}):
        # type: (str, list[str], dict) -> BaseKnifeLightEffectRenderer.BoneBinder
        """ 创建一个绑定定位器 重复创建将会不生效
            - BoneName不代表真的是某个Bone仅用于区分键值储存 具体以locators为准
        """
        if boneName in self._binderMap:
            binder = self._binderMap[boneName]
            return binder
        # 青云非要用DICT传数据 感觉不如对象模型
        binder = self.__class__.BoneBinder(self.entityId, boneName, locators)
        customArgs["width"] = customArgs.get("width", 0.5)
        customArgs["offset"] = customArgs.get("offset", 0)
        customArgs["length"] = customArgs.get("length", 0.7)
        customArgs["startColor"] = customArgs.get("startColor", (1, 1, 1, 1))
        customArgs["endColor"] = customArgs.get("endColor", (1, 1, 1, 0))
        customArgs["knifeLightModel"] = customArgs.get("knifeLightModel", 0)
        customArgs["texture"] = customArgs.get("texture", "knife_light")
        customArgs["bloom"] = customArgs.get("bloom", False)
        customArgs["rotate"] = customArgs.get("rotate", (0, 0))
        customArgs["motion"] = customArgs.get("motion", (0, 0, 0))
        binder.customArgs = customArgs
        self._binderMap[boneName] = binder
        binder.onCreate()
        return binder

    def getBinder(self, boneName):
        # type: (str) -> BaseKnifeLightEffectRenderer.BoneBinder | None
        """ 基于BoneName获取相关绑定器 """
        return self._binderMap.get(boneName, None)

    def removeBinder(self, boneName):
        # type: (str) -> None
        """ 删除绑定器 如果存在 """
        if boneName in self._binderMap:
            binder = self._binderMap[boneName]
            del self._binderMap[boneName]
            binder.onFree()

    def removeAllBinder(self):
        # type: () -> None
        """ 删除所有绑定器 """
        for boneName in copy(self._binderMap):
            self.removeBinder(boneName)

    def updateAllBinder(self, moveTime=0.033):
        # type: (float) -> None
        """ 更新所有绑定器 """
        for binder in copy(self._binderMap.values()):
            TRY_EXEC_FUN(binder.renderUpdate, moveTime)

    def onGameTick(self):
        QBaseEntityComp.onGameTick(self)
        # 30Tick事件
        if self.getRenderUpdateMode() == BaseKnifeLightEffectRenderer._USE_TICK:
            # 启用Tick模式时 取消FPS事件
            self.unListenFPSEvent()
            self.updateAllBinder()
            return
        # 使用FPS事件
        self.listenFPSEvent()

    def onFPSEvent(self):
        # 帧事件处理更新
        self.updateAllBinder(200.0 / clientApi.GetEngineCompFactory().CreateGame(levelId).GetFps())

    def onUnBind(self):
        QBaseEntityComp.onUnBind(self)
        self.unListenFPSEvent()
        if self.getUnBindINFO().isGameOver():
            # 若因游戏关闭触发解绑 则不需要回收相关渲染资源
            return
        self.removeAllBinder()

# class BaseEntityAttackKnifeLightRenderer(BaseKnifeLightEffectRenderer):
#     """ 实体攻击刀光渲染器 """
#     def __init__(self):
#         BaseKnifeLightEffectRenderer.__init__(self)

#     def onGameTick(self):
#         BaseKnifeLightEffectRenderer.onGameTick(self)
#         if True:    #  在此处编写你的渲染条件
#             self.createBinder("rightItem", ["right_begin", "right_end"], {"startColor": (1, 1, 1, 1), "endColor": (1, 1, 1, 0), "length": 1, "width": 1, "offset": 0, "texture": "knife_light", "bloom": False, "rotate": (0, 0)})
#         else:
#             self.removeAllBinder()