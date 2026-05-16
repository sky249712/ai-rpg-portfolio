import pygame
import time
from .constants import (
    COLOR_CYBER_GREEN, COLOR_YELLOW, COLOR_BLACK, COLOR_BG_BLACK, COLOR_WHITE,
    COLOR_AMBER, COLOR_BRIGHT_GREEN, COLOR_DARK_GREEN, COLOR_PALE_GREEN,
    COLOR_DARK_GREEN_TEXT, COLOR_DARK_AMBER_TEXT,
    PANEL_PADDING, FRAME_WIDTH, DEFAULT_FONT_SIZE, TITLE_FONT_SIZE
)
from .renderer import TextRenderer

class BasePanel:
    def __init__(self, rect, title="", theme_color=COLOR_CYBER_GREEN):
        self.rect = pygame.Rect(rect)
        self.title = title
        self.theme_color = theme_color
        self.renderer = TextRenderer(DEFAULT_FONT_SIZE)
        self.title_renderer = TextRenderer(TITLE_FONT_SIZE)
        
        # 背景用Surface (透過)
        self.bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.bg_surface.fill((*COLOR_BG_BLACK, 245))

    def draw_frame(self, surface):
        # 背景塗りつぶし
        surface.blit(self.bg_surface, (self.rect.x, self.rect.y))
        
        # 枠線のグロー効果 (box-shadow風)
        glow_color = (*self.theme_color, 100)
        for i in range(1, 4):
            glow_rect = self.rect.inflate(i*2, i*2)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.theme_color, 40 // i), (0, 0, glow_rect.width, glow_rect.height), 1, border_radius=4)
            surface.blit(glow_surf, (glow_rect.x, glow_rect.y))

        # 外枠
        pygame.draw.rect(surface, self.theme_color, self.rect, 2, border_radius=4)
        
        # ウィンドウタイトルバー (透過ベタ塗り)
        if self.title:
            title_bar_height = 28
            title_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, title_bar_height)
            
            # 透過ヘッダー
            header_alpha = 230 # より不透明に
            header_surf = pygame.Surface((title_rect.width, title_rect.height), pygame.SRCALPHA)
            header_surf.fill((*self.theme_color, header_alpha))
            surface.blit(header_surf, (title_rect.x, title_rect.y))
            
            # タイトル文字色 (白で統一して視認性向上)
            self.title_renderer.draw_text(
                surface, self.title, 
                self.rect.x + 10, self.rect.y + 4, 
                COLOR_WHITE,
                glow=True # グローも追加
            )

class StatusPanel(BasePanel):
    def __init__(self, rect, title, role="SYSTEM"):
        if role == "HERO":
            color = COLOR_AMBER
            title = "勇者ステータス" 
        elif role == "MAOU":
            color = COLOR_DARK_GREEN
            title = "魔王（あなた）"
        else:
            color = COLOR_DARK_GREEN
            
        super().__init__(rect, title, color)
        self.character = None
        self.generation = 1
        self.role = role
        self.scroll_offset = 0
        
        self.gen_renderer = TextRenderer(28) 
        self.stats_renderer = TextRenderer(20) 
        self.desc_renderer = TextRenderer(20)
        # 内部文字色を役割に合わせる
        self.text_color = COLOR_AMBER if role == "HERO" else COLOR_BRIGHT_GREEN

    def update_data(self, character, generation=1):
        self.character = character
        self.generation = generation
        # キャラクターが変わったらスクロールリセット
        self.scroll_offset = 0

    def handle_scroll(self, y_amount):
        """マウスホイールでのスクロール処理"""
        self.scroll_offset += y_amount * 20 # 少し速めに
        # 上限チェック (上にスクロールしすぎない)
        if self.scroll_offset > 0:
            self.scroll_offset = 0
        # 下限チェックはdraw時にコンテンツ高さを計算しないと難しいが、
        # 簡易的に制限なし、または適当な値で止める。
        # ここでは無制限にするが、drawでコンテンツがなくなったら止めるロジックを入れるのが理想

    def draw(self, surface):
        self.draw_frame(surface)
        if not self.character:
            return

        # クリッピング領域を再定義 (タイトルバー 28px のすぐ下から開始)
        # inflateを使用せず、絶対座標で指定して確実に制御する
        clip_y = self.rect.y + 32
        clip_h = self.rect.height - 32 - 5 # 下端の枠線分を引く
        clip_rect = pygame.Rect(self.rect.x + 5, clip_y, self.rect.width - 10, clip_h)
        
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        x = self.rect.x + PANEL_PADDING
        # テキスト開始位置をクリッピング領域内に確実に配置 (余白 8px)
        y = clip_y + 8 + self.scroll_offset 

        if self.role == "HERO":
            gen_text = f"【 第 {self.generation} 世代 】"
            text_w = self.gen_renderer.get_width(gen_text)
            bg_rect = pygame.Rect(x, y, text_w + 20, 36)
            pygame.draw.rect(surface, self.theme_color, bg_rect)
            self.gen_renderer.draw_text(surface, gen_text, x + 10, y + 2, COLOR_BLACK) 
            y += 45 

        # ステータス表示
        y = self.stats_renderer.draw_text(surface, f"NAME: {self.character.name}", x, y, self.text_color, glow=True)
        y = self.stats_renderer.draw_text(surface, f"HP: {self.character.hp}", x, y, self.text_color, glow=True)
        y = self.stats_renderer.draw_text(surface, f"ATK: {self.character.attack} / DEF: {self.character.defense}", x, y, self.text_color, glow=True)
        y += 10

        self.desc_renderer.draw_text(
            surface, self.character.personality, x, y, 
            self.text_color,
            max_width=self.rect.width - (PANEL_PADDING * 2),
            glow=True
        )
        
        surface.set_clip(old_clip)

