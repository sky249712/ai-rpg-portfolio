
# 画面・レイアウト定数
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# パネル比率
LEFT_COLUMN_WIDTH = int(SCREEN_WIDTH * 0.3)  # 384
RIGHT_COLUMN_WIDTH = SCREEN_WIDTH - LEFT_COLUMN_WIDTH # 896

L_HERO_PANEL_HEIGHT = int(SCREEN_HEIGHT * 0.65) # 勇者エリア 65%
L_MAOU_PANEL_HEIGHT = SCREEN_HEIGHT - L_HERO_PANEL_HEIGHT # 魔王エリア 35%

R1_PANEL_HEIGHT = int(SCREEN_HEIGHT * 0.4) # 288
R2_PANEL_HEIGHT = SCREEN_HEIGHT - R1_PANEL_HEIGHT # 432

# カラーパレット
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_BG_BLACK = (0, 5, 0) # わずかに緑がかった黒
COLOR_CYBER_GREEN = (0, 255, 0)
COLOR_YELLOW = (255, 255, 0)

# Role Colors
COLOR_AMBER = (255, 176, 0)       # TARGET / WARNING
COLOR_AMBER_TEXT = (255, 190, 0)  # Brighter for text
COLOR_BRIGHT_GREEN = (74, 246, 38) # Terminal Green
COLOR_DARK_GREEN = (0, 136, 0)    # SYSTEM Background/Base
COLOR_DARK_GREEN_TEXT = (0, 51, 0) # For header text on green bg
COLOR_DARK_AMBER_TEXT = (51, 0, 0) # For header text on amber bg
COLOR_PALE_GREEN = (150, 220, 150)# LOG

# フォント設定 (Windows/OS標準フォントを優先)
# 日本語が表示できるフォントを最優先にする必要がある
FONT_CANDIDATES = [
    "msgothic",       # MS Gothic (Windows標準のドット風ゴシック)
    "msmincho",       # MS Mincho
    "meiryo",
    "bizudgothic", 
    "yugothic", 
    "vt323",          # 欧文のみ (インストールされている場合)
    "dotgothic16",    # 日本語対応 (インストールされている場合)
    "consolas", 
    "couriernew",
    "arialunicode"
]
DEFAULT_FONT_SIZE = 18
TITLE_FONT_SIZE = 24

# UI設定
PANEL_PADDING = 15
LINE_SPACING = 5
FRAME_WIDTH = 2
