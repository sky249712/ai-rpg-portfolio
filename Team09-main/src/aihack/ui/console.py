from typing import List, Optional, Dict, Any
from ..models import Hero, Maou, Monster, Field
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.json import JSON
import json

class ConsoleUI:
    def __init__(self):
        self.console = Console()

    def show_loading(self, task_func, message="処理中..."):
        """
        コンソール版: ロード画面は出さず、同期的に実行して結果を返す。
        """
        print(f"\n[Info] {message}")
        return task_func()

    def display_status(self, hero: Hero, maou: Maou, field: Field, monsters: List[Monster], generation: int = 1):
        print(f"\n=== ステータス確認 (第{generation}世代) ===")
        print(f"【フィールド】: {field.name} (属性: {field.attribute})")
        print(f"【魔王】 HP: {maou.hp}, ATK: {maou.attack}, DEF: {maou.defense}")
        print(f"【{hero.name}】 HP: {hero.hp}, ATK: {hero.attack}, DEF: {hero.defense}")
        print(f"【{hero.name}の性格】: {hero.personality}")
        print("\n【配下モンスター】")
        for i, m in enumerate(monsters):
            print(f"{i+1}. {m.name} (属性: {m.attribute}) HP: {m.hp}, ATK: {m.attack}, DEF: {m.defense}, 性格: {m.personality}")

    def prompt_monster_selection(self) -> List[int]:
        print("\n魔王様、迎撃に向かわせるモンスターを2体選んでください（番号をスペース区切りで入力）")
        try:
            indices = input("> ").split()
            if len(indices) != 2:
                print("2体選んでください。デフォルトで1, 2番を選択します。")
                return [0, 1]
            return [int(i)-1 for i in indices]
        except:
            print("入力エラー。デフォルトで1, 2番を選択します。")
            return [0, 1]

    def prompt_command(self, monster_name: str) -> str:
        print(f"\n{monster_name}への命令を入力してください")
        return input(f"{monster_name}へ> ")

    def display_reaction(self, monster_name: str, reaction: str):
        print(f"{monster_name}の反応: {reaction}")

    def display_message(self, message: str):
        print(message)

    def display_story(self, title: str, story: str, result: str):
        print(f"\n【{title}】")
        print(story)
        print(f"\n結果: {result}")
    
    def display_will(self, will: str, title: str = "勇者の最期"):
         print(f"\n【{title}】")
         print(will)
         if title == "勇者の最期":
             print("\n（勇者の遺言が次世代の勇者へと継承されます...）")

    def display_llm_debug(self, prompt_data: Dict[str, str], response_data: Dict[str, Any]):
        """
        LLMへのプロンプトと応答JSONをRichを使って整形表示します。
        """
        self.console.print("\n[bold cyan]--- LLM Interaction Start ---[/bold cyan]")
        
        # System Prompt
        if prompt_data.get("system"):
            self.console.print(Panel(prompt_data["system"], title="[bold magenta]System Prompt[/bold magenta]", border_style="magenta"))
        
        # User Prompt
        if prompt_data.get("user"):
            self.console.print(Panel(prompt_data["user"], title="[bold green]User Prompt[/bold green]", border_style="green"))

        # Response JSON
        json_str = json.dumps(response_data, ensure_ascii=False, indent=2)
        self.console.print(Panel(JSON(json_str), title="[bold yellow]LLM Response (JSON)[/bold yellow]", border_style="yellow"))
        
        self.console.print("[bold cyan]--- LLM Interaction End ---[/bold cyan]\n")