# CLI Tool Example

A production-ready command-line interface for interacting with Claude API using OAuth authentication. Features interactive mode, file I/O, and comprehensive configuration options.

## Features

- **Interactive Mode**: Chat with Claude in your terminal
- **Non-Interactive Mode**: Single command execution
- **File I/O**: Read prompts from files, save responses
- **Configuration**: Persistent settings and defaults
- **History**: Command history tracking
- **Rich Output**: Beautiful terminal output with colors and formatting
- **Batch Processing**: Process multiple prompts from file
- **Progress Indicators**: Visual feedback for long operations

## Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Make executable (optional):**
   ```bash
   chmod +x claude_cli.py
   ```

4. **Set up authentication:**

   **Option A: Claude Code OAuth**
   ```bash
   # Automatic if Claude Code is installed
   ```

   **Option B: API key**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-api03-..."
   ```

   **Option C: OAuth token**
   ```bash
   export ANTHROPIC_AUTH_TOKEN="sk-ant-oat01-..."
   ```

## Usage

### Quick Start

```bash
# Ask a question
python claude_cli.py ask "What is Python?"

# Interactive mode
python claude_cli.py interactive

# Check auth status
python claude_cli.py auth-status

# Configure settings
python claude_cli.py config

# Show help
python claude_cli.py --help
```

### Commands

#### ask - Ask a Question

```bash
# Simple question
python claude_cli.py ask "Explain machine learning"

# From file
python claude_cli.py ask --file prompt.txt

# Save to file
python claude_cli.py ask "Write a poem" --output poem.txt

# With options
python claude_cli.py ask "Explain AI" \
  --max-tokens 500 \
  --temperature 0.8 \
  --format markdown

# With system prompt
python claude_cli.py ask "What should I do?" \
  --system "You are a helpful life coach"

# JSON output
python claude_cli.py ask "List 3 facts" --format json

# Verbose mode
python claude_cli.py ask "Hello" --verbose
```

Options:
- `--file, -f`: Read prompt from file
- `--output, -o`: Save response to file
- `--max-tokens, -m`: Maximum tokens to generate
- `--temperature, -t`: Sampling temperature (0-1)
- `--system, -s`: System prompt
- `--format`: Output format (text, json, markdown)
- `--verbose, -v`: Verbose output
- `--no-history`: Don't save to history

#### interactive - Interactive Mode

```bash
python claude_cli.py interactive
```

This starts an interactive chat session where you can have a back-and-forth conversation with Claude. The context is maintained across messages.

Features:
- Maintains conversation context
- Markdown rendering
- Progress indicators
- Type `exit`, `quit`, or press Ctrl+D to quit

#### auth-status - Check Authentication

```bash
python claude_cli.py auth-status
```

Displays:
- Current authentication method
- Available credential sources
- Authentication status for each source
- Active credentials being used

#### config - Configure Settings

```bash
python claude_cli.py config
```

Interactive configuration of:
- Default model
- Default temperature
- Default max tokens
- Default output format

Settings are saved to `~/.claude-cli/config.json`

#### history - View History

```bash
python claude_cli.py history
```

Shows last 20 commands with:
- Timestamp
- Prompt
- Response preview

History is saved to `~/.claude-cli/history.json`

#### clear-history - Clear History

```bash
python claude_cli.py clear-history
```

Clears all command history after confirmation.

#### batch - Batch Processing

```bash
python claude_cli.py batch prompts.txt responses.json
```

Process multiple prompts from a file:
- Input file: One prompt per line
- Output file: JSON with all responses
- Shows progress bar
- Handles errors gracefully

Example `prompts.txt`:
```
What is Python?
Explain machine learning
Write a haiku about programming
```

## Configuration

Configuration is stored in `~/.claude-cli/config.json`:

```json
{
  "default_model": "claude-sonnet-4-5-20250929",
  "default_temperature": 0.7,
  "default_max_tokens": 4096,
  "output_format": "text"
}
```

You can:
- Edit manually
- Use `config` command
- Override with command-line options

## Output Formats

### Text (default)

Plain text output with nice panel formatting:
```
╭─ Response ─────────────────────╮
│ Python is a high-level...      │
╰────────────────────────────────╯
```

### JSON

Structured JSON output:
```json
{
  "success": true,
  "prompt": "What is Python?",
  "response": "Python is a high-level...",
  "model": "claude-sonnet-4-5-20250929",
  "timestamp": "2025-10-24T12:00:00"
}
```

### Markdown

Markdown formatted output with rendering:
```markdown
# Response

Python is a **high-level** programming language...
```

## Examples

### Generate Code

```bash
python claude_cli.py ask "Write a Python function to sort a list" \
  --format markdown \
  --output sorting_function.md
```

### Creative Writing

```bash
python claude_cli.py ask "Write a short story about robots" \
  --temperature 0.9 \
  --max-tokens 1000
