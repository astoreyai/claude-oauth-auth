# Performance Benchmarks

This directory contains comprehensive performance benchmarks and load testing for the `claude-oauth-auth` package.

## Overview

The benchmarks measure various performance aspects of the authentication system:

1. **Credential Discovery** - Speed of finding credentials from different sources
2. **Client Initialization** - Overhead of creating ClaudeClient instances
3. **Concurrent Usage** - Thread safety and parallel performance
4. **OAuth Operations** - Token validation and file parsing performance
5. **Load Testing** - Stress testing and resource usage

## Running Benchmarks

### Prerequisites

Install benchmark dependencies:

```bash
pip install pytest-benchmark memory_profiler psutil
```

### Run All Benchmarks

```bash
# Run all benchmark scripts
python benchmarks/bench_discovery.py
python benchmarks/bench_init.py
python benchmarks/bench_concurrent.py
python benchmarks/bench_oauth.py
python benchmarks/load_test.py

# Run pytest-benchmark tests
pytest tests/test_performance.py --benchmark-only
```

### Individual Benchmarks

```bash
# Credential discovery benchmark
python benchmarks/bench_discovery.py

# Client initialization benchmark
python benchmarks/bench_init.py

# Concurrent usage benchmark
python benchmarks/bench_concurrent.py

# OAuth token operations
python benchmarks/bench_oauth.py

# Load testing
python benchmarks/load_test.py
```

## Benchmark Scripts

### bench_discovery.py
Measures credential discovery performance:
- OAuth credentials discovery time
- API key discovery time
- Config file parsing time
- Cold start vs warm start (cached)
- Comparison table of all sources

### bench_init.py
Measures client initialization performance:
- ClaudeClient creation time
- Memory usage during initialization
- Comparison with raw Anthropic client
- Different credential source overhead

### bench_concurrent.py
Tests thread safety and concurrent performance:
- Multiple threads using same client
- Multiple clients in parallel
- Throughput and latency measurements
- Lock contention analysis

### bench_oauth.py
Measures OAuth-specific operations:
- Token validation speed
- Expiration checking performance
- Credential file parsing
- Thread-safe caching performance

### load_test.py
Stress testing and resource monitoring:
- High request volume simulation
- Memory leak detection
- Resource cleanup verification
- Error handling under stress

### test_performance.py
Integration with pytest-benchmark:
- Regression testing
- Performance baselines
- Automated benchmarking in CI

## Results

See [RESULTS.md](RESULTS.md) for detailed benchmark results, performance analysis, and recommendations.

## System Specifications

Benchmarks were run on:
- OS: Linux 6.1.0-40-amd64
- Python: 3.11.2
- Date: 2025-10-24

## Performance Targets

Expected performance baselines:
- Credential discovery: < 5ms (cached), < 50ms (uncached)
- Client initialization: < 100ms
- OAuth token validation: < 1ms
- Concurrent throughput: > 100 clients/second

## Continuous Monitoring

Use pytest-benchmark for regression testing:

```bash
# Save baseline
pytest tests/test_performance.py --benchmark-only --benchmark-save=baseline

# Compare against baseline
pytest tests/test_performance.py --benchmark-only --benchmark-compare=baseline
```
