# NJU_Game

南京大学鼓楼校区主题的 2D RPG 原型。游戏使用 Pygame 实现，当前重点是：在手绘校园地图上移动、根据碰撞图限制通行、靠近指定建筑触发交互，并进入建筑对话场景。

## 当前功能

- 开始界面：按空格进入大地图。
- 手绘校园大地图：使用 `assets/images/nju_handdrawn_original.jpg` 作为地图背景。
- 玩家移动：方向键控制角色在地图上移动。
- 摄像机跟随：地图会跟随玩家滚动，并限制在地图边界内。
- 地图显示缩放：`src/config.py` 中的 `MAP_DISPLAY_SCALE` 控制地图和玩家的显示倍率，当前为 `1.3`。
- 像素级碰撞：使用 `assets/images/nju_handdrawn_collision_mask.png` 控制可通行区域。
- 建筑交互：靠近 `data/map.json` 中保留的建筑或校门时，屏幕上方显示“按 E 进入 XX”。
- 建筑场景：按 E 进入建筑内部，显示建筑名称和对话内容。
- 对话推进：在建筑场景中按空格或 E 推进对话；对话结束后返回大地图。

## 地图系统

当前地图不再主要依赖旧的 0/1 图块矩阵，而是使用“背景图 + 碰撞 mask + 建筑交互区域”的方式。

### 背景图

`assets/images/nju_handdrawn_original.jpg` 是游戏中真正显示的地图图片。

### 碰撞图

`assets/images/nju_handdrawn_collision_mask.png` 是游戏实际读取的碰撞图。

- 白色或浅色区域：不可通行。
- 黑色或深色区域：可通行。
- 游戏运行时会在 `src/map.py` 中读取这张图，并根据玩家矩形采样判断是否碰撞。

### 碰撞预览图

`assets/images/nju_handdrawn_collision_debug.png` 只是调试图。它把碰撞 mask 以红色半透明方式叠在原地图上，方便人工检查通路是否合理。游戏不会读取这张图。

### 建筑标注图

`assets/images/nju_handdrawn_annotated_debug.png` 用来检查建筑编号、建筑名称、交互范围和校门区域。游戏不会直接读取这张图。

## 重要文件

### 运行入口

- `main.py`：初始化 Pygame，创建窗口，启动场景管理器。

### 核心代码

- `src/config.py`：窗口大小、帧率、玩家速度、地图显示缩放倍率、字体路径等配置。
- `src/scene_manager.py`：管理开始界面、大地图、建筑内部场景之间的切换。
- `src/start_screen.py`：开始界面。
- `src/overworld.py`：大地图场景，负责玩家移动、摄像机、建筑交互检测。
- `src/map.py`：加载 `data/map.json`、背景图和碰撞 mask，并绘制地图。
- `src/player.py`：玩家移动、碰撞检测调用、玩家绘制。
- `src/building.py`：根据玩家位置检测附近可交互建筑。
- `src/building_scene.py`：建筑内部场景，显示建筑名和对话。
- `src/dialog.py`：简单对话推进逻辑。
- `src/ui.py`：提示框和对话框绘制。

### 数据文件

- `data/map.json`：当前游戏实际读取的地图数据，包括背景图路径、碰撞 mask 路径、玩家出生点、可交互建筑列表。
- `data/annotated_handdrawn_regions.json`：生成脚本输出的建筑区域辅助数据，主要用于校对。
- `data/简化地图.xlsx`：早期用于生成占位地图的表格，目前不是主地图逻辑的核心。

### 当前建议保留的图片

- `assets/images/nju_handdrawn_original.jpg`：游戏显示的手绘地图背景，必须保留。
- `assets/images/nju_handdrawn_map.jpg`：红线/蓝线标注源图，用于从标注图重新生成碰撞 mask，建议保留。
- `assets/images/nju_handdrawn_collision_mask.png`：游戏实际碰撞图，必须保留。
- `assets/images/nju_handdrawn_collision_debug.png`：碰撞预览图，建议保留。
- `assets/images/nju_handdrawn_annotated_debug.png`：建筑交互范围预览图，建议保留。

