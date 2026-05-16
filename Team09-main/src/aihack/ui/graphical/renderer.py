import pygame
from .constants import FONT_CANDIDATES, DEFAULT_FONT_SIZE, COLOR_CYBER_GREEN

class TextRenderer:
    def __init__(self, font_size=DEFAULT_FONT_SIZE):
        pygame.font.init()
        self.font = self._load_font(font_size)
        self.font_size = font_size

    def _load_font(self, size):
        available = pygame.font.get_fonts()
        for candidate in FONT_CANDIDATES:
            if candidate in available:
                print(f"Debug: Loaded font '{candidate}'")
                return pygame.font.SysFont(candidate, size)
        
        print("Debug: Loaded default system font (potential mojibake warning)")
        return pygame.font.SysFont(None, size)

    def draw_text(self, surface, text, x, y, color=COLOR_CYBER_GREEN, max_width=None, glow=False):
        """
        指定された座標にテキストを描画する。max_widthが指定されている場合は折り返す。
        """
        if text is None:
            text = ""
        text = str(text)

        if not max_width:
            if glow:
                # 発光演出: 複数回重ねて描画
                glow_surf = self.font.render(text, False, color)
                for dx, dy in [(1,1), (-1,-1), (1,-1), (-1,1), (0,1), (0,-1), (1,0), (-1,0)]:
                    glow_surf.set_alpha(60)
                    surface.blit(glow_surf, (x+dx, y+dy))

            img = self.font.render(text, False, color)
            surface.blit(img, (x, y))
            return y + self.font_size + 5

        words = self._split_text(text)
        line = ""
        current_y = y

        for word in words:
            test_line = line + word
            if self.font.size(test_line)[0] < max_width:
                line = test_line
            else:
                if glow:
                    g_img = self.font.render(line, False, color)
                    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                        g_img.set_alpha(80)
                        surface.blit(g_img, (x+dx, current_y+dy))
                    
                img = self.font.render(line, False, color)
                surface.blit(img, (x, current_y))
                current_y += self.font_size + 5
                line = word
        
        if line:
            if glow:
                g_img = self.font.render(line, False, color)
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    g_img.set_alpha(80)
                    surface.blit(g_img, (x+dx, current_y+dy))
                
            img = self.font.render(line, False, color)
            surface.blit(img, (x, current_y))
            current_y += self.font_size + 5
        
        return current_y

    def _split_text(self, text):
        """
        日本語文字単位、または英単語単位で分割する簡易ロジック
        """
        chars = []
        for char in text:
            chars.append(char)
        return chars

    def get_height(self, text, max_width):
        """
        折り返しを考慮した時の描画高さを計算する
        """
        if not max_width:
            return self.font_size + 5
        
        words = self._split_text(text)
        line = ""
        lines = 1
        for word in words:
            test_line = line + word
            if self.font.size(test_line)[0] < max_width:
                line = test_line
            else:
                lines += 1
                line = word
        return lines * (self.font_size + 5)

    def get_width(self, text):
        """
        テキストの描画幅（ピクセル）を取得する
        """
        if text is None:
            return 0
        return self.font.size(str(text))[0]
