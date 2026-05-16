import pygame
import sys
from typing import List, Dict, Any
from .graphical.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BLACK,
    LEFT_COLUMN_WIDTH, L_HERO_PANEL_HEIGHT, L_MAOU_PANEL_HEIGHT, R1_PANEL_HEIGHT, R2_PANEL_HEIGHT
)
from .graphical.components import StatusPanel, MonsterListPanel, LogConsolePanel
from ..models import Hero, Maou, Monster, Field

class PygameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("魔王 VS 勇者 - Cyber Simulation")
        self.clock = pygame.time.Clock()
        
        # パネルの初期化
        self.hero_panel = StatusPanel((0, 0, LEFT_COLUMN_WIDTH, L_HERO_PANEL_HEIGHT), "勇者ステータス", role="HERO")
        self.maou_panel = StatusPanel((0, L_HERO_PANEL_HEIGHT, LEFT_COLUMN_WIDTH, L_MAOU_PANEL_HEIGHT), "魔王（あなた）", role="MAOU")
        self.monster_panel = MonsterListPanel((LEFT_COLUMN_WIDTH, 0, SCREEN_WIDTH - LEFT_COLUMN_WIDTH, R1_PANEL_HEIGHT))
        self.log_panel = LogConsolePanel((LEFT_COLUMN_WIDTH, R1_PANEL_HEIGHT, SCREEN_WIDTH - LEFT_COLUMN_WIDTH, R2_PANEL_HEIGHT))
        
        self.current_monsters = []
        self.selected_indices = []
        self.cursor_index = 0
        self.generation = 1
        
        # エフェクト用Surface
        self.scanline_surface = self._create_scanline_surface()
        self.vignette_surface = self._create_vignette_surface()

    def _create_scanline_surface(self):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 2):
            pygame.draw.line(surf, (0, 0, 0, 50), (0, y), (SCREEN_WIDTH, y), 1)
        return surf

    def _create_vignette_surface(self):
        # 簡易的な四隅減光
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        return surf 

    def show_title_screen(self):
        """タイトル画面を表示し、ユーザー入力を待つ"""
        import os
        from .graphical.renderer import TextRenderer
        from .graphical.constants import COLOR_CYBER_GREEN, COLOR_BLACK, COLOR_AMBER, COLOR_WHITE

        # 画像の読み込み
        image_path = os.path.join("asset", "graphics", "title_full_size2.PNG")
        try:
            bg_image = pygame.image.load(image_path)
            bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Title image not found at {image_path}. Using plain background. ({e})")
            bg_image = None

        title_renderer = TextRenderer(64) # 大きめのフォント
        sub_renderer = TextRenderer(32)   # 案内用
        blink_timer = 0
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return # ゲーム開始
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return # ゲーム開始

            # 描画
            self.screen.fill(COLOR_BLACK)
            if bg_image:
                self.screen.blit(bg_image, (0, 0))
            
            # 枠線
            pygame.draw.rect(self.screen, COLOR_CYBER_GREEN, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 5)

            # タイトルロゴ (GAME START)
            text_main = "GAME START"
            x_main = (SCREEN_WIDTH - title_renderer.get_width(text_main)) // 2
            y_main = SCREEN_HEIGHT - 180
            title_renderer.draw_text(self.screen, text_main, x_main, y_main, COLOR_CYBER_GREEN, glow=True)

            # 操作ガイド (タグ形式で固定表示)
            text_sub = "[ PRESS ENTER KEY TO START ]"
            text_w = sub_renderer.get_width(text_sub)
            x_sub = (SCREEN_WIDTH - text_w) // 2
            y_sub = y_main + 80
            
            # ハイコントラストな背景バー
            bg_rect = pygame.Rect(x_sub - 20, y_sub - 5, text_w + 40, 45)
            pygame.draw.rect(self.screen, COLOR_AMBER, bg_rect)
            pygame.draw.rect(self.screen, COLOR_WHITE, bg_rect, 2) # 外枠
            
            # 黒文字で描画
            from .graphical.constants import COLOR_DARK_AMBER_TEXT
            sub_renderer.draw_text(self.screen, text_sub, x_sub, y_sub + 2, COLOR_DARK_AMBER_TEXT)

            pygame.display.flip()
            self.clock.tick(60)

    def show_inheritance_loading(self, next_generation: int):
        """継承演出（ロード画面）"""
        from .graphical.renderer import TextRenderer
        from .graphical.constants import COLOR_CYBER_GREEN, COLOR_BLACK
        
        renderer = TextRenderer(48)
        text = f"第 {next_generation} 世代 継承中..."
        text_w = renderer.get_width(text)
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        # フェードアウト（黒で塗りつぶし）
        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.fill(COLOR_BLACK)
        
        # 3秒間演出
        start_ticks = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_ticks < 3000:
            pygame.event.pump() # 応答なし対策
            
            self.screen.fill(COLOR_BLACK)
            
            # テキスト表示
            renderer.draw_text(self.screen, text, cx - text_w // 2, cy - 50, COLOR_CYBER_GREEN)
            
            # プログレスバー風アニメーション
            elapsed = pygame.time.get_ticks() - start_ticks
            progress = min(1.0, elapsed / 2500)
            bar_width = 400
            bar_h = 4
            bar_x = cx - bar_width // 2
            bar_y = cy + 50
            
            pygame.draw.rect(self.screen, (0, 50, 0), (bar_x, bar_y, bar_width, bar_h))
            pygame.draw.rect(self.screen, COLOR_CYBER_GREEN, (bar_x, bar_y, int(bar_width * progress), bar_h))
            
            pygame.display.flip()
            self.clock.tick(60)

    def show_game_over_sequence(self):
        """魔王敗北時のシステム崩壊・浄化演出"""
        from .graphical.renderer import TextRenderer
        from .graphical.constants import COLOR_RED, COLOR_YELLOW, COLOR_CYAN, COLOR_WHITE, COLOR_BLACK
        import random
        import time

        # Step 1: Crash (崩壊) - 赤エラーログ
        crash_logs = [
            "[CRITICAL] UNAUTHORIZED LIGHT DETECTED!",
            "[ERROR] DARKNESS_SHIELD BROKEN.",
            "[FATAL] MAOU_LIFE_SIGNAL LOST.",
            "SYSTEM FAILURE...",
            "CORE DUMPING...",
            "ABORTING PROTOCOL 666..."
        ]
        
        renderer_log = TextRenderer(24)
        for _ in range(20): # 高速点滅ループ
            pygame.event.pump()
            self.screen.fill(COLOR_BLACK)
            
            # ランダムな位置に赤ログ
            for log in crash_logs:
                x = random.randint(50, SCREEN_WIDTH - 300)
                y = random.randint(50, SCREEN_HEIGHT - 50)
                renderer_log.draw_text(self.screen, log, x, y, COLOR_RED, glow=True)
            
            # 赤オーバーレイ点滅
            if random.random() > 0.5:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 50))
                self.screen.blit(overlay, (0, 0))

            pygame.display.flip()
            self.clock.tick(15) # 高速だが少し見せる

        # Step 2: Glitch (侵食) - 文字化けとノイズ
        glitch_chars = "SysT3m... Fa1L...uRe... H3R0_PR0T0C0L... 1niTiA7iNg... #@!$%^&*"
        renderer_glitch = TextRenderer(64)
        
        start_ticks = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_ticks < 2000:
            pygame.event.pump()
            self.screen.fill(COLOR_BLACK)
            
            # ノイズ矩形
            for _ in range(10):
                w = random.randint(10, 200)
                h = random.randint(2, 20)
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.rect(self.screen, COLOR_YELLOW, (x, y, w, h))

            # 文字化けテキスト
            glitch_text = "".join(random.choices(glitch_chars, k=15))
            cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            x = cx - renderer_glitch.get_width(glitch_text) // 2 + random.randint(-5, 5)
            y = cy + random.randint(-5, 5)
            renderer_glitch.draw_text(self.screen, glitch_text, x, y, COLOR_YELLOW, glow=True)
            
            pygame.display.flip()
            self.clock.tick(10)

        # Step 3: Purification (浄化) - ホワイトアウトとメッセージ
        # ホワイトアウト
        for alpha in range(0, 256, 5):
            pygame.event.pump()
            white_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            white_surf.fill(COLOR_WHITE)
            white_surf.set_alpha(alpha)
            self.screen.blit(white_surf, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)
        
        self.screen.fill(COLOR_WHITE) # 完全に白に
        pygame.display.flip()
        time.sleep(1)

        # 浄化メッセージ
        messages = [
            ">>> 悪性プログラム「MAOU」の削除に成功しました。",
            ">>> 世界の浄化プロセス... 完了。",
            ">>> 平和な世界へようこそ。"
        ]
        
        renderer_msg = TextRenderer(32)
        y_pos = SCREEN_HEIGHT // 3
        
        for msg in messages:
            # 1文字ずつ表示 (タイプライター)
            current_text = ""
            for char in msg:
                pygame.event.pump()
                current_text += char
                self.screen.fill(COLOR_WHITE) # 背景白
                
                # 既に表示済みの行を描画
                for i, past_msg in enumerate(messages):
                    if messages[i] == msg: break
                    msg_w = renderer_msg.get_width(past_msg)
                    renderer_msg.draw_text(self.screen, past_msg, (SCREEN_WIDTH - msg_w)//2, y_pos + i*60, COLOR_CYAN)
                
                # 現在の行を描画
                curr_w = renderer_msg.get_width(current_text)
                renderer_msg.draw_text(self.screen, current_text, (SCREEN_WIDTH - curr_w)//2, y_pos + messages.index(msg)*60, COLOR_CYAN)
                
                pygame.display.flip()
                time.sleep(0.05)
            time.sleep(0.8)

        # Step 4: 終了待機 (Wait for Exit)
        renderer_title = TextRenderer(80)
        renderer_sub = TextRenderer(32)
        
        title_text = "GAME OVER"
        sub_text = "[ PRESS ENTER TO SHUTDOWN ]"
        
        title_w = renderer_title.get_width(title_text)
        sub_w = renderer_sub.get_width(sub_text)
        
        blink_timer = 0
        while True:
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(COLOR_WHITE)
            
            # メッセージ再描画（薄く残す）
            for i, msg in enumerate(messages):
                msg_w = renderer_msg.get_width(msg)
                renderer_msg.draw_text(self.screen, msg, (SCREEN_WIDTH - msg_w)//2, y_pos + i*60, (200, 255, 255)) # 薄いシアン

            # GAME OVER
            renderer_title.draw_text(self.screen, title_text, (SCREEN_WIDTH - title_w)//2, SCREEN_HEIGHT - 250, COLOR_CYAN)
            
            # 点滅テキスト
            blink_timer += 1
            if (blink_timer // 30) % 2 == 0:
                renderer_sub.draw_text(self.screen, sub_text, (SCREEN_WIDTH - sub_w)//2, SCREEN_HEIGHT - 100, COLOR_CYAN)
            
            pygame.display.flip()
            self.clock.tick(60)

    def _refresh(self, flip=True):
        pygame.event.pump() # 常に応答シグナルを送る
        self.screen.fill(COLOR_BLACK)
        self.log_panel.update() # タイピング演出の更新
        self.hero_panel.draw(self.screen)
        self.maou_panel.draw(self.screen)
        self.monster_panel.draw(self.screen)
        self.log_panel.draw(self.screen)
        
        # エフェクト適用
        self.screen.blit(self.scanline_surface, (0, 0))
        
        if flip:
            pygame.display.flip()
            self.clock.tick(60) # 速度調整のため60FPSに

    def _handle_scroll_event(self, event):
        """マウスホイールイベントを一元管理"""
        mx, my = pygame.mouse.get_pos()
        if self.hero_panel.rect.collidepoint(mx, my):
            self.hero_panel.handle_scroll(event.y)
        else:
            # デフォルトはログパネル（またはカーソルが上にあれば）
            # ここではシンプルにhero以外はlogとするが、monster_panelなどがスクロール対応したら分岐増やす
            self.log_panel.handle_scroll(event.y)

    def display_status(self, hero: Hero, maou: Maou, field: Field, monsters: List[Monster], generation: int = 1):
        self.generation = generation
        self.hero_panel.update_data(hero, generation)
        self.maou_panel.update_data(maou)
        self.current_monsters = monsters
        
        field_info = f"{field.name} [属性:{field.attribute}]"
        self.monster_panel.update_data(monsters, [], 0, field_info)
        
        self.log_panel.add_log(f"Stage: {field.name} [{field.attribute}]")
        self._refresh()

    def prompt_monster_selection(self) -> List[int]:
        self.selected_indices = []
        self.cursor_index = 0
        self.log_panel.add_log("--- 迎撃部隊編成 ---")
        self.log_panel.add_log("魔王様、迎撃に向かわせるモンスターを2体選んでください。")

        while len(self.selected_indices) < 2:
            self.monster_panel.update_data(self.current_monsters, self.selected_indices, self.cursor_index)
            self._refresh()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                     self._handle_scroll_event(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.cursor_index = (self.cursor_index - 1) % len(self.current_monsters)
                    elif event.key == pygame.K_DOWN:
                        self.cursor_index = (self.cursor_index + 1) % len(self.current_monsters)
                    elif event.key == pygame.K_SPACE:
                        if self.cursor_index in self.selected_indices:
                            self.selected_indices.remove(self.cursor_index)
                        elif len(self.selected_indices) < 2:
                            self.selected_indices.append(self.cursor_index)
                    elif event.key == pygame.K_RETURN:
                        if len(self.selected_indices) == 2:
                            return self.selected_indices
                        else:
                            self.log_panel.add_log(f"※あと{2 - len(self.selected_indices)}体選択してください")
        return self.selected_indices

    def prompt_command(self, monster_name: str) -> str:
        input_text = ""
        composition_text = "" # 変換中の文字列
        
        # IME入力開始
        pygame.key.start_text_input()
        
        # プロンプト更新
        self.log_panel.add_log(f"--- 戦術指揮 ---")
        self.log_panel.add_log(f"[入力待機中] {monster_name}への指示を入力してください >")
        self.log_panel.set_input("")
        
        while True:
            self._refresh()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    self._handle_scroll_event(event)
                
                if event.type == pygame.TEXTINPUT:
                    input_text += event.text
                    composition_text = "" # 確定したのでクリア
                
                if event.type == pygame.TEXTEDITING:
                    composition_text = event.text
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # 変換中(composition_textあり)の場合は何もしない（IMEが処理する）
                        # ただしPygameの仕様によってはEnterも飛んでくるので注意が必要
                        # composition_textが空のときのみ確定とみなすのが安全
                        if not composition_text:
                            if input_text:
                                self.log_panel.add_log(f"命令: {input_text}")
                                self.log_panel.set_input("")
                                pygame.key.stop_text_input()
                                return input_text
                    elif event.key == pygame.K_BACKSPACE:
                        if not composition_text:
                            input_text = input_text[:-1]
                        
                # カーソル表現: 確定済み + [変換中] + |
                display_text = input_text + composition_text
                self.log_panel.set_input(display_text + "|")


    def display_reaction(self, monster_name: str, reaction: str):
        self.log_panel.add_log(f"{monster_name}: {reaction}")
        self._wait_for_click()

    def display_message(self, message: str):
        self.log_panel.add_log(message)
        self._wait_for_click()

    def display_story(self, title: str, story: str, result: str):
        self.log_panel.add_log(f"--- {title} ---")
        self.log_panel.add_log(story)
        self.log_panel.add_log(f"結果: {result}")
        self._wait_for_click()
    
    def display_will(self, will: str, title: str = "勇者の最期"):
         self.log_panel.add_log(f"--- {title} ---")
         self.log_panel.add_log(will)
         self._wait_for_click()

    def display_llm_debug(self, prompt_data: Dict[str, str], response_data: Dict[str, Any]):
        pass

    def show_loading(self, task_func, message="処理中..."):
        """
        別スレッドでtask_funcを実行し、完了するまでローディング画面を表示し続ける。
        task_funcは引数なしの関数として渡すこと。
        戻り値としてtask_funcの実行結果を返す。
        """
        import threading
        import math
        from .graphical.renderer import TextRenderer
        from .graphical.constants import COLOR_CYBER_GREEN, COLOR_BLACK, SCREEN_WIDTH, SCREEN_HEIGHT

        result_container = {}
        exception_container = {}

        def runner():
            try:
                result_container["data"] = task_func()
            except Exception as e:
                exception_container["error"] = e

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

        renderer = TextRenderer(24)
        angle = 0
        
        # 待機ループ
        while thread.is_alive():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # 背景（現在の画面を維持しつつ少し暗くするなどの演出も可能だが、今回は単純にオーバーレイ）
            # self._refresh() # これを呼ぶと裏で動いている入力待ちなどと競合する可能性があるが、静止画としては有効
            # ここではシンプルに黒背景＋インジケーターにするか、直前の画面の上に描画するか。
            # 直前の画面を維持するには、_refreshを呼ばずに上書き描画する。
            
            # 半透明の黒オーバーレイ
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))

            # テキスト
            text_width = renderer.get_width(message)
            cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            renderer.draw_text(self.screen, message, cx - text_width // 2, cy - 40, COLOR_CYBER_GREEN)

            # スピナー (円周上を回る円)
            spinner_radius = 20
            num_dots = 8
            for i in range(num_dots):
                theta = angle + (i * (360 / num_dots))
                rad = math.radians(theta)
                dot_x = cx + math.cos(rad) * spinner_radius
                dot_y = cy + 20 + math.sin(rad) * spinner_radius
                
                # 濃淡をつける
                alpha = int(255 * (i / num_dots))
                dot_color = (0, 255, 0, alpha) # Pygameのdraw.circleはalpha非対応の場合があるが、Surfaceを使えば可
                pygame.draw.circle(self.screen, (0, 255, 0), (int(dot_x), int(dot_y)), 3)

            angle += 5
            pygame.display.flip()
            self.clock.tick(60)

        if "error" in exception_container:
            raise exception_container["error"]
        return result_container.get("data")

    def _wait_for_click(self):
        waiting = True
        from .graphical.renderer import TextRenderer
        from .graphical.constants import COLOR_YELLOW, COLOR_BRIGHT_GREEN
        indicator_renderer = TextRenderer(24) 

        while waiting:
            # 応答なし対策
            pygame.event.pump()
            
            # 画面を描画（フリップしない）
            self._refresh(flip=False)
            is_animating = self.log_panel.is_animating()
            
            # 待機インジケーター描画 (アニメーション完了後は常時表示)
            if not is_animating:
                text = "Next [Enter] >>"
                text_w = indicator_renderer.get_width(text)
                
                # ログパネルの右下隅に配置
                x = self.log_panel.rect.right - text_w - 20
                y = self.log_panel.rect.bottom - 30
                
                indicator_renderer.draw_text(self.screen, text, x, y, COLOR_YELLOW, glow=True)
            
            # 最後にまとめてフリップ
            pygame.display.flip()
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    self._handle_scroll_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                    if is_animating:
                        # 全てのペンディング行を一気に表示 (フリーズ対策)
                        self.log_panel.skip_all_typing()
                    else:
                        waiting = False