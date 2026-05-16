import yaml
import os
from typing import Any, Dict

class PromptManager:
    def __init__(self, prompt_dir: str):
        self.prompt_dir = prompt_dir

    def load_and_format(self, prompt_name: str, **kwargs) -> Dict[str, str]:
        """
        YAMLプロンプトを読み込み、プレースホルダを埋めて、システムプロンプトとユーザープロンプトを返します。
        """
        path = os.path.join(self.prompt_dir, f"{prompt_name}.yaml")
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        system_prompt_template = data.get("system_prompt", "")
        user_prompt_template = data.get("user_prompt", "")
        
        try:
            return {
                "system": system_prompt_template.format(**kwargs),
                "user": user_prompt_template.format(**kwargs)
            }
        except KeyError as e:
            print(f"Warning: Missing placeholder key in prompt {prompt_name}: {e}")
            return {
                "system": system_prompt_template,
                "user": user_prompt_template
            }
