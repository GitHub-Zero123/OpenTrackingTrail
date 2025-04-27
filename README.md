# OpenTrackingTrail 追踪刀光

OpenTrackingTrail 提供了适用于网易我的世界实时追踪刀光的解决方案

By 棱花 && KID团队

## 运行环境
该项目依赖QuModLibs组件绑定支持 您可以下载相关模块使用
- [QuModLibs下载](https://gitee.com/bili_zero123/qu_mod_libs)
- [动作优化模型标准(参考定位器位置)](https://gitee.com/bili_zero123/ksopen-aopt/tree/main/Models)

## 示例代码

```python
# -*- coding: utf-8 -*-
from QuModLibs.Client import *
from Modules.TrackingTrail.Client import BaseKnifeLightEffectRenderer
lambda: "OpenTrackingTrail Client"

# 顺带给生物HUSK也绑定一份
@BaseKnifeLightEffectRenderer.regEntity("minecraft:husk")
class TestKLRenderer(BaseKnifeLightEffectRenderer):
    """ 测试刀光渲染器 """
    def onGameTick(self):
        BaseKnifeLightEffectRenderer.onGameTick(self)
        if True:    #  在此处编写你的渲染条件 为了测试 这里始终开启
            # ["rightarm", "rightitem"] 为绑定的骨骼/定位器名字 可根据实际需求在模型上调整
            # createBinder需要一个唯一key名 确保tick下重复调用不会重复创建 实现实时更新渲染开关
            self.createBinder("default", ["rightarm", "rightitem"], {"startColor": (1, 1, 1, 1), "endColor": (1, 1, 1, 0), "length": 5, "width": 3, "offset": 0, "texture": "open_knife_light", "bloom": False})
        else:
            self.removeAllBinder()

@Listen("AddPlayerCreatedClientEvent")
def AddPlayerCreatedClientEvent(args={}):
    # 截至当前版本QuModLibs暂未提供组件快捷玩家注册装饰器 需自行监听
    TestKLRenderer().bind(args["playerId"])
```
为避免多MOD冲突问题 若需大量魔改 请重新命名模型/材质/着色器相关名称，避免多MOD冲突。