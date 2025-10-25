# AI Scientist Integration Section
## To be added to README.md

Add this section after "Quick Start" and before "Advanced Usage":

---

## Used By

### AI Scientist

This package is used by [AI Scientist](https://github.com/astoreyai/ai_scientist), an autonomous research framework powered by Claude. The AI Scientist uses `claude-oauth-auth` for seamless authentication across multiple credential sources.

**Integration Benefits:**
- Zero-configuration setup with Claude Code
- Automatic credential discovery (OAuth, API keys, env vars)
- Enhanced error messages for debugging
- Comprehensive diagnostics and validation

**Example from AI Scientist:**

```python
from claude_oauth_auth import ClaudeClient, get_auth_status

# Check authentication status
status = get_auth_status()
print(status['summary'])

# Create client with automatic credential discovery
client = ClaudeClient(
    model="claude-sonnet-4-5-20250929",
    temperature=0.7,
    max_tokens=4096
)

# Use in Tree-of-Thoughts workflow
from ai_scientist.core import TreeOfThoughts

tot = TreeOfThoughts(llm_client=client)
hypotheses = tot.generate("Research quantum computing applications")
```

**Migration Guide:**

If you're migrating AI Scientist from embedded authentication code to this package, see:
- [AI Scientist Migration Guide](docs/ai_scientist_migration.md)
- [Compatibility Analysis](docs/COMPATIBILITY_ANALYSIS.md)
- [Integration Examples](examples/ai_scientist_integration/)

---

## Additional Documentation

Add these links to the documentation section:

### For AI Scientist Users

- **[AI Scientist Migration Guide](docs/ai_scientist_migration.md)** - Complete guide to migrating from embedded auth code
- **[AI Scientist Integration Example](examples/ai_scientist_integration/)** - Integration patterns and best practices
- **[Compatibility Analysis](docs/COMPATIBILITY_ANALYSIS.md)** - Detailed compatibility assessment
- **[Performance Analysis](docs/PERFORMANCE_ANALYSIS.md)** - Performance impact analysis
- **[Rollout Plan](AI_SCIENTIST_ROLLOUT.md)** - Phased migration strategy