class MonsterListPanel(BasePanel):
    def __init__(self, rect):
        super().__init__(rect, "TACTICS: 迎撃部隊編成", COLOR_BRIGHT_GREEN)
        self.monsters = []
        self.selected_indices = []
        self.cursor_index = 0
        self.guide_renderer = TextRenderer(16)
        self.list_renderer = TextRenderer(18) # 情報を増やすため少し小さく
        self.header_renderer = TextRenderer(20)
        self.field_info = ""

    def update_data(self, monsters, selected_indices, cursor_index, field_info=""):
        self.monsters = monsters
        self.selected_indices = selected_indices
        self.cursor_index = cursor_index
        if field_info:
            self.field_info = field_info

    def draw(self, surface):
        self.draw_frame(surface)
        x = self.rect.x + PANEL_PADDING
        y = self.rect.y + 50 

        if self.field_info:
            self.header_renderer.draw_text(surface, f"■ TARGET AREA: {self.field_info}", x, y, COLOR_BRIGHT_GREEN, glow=True)
            y += 30
            pygame.draw.line(surface, self.theme_color, (x, y-5), (self.rect.right - PANEL_PADDING, y-5), 1)

        for i, m in enumerate(self.monsters):
            is_cursor = (i == self.cursor_index)
            is_selected = (i in self.selected_indices)
            
            if is_cursor:
                text_color = COLOR_YELLOW
            elif is_selected:
                text_color = COLOR_AMBER
            else:
                text_color = COLOR_BRIGHT_GREEN

            prefix = ">" if is_cursor else " "
            mark = "[x]" if is_selected else "[ ]"
            
            # 性格を追加。長すぎる場合はカット
            p_text = m.personality[:15] + ".." if len(m.personality) > 15 else m.personality
            text = f"{prefix} {mark} {m.name} [{m.attribute}] (HP:{m.hp} A:{m.attack} D:{m.defense}) 性格:{p_text}"
            
            y = self.list_renderer.draw_text(surface, text, x, y, text_color, glow=is_cursor)
            y += 5


        guide_y = self.rect.bottom - 25
        guide_text = "CMD: [UP/DOWN]SELECT [SPACE]TOGGLE [ENTER]EXECUTE"
        self.guide_renderer.draw_text(surface, guide_text, x, guide_y, COLOR_BRIGHT_GREEN)

