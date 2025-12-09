"""互動式選擇器"""

from typing import List, Optional, Union

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from .crew_loader import CrewInfo, CrewLoader
from .flow_loader import FlowInfo, FlowLoader

console = Console()


class Selector:
    """互動式 Crew/Flow 選擇器"""

    def __init__(self, base_path: str = ".", verbose: bool = False):
        self.crew_loader = CrewLoader(base_path, verbose=verbose)
        self.flow_loader = FlowLoader(base_path, verbose=verbose)
        self.crews: List[CrewInfo] = []
        self.flows: List[FlowInfo] = []
        self.verbose = verbose

    def discover_all(self) -> None:
        """發現所有 Crews 和 Flows"""
        console.print("\n[bold blue]🔍 掃描專案中的 Crews 和 Flows...[/bold blue]\n")

        self.crews = self.crew_loader.discover_crews()
        self.flows = self.flow_loader.discover_flows()

        console.print(
            f"\n[green]✓[/green] 發現 {len(self.crews)} 個 Crews, "
            f"{len(self.flows)} 個 Flows\n"
        )

    def display_menu(self) -> None:
        """顯示選單"""
        table = Table(title="可用的 Crews 和 Flows", show_header=True)
        table.add_column("#", style="cyan", width=4)
        table.add_column("類型", style="magenta", width=8)
        table.add_column("名稱", style="green")
        table.add_column("位置", style="dim")

        index = 1

        # 添加 Crews
        for crew in self.crews:
            table.add_row(str(index), "Crew", crew.name, crew.path)
            index += 1

        # 添加 Flows
        for flow in self.flows:
            table.add_row(str(index), "Flow", flow.name, flow.path)
            index += 1

        console.print(table)

    def select(self) -> Optional[Union[CrewInfo, FlowInfo]]:
        """互動式選擇"""
        if not self.crews and not self.flows:
            console.print("[red]✗[/red] 未找到任何 Crews 或 Flows")
            return None

        self.display_menu()

        total_items = len(self.crews) + len(self.flows)

        choice = Prompt.ask(
            "\n選擇要運行的項目",
            choices=[str(i) for i in range(1, total_items + 1)] + ["q"],
            default="q",
        )

        if choice.lower() == "q":
            console.print("[yellow]取消選擇[/yellow]")
            return None

        index = int(choice) - 1

        # 判斷選擇的是 Crew 還是 Flow
        if index < len(self.crews):
            return self.crews[index]
        else:
            flow_index = index - len(self.crews)
            return self.flows[flow_index]

    def run_crew(self, crew_info: CrewInfo, inputs: dict = None) -> None:
        """運行選中的 Crew"""
        console.print(f"\n[bold green]🚀 運行 Crew: {crew_info.name}[/bold green]\n")

        try:
            crew = crew_info.instance.crew()

            if inputs is None:
                inputs = self._prompt_for_inputs(crew)

            result = crew.kickoff(inputs=inputs)

            console.print("\n[bold green]✓ Crew 執行完成[/bold green]\n")
            console.print("[bold]結果:[/bold]")
            console.print(result)

        except Exception as e:
            console.print(f"[red]✗ 執行失敗: {e}[/red]")
            raise

    def run_flow(self, flow_info: FlowInfo, inputs: dict = None) -> None:
        """運行選中的 Flow"""
        console.print(f"\n[bold green]🚀 運行 Flow: {flow_info.name}[/bold green]\n")

        try:
            flow_instance = flow_info.flow_class()

            if inputs is None:
                inputs = {}

            result = flow_instance.kickoff(inputs)

            console.print("\n[bold green]✓ Flow 執行完成[/bold green]\n")
            console.print("[bold]結果:[/bold]")
            console.print(result)

        except Exception as e:
            console.print(f"[red]✗ 執行失敗: {e}[/red]")
            raise

    def _prompt_for_inputs(self, crew) -> dict:
        """提示用戶輸入參數"""
        try:
            required_inputs = crew.fetch_inputs()

            if not required_inputs:
                return {}

            console.print("\n[bold]需要以下輸入:[/bold]")
            inputs = {}

            for input_name in required_inputs:
                value = Prompt.ask(f"  {input_name}")
                inputs[input_name] = value

            return inputs

        except Exception:
            return {}
