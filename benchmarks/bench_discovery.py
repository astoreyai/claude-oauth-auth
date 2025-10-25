#!/usr/bin/env python3
"""
Credential Discovery Performance Benchmark

Measures the performance of credential discovery from various sources:
- OAuth credentials from Claude Code
- API keys from environment variables
- Config file parsing
- Cold start vs warm start (cached)

Usage:
    python benchmarks/bench_discovery.py
"""

import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claude_oauth_auth.auth_manager import UnifiedAuthManager
from claude_oauth_auth.oauth_manager import OAuthTokenManager


def benchmark_oauth_discovery(iterations: int = 1000) -> Dict[str, float]:
    """Benchmark OAuth credential discovery."""
    manager = OAuthTokenManager()

    # Cold start (first load)
    start = time.perf_counter()
    manager._load_credentials(force_reload=True)
    cold_start_time = time.perf_counter() - start

    # Warm start (cached)
    warm_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        manager._load_credentials(force_reload=False)
        warm_times.append(time.perf_counter() - start)

    # Token validation
    validation_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        manager.is_token_expired()
        validation_times.append(time.perf_counter() - start)

    return {
        "cold_start_ms": cold_start_time * 1000,
        "warm_start_avg_ms": (sum(warm_times) / len(warm_times)) * 1000,
        "warm_start_min_ms": min(warm_times) * 1000,
        "warm_start_max_ms": max(warm_times) * 1000,
        "validation_avg_ms": (sum(validation_times) / len(validation_times)) * 1000,
    }


