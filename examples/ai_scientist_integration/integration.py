#!/usr/bin/env python3
"""
AI Scientist Integration Example

Demonstrates how AI Scientist uses claude-oauth-auth for Claude API authentication.
Shows common patterns and best practices for the integration.
"""

import sys
from pathlib import Path

# Add package to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from claude_oauth_auth import (
    ClaudeClient,
    get_auth_status,
    is_oauth_available,
    get_oauth_info,
    diagnose,
)


def example_1_basic_usage():
    """Example 1: Basic client creation and usage."""
    print("=" * 70)
    print("Example 1: Basic Client Usage")
    print("=" * 70)

    try:
        # Create client with automatic credential discovery
        client = ClaudeClient()
        print(f"✓ Client created: {client}")

        # Check what authentication method is being used
        status = get_auth_status()
        print(f"\nAuthentication status:")
        print(status['summary'])

        # Generate simple response
        print("\nGenerating response...")
        response = client.generate(
            "Say 'Authentication working!' in a creative way",
            max_tokens=100
        )
        print(f"\nClaude says: {response}")

    except ValueError as e:
        print(f"\n⚠ Authentication not configured: {e}")
        print("\nRun diagnostics:")
        diagnose()


def example_2_oauth_preferred():
    """Example 2: Preferring OAuth when available."""
    print("\n" + "=" * 70)
    print("Example 2: OAuth Preference (Claude Max Subscription)")
    print("=" * 70)

    # Check if OAuth is available
    if is_oauth_available():
        print("✓ OAuth available - using Claude Max subscription")

        # Get OAuth info
        info = get_oauth_info()
        print(f"\nOAuth Details:")
        print(f"  Subscription: {info.get('subscription_type')}")
        print(f"  Expires: {info.get('expires_at')}")
        print(f"  Scopes: {', '.join(info.get('scopes', []))}")

        # Create client (will automatically use OAuth)
        client = ClaudeClient()
        print(f"\n✓ Client using OAuth: {client}")

    else:
        print("⚠ OAuth not available - will use API key if present")

        # Create client (will fall back to API key)
        try:
            client = ClaudeClient()
            print(f"✓ Client using API key: {client}")
        except ValueError as e:
            print(f"✗ No credentials available: {e}")


def example_3_custom_configuration():
    """Example 3: Custom client configuration."""
    print("\n" + "=" * 70)
    print("Example 3: Custom Client Configuration")
    print("=" * 70)

    try:
        # Create client with custom settings for research
        client = ClaudeClient(
            model="claude-sonnet-4-5-20250929",
            temperature=0.8,        # Higher creativity
            max_tokens=4096,        # Longer responses
            verbose=True            # Show auth details
        )

        print(f"\n✓ Client created with custom settings")
        print(f"  Model: {client.model}")
        print(f"  Temperature: {client.temperature}")
        print(f"  Max tokens: {client.max_tokens}")

        # Generate research hypothesis
        print("\nGenerating research hypothesis...")
        hypothesis = client.generate(
            "Generate a novel hypothesis about quantum error correction",
            max_tokens=500
        )
        print(f"\nHypothesis: {hypothesis[:200]}...")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_4_error_handling():
    """Example 4: Proper error handling."""
    print("\n" + "=" * 70)
    print("Example 4: Error Handling and Diagnostics")
    print("=" * 70)

    try:
        # Attempt client creation
        client = ClaudeClient(verbose=True)
        print("✓ Authentication successful")

    except ValueError as e:
        print(f"✗ Authentication failed: {e}")

        # Run diagnostics
        print("\nRunning diagnostics...")
        from claude_oauth_auth import get_diagnostics

        diagnostics = get_diagnostics()

        print("\nCredentials:")
        for key, value in diagnostics['credentials'].items():
            print(f"  {key}: {value}")

        print("\nEnvironment:")
        for key, value in diagnostics['environment'].items():
            print(f"  {key}: {value}")

        print("\nRecommended actions:")
        print("1. Set ANTHROPIC_API_KEY environment variable, OR")
        print("2. Authenticate with Claude Code (claude auth login)")


