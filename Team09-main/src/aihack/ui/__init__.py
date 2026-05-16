from .console import ConsoleUI
try:
    from .pygame_ui import PygameUI
except ImportError as e:
    print(f"Warning: Failed to import PygameUI. Fallback to ConsoleUI. Error: {e}")
    import traceback
    traceback.print_exc()
    # Pygameがインストールされていない場合などのためのフォールバック
    PygameUI = ConsoleUI

__all__ = ["ConsoleUI", "PygameUI"]