#!/usr/bin/env python3
"""
Claude CLI Tool with OAuth Integration

A production-ready command-line interface for interacting with Claude API
using OAuth authentication. Features interactive mode, file I/O, and
comprehensive configuration options.

Features:
- Interactive and non-interactive modes
- File input/output support
- Configuration file management
- Progress indicators
- Rich terminal output with colors
- History management
- Multiple output formats (text, JSON, markdown)

Usage:
    # Interactive mode
    python claude_cli.py

    # Single prompt
    python claude_cli.py ask "What is Python?"

    # From file
    python claude_cli.py ask --file prompt.txt --output response.txt

    # With options
    python claude_cli.py ask "Explain AI" --max-tokens 500 --temperature 0.8

    # Check auth status
    python claude_cli.py auth-status

Install:
    pip install -r requirements.txt
    chmod +x claude_cli.py  # Make executable
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

from claude_oauth_auth import ClaudeClient, get_auth_status


# Initialize rich console for beautiful output
console = Console()

# Configuration file path
CONFIG_DIR = Path.home() / ".claude-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"


def ensure_config_dir() -> None:
    """Ensure configuration directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """
    Load configuration from file.

    Returns:
        Configuration dictionary
    """
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
    return {
        "default_model": "claude-sonnet-4-5-20250929",
        "default_temperature": 0.7,
        "default_max_tokens": 4096,
        "output_format": "text",
    }


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        console.print(f"[green]Configuration saved to {CONFIG_FILE}[/green]")
    except Exception as e:
        console.print(f"[red]Error saving config: {e}[/red]")


def add_to_history(prompt: str, response: str) -> None:
    """Add interaction to history file."""
    ensure_config_dir()
    try:
        history = []
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE) as f:
                history = json.load(f)

        history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "prompt": prompt,
                "response": response[:500],  # Truncate for history
            }
        )

        # Keep only last 100 entries
        history = history[-100:]

        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not save to history: {e}[/yellow]")


def get_client(verbose: bool = False) -> Optional[ClaudeClient]:
    """
    Initialize Claude client with error handling.

    Args:
        verbose: Enable verbose output

    Returns:
        ClaudeClient instance or None if initialization fails
    """
    try:
        config = load_config()
        client = ClaudeClient(
            model=config.get("default_model", "claude-sonnet-4-5-20250929"),
            temperature=config.get("default_temperature", 0.7),
            max_tokens=config.get("default_max_tokens", 4096),
            verbose=verbose,
        )
        return client
    except ValueError as e:
        console.print(Panel(f"[red]Authentication Error[/red]\n\n{e}", border_style="red"))
        console.print("\n[yellow]Please set up authentication:[/yellow]")
        console.print("1. Set ANTHROPIC_API_KEY environment variable")
        console.print("2. Set ANTHROPIC_AUTH_TOKEN environment variable")
        console.print("3. Install and authenticate with Claude Code")
        return None


@click.group()
@click.version_option(version="1.0.0")
def cli() -> None:
    """
    Claude CLI - Command-line interface for Claude API with OAuth support.

    A powerful CLI tool for interacting with Claude AI from your terminal.
    """
    pass


