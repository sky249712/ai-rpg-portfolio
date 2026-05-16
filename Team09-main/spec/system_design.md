# システム設計書

## 概要
魔王となって勇者を迎撃するシミュレーションゲーム。

## モジュール構成

### 1. Models (`src/models.py`)
- `Character`: 共通のステータスを持つ基底クラス
- `Hero`: 勇者クラス
- `Maou`: 魔王クラス
- `Monster`: 配下のモンスタークラス
- `Field`: 戦闘フィールドクラス

### 2. Services
- `DataLoader`: `JsonFolder` からのデータ読み込み
- `BattleService`: 戦闘ロジックの実行
- `StatusService`: 属性補正や性格更新の処理

### 3. Game Engine (`src/engine.py`)
- 各フェーズ（初期化、魔王、反応、戦闘、結果）を管理するメインロジック

## 属性補正ルール
- キャラクターの属性とフィールドの属性が一致する場合：
  - HP, Attack, Defense を 1.1倍（小数点以下切り捨て、または浮動小数点保持は実装時に決定）

## 戦闘ロジック (簡易版)
- 勇者 vs モンスター2体
- 交互に攻撃し、HPが0になったら脱落
- 詳細は `BattleService` で定義