def example_5_ai_scientist_pattern():
    """Example 5: Typical AI Scientist usage pattern."""
    print("\n" + "=" * 70)
    print("Example 5: AI Scientist Integration Pattern")
    print("=" * 70)

    try:
        # This is how AI Scientist typically uses the client
        print("Creating client for AI Scientist workflow...")

        # Create client with settings optimized for research
        client = ClaudeClient(
            model="claude-sonnet-4-5-20250929",
            temperature=0.7,        # Balance creativity/coherence
            max_tokens=4096         # Long-form research outputs
        )

        print(f"✓ Client ready for research workflow")

        # Simulate hypothesis generation (AI Scientist use case)
        print("\nSimulating Tree-of-Thoughts hypothesis generation...")

        prompt = """Generate 3 research hypotheses about improving neural network efficiency.

Each hypothesis should:
1. Be scientifically plausible
2. Be testable with experiments
3. Offer novel insights

Format as numbered list."""

        response = client.generate(prompt, temperature=0.8, max_tokens=2000)

        print("\nGenerated Hypotheses:")
        print("-" * 70)
        print(response)
        print("-" * 70)

        # Check token usage (if available)
        print("\n✓ Research workflow completed successfully")

    except Exception as e:
        print(f"✗ Workflow failed: {e}")
        import traceback
        traceback.print_exc()


def example_6_multi_turn_conversation():
    """Example 6: Multi-turn conversation for research refinement."""
    print("\n" + "=" * 70)
    print("Example 6: Multi-Turn Research Conversation")
    print("=" * 70)

    try:
        client = ClaudeClient(temperature=0.7, max_tokens=1000)

        # First turn: Generate hypothesis
        print("Turn 1: Generate initial hypothesis")
        hypothesis = client.generate(
            "Generate one hypothesis about quantum computing applications",
            max_tokens=300
        )
        print(f"Hypothesis: {hypothesis[:150]}...")

        # Second turn: Refine hypothesis
        print("\nTurn 2: Refine hypothesis")
        refinement = client.generate(
            f"Given this hypothesis: '{hypothesis[:100]}...', "
            "suggest specific experiments to test it",
            max_tokens=500
        )
        print(f"Experiments: {refinement[:150]}...")

        # Third turn: Identify challenges
        print("\nTurn 3: Identify challenges")
        challenges = client.generate(
            f"What are the main technical challenges in testing: '{hypothesis[:100]}...'",
            max_tokens=400
        )
        print(f"Challenges: {challenges[:150]}...")

        print("\n✓ Multi-turn research refinement completed")

    except Exception as e:
        print(f"✗ Conversation failed: {e}")


def example_7_batch_processing():
    """Example 7: Batch processing multiple research topics."""
    print("\n" + "=" * 70)
    print("Example 7: Batch Hypothesis Generation")
    print("=" * 70)

    try:
        client = ClaudeClient(temperature=0.8, max_tokens=500)

        topics = [
            "quantum error correction",
            "neural architecture search",
            "few-shot learning"
        ]

        print(f"Generating hypotheses for {len(topics)} topics...\n")

        hypotheses = []
        for i, topic in enumerate(topics, 1):
            print(f"[{i}/{len(topics)}] Processing: {topic}")

            hypothesis = client.generate(
                f"Generate a novel research hypothesis about {topic}",
                max_tokens=300
            )

            hypotheses.append({
                'topic': topic,
                'hypothesis': hypothesis[:100] + "..."
            })

        print("\n✓ Batch processing complete")
        print("\nResults:")
        for item in hypotheses:
            print(f"\nTopic: {item['topic']}")
            print(f"Hypothesis: {item['hypothesis']}")

    except Exception as e:
        print(f"✗ Batch processing failed: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("AI SCIENTIST INTEGRATION EXAMPLES")
    print("claude-oauth-auth Package")
    print("=" * 70)

    # Check initial authentication status
    print("\nInitial authentication check...")
    status = get_auth_status()

    if status['is_valid']:
        print(f"✓ Authentication configured")
        print(f"  Type: {status['auth_type']}")
        print(f"  Source: {status['source']}")
    else:
        print("⚠ No authentication configured")
        print("Some examples may fail - this is expected")

    # Run examples
    try:
        example_1_basic_usage()
        example_2_oauth_preferred()
        example_3_custom_configuration()
        example_4_error_handling()
        example_5_ai_scientist_pattern()
        example_6_multi_turn_conversation()
        example_7_batch_processing()

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)

    print("\nFor more information:")
    print("- Package docs: /home/aaron/projects/claude-oauth-auth/README.md")
    print("- API reference: /home/aaron/projects/claude-oauth-auth/docs/API.md")
    print("- Migration guide: docs/ai_scientist_migration.md")
    print("=" * 70)


if __name__ == "__main__":
    main()
