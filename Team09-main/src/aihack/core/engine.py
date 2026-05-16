import os
import sys
from ..services import DataLoader, StatusService, PromptManager
from ..llm import GoogleGenAIService
from ..ui import PygameUI, ConsoleUI
from ..models import Hero, Maou, Monster, Field

class GameEngine:
    def __init__(self, data_dir: str, prompt_dir: str, ui_mode: str = "graphical"):
        self.loader = DataLoader(data_dir)
        self.prompt_manager = PromptManager(prompt_dir)
        self.llm_service = GoogleGenAIService()
        
        if ui_mode == "console":
            self.ui = ConsoleUI()
        else:
            self.ui = PygameUI()
            
        self.hero = None
        self.maou = None
        self.field = None
        self.monsters = []
        self.selected_monsters = []
        self.previous_hero_will = ""
        self.generation = 1
        
        # ステータスポイント管理
        self.hero_points = 10
        self.maou_points = 30
        self.monster_points = 10

    def setup_automated(self):
        """
        LLM連携を使用して初期状態を生成します。
        """
        # 世代更新をUIに反映（前世代のステータスのまま、世代表記だけ更新）
        if self.hero and self.maou:
             self.ui.display_status(self.hero, self.maou, self.field, self.monsters, self.generation)

        self.ui.display_message(f"\n========== 第{self.generation}世代 開始 ==========")
        self.ui.display_message("--- 初期設定の生成中 (LLM) ---")
        
        # 1. 魔王の生成
        maou_prompts = self.prompt_manager.load_and_format(
            "maou", 
            user_input=f"第{self.generation}世代",
            total_points=int(self.maou_points)
        )
        maou_data = self.ui.show_loading(
            lambda: self.llm_service.call_llm_with_retry(maou_prompts),
            message="魔王軍の戦力を構築中..."
        ) if isinstance(self.ui, PygameUI) else self.llm_service.call_llm_with_retry(maou_prompts)
        
        self.ui.display_llm_debug(maou_prompts, maou_data)
        self.maou = Maou(
            name="魔王",
            attribute=maou_data["Attribute"],
            hp=maou_data["HP"],
            attack=maou_data["Attack"],
            defense=maou_data["Defense"],
            personality=maou_data["Personality"]
        )

        # 2. 勇者の生成
        hero_prompts = self.prompt_manager.load_and_format(
            "yuusya",
            generation=self.generation,
            total_points=int(self.hero_points),
            inheritance_info="なし",
            previous_hero_will=self.previous_hero_will
        )
        hero_data = self.ui.show_loading(
             lambda: self.llm_service.call_llm_with_retry(hero_prompts),
             message="新たな勇者が誕生しようとしています..."
        ) if isinstance(self.ui, PygameUI) else self.llm_service.call_llm_with_retry(hero_prompts)
        
        self.ui.display_llm_debug(hero_prompts, hero_data)
        self.hero = Hero(
            name=hero_data.get("Name", "名無しの勇者"),
            attribute=hero_data["Attribute"],
            hp=hero_data["HP"],
            attack=hero_data["Attack"],
            defense=hero_data["Defense"],
            personality=hero_data["Personality"]
        )

        # 3. フィールドとモンスター
        self.field = self.loader.load_field()
        
        # モンスターリストをリセット
        self.monsters = []
        
        monster_prompts = self.prompt_manager.load_and_format(
            "monster",
            generation=self.generation,
            count=5,
            total_points=int(self.monster_points)
        )
        monster_data = self.ui.show_loading(
            lambda: self.llm_service.call_llm_with_retry(monster_prompts),
            message="フィールドモンスターを召喚中..."
        ) if isinstance(self.ui, PygameUI) else self.llm_service.call_llm_with_retry(monster_prompts)
        
        self.ui.display_llm_debug(monster_prompts, monster_data)
        self.monsters = []
        for m in monster_data["monsters"]:
            self.monsters.append(Monster(
                name=m["name"],
                attribute=m["attribute"],
                hp=m["stats"]["HP"],
                attack=m["stats"]["Attack"],
                defense=m["stats"]["Defense"],
                personality=m["personality"]
            ))

        # 属性ボーナスの適用
        StatusService.apply_field_bonus(self.hero, self.field)
        StatusService.apply_field_bonus(self.maou, self.field)
        for m in self.monsters:
            StatusService.apply_field_bonus(m, self.field)

    def run(self):
        try:
            # タイトル画面の表示 (グラフィカルモードのみ)
            if hasattr(self.ui, 'show_title_screen'):
                self.ui.show_title_screen()

            while True:
                try:
                    self.setup_automated()
                except Exception as e:
                    self.ui.display_message(f"セットアップ中に致命的なエラーが発生しました: {e}")
                    break

                self.ui.display_status(self.hero, self.maou, self.field, self.monsters, self.generation)
                
                # モンスター選択
                selected_indices = self.ui.prompt_monster_selection()
                valid_indices = [i for i in selected_indices if 0 <= i < len(self.monsters)]
                if len(valid_indices) < 2:
                     self.selected_monsters = [self.monsters[0], self.monsters[1]]
                else:
                     self.selected_monsters = [self.monsters[i] for i in valid_indices]

                # 命令と反応 (LLM)
                for m in self.selected_monsters:
                    command = self.ui.prompt_command(m.name)
                    m.command = command
                    personality_prompts = self.prompt_manager.load_and_format(
                        "personality",
                        monster_name=m.name,
                        monster_personality=m.personality,
                        maou_command=command
                    )
                    reaction_data = self.ui.show_loading(
                        lambda: self.llm_service.call_llm_with_retry(personality_prompts),
                        message=f"{m.name} の反応を伺っています..."
                    ) if isinstance(self.ui, PygameUI) else self.llm_service.call_llm_with_retry(personality_prompts)
                    
                    self.ui.display_llm_debug(personality_prompts, reaction_data)
                    # Thought対応: Personalityの上書きではなくthoughtに格納
                    m.thought = reaction_data.get("thought", "")
                    self.ui.display_reaction(m.name, m.thought)

                    # motivationによるステータス変化
                    motivation = reaction_data.get("motivation", 1.0)
                    m.motivation = motivation
                    if motivation != 1.0:
                        old_stats = f"HP:{m.hp}, ATK:{m.attack}, DEF:{m.defense}"
                        m.hp = int(m.hp * motivation)
                        m.attack = int(m.attack * motivation)
                        m.defense = int(m.defense * motivation)
                        new_stats = f"HP:{m.hp}, ATK:{m.attack}, DEF:{m.defense}"
                        self.ui.display_message(f"  -> モチベーション変動 ({motivation}): {old_stats} -> {new_stats}")

                # 戦闘1: 勇者 vs モンスター（LLM）
                self.ui.display_message("\n--- 勇者が現れました。迎撃を開始します... ---")
                battle1_prompts = self.prompt_manager.load_and_format(
                    "monster_story",
                    hero_hp=self.hero.hp,
                    hero_attack=self.hero.attack,
                    hero_defense=self.hero.defense,
                    hero_personality=self.hero.personality,
                    hero_attribute=self.hero.attribute,
                    monster1_name=self.selected_monsters[0].name,
                    monster1_hp=self.selected_monsters[0].hp,
                    monster1_attack=self.selected_monsters[0].attack,
                    monster1_defense=self.selected_monsters[0].defense,
                    monster1_personality=self.selected_monsters[0].personality,
                    monster1_attribute=self.selected_monsters[0].attribute,
                    monster1_motivation=self.selected_monsters[0].motivation,
                    monster1_command=self.selected_monsters[0].command,
                    monster1_thought=self.selected_monsters[0].thought,
                    monster2_name=self.selected_monsters[1].name,
                    monster2_hp=self.selected_monsters[1].hp,
                    monster2_attack=self.selected_monsters[1].attack,
                    monster2_defense=self.selected_monsters[1].defense,
                    monster2_personality=self.selected_monsters[1].personality,
                    monster2_attribute=self.selected_monsters[1].attribute,
                    monster2_motivation=self.selected_monsters[1].motivation,
                    monster2_command=self.selected_monsters[1].command,
                    monster2_thought=self.selected_monsters[1].thought,
                    hero_action="戦う"
                )
                battle1_data = self.ui.show_loading(
                    lambda: self.llm_service.call_llm_with_retry(battle1_prompts),
                    message="戦闘のシミュレーションを実行中..."
                ) if isinstance(self.ui, PygameUI) else self.llm_service.call_llm_with_retry(battle1_prompts)
                
                self.ui.display_llm_debug(battle1_prompts, battle1_data)
                
                is_hero_victory_monster = "勝利" in battle1_data["Victory"]
                self.ui.display_story("戦闘描写", battle1_data["Story"], battle1_data["Victory"])

                # HPの更新 (次戦へ持ち越し)
                remaining_hp = battle1_data.get("RemainingHP")
                if remaining_hp is not None:
                    self.hero.hp = int(remaining_hp)
                else:
                     # fallback if LLM misses the key
                     if is_hero_victory_monster:
                          self.hero.hp = max(1, int(self.hero.hp * 0.5)) # 仮の減少
                     else:
                          self.hero.hp = 0

                # モンスター戦の結果メッセージ表示
                if is_hero_victory_monster:
                    self.ui.display_will(battle1_data.get("Will", ""), title="勇者の勝利台詞")
                    self.ui.display_message(f"勇者の残りHP: {self.hero.hp}")
                else:
                    self.ui.display_will(battle1_data.get("Will", ""), title="勇者の最期")
                    self.previous_hero_will = battle1_data.get("Will", "")
                    self._proceed_to_next_generation()
                    continue

                # 戦闘2: 勇者 vs 魔王（LLM）
                self.ui.display_message("\n--- 勇者が魔王城に到達しました！ 最終決戦を開始します... ---")
                battle2_prompts = self.prompt_manager.load_and_format(
                    "final_story",
                    hero_hp=self.hero.hp,
                    hero_attack=self.hero.attack,
                    hero_defense=self.hero.defense,
                    hero_personality=self.hero.personality,
                    hero_attribute=self.hero.attribute,
                    maou_hp=self.maou.hp,
                    maou_attack=self.maou.attack,
                    maou_defense=self.maou.defense,
                    maou_personality=self.maou.personality,
                    maou_attribute=self.maou.attribute,
                    hero_action="戦う"
                )
                battle2_data = self.ui.show_loading(
                    lambda: self.llm_service.call_llm_with_retry(battle2_prompts),
                    message="魔王決戦の行方を演算中..."
                ) if isinstance(self.ui, PygameUI) else self.llm_service.call_llm_with_retry(battle2_prompts)
                
                self.ui.display_llm_debug(battle2_prompts, battle2_data)
                self.ui.display_story("戦闘描写", battle2_data["Story"], battle2_data["Victory"])
                
                is_hero_victory_maou = "勝利" in battle2_data["Victory"]
                
                if is_hero_victory_maou:
                     self.ui.display_will(battle2_data.get("Will", ""), title="勇者の勝利台詞")
                     if isinstance(self.ui, PygameUI):
                         self.ui.show_game_over_sequence()
                     else:
                         self.ui.display_message("\n=== 魔王討伐完了！ 世界に平和が訪れました ===\n")
                     break # ゲームクリア
                else:
                     self.ui.display_will(battle2_data.get("Will", ""), title="勇者の最期")
                     self.previous_hero_will = battle2_data.get("Will", "")
                     self._proceed_to_next_generation()
        finally:
            import pygame
            pygame.quit()

    def _proceed_to_next_generation(self):
        """次世代の準備（ステータスインフレ）"""
        self.ui.display_message("\n>> 勇者の意志は次世代へ受け継がれます...")
        
        # 継承ロード演出 (PygameUIのみ)
        if isinstance(self.ui, PygameUI):
            self.ui.show_inheritance_loading(self.generation + 1)
            
        self.generation += 1
        self.hero_points = int(self.hero_points * 2)
        
        # モンスターデッキをリセットして次世代で再生成させる
        self.monsters = []
        self.selected_monsters = []
        self.maou = None
        self.hero = None
        self.maou_points = int(self.maou_points * 1.5)
        self.monster_points = int(self.monster_points * 1.5)
        self.ui.display_message(f"\n>> 勇者の意志は次世代へ... (次世代ポイント - 勇者:{self.hero_points}, 魔王:{self.maou_points}, モンスター:{self.monster_points})")