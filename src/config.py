#窗口大小（单位是像素）
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

#帧率
FPS = 60

#地图图块大小（单位是像素）
TILE_SIZE = 32

# 大地图显示缩放倍数。只影响屏幕显示，不改变 map.json、碰撞 mask 或建筑坐标。
MAP_DISPLAY_SCALE = 1.3

#地图规模（由多少行列图块组成）
MAP_COLS = 52
MAP_ROWS = 72

#临时颜色定义
COLOR_BUILDING = (128, 128, 128) #建筑或墙壁，灰色
COLOR_PATH = (200, 200, 200) #道路，浅灰色
COLOR_ROAD = (235, 225, 180) #命名路段，浅色
COLOR_PLAYER = (0, 0, 255) #玩家角色，蓝色

#角色移动速度（每帧每像素）
PLAYER_SPEED = 2

# 场景名称统一标识
class Scene:
    START = "start" #开始游戏页面
    OVERWORLD = "overworld" #大地图页面
    BUILDING = "building" #建筑物页面

#字体路径
font1_path = "assets/fonts/NotoSerifSC-VariableFont_wght.ttf" #思源宋体，适合标题
font2_path ="assets/fonts/NotoSansSC-VariableFont_wght.ttf" #思源黑体，适合对话和UI
