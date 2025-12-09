"""CLI 主程式"""

import click
from rich.console import Console

from .selector import Selector
from .crew_loader import CrewInfo
from .flow_loader import FlowInfo

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """CrewAI Selector - 選擇並運行特定的 Crews 或 Flows"""
    pass


@main.command()
@click.option("--path", "-p", default=".", help="專案路徑 (預設: 當前目錄)")
@click.option("--name", "-n", default=None, help="直接指定要運行的 Crew 或 Flow 名稱")
@click.option("--inputs", "-i", default=None, help="JSON 格式的輸入參數")
@click.option("--verbose", "-v", is_flag=True, default=False, help="顯示詳細的掃描訊息")
def run(path: str, name: str, inputs: str, verbose: bool):
    """運行選中的 Crew 或 Flow"""
    import json

    selector = Selector(path, verbose=verbose)
    selector.discover_all()

    # 解析輸入參數
    input_dict = None
    if inputs:
        try:
            input_dict = json.loads(inputs)
        except json.JSONDecodeError:
            console.print("[red]✗ 無效的 JSON 輸入[/red]")
            return

    # 如果指定了名稱，直接運行
    if name:
        crew = selector.crew_loader.get_crew(name)
        if crew:
            selector.run_crew(crew, input_dict)
            return

        flow = selector.flow_loader.get_flow(name)
        if flow:
            selector.run_flow(flow, input_dict)
            return

        console.print(f"[red]✗ 找不到名為 '{name}' 的 Crew 或 Flow[/red]")
        return

    # 互動式選擇
    selected = selector.select()

    if selected is None:
        return

    if isinstance(selected, CrewInfo):
        selector.run_crew(selected, input_dict)
    elif isinstance(selected, FlowInfo):
        selector.run_flow(selected, input_dict)


@main.command()
@click.option("--path", "-p", default=".", help="專案路徑 (預設: 當前目錄)")
@click.option("--verbose", "-v", is_flag=True, default=False, help="顯示詳細的掃描訊息")
def list(path: str, verbose: bool):
    """列出所有可用的 Crews 和 Flows"""
    selector = Selector(path, verbose=verbose)
    selector.discover_all()
    selector.display_menu()


@main.command()
@click.option("--path", "-p", default=".", help="專案路徑 (預設: 當前目錄)")
@click.option("--verbose", "-v", is_flag=True, default=False, help="顯示詳細的掃描訊息")
def plot(path: str, verbose: bool):
    """視覺化 Flow 結構"""
    selector = Selector(path, verbose=verbose)
    selector.discover_all()

    if not selector.flows:
        console.print("[yellow]未找到任何 Flows[/yellow]")
        return

    selector.display_menu()

    from rich.prompt import Prompt

    flow_choices = [
        str(i + len(selector.crews) + 1) for i in range(len(selector.flows))
    ]

    if not flow_choices:
        console.print("[yellow]沒有 Flow 可以視覺化[/yellow]")
        return

    choice = Prompt.ask(
        "\n選擇要視覺化的 Flow", choices=flow_choices + ["q"], default="q"
    )

    if choice.lower() == "q":
        return

    index = int(choice) - len(selector.crews) - 1
    flow_info = selector.flows[index]

    console.print(f"\n[bold blue]📊 視覺化 Flow: {flow_info.name}[/bold blue]\n")

    try:
        flow_instance = flow_info.flow_class()
        flow_instance.plot()
        console.print("[green]✓ Flow 視覺化完成[/green]")
    except Exception as e:
        console.print(f"[red]✗ 視覺化失敗: {e}[/red]")


if __name__ == "__main__":
    main()