@cli.command()
@click.argument("prompt", required=False)
@click.option("--file", "-f", type=click.Path(exists=True), help="Read prompt from file")
@click.option("--output", "-o", type=click.Path(), help="Save response to file")
@click.option("--max-tokens", "-m", type=int, help="Maximum tokens to generate")
@click.option("--temperature", "-t", type=float, help="Sampling temperature (0-1)")
@click.option("--system", "-s", help="System prompt")
@click.option("--format", type=click.Choice(["text", "json", "markdown"]), help="Output format")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--no-history", is_flag=True, help="Don't save to history")
def ask(
    prompt: Optional[str],
    file: Optional[str],
    output: Optional[str],
    max_tokens: Optional[int],
    temperature: Optional[float],
    system: Optional[str],
    format: Optional[str],
    verbose: bool,
    no_history: bool,
) -> None:
    """
    Ask Claude a question and get a response.

    Examples:

        claude_cli.py ask "What is machine learning?"

        claude_cli.py ask --file prompt.txt --output response.txt

        claude_cli.py ask "Explain AI" --max-tokens 500 --temperature 0.8
    """
    # Get prompt from argument or file
    if file:
        try:
            with open(file) as f:
                prompt = f.read().strip()
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            sys.exit(1)
    elif not prompt:
        console.print("[red]Error: Prompt required (use argument or --file)[/red]")
        sys.exit(1)

    # Initialize client
    client = get_client(verbose=verbose)
    if not client:
        sys.exit(1)

    # Load config for defaults
    config = load_config()
    output_format = format or config.get("output_format", "text")

    # Build kwargs
    kwargs = {}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if temperature is not None:
        kwargs["temperature"] = temperature
    if system is not None:
        kwargs["system"] = system

    # Show progress while generating
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating response...", total=None)
            response = client.generate(prompt, **kwargs)
            progress.remove_task(task)

        # Format output
        if output_format == "json":
            result = {
                "success": True,
                "prompt": prompt,
                "response": response,
                "model": client.model,
                "timestamp": datetime.utcnow().isoformat(),
            }
            output_text = json.dumps(result, indent=2)
        elif output_format == "markdown":
            output_text = f"# Response\n\n{response}"
        else:
            output_text = response

        # Display or save
        if output:
            try:
                with open(output, "w") as f:
                    f.write(output_text)
                console.print(f"[green]Response saved to {output}[/green]")
            except Exception as e:
                console.print(f"[red]Error writing file: {e}[/red]")
                sys.exit(1)
        else:
            # Display with nice formatting
            if output_format == "json":
                syntax = Syntax(output_text, "json", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title="Response", border_style="green"))
            elif output_format == "markdown":
                md = Markdown(response)
                console.print(Panel(md, title="Response", border_style="green"))
            else:
                console.print(Panel(response, title="Response", border_style="green"))

        # Save to history
        if not no_history:
            add_to_history(prompt, response)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def interactive(verbose: bool) -> None:
    """
    Start interactive chat session with Claude.

    Press Ctrl+D or type 'exit' to quit.
    """
    client = get_client(verbose=verbose)
    if not client:
        sys.exit(1)

    console.print(Panel("[bold green]Claude Interactive Mode[/bold green]\n\nType your messages. Press Ctrl+D or type 'exit' to quit.", border_style="green"))

    chat_history = []

    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

            if user_input.lower() in ["exit", "quit", "q"]:
                break

            if not user_input.strip():
                continue

            # Add to history
            chat_history.append({"role": "user", "content": user_input})

            # Build context
            context_messages = chat_history[-10:]  # Last 10 messages
            context_prompt = "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in context_messages]
            )

            # Generate response
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Thinking...", total=None)
                    response = client.generate(context_prompt + "\nassistant:")
                    progress.remove_task(task)

                # Display response
                console.print(f"\n[bold green]Claude[/bold green]")
                md = Markdown(response)
                console.print(md)

                # Add to history
                chat_history.append({"role": "assistant", "content": response})

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        except EOFError:
            # Ctrl+D pressed
            break
        except KeyboardInterrupt:
            # Ctrl+C pressed
            console.print("\n[yellow]Interrupted[/yellow]")
            break

    console.print("\n[green]Goodbye![/green]")


