# AI Scientist Integration Example

This example demonstrates how the AI Scientist project integrates with the `claude-oauth-auth` package for Claude API authentication.

## Overview

The AI Scientist is an autonomous research framework that uses Claude for hypothesis generation, literature review, and scientific reasoning. It relies on `claude-oauth-auth` for seamless authentication across multiple credential sources.

## Installation

```bash
# Install AI Scientist with claude-oauth-auth
pip install ai-scientist

# Or install from source with the package
cd /path/to/ai_scientist
pip install -e .  # This will also install claude-oauth-auth
```

## Quick Start

### Basic Client Usage

```python
from claude_oauth_auth import ClaudeClient

# Automatic credential discovery
client = ClaudeClient()

# Generate research hypotheses
response = client.generate(
    "Generate 3 novel hypotheses about quantum error correction",
    temperature=0.8,
    max_tokens=2000
)

print(response)
```

### Tree-of-Thoughts Integration

```python
from claude_oauth_auth import ClaudeClient
from ai_scientist.core import TreeOfThoughts

# Create Claude client
client = ClaudeClient(temperature=0.8, max_tokens=4096)

# Initialize Tree-of-Thoughts with Claude
tot = TreeOfThoughts(
    llm_client=client,
    max_depth=3,
    branching_factor=3
)

# Generate thought tree for research task
task = "Design a novel architecture for efficient transformer models"
best_thoughts = tot.generate(task, num_thoughts=5)

for thought in best_thoughts:
    print(f"Hypothesis: {thought.content}")
    print(f"Score: {thought.score:.2f}\n")
```

### Authentication Discovery

```python
from claude_oauth_auth import get_auth_status

# Check authentication status
status = get_auth_status()
print(status['summary'])
```

## Common Integration Patterns

### Pattern 1: Autonomous Research Pipeline

```python
from claude_oauth_auth import ClaudeClient
from ai_scientist import ScientificResearchPipeline

# Create pipeline with Claude authentication
client = ClaudeClient()
pipeline = ScientificResearchPipeline(llm_client=client)

# Run autonomous research
results = pipeline.research(
    goal="Investigate novel approaches to few-shot learning",
    domain="machine_learning"
)
```

### Pattern 2: Interactive Research Session

```python
from claude_oauth_auth import ClaudeClient, get_oauth_info
from ai_scientist import InteractiveResearchSession

# Check OAuth status
oauth_info = get_oauth_info()
if oauth_info['is_valid']:
    print(f"Using {oauth_info['subscription_type']} subscription")

# Create interactive session
client = ClaudeClient(verbose=True)
session = InteractiveResearchSession(
    llm_client=client,
    research_goal="Explore quantum computing applications"
)

# Run with human-in-the-loop
results = session.run_interactive()
```

### Pattern 3: Hypothesis Generation Agent

```python
from claude_oauth_auth import ClaudeClient
from ai_scientist.core import GenerationAgent

# Create agent with Claude backend
client = ClaudeClient(
    model="claude-sonnet-4-5-20250929",
    temperature=0.9,  # High creativity for hypothesis generation
    max_tokens=4096
)

agent = GenerationAgent(llm_client=client)

# Generate hypotheses
hypotheses = agent.generate_hypotheses(
    topic="neural network optimization",
    num_hypotheses=10,
    creativity=0.8
)
```

### Pattern 4: Literature Review with Authentication

```python
from claude_oauth_auth import ClaudeClient, is_oauth_available
from ai_scientist.skills import LiteratureSearchSkill

# Check if OAuth is available (preferred for Max subscription)
if is_oauth_available():
    print("Using Claude Max subscription - no API costs!")
    client = ClaudeClient()
else:
    print("Using API key - usage will be billed")
    client = ClaudeClient(api_key="sk-ant-...")

# Use for literature analysis
lit_skill = LiteratureSearchSkill(llm_client=client)
summary = lit_skill.analyze_paper("quantum_computing_paper.pdf")
```

## Configuration

### Environment Variables

```bash
# Priority 1: API key (if you have one)
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Priority 2: OAuth token (if not using Claude Code)
export ANTHROPIC_AUTH_TOKEN="sk-ant-oat01-..."

# For verbose logging
export CLAUDE_AUTH_VERBOSE=1
```

### Claude Code Integration

If using Claude Code, authentication is automatic:

```python
from claude_oauth_auth import ClaudeClient

# No configuration needed - uses ~/.claude/.credentials.json
client = ClaudeClient()
```

### Manual Configuration

```python
from claude_oauth_auth import ClaudeClient

# Option 1: Explicit API key
client = ClaudeClient(api_key="sk-ant-api03-...")

# Option 2: Explicit OAuth token
client = ClaudeClient(auth_token="sk-ant-oat01-...")

# Option 3: Custom credentials path
from claude_oauth_auth import OAuthTokenManager

manager = OAuthTokenManager(
    credentials_path="/custom/path/.credentials.json"
)
token = manager.get_access_token()
client = ClaudeClient(auth_token=token)
```