def benchmark_env_var_discovery(iterations: int = 1000) -> Dict[str, float]:
    """Benchmark environment variable discovery."""
    # Set up test environment
    test_key = "sk-ant-api03-test-key-for-benchmarking-purposes-only"
    os.environ["ANTHROPIC_API_KEY"] = test_key

    try:
        times = []
        for _ in range(iterations):
            manager = UnifiedAuthManager(verbose=False)
            start = time.perf_counter()
            creds = manager.discover_credentials()
            times.append(time.perf_counter() - start)

        return {
            "avg_ms": (sum(times) / len(times)) * 1000,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
            "p50_ms": sorted(times)[len(times) // 2] * 1000,
            "p95_ms": sorted(times)[int(len(times) * 0.95)] * 1000,
            "p99_ms": sorted(times)[int(len(times) * 0.99)] * 1000,
        }
    finally:
        # Clean up
        os.environ.pop("ANTHROPIC_API_KEY", None)


def benchmark_explicit_key_discovery(iterations: int = 1000) -> Dict[str, float]:
    """Benchmark explicit API key parameter discovery."""
    test_key = "sk-ant-api03-test-key-for-benchmarking-purposes-only"

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        manager = UnifiedAuthManager(api_key=test_key, verbose=False)
        creds = manager.discover_credentials()
        times.append(time.perf_counter() - start)

    return {
        "avg_ms": (sum(times) / len(times)) * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
        "p50_ms": sorted(times)[len(times) // 2] * 1000,
        "p95_ms": sorted(times)[int(len(times) * 0.95)] * 1000,
        "p99_ms": sorted(times)[int(len(times) * 0.99)] * 1000,
    }


def benchmark_config_file_discovery(iterations: int = 100) -> Dict[str, float]:
    """Benchmark config file parsing."""
    # Create temporary config file
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        config_file.write_text('{"api_key": "sk-ant-api03-test-key"}')

        times = []
        for _ in range(iterations):
            manager = UnifiedAuthManager(verbose=False)
            start = time.perf_counter()
            result = manager._read_json_config(config_file)
            times.append(time.perf_counter() - start)

        return {
            "avg_ms": (sum(times) / len(times)) * 1000,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
        }


def benchmark_full_discovery_cascade(iterations: int = 100) -> Dict[str, float]:
    """Benchmark full credential discovery cascade."""
    # Remove env vars to force full cascade
    env_backup = {}
    for key in ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"]:
        if key in os.environ:
            env_backup[key] = os.environ.pop(key)

    try:
        times = []
        for _ in range(iterations):
            manager = UnifiedAuthManager(verbose=False)
            start = time.perf_counter()
            try:
                creds = manager.discover_credentials()
            except ValueError:
                # Expected if no credentials available
                pass
            times.append(time.perf_counter() - start)

        return {
            "avg_ms": (sum(times) / len(times)) * 1000,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
        }
    finally:
        # Restore env vars
        os.environ.update(env_backup)


def print_results_table(results: Dict[str, Dict[str, float]]) -> None:
    """Print results in a formatted table."""
    print("\n" + "=" * 80)
    print("CREDENTIAL DISCOVERY PERFORMANCE BENCHMARK")
    print("=" * 80)

    print("\n1. OAuth Credentials Discovery (Claude Code)")
    print("-" * 80)
    oauth_results = results["oauth"]
    print(f"  Cold Start (first load):    {oauth_results['cold_start_ms']:>8.3f} ms")
    print(f"  Warm Start (cached):        {oauth_results['warm_start_avg_ms']:>8.3f} ms (avg)")
    print(f"                              {oauth_results['warm_start_min_ms']:>8.3f} ms (min)")
    print(f"                              {oauth_results['warm_start_max_ms']:>8.3f} ms (max)")
    print(f"  Token Validation:           {oauth_results['validation_avg_ms']:>8.3f} ms (avg)")

    print("\n2. Environment Variable Discovery (ANTHROPIC_API_KEY)")
    print("-" * 80)
    env_results = results["env_var"]
    print(f"  Average:                    {env_results['avg_ms']:>8.3f} ms")
    print(f"  Min:                        {env_results['min_ms']:>8.3f} ms")
    print(f"  Max:                        {env_results['max_ms']:>8.3f} ms")
    print(f"  p50:                        {env_results['p50_ms']:>8.3f} ms")
    print(f"  p95:                        {env_results['p95_ms']:>8.3f} ms")
    print(f"  p99:                        {env_results['p99_ms']:>8.3f} ms")

    print("\n3. Explicit API Key Parameter")
    print("-" * 80)
    explicit_results = results["explicit_key"]
    print(f"  Average:                    {explicit_results['avg_ms']:>8.3f} ms")
    print(f"  Min:                        {explicit_results['min_ms']:>8.3f} ms")
    print(f"  Max:                        {explicit_results['max_ms']:>8.3f} ms")
    print(f"  p50:                        {explicit_results['p50_ms']:>8.3f} ms")
    print(f"  p95:                        {explicit_results['p95_ms']:>8.3f} ms")
    print(f"  p99:                        {explicit_results['p99_ms']:>8.3f} ms")

    print("\n4. Config File Parsing (JSON)")
    print("-" * 80)
    config_results = results["config_file"]
    print(f"  Average:                    {config_results['avg_ms']:>8.3f} ms")
    print(f"  Min:                        {config_results['min_ms']:>8.3f} ms")
    print(f"  Max:                        {config_results['max_ms']:>8.3f} ms")

    print("\n5. Full Discovery Cascade (All Sources)")
    print("-" * 80)
    cascade_results = results["full_cascade"]
    print(f"  Average:                    {cascade_results['avg_ms']:>8.3f} ms")
    print(f"  Min:                        {cascade_results['min_ms']:>8.3f} ms")
    print(f"  Max:                        {cascade_results['max_ms']:>8.3f} ms")

    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)
    print("\nFastest to Slowest:")

    # Create comparison list
    comparisons = [
        ("Explicit API Key (avg)", explicit_results['avg_ms']),
        ("Environment Variable (avg)", env_results['avg_ms']),
        ("OAuth Cached (avg)", oauth_results['warm_start_avg_ms']),
        ("OAuth Cold Start", oauth_results['cold_start_ms']),
        ("Config File (avg)", config_results['avg_ms']),
        ("Full Cascade (avg)", cascade_results['avg_ms']),
    ]

    comparisons.sort(key=lambda x: x[1])

    for i, (name, time_ms) in enumerate(comparisons, 1):
        print(f"  {i}. {name:<30} {time_ms:>8.3f} ms")

    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)

    print("\n1. Explicit parameters are fastest (no discovery overhead)")
    print("2. Environment variables are very fast (simple OS call)")
    print("3. OAuth caching provides significant speedup vs cold start")
    print("4. Config file parsing has measurable overhead")
    print("5. Full cascade is slowest (tries multiple sources)")

    print("\nRECOMMENDATIONS:")
    print("- For production: Use explicit parameters or environment variables")
    print("- For development: OAuth caching makes repeated discovery fast")
    print("- Avoid full cascade in tight loops (cache credentials)")

    print("\n" + "=" * 80)
    print()


def main() -> None:
    """Run all benchmarks and display results."""
    print("Starting credential discovery benchmarks...")
    print("This may take a minute...\n")

    results = {}

    print("Running OAuth discovery benchmark...")
    results["oauth"] = benchmark_oauth_discovery(iterations=1000)

    print("Running environment variable benchmark...")
    results["env_var"] = benchmark_env_var_discovery(iterations=1000)

    print("Running explicit key benchmark...")
    results["explicit_key"] = benchmark_explicit_key_discovery(iterations=1000)

    print("Running config file benchmark...")
    results["config_file"] = benchmark_config_file_discovery(iterations=100)

    print("Running full cascade benchmark...")
    results["full_cascade"] = benchmark_full_discovery_cascade(iterations=100)

    print("\nBenchmarks complete!")
    print_results_table(results)


if __name__ == "__main__":
    main()
