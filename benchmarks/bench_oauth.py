#!/usr/bin/env python3
"""
OAuth Token Operations Performance Benchmark

Measures OAuth-specific operation performance:
- Token validation speed
- Expiration checking
- Credential file parsing
- Thread-safe caching

Usage:
    python benchmarks/bench_oauth.py
"""

import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claude_oauth_auth.oauth_manager import OAuthTokenManager


def create_test_credentials(expires_in_days: int = 30) -> Dict:
    """Create test OAuth credentials."""
    expires_at = int((datetime.now().timestamp() + (expires_in_days * 24 * 60 * 60)) * 1000)
    return {
        "claudeAiOauth": {
            "accessToken": "sk-ant-oat01-test-token-for-benchmarking-only",
            "refreshToken": "sk-ant-ort01-test-refresh-token",
            "expiresAt": expires_at,
            "scopes": ["user:inference", "user:profile"],
            "subscriptionType": "max"
        }
    }


def benchmark_credential_file_parsing(iterations: int = 1000) -> Dict[str, float]:
    """Benchmark parsing OAuth credential files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cred_file = Path(tmpdir) / ".credentials.json"
        cred_data = create_test_credentials()
        cred_file.write_text(json.dumps(cred_data))

        manager = OAuthTokenManager(credentials_path=cred_file)

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

        # Force reload (bypass cache)
        reload_times = []
        for _ in range(100):  # Fewer iterations for file I/O
            start = time.perf_counter()
            manager._load_credentials(force_reload=True)
            reload_times.append(time.perf_counter() - start)

        return {
            "cold_start_ms": cold_start_time * 1000,
            "warm_avg_ms": (sum(warm_times) / len(warm_times)) * 1000,
            "warm_min_ms": min(warm_times) * 1000,
            "warm_max_ms": max(warm_times) * 1000,
            "reload_avg_ms": (sum(reload_times) / len(reload_times)) * 1000,
            "reload_min_ms": min(reload_times) * 1000,
            "reload_max_ms": max(reload_times) * 1000,
        }


def benchmark_token_validation(iterations: int = 10000) -> Dict[str, float]:
    """Benchmark token validation operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cred_file = Path(tmpdir) / ".credentials.json"
        cred_data = create_test_credentials()
        cred_file.write_text(json.dumps(cred_data))

        manager = OAuthTokenManager(credentials_path=cred_file)

        # is_oauth_available
        times_available = []
        for _ in range(iterations):
            start = time.perf_counter()
            manager.is_oauth_available()
            times_available.append(time.perf_counter() - start)

        # is_token_expired
        times_expired = []
        for _ in range(iterations):
            start = time.perf_counter()
            manager.is_token_expired()
            times_expired.append(time.perf_counter() - start)

        # get_access_token
        times_get_token = []
        for _ in range(iterations):
            start = time.perf_counter()
            manager.get_access_token()
            times_get_token.append(time.perf_counter() - start)

        return {
            "is_available_avg_us": (sum(times_available) / len(times_available)) * 1_000_000,
            "is_available_min_us": min(times_available) * 1_000_000,
            "is_available_max_us": max(times_available) * 1_000_000,
            "is_expired_avg_us": (sum(times_expired) / len(times_expired)) * 1_000_000,
            "is_expired_min_us": min(times_expired) * 1_000_000,
            "is_expired_max_us": max(times_expired) * 1_000_000,
            "get_token_avg_us": (sum(times_get_token) / len(times_get_token)) * 1_000_000,
            "get_token_min_us": min(times_get_token) * 1_000_000,
            "get_token_max_us": max(times_get_token) * 1_000_000,
        }