## Error Handling

### Credential Discovery Errors

```python
from claude_oauth_auth import ClaudeClient, diagnose

try:
    client = ClaudeClient()
except ValueError as e:
    print("Authentication failed:", e)

    # Run diagnostics
    print("\nRunning diagnostics...")
    diagnose()
```

### Token Expiration

```python
from claude_oauth_auth import is_oauth_available, get_oauth_info

if is_oauth_available():
    info = get_oauth_info()
    if not info['is_valid']:
        print(f"Token expired at: {info['expires_at']}")
        print("Please re-authenticate with Claude Code")
```

### Fallback Strategy

```python
from claude_oauth_auth import ClaudeClient, is_oauth_available
import os

# Try OAuth first, fall back to API key
if is_oauth_available():
    client = ClaudeClient()
    print("Using OAuth (Claude Max subscription)")
elif os.getenv('ANTHROPIC_API_KEY'):
    client = ClaudeClient()
    print("Using API key")
else:
    raise ValueError("No authentication method available")
```

## Testing

### Unit Tests

```python
import pytest
from claude_oauth_auth import ClaudeClient
from unittest.mock import Mock, patch

def test_client_creation():
    """Test client can be created with mock credentials."""
    with patch('claude_oauth_auth.get_oauth_token') as mock_token:
        mock_token.return_value = "sk-ant-oat01-test"
        client = ClaudeClient()
        assert client is not None

def test_hypothesis_generation():
    """Test hypothesis generation with mock LLM."""
    mock_llm = Mock()
    mock_llm.generate.return_value = "Test hypothesis"

    from ai_scientist.core import GenerationAgent
    agent = GenerationAgent(llm_client=mock_llm)

    hypotheses = agent.generate_hypotheses("test topic", num_hypotheses=1)
    assert len(hypotheses) >= 1
```

### Integration Tests

```python
import pytest
from claude_oauth_auth import ClaudeClient, is_oauth_available

@pytest.mark.skipif(not is_oauth_available(), reason="OAuth not available")
def test_real_api_call():
    """Test with real Claude API (requires valid credentials)."""
    client = ClaudeClient()
    response = client.generate("Say 'test successful'", max_tokens=50)
    assert "test successful" in response.lower()
```

## Performance Considerations

### Token Caching

The package automatically caches OAuth tokens to avoid repeated file reads:

```python
from claude_oauth_auth import get_token_manager

# First call reads from file
manager = get_token_manager()
token1 = manager.get_access_token()  # File read

# Subsequent calls use cache
token2 = manager.get_access_token()  # Cached
token3 = manager.get_access_token()  # Cached

# Force reload if needed
manager.reload()
token4 = manager.get_access_token()  # File read
```

### Batch Processing

For batch hypothesis generation:

```python
from claude_oauth_auth import ClaudeClient
from concurrent.futures import ThreadPoolExecutor

client = ClaudeClient()

def generate_hypothesis(topic):
    return client.generate(
        f"Generate a hypothesis about {topic}",
        max_tokens=500
    )

topics = ["quantum computing", "neural networks", "genetic algorithms"]

# Process in parallel
with ThreadPoolExecutor(max_workers=3) as executor:
    hypotheses = list(executor.map(generate_hypothesis, topics))
```

## Troubleshooting

### Import Errors

```python
# If you get: ImportError: cannot import name 'ClaudeClient'
# Check package is installed:
import claude_oauth_auth
print(claude_oauth_auth.__version__)  # Should print 0.1.0 or higher

# Check what's available:
print(dir(claude_oauth_auth))
```

### Authentication Issues

```python
from claude_oauth_auth import diagnose, get_diagnostics

# Run interactive diagnostics
diagnose()

# Or get programmatic diagnostics
diagnostics = get_diagnostics()
print(diagnostics['credentials'])
print(diagnostics['environment'])
```

### Version Compatibility

```python
# Check AI Scientist is using the package
import ai_scientist.core.oauth_manager as om
print(om.__file__)  # Should show claude_oauth_auth path, not ai_scientist
```

## Additional Resources

- **AI Scientist Documentation**: `/home/aaron/projects/ai_scientist/README.md`
- **Package API Reference**: `/home/aaron/projects/claude-oauth-auth/docs/API.md`
- **Migration Guide**: `/home/aaron/projects/claude-oauth-auth/docs/ai_scientist_migration.md`
- **Troubleshooting**: Run `python -m claude_oauth_auth diagnose`

## Support

For issues specific to AI Scientist integration:
1. Check migration guide: `docs/ai_scientist_migration.md`
2. Run diagnostics: `python -m claude_oauth_auth diagnose`
3. Review integration example: `examples/ai_scientist_integration/integration.py`
4. Check test suite: `tests/test_oauth_integration.py`
