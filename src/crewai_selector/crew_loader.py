"""載入和管理 Crew 實例"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, List, Optional, Set

from crewai import Crew
from crewai.project import CrewBase
from rich.console import Console

from .constants import EXCLUDED_DIRS

console = Console()


class CrewInfo:
    """Crew 資訊"""

    def __init__(self, name: str, path: str, class_name: str, instance: Any):
        self.name = name
        self.path = path
        self.class_name = class_name
        self.instance = instance

    def __repr__(self) -> str:
        return f"CrewInfo(name={self.name}, class={self.class_name})"


class CrewLoader:
    """載入專案中的所有 Crews"""

    def __init__(self, base_path: str = ".", verbose: bool = False):
        self.base_path = Path(base_path).resolve()
        self.crews: List[CrewInfo] = []
        self.verbose = verbose
        self._seen_files: Set[Path] = set()  # 避免重複掃描

    def discover_crews(self) -> List[CrewInfo]:
        """自動發現專案中的所有 Crews"""
        self.crews = []

        # 搜尋 src 目錄和當前目錄
        search_paths = []
        src_dir = self.base_path / "src"
        if src_dir.exists():
            search_paths.append(src_dir)
        search_paths.append(self.base_path)

        for search_path in search_paths:
            self._scan_directory(search_path)

        return self.crews

    def _should_skip_path(self, path: Path) -> bool:
        """檢查是否應該跳過此路徑"""
        # 使用字串比對來確保能正確識別排除的目錄
        path_str = str(path)
        for excluded in EXCLUDED_DIRS:
            # 檢查路徑中是否包含排除的目錄（作為目錄名）
            if f"/{excluded}/" in path_str or f"\\{excluded}\\" in path_str:
                return True
            # 檢查路徑是否以排除的目錄開頭
            if path_str.startswith(f"{excluded}/") or path_str.startswith(f"{excluded}\\"):
                return True

        # 使用 parts 檢查隱藏目錄
        for part in path.parts:
            if part in EXCLUDED_DIRS:
                return True
            # 跳過以 . 開頭的隱藏目錄 (除了 . 和 ..)
            if part.startswith(".") and part not in {".", ".."}:
                return True
        return False

    def _scan_directory(self, directory: Path) -> None:
        """掃描目錄尋找 Crew 定義"""
        # 尋找所有 Python 檔案
        for py_file in directory.rglob("*.py"):
            # 解析完整路徑以避免重複
            resolved = py_file.resolve()
            if resolved in self._seen_files:
                continue
            self._seen_files.add(resolved)

            # 檢查是否應該跳過 (使用解析後的絕對路徑)
            if self._should_skip_path(resolved):
                continue

            # 跳過測試檔案
            if "test_" in py_file.name or py_file.name.startswith("test"):
                continue

            self._load_crews_from_file(py_file)

    def _load_crews_from_file(self, file_path: Path) -> None:
        """從 Python 檔案載入 Crew 類別"""
        try:
            # 動態導入模組
            module_name = f"temp_module_{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)

            if not spec or not spec.loader:
                return

            module = importlib.util.module_from_spec(spec)

            # 將專案根目錄加入 sys.path
            project_root = str(self.base_path.absolute())
            src_path = str((self.base_path / "src").absolute())

            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            if (self.base_path / "src").exists() and src_path not in sys.path:
                sys.path.insert(0, src_path)

            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # 尋找 CrewBase 裝飾的類別
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                # 檢查是否為 CrewBase 類別
                if (
                    isinstance(attr, type)
                    and hasattr(attr, "is_crew_class")
                    and attr.is_crew_class
                ):
                    try:
                        # 實例化並獲取 crew
                        instance = attr()
                        crew = instance.crew()

                        if isinstance(crew, Crew):
                            crew_info = CrewInfo(
                                name=attr_name,
                                path=str(file_path.relative_to(self.base_path)),
                                class_name=attr_name,
                                instance=instance,
                            )
                            self.crews.append(crew_info)
                            console.print(
                                f"[green]✓[/green] 發現 Crew: {attr_name} "
                                f"[dim]({file_path.relative_to(self.base_path)})[/dim]"
                            )
                    except Exception as e:
                        if self.verbose:
                            console.print(
                                f"[yellow]![/yellow] 無法實例化 {attr_name}: {e}",
                                style="dim",
                            )

            # 清理
            sys.modules.pop(module_name, None)

        except Exception as e:
            if self.verbose:
                console.print(f"[dim]跳過 {file_path.name}: {e}[/dim]", style="dim")

    def get_crew(self, name: str) -> Optional[CrewInfo]:
        """根據名稱獲取 Crew"""
        for crew in self.crews:
            if crew.name == name:
                return crew
        return None


def test_crew_loader():
    """測試 CrewLoader"""
    loader = CrewLoader()
    crews = loader.discover_crews()

    console.print(f"\n找到 {len(crews)} 個 Crews:")
    for crew in crews:
        console.print(f"  - {crew}")


if __name__ == "__main__":
    test_crew_loader()