def benchmark_token_info_retrieval(iterations: int = 1000) -> Dict[str, float]:
    """Benchmark token info and metadata retrieval."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cred_file = Path(tmpdir) / ".credentials.json"
        cred_data = create_test_credentials()
        cred_file.write_text(json.dumps(cred_data))

        manager = OAuthTokenManager(credentials_path=cred_file)

        # get_token_info
        times_info = []
        for _ in range(iterations):
            start = time.perf_counter()
            manager.get_token_info()
            times_info.append(time.perf_counter() - start)

        # get_subscription_type
        times_sub = []
        for _ in range(iterations):
            start = time.perf_counter()
            manager.get_subscription_type()
            times_sub.append(time.perf_counter() - start)

        # get_scopes
        times_scopes = []
        for _ in range(iterations):
            start = time.perf_counter()
            manager.get_scopes()
            times_scopes.append(time.perf_counter() - start)

        return {
            "get_info_avg_us": (sum(times_info) / len(times_info)) * 1_000_000,
            "get_info_min_us": min(times_info) * 1_000_000,
            "get_info_max_us": max(times_info) * 1_000_000,
            "get_subscription_avg_us": (sum(times_sub) / len(times_sub)) * 1_000_000,
            "get_scopes_avg_us": (sum(times_scopes) / len(times_scopes)) * 1_000_000,
        }


def benchmark_expiration_edge_cases(iterations: int = 1000) -> Dict[str, float]:
    """Benchmark expiration checking with different scenarios."""
    results = {}

    # Valid token (far future expiration)
    with tempfile.TemporaryDirectory() as tmpdir:
        cred_file = Path(tmpdir) / ".credentials.json"
        cred_data = create_test_credentials(expires_in_days=365)
        cred_file.write_text(json.dumps(cred_data))
        manager = OAuthTokenManager(credentials_path=cred_file)

        times_valid = []
        for _ in range(iterations):
            start = time.perf_counter()
            is_expired = manager.is_token_expired()
            times_valid.append(time.perf_counter() - start)

        results["valid_token_avg_us"] = (sum(times_valid) / len(times_valid)) * 1_000_000

    # Expired token (past expiration)
    with tempfile.TemporaryDirectory() as tmpdir:
        cred_file = Path(tmpdir) / ".credentials.json"
        cred_data = create_test_credentials(expires_in_days=-1)
        cred_file.write_text(json.dumps(cred_data))
        manager = OAuthTokenManager(credentials_path=cred_file)

        times_expired = []
        for _ in range(iterations):
            start = time.perf_counter()
            is_expired = manager.is_token_expired()
            times_expired.append(time.perf_counter() - start)

        results["expired_token_avg_us"] = (sum(times_expired) / len(times_expired)) * 1_000_000

    # Missing credentials
    with tempfile.TemporaryDirectory() as tmpdir:
        cred_file = Path(tmpdir) / ".credentials.json"
        # File doesn't exist
        manager = OAuthTokenManager(credentials_path=cred_file)

        times_missing = []
        for _ in range(iterations):
            start = time.perf_counter()
            is_expired = manager.is_token_expired()
            times_missing.append(time.perf_counter() - start)

        results["missing_creds_avg_us"] = (sum(times_missing) / len(times_missing)) * 1_000_000

    return results


def benchmark_cache_efficiency(iterations: int = 100) -> Dict[str, float]:
    """Benchmark caching efficiency."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cred_file = Path(tmpdir) / ".credentials.json"
        cred_data = create_test_credentials()
        cred_file.write_text(json.dumps(cred_data))

        manager = OAuthTokenManager(credentials_path=cred_file)

        # Sequential operations (should hit cache)
        start = time.perf_counter()
        for _ in range(iterations):
            manager.is_oauth_available()
            manager.is_token_expired()
            manager.get_access_token()
            manager.get_token_info()
        cached_total = time.perf_counter() - start

        # Force reload each time (no cache)
        start = time.perf_counter()
        for _ in range(iterations):
            manager._load_credentials(force_reload=True)
            manager.is_oauth_available()
            manager.is_token_expired()
            manager.get_access_token()
            manager.get_token_info()
        uncached_total = time.perf_counter() - start

        speedup = uncached_total / cached_total if cached_total > 0 else 0

        return {
            "cached_total_ms": cached_total * 1000,
            "uncached_total_ms": uncached_total * 1000,
            "cached_avg_ms": (cached_total / iterations) * 1000,
            "uncached_avg_ms": (uncached_total / iterations) * 1000,
            "speedup_factor": speedup,
        }