```

### Data Analysis

```bash
# Prompt in file
echo "Analyze this CSV data and provide insights" > prompt.txt
cat data.csv >> prompt.txt

python claude_cli.py ask --file prompt.txt --format json
```

### Interactive Research

```bash
python claude_cli.py interactive

You: What is quantum computing?
Claude: [Explains quantum computing...]

You: What are its practical applications?
Claude: [Discusses applications with context...]
```

### Batch Translation

Create `translations.txt`:
```
Translate to Spanish: Hello, how are you?
Translate to French: Good morning
Translate to German: Thank you very much
```

Process:
```bash
python claude_cli.py batch translations.txt translated.json
```

## File I/O Examples

### Read from file, display on screen

```bash
python claude_cli.py ask --file my_prompt.txt
```

### Read from file, save to file

```bash
python claude_cli.py ask --file prompt.txt --output response.txt
```

### Pipe from stdin (bash)

```bash
echo "What is AI?" | python claude_cli.py ask "$(cat -)"
```

### Chain with other commands

```bash
# Get code from Claude and save
python claude_cli.py ask "Write a Python hello world" \
  --format text \
  --output hello.py

# Run the generated code
python hello.py
```

## Advanced Usage

### Custom System Prompts

```bash
python claude_cli.py ask "Review this code: def foo(): pass" \
  --system "You are an expert code reviewer. Provide constructive feedback."
```

### Temperature Control

```bash
# More creative (higher temperature)
python claude_cli.py ask "Write a poem" --temperature 0.9

# More focused (lower temperature)
python claude_cli.py ask "What is 2+2?" --temperature 0.1
```

### Combining Options

```bash
python claude_cli.py ask \
  --file complex_prompt.txt \
  --output detailed_response.md \
  --format markdown \
  --max-tokens 2000 \
  --temperature 0.7 \
  --system "You are a technical writer" \
  --verbose
```

## Troubleshooting

### Issue: "Authentication Error"

**Cause:** No credentials found.

**Solution:**
```bash
# Check auth status
python claude_cli.py auth-status

# Set credentials
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Or use Claude Code OAuth (install Claude Code)
```

### Issue: Command not found

**Cause:** Python not in PATH or not executable.

**Solution:**
```bash
# Use full python path
/usr/bin/python3 claude_cli.py ask "Hello"

# Or make executable and add to PATH
chmod +x claude_cli.py
mv claude_cli.py ~/bin/claude
claude ask "Hello"
```

### Issue: "Rich" formatting not working

**Cause:** Terminal doesn't support colors/rich output.

**Solution:**
```bash
# Force basic output
export TERM=dumb
python claude_cli.py ask "Hello"

# Or pipe to file
python claude_cli.py ask "Hello" > output.txt
```

## Integration Examples

### Shell Script

```bash
#!/bin/bash
# analyze.sh - Analyze log files

LOGS=$(tail -n 100 app.log)
PROMPT="Analyze these logs and identify errors:\n$LOGS"

python claude_cli.py ask "$PROMPT" --format json > analysis.json
```

### Git Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Get commit message suggestions

DIFF=$(git diff --cached)
MSG=$(python claude_cli.py ask "Suggest a commit message for: $DIFF" --max-tokens 100)

echo "Suggested commit message:"
echo "$MSG"
```

### Cron Job

```bash
# Crontab entry - daily summary
0 9 * * * cd /path/to/project && python claude_cli.py ask "Summarize today's tasks" --output daily_summary.txt
```

## Tips and Best Practices

1. **Use config for defaults**: Set up common options in config
2. **Save important prompts**: Keep complex prompts in files
3. **Use --format json for scripting**: Easier to parse
4. **Enable history**: Useful for reviewing past interactions
5. **Use --verbose for debugging**: See authentication details
6. **Batch for multiple prompts**: More efficient than individual calls

## Performance

- **Batch processing**: ~2-3 seconds per prompt
- **Interactive mode**: Real-time responses
- **File I/O**: Minimal overhead
- **Configuration**: Loaded once, cached

## Security

- **Never commit credentials**: Don't put API keys in scripts
- **Use environment variables**: Keep credentials secure
- **Review history**: May contain sensitive information
- **Clear history if needed**: Use `clear-history` command

## Customization

### Add New Commands

Edit `claude_cli.py`:

```python
@cli.command()
@click.argument("topic")
def research(topic: str) -> None:
    """Research a topic in depth."""
    client = get_client()
    prompt = f"Research {topic} and provide comprehensive overview"
    response = client.generate(prompt, max_tokens=2000)
    console.print(response)
```

### Custom Output Formatting

```python
def custom_format(response: str) -> str:
    """Custom formatting function."""
    # Your formatting logic
    return formatted_response
```

## Next Steps

- Add completion support (bash/zsh)
- Implement caching for repeated prompts
- Add template support
- Create aliases for common prompts
- Add export to different formats

## License

MIT License - see main package for details.