@cli.command()
def auth_status() -> None:
    """Display comprehensive authentication status."""
    try:
        status = get_auth_status()

        # Create table
        table = Table(title="Authentication Status", show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Summary", status.get("summary", "N/A"))
        table.add_row("Available Methods", ", ".join(status.get("available_methods", [])))

        if status.get("credentials_found"):
            creds = status.get("credentials_found", {})
            table.add_row("Active Auth Type", creds.get("auth_type", "N/A"))
            table.add_row("Active Source", creds.get("source", "N/A"))

        console.print(table)

        # Show all sources
        if status.get("sources"):
            console.print("\n[bold]Credential Sources:[/bold]")
            for source_name, source_data in status["sources"].items():
                available = source_data.get("available", False)
                style = "green" if available else "red"
                console.print(f"  [{style}]{'✓' if available else '✗'}[/{style}] {source_name}")

    except Exception as e:
        console.print(f"[red]Error getting auth status: {e}[/red]")
        sys.exit(1)


@cli.command()
def config() -> None:
    """Configure CLI settings interactively."""
    current_config = load_config()

    console.print(Panel("[bold]Claude CLI Configuration[/bold]", border_style="blue"))

    # Model
    model = Prompt.ask(
        "Default model",
        default=current_config.get("default_model", "claude-sonnet-4-5-20250929"),
    )

    # Temperature
    temperature_str = Prompt.ask(
        "Default temperature (0-1)", default=str(current_config.get("default_temperature", 0.7))
    )
    try:
        temperature = float(temperature_str)
    except ValueError:
        temperature = 0.7

    # Max tokens
    max_tokens_str = Prompt.ask(
        "Default max tokens", default=str(current_config.get("default_max_tokens", 4096))
    )
    try:
        max_tokens = int(max_tokens_str)
    except ValueError:
        max_tokens = 4096

    # Output format
    output_format = Prompt.ask(
        "Default output format",
        choices=["text", "json", "markdown"],
        default=current_config.get("output_format", "text"),
    )

    # Save configuration
    new_config = {
        "default_model": model,
        "default_temperature": temperature,
        "default_max_tokens": max_tokens,
        "output_format": output_format,
    }

    save_config(new_config)


@cli.command()
def history() -> None:
    """Show command history."""
    if not HISTORY_FILE.exists():
        console.print("[yellow]No history found[/yellow]")
        return

    try:
        with open(HISTORY_FILE) as f:
            history_data = json.load(f)

        if not history_data:
            console.print("[yellow]History is empty[/yellow]")
            return

        table = Table(title="Command History", show_header=True, header_style="bold magenta")
        table.add_column("Time", style="cyan")
        table.add_column("Prompt", style="yellow", max_width=50)
        table.add_column("Response Preview", style="green", max_width=50)

        for entry in history_data[-20:]:  # Last 20 entries
            timestamp = entry.get("timestamp", "N/A")
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                time_str = timestamp

            prompt = entry.get("prompt", "")[:50]
            response = entry.get("response", "")[:50]

            table.add_row(time_str, prompt, response)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error reading history: {e}[/red]")


@cli.command()
def clear_history() -> None:
    """Clear command history."""
    if Confirm.ask("Are you sure you want to clear history?"):
        try:
            if HISTORY_FILE.exists():
                HISTORY_FILE.unlink()
            console.print("[green]History cleared[/green]")
        except Exception as e:
            console.print(f"[red]Error clearing history: {e}[/red]")
    else:
        console.print("[yellow]Cancelled[/yellow]")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def batch(input_file: str, output_file: str, verbose: bool) -> None:
    """
    Process multiple prompts from a file.

    Input file should have one prompt per line.
    Output will be JSON with all responses.
    """
    client = get_client(verbose=verbose)
    if not client:
        sys.exit(1)

    try:
        # Read prompts
        with open(input_file) as f:
            prompts = [line.strip() for line in f if line.strip()]

        console.print(f"[cyan]Processing {len(prompts)} prompts...[/cyan]")

        results = []

        with Progress(console=console) as progress:
            task = progress.add_task("Processing...", total=len(prompts))

            for i, prompt in enumerate(prompts, 1):
                try:
                    response = client.generate(prompt)
                    results.append(
                        {
                            "prompt": prompt,
                            "response": response,
                            "success": True,
                            "index": i,
                        }
                    )
                except Exception as e:
                    results.append(
                        {"prompt": prompt, "error": str(e), "success": False, "index": i}
                    )

                progress.update(task, advance=1)

        # Save results
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        console.print(f"[green]Results saved to {output_file}[/green]")
        console.print(f"[cyan]Processed: {len(results)} prompts[/cyan]")
        console.print(
            f"[green]Successful: {sum(1 for r in results if r['success'])}[/green]"
        )
        console.print(f"[red]Failed: {sum(1 for r in results if not r['success'])}[/red]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