## 地图生成脚本

### 地图自动生成脚本
```powershell
python scripts\generate_annotated_handdrawn_map.py
```

它会根据 `nju_handdrawn_map.jpg` 中的红线/蓝线重新生成：

- `data/map.json`
- `data/annotated_handdrawn_regions.json`
- `assets/images/nju_handdrawn_collision_mask.png`
- `assets/images/nju_handdrawn_collision_debug.png`
- `assets/images/nju_handdrawn_annotated_debug.png`

注意：这个命令会覆盖 `nju_handdrawn_collision_mask.png`。如果你手动改过碰撞图，不要直接运行这个命令。

### 地图手动生成脚本（推荐）

如果你已经手动修改了 `nju_handdrawn_collision_mask.png`，请运行：

```powershell
python scripts\generate_annotated_handdrawn_map.py --from-existing-mask
```

这个模式会读取当前已有的 `nju_handdrawn_collision_mask.png`，不会覆盖它，只会刷新：

- `data/map.json`
- `data/annotated_handdrawn_regions.json`
- `assets/images/nju_handdrawn_collision_debug.png`
- `assets/images/nju_handdrawn_annotated_debug.png`

## 如何调整地图

### 调整碰撞区域

推荐两种方式：

1. 修改 `assets/images/nju_handdrawn_map.jpg` 上的红色线条，然后运行：

```powershell
python scripts\generate_annotated_handdrawn_map.py
```

2. 直接修改 `assets/images/nju_handdrawn_collision_mask.png`，然后运行：

```powershell
python scripts\generate_annotated_handdrawn_map.py --from-existing-mask
```

### 调整建筑交互范围和名称

修改 `scripts/generate_annotated_handdrawn_map.py` 中的 `MANUAL_REGIONS`。

每一项格式类似：

```python
("北大楼", "building", poly([(980, 540), (1085, 545), (1090, 610), (980, 610)]))
```

- 第一个字段是建筑名称。
- 第二个字段是类型，`building` 表示建筑，`gate` 表示门或校门。
- 第三个字段是交互范围多边形坐标。

修改后建议运行：

```powershell
python scripts\generate_annotated_handdrawn_map.py --from-existing-mask
```

这样可以保留手动调整过的碰撞图，只刷新交互数据和调试图。

### 只保留部分建筑可交互

脚本中有白名单：

```python
INTERACTIVE_BUILDINGS = {
    "大礼堂",
    "北大楼",
}
```

非校门建筑只有出现在这个集合里，才会写入 `data/map.json` 并在游戏中可交互。你可以继续往里面添加建筑名。

当前逻辑会自动保留所有 `gate` 类型区域。如果以后不想让校门交互，可以在 `build_map()` 中调整白名单过滤条件。

### 调整地图显示大小

修改 `src/config.py`：

```python
MAP_DISPLAY_SCALE = 1.3
```

- 数值越大，地图显示越近。
- 数值越小，地图显示越远。
- 这个设置只影响显示，不改变 `map.json`、碰撞 mask 或建筑坐标。

## 运行游戏

```powershell
python main.py
```

操作方式：

- 空格：从开始界面进入游戏。
- 方向键：移动玩家。
- E：靠近可交互建筑或校门时进入。
- 空格或 E：在建筑内部推进对话。
- Esc：从大地图返回开始界面，或从建筑内部返回大地图。

## 开发注意事项

- 如果你手动修改了 `nju_handdrawn_collision_mask.png`，后续生成地图时优先使用 `--from-existing-mask`。
- 如果你修改的是 `nju_handdrawn_map.jpg` 的红线/蓝线，则需要运行不带参数的生成脚本。
- `nju_handdrawn_collision_debug.png` 和 `nju_handdrawn_annotated_debug.png` 都是调试图，不参与游戏逻辑。
- 当前碰撞逻辑来自碰撞 mask，建筑交互逻辑来自 `data/map.json` 的 `buildings` 列表，两者是分开的。
