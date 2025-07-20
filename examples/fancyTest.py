# Enhanced chat example with beautiful terminal experience
from core.agent.agent import Agent
import asyncio
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.table import Table
from rich.align import Align
from rich.layout import Layout
from rich.columns import Columns

console = Console()

class EnhancedCallback:
    def __init__(self):
        self.start_time = time.time()
        self.step_count = 0
        
    def __call__(self, action_type, message, tool_calls):
        """Enhanced callback function with beautiful terminal output"""
        self.step_count += 1
        elapsed = time.time() - self.start_time
        
        if action_type == 'planning':
            self._show_planning(message, elapsed)
        elif action_type == 'reasoning':
            self._show_reasoning(message, elapsed)
        elif action_type == 'acting':
            self._show_acting(message, tool_calls, elapsed)
    
    def _show_planning(self, message, elapsed):
        """Display planning phase with brain icon and blue colors"""
        icon = "🧠"
        title = f"{icon} [bold blue]PLANNING[/bold blue] [dim](Step {self.step_count} • {elapsed:.1f}s)[/dim]"
        
        # Truncate message intelligently
        if len(message) > 120:
            preview = message[:117] + "..."
        else:
            preview = message
            
        panel = Panel(
            Text(preview, style="blue"),
            title=title,
            border_style="blue",
            padding=(0, 1)
        )
        console.print(panel)
    
    def _show_reasoning(self, message, elapsed):
        """Display reasoning phase with thinking icon and yellow colors"""
        icon = "🤔"
        title = f"{icon} [bold yellow]REASONING[/bold yellow] [dim](Step {self.step_count} • {elapsed:.1f}s)[/dim]"
        
        # Truncate message intelligently
        if len(message) > 120:
            preview = message[:117] + "..."
        else:
            preview = message
            
        panel = Panel(
            Text(preview, style="yellow"),
            title=title,
            border_style="yellow",
            padding=(0, 1)
        )
        console.print(panel)
    
    def _show_acting(self, message, tool_calls, elapsed):
        """Display acting phase with action icon and green colors"""
        icon = "⚡"
        title = f"{icon} [bold green]ACTING[/bold green] [dim](Step {self.step_count} • {elapsed:.1f}s)[/dim]"
        
        if tool_calls:
            # Create a nice table for tool calls
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_column("Tool", style="bold green")
            table.add_column("Status", style="green")
            
            for tool in tool_calls:
                table.add_row(f"🔧 {tool['name']}", "✓ Executing")
            
            panel = Panel(
                table,
                title=title,
                border_style="green",
                padding=(0, 1)
            )
        else:
            # Show message if no tool calls
            content = message[:100] + "..." if message and len(message) > 100 else (message or "Executing action...")
            panel = Panel(
                Text(content, style="green"),
                title=title,
                border_style="green",
                padding=(0, 1)
            )
        
        console.print(panel)

def show_welcome():
    """Display a beautiful welcome message"""
    welcome_text = Text()
    welcome_text.append("🤖 ", style="bold blue")
    welcome_text.append("Agent Core", style="bold blue")
    welcome_text.append(" - Enhanced Terminal Experience", style="dim blue")
    
    panel = Panel(
        Align.center(welcome_text),
        title="[bold]Welcome[/bold]",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

def show_task_start(task):
    """Display task start with nice formatting"""
    task_panel = Panel(
        Text(task, style="bold white"),
        title="[bold cyan]🎯 Task[/bold cyan]",
        border_style="cyan",
        padding=(0, 1)
    )
    console.print(task_panel)
    console.print()

def show_final_result(result, total_time):
    """Display final result with celebration"""
    # Create result content
    result_text = Text()
    result_text.append("✅ ", style="bold green")
    result_text.append("Task completed successfully!", style="bold green")
    result_text.append(f"\n\n📊 Total execution time: {total_time:.2f}s", style="dim")
    result_text.append(f"\n🎉 Result: {result}", style="white")
    
    panel = Panel(
        result_text,
        title="[bold green]🏆 SUCCESS[/bold green]",
        border_style="green",
        padding=(1, 2)
    )
    console.print()
    console.print(panel)

async def main():
    start_time = time.time()
    
    # Show welcome
    show_welcome()
    
    # Show task
    task = "Read the file 'README.md' and then write a python script that would use 'examples/mcp_server.py' and 'gpt-4o-mini' to perform a simple task."
    show_task_start(task)
    
    # Create enhanced callback
    callback = EnhancedCallback()
    
    # Show agent initialization
    with console.status("[bold blue]🔧 Initializing agent...", spinner="dots"):
        agent = await Agent.create(
            model='claude-3-5-sonnet-20241022',
            mcp_servers=['examples/mcp_server.py'],
            type='hybrid',
            callback=callback
        )
    
    console.print("[bold green]✅ Agent initialized successfully![/bold green]")
    console.print()
    
    # Run the task
    result = await agent.run(task)
    await agent.close()
    
    # Show final result
    total_time = time.time() - start_time
    show_final_result(result['state'], total_time)
    
    return result

if __name__ == '__main__':
    try:
        result = asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red]❌ Task interrupted by user[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]💥 Error: {str(e)}[/bold red]")