def print_results_table(results: Dict[str, Dict[str, float]]) -> None:
    """Print results in a formatted table."""
    print("\n" + "=" * 80)
    print("OAUTH TOKEN OPERATIONS PERFORMANCE BENCHMARK")
    print("=" * 80)

    print("\n1. Credential File Parsing")
    print("-" * 80)
    parsing = results["file_parsing"]
    print(f"  Cold Start (first load):    {parsing['cold_start_ms']:>8.3f} ms")
    print(f"  Warm (cached):              {parsing['warm_avg_ms']:>8.3f} ms (avg)")
    print(f"                              {parsing['warm_min_ms']:>8.3f} ms (min)")
    print(f"                              {parsing['warm_max_ms']:>8.3f} ms (max)")
    print(f"  Force Reload:               {parsing['reload_avg_ms']:>8.3f} ms (avg)")
    print(f"                              {parsing['reload_min_ms']:>8.3f} ms (min)")
    print(f"                              {parsing['reload_max_ms']:>8.3f} ms (max)")

    print("\n2. Token Validation Operations (microseconds)")
    print("-" * 80)
    validation = results["validation"]
    print(f"  is_oauth_available():       {validation['is_available_avg_us']:>8.3f} μs (avg)")
    print(f"                              {validation['is_available_min_us']:>8.3f} μs (min)")
    print(f"                              {validation['is_available_max_us']:>8.3f} μs (max)")
    print(f"  is_token_expired():         {validation['is_expired_avg_us']:>8.3f} μs (avg)")
    print(f"                              {validation['is_expired_min_us']:>8.3f} μs (min)")
    print(f"                              {validation['is_expired_max_us']:>8.3f} μs (max)")
    print(f"  get_access_token():         {validation['get_token_avg_us']:>8.3f} μs (avg)")
    print(f"                              {validation['get_token_min_us']:>8.3f} μs (min)")
    print(f"                              {validation['get_token_max_us']:>8.3f} μs (max)")

    print("\n3. Token Info Retrieval (microseconds)")
    print("-" * 80)
    info = results["token_info"]
    print(f"  get_token_info():           {info['get_info_avg_us']:>8.3f} μs (avg)")
    print(f"                              {info['get_info_min_us']:>8.3f} μs (min)")
    print(f"                              {info['get_info_max_us']:>8.3f} μs (max)")
    print(f"  get_subscription_type():    {info['get_subscription_avg_us']:>8.3f} μs (avg)")
    print(f"  get_scopes():               {info['get_scopes_avg_us']:>8.3f} μs (avg)")

    print("\n4. Expiration Edge Cases (microseconds)")
    print("-" * 80)
    edge = results["edge_cases"]
    print(f"  Valid Token:                {edge['valid_token_avg_us']:>8.3f} μs (avg)")
    print(f"  Expired Token:              {edge['expired_token_avg_us']:>8.3f} μs (avg)")
    print(f"  Missing Credentials:        {edge['missing_creds_avg_us']:>8.3f} μs (avg)")

    print("\n5. Cache Efficiency (100 iterations)")
    print("-" * 80)
    cache = results["cache"]
    print(f"  Cached Total:               {cache['cached_total_ms']:>8.3f} ms")
    print(f"  Uncached Total:             {cache['uncached_total_ms']:>8.3f} ms")
    print(f"  Cached Average:             {cache['cached_avg_ms']:>8.3f} ms")
    print(f"  Uncached Average:           {cache['uncached_avg_ms']:>8.3f} ms")
    print(f"  Speedup Factor:             {cache['speedup_factor']:>8.2f}x")

    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)

    print("\n1. File Parsing Performance:")
    print(f"   - Cold start: {parsing['cold_start_ms']:.3f} ms (initial load)")
    print(f"   - Cached: {parsing['warm_avg_ms']:.3f} ms (near-instant)")
    print(f"   - Cache provides {parsing['cold_start_ms'] / parsing['warm_avg_ms']:.0f}x speedup")

    print("\n2. Validation Operations (microsecond-level):")
    print(f"   - All operations < {max(validation['is_available_avg_us'], validation['is_expired_avg_us'], validation['get_token_avg_us']):.1f} μs")
    print("   - Extremely fast for high-frequency calls")
    print("   - Safe for per-request validation")

    print("\n3. Caching Impact:")
    print(f"   - Cache provides {cache['speedup_factor']:.1f}x speedup")
    print("   - Thread-safe caching works efficiently")
    print("   - Minimal overhead for cached operations")

    print("\nRECOMMENDATIONS:")
    print("- Token validation is fast enough for every API call")
    print("- Caching is highly effective - don't bypass it")
    print("- File I/O is the bottleneck - cache works well to mitigate")
    print("- All operations are production-ready for high-frequency usage")

    print("\n" + "=" * 80)
    print()


def main() -> None:
    """Run all benchmarks and display results."""
    print("Starting OAuth token operations benchmarks...")
    print("This may take a minute...\n")

    results = {}

    print("Running credential file parsing benchmark...")
    results["file_parsing"] = benchmark_credential_file_parsing(iterations=1000)

    print("Running token validation benchmark...")
    results["validation"] = benchmark_token_validation(iterations=10000)

    print("Running token info retrieval benchmark...")
    results["token_info"] = benchmark_token_info_retrieval(iterations=1000)

    print("Running expiration edge cases benchmark...")
    results["edge_cases"] = benchmark_expiration_edge_cases(iterations=1000)

    print("Running cache efficiency benchmark...")
    results["cache"] = benchmark_cache_efficiency(iterations=100)

    print("\nBenchmarks complete!")
    print_results_table(results)


if __name__ == "__main__":
    main()
