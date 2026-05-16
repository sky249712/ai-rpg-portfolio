from aihack.core import GameEngine
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="魔王 vs 勇者 - Cyber Simulation")
    parser.add_argument("--gui", type=str, default="true", choices=["true"], help="Graphical UI mode (true or false)")
    args = parser.parse_args()

    # PromptYaml directory
    prompt_dir = "PromptYaml"
    data_dir = "JsonFolder"
    
    ui_mode = "graphical" if args.gui.lower() == "true" else "console"
    
    game = GameEngine(data_dir=data_dir, prompt_dir=prompt_dir, ui_mode=ui_mode)
    game.run()

if __name__ == "__main__":
    main()
