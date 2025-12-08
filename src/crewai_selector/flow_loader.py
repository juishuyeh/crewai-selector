"""載入和管理 Flow 實例"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, List, Optional

from crewai.flow import Flow
from rich.console import Console

console = Console()


class FlowInfo:
    """Flow 資訊"""

    def __init__(self, name: str, path: str, class_name: str, flow_class: Any):
        self.name = name
        self.path = path
        self.class_name = class_name
        self.flow_class = flow_class

    def __repr__(self) -> str:
        return f"FlowInfo(name={self.name}, class={self.class_name})"


class FlowLoader:
    """載入專案中的所有 Flows"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.flows: List[FlowInfo] = []

    def discover_flows(self) -> List[FlowInfo]:
        """自動發現專案中的所有 Flows"""
        self.flows = []

        # 搜尋 src 目錄和當前目錄
        search_paths = []
        src_dir = self.base_path / "src"
        if src_dir.exists():
            search_paths.append(src_dir)
        search_paths.append(self.base_path)

        for search_path in search_paths:
            self._scan_directory(search_path)

        return self.flows

    def _scan_directory(self, directory: Path) -> None:
        """掃描目錄尋找 Flow 定義"""
        for py_file in directory.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue

            self._load_flows_from_file(py_file)

    def _load_flows_from_file(self, file_path: Path) -> None:
        """從 Python 檔案載入 Flow 類別"""
        try:
            module_name = f"temp_flow_module_{file_path.stem}"
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

            # 尋找 Flow 子類別
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                if (
                    isinstance(attr, type)
                    and issubclass(attr, Flow)
                    and attr != Flow  # 排除 Flow 基類
                ):
                    flow_info = FlowInfo(
                        name=attr_name,
                        path=str(file_path.relative_to(self.base_path)),
                        class_name=attr_name,
                        flow_class=attr,
                    )
                    self.flows.append(flow_info)
                    console.print(
                        f"[green]✓[/green] 發現 Flow: {attr_name} "
                        f"[dim]({file_path.relative_to(self.base_path)})[/dim]"
                    )

            # 清理
            sys.modules.pop(module_name, None)

        except Exception as e:
            console.print(f"[dim]跳過 {file_path.name}: {e}[/dim]", style="dim")

    def get_flow(self, name: str) -> Optional[FlowInfo]:
        """根據名稱獲取 Flow"""
        for flow in self.flows:
            if flow.name == name:
                return flow
        return None


def test_flow_loader():
    """測試 FlowLoader"""
    loader = FlowLoader()
    flows = loader.discover_flows()

    console.print(f"\n找到 {len(flows)} 個 Flows:")
    for flow in flows:
        console.print(f"  - {flow}")


if __name__ == "__main__":
    test_flow_loader()
