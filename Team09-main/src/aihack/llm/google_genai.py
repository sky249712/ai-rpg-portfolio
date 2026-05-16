import json
import time
import os
import re
from typing import Any, Dict, Optional
from google import genai
from google.genai import types
from .abstract import LLMService

class GoogleGenAIService(LLMService):
    def __init__(self):
        # 環境変数からプロジェクトIDとロケーションを取得
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
        
        # クライアントの初期化 (Vertex AI モード)
        self.client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location
        )
        self.model_id = "gemini-2.0-flash-exp" # サンプルは2.5でしたが、利用可能な最新のflashを使用

    def generate_reaction(self, monster_personality: str, command: str) -> str:
        # 抽象クラスのメソッド。必要に応じて実装。
        pass

    def call_llm_with_retry(self, prompts: Dict[str, str], retries: int = 3, delay: int = 3) -> Dict[str, Any]:
        """
        LLMを呼び出し、JSONを抽出します。失敗時はリトライします。
        """
        system_instruction = prompts.get("system", "")
        user_prompt = prompts.get("user", "")

        # コンフィグの設定
        config = types.GenerateContentConfig(
            temperature=1.0,
            top_p=0.95,
            max_output_tokens=8192,
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
            ],
            system_instruction=[types.Part.from_text(text=system_instruction)] if system_instruction else None
        )

        for attempt in range(1, retries + 1):
            try:
                print(f"[LLM] Generating content... (Attempt {attempt}/{retries})")
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=[types.Part.from_text(text=user_prompt)],
                    config=config
                )
                text = response.text
                
                # Markdownコードブロック等からJSON部分を抽出
                json_match = re.search(r"\{.*\}", text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    # 全角コロン等の正規化
                    json_str = json_str.replace("：", ":")
                    return json.loads(json_str)
                else:
                    raise ValueError(f"LLMの応答にJSONが見つかりませんでした: {text}")

            except Exception as e:
                print(f"\n[LLMエラー] 試行 {attempt}/{retries} 失敗: {e}")
                if attempt < retries:
                    print(f"{delay}秒後にリトライします...")
                    time.sleep(delay)
                else:
                    print("リトライ上限に達しました。プログラムを終了します。")
                    raise e
        return {}