class LogConsolePanel(BasePanel):
    def __init__(self, rect):
        super().__init__(rect, "LOG: 戦闘記録", COLOR_PALE_GREEN)
        self.full_logs = [] 
        self.pending_queue = [] 
        self.current_typing_line = ""
        self.target_line = ""
        self.input_text = ""
        self.timer = 0
        self.char_interval = 1 
        self.scroll_offset = 0 

    def add_log(self, text):
        if not text: return
        # エスケープされた改行文字を実際の改行に変換
        text = text.replace('\\n', '\n')
        for line in text.split('\n'):
            if line.strip():
                self.pending_queue.append(line.strip())

    def handle_scroll(self, y_amount):
        self.scroll_offset += y_amount
        if self.scroll_offset < 0:
            self.scroll_offset = 0
        max_scroll = max(0, len(self.full_logs) - 5)
        if self.scroll_offset > max_scroll:
            self.scroll_offset = max_scroll

    def update(self):
        if not self.target_line and self.pending_queue:
            self.target_line = self.pending_queue.pop(0)
            self.current_typing_line = ""
            self.timer = 0
            self.scroll_offset = 0

        if self.target_line:
            for _ in range(5):
                if len(self.current_typing_line) < len(self.target_line):
                    self.current_typing_line += self.target_line[len(self.current_typing_line)]
                else:
                    self.full_logs.append(self.current_typing_line)
                    self.target_line = ""
                    self.current_typing_line = ""
                    break
        
        if len(self.full_logs) > 200:
            self.full_logs.pop(0)

    def skip_typing(self):
        """現在タイピング中の演出をスキップして即座に表示完了させる"""
        if self.target_line:
            self.full_logs.append(self.target_line)
            self.target_line = ""
            self.current_typing_line = ""
        self.scroll_offset = 0

    def skip_all_typing(self):
        """待機中の全てのログを一気に表示完了させる"""
        self.skip_typing() # 現在の行を完了
        while self.pending_queue:
            line = self.pending_queue.pop(0)
            self.full_logs.append(line)
        self.scroll_offset = 0

    def is_animating(self):
        return bool(self.target_line or self.pending_queue)

    def set_input(self, text):
        self.input_text = text

    def draw(self, surface):
        self.draw_frame(surface)
        
        log_x = self.rect.x + PANEL_PADDING
        log_bottom = self.rect.bottom - 40
        current_y = log_bottom
        
        display_full_logs = self.full_logs[:]
        if self.scroll_offset > 0:
            end_idx = len(display_full_logs) - self.scroll_offset
            display_full_logs = display_full_logs[:end_idx]
        elif self.current_typing_line:
            display_full_logs.append(self.current_typing_line)
        
        for log in reversed(display_full_logs):
            height = self.renderer.get_height(log, self.rect.width - PANEL_PADDING*2 - 20) 
            current_y -= height
            if current_y < self.rect.y + 50:
                break
            self.renderer.draw_text(surface, log, log_x, current_y, self.theme_color, max_width=self.rect.width - PANEL_PADDING*2 - 20, glow=True)
        
        # スクロールバー
        if len(self.full_logs) > 5:
            bar_height = self.rect.height - 90
            bar_x = self.rect.right - 18
            bar_y_start = self.rect.y + 50
            pygame.draw.rect(surface, (0, 30, 0), (bar_x, bar_y_start, 10, bar_height))
            pygame.draw.rect(surface, self.theme_color, (bar_x, bar_y_start, 10, bar_height), 1)
            total_logs = len(self.full_logs) + (1 if self.current_typing_line else 0)
            knob_height = max(30, bar_height * (15 / max(1, total_logs)))
            max_scroll = max(1, total_logs - 5)
            scroll_ratio = self.scroll_offset / max_scroll
            knob_y = (bar_y_start + bar_height - knob_height) - (scroll_ratio * (bar_height - knob_height))
            pygame.draw.rect(surface, self.theme_color, (bar_x + 1, knob_y, 8, knob_height))

        # 入力プロンプト + 点滅カーソル
        prompt_y = self.rect.bottom - 30
        pygame.draw.line(surface, self.theme_color, (self.rect.x, prompt_y - 5), (self.rect.right, prompt_y - 5), 1)
        
        cursor = "_" if (int(time.time() * 2) % 2 == 0) else ""
        self.renderer.draw_text(surface, f"> {self.input_text}{cursor}", log_x, prompt_y, COLOR_BRIGHT_GREEN, glow=True)
