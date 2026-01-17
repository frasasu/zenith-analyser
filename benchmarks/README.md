# Benchmarks
# Zenith Analyser Benchmarks

This directory contains performance and memory benchmarks for Zenith Analyser.

## 📊 Benchmark Suites

### 1. **benchmark_performance.py** - Performance Benchmarks
- Lexer tokenization speed
- Parser AST construction speed
- Complete analysis performance
- Concurrent processing capabilities
- Unparser performance

### 2. **benchmark_memory.py** - Memory Usage Benchmarks
- Component memory usage (Lexer, Parser, Analyser)
- Memory scaling with input size
- Memory leak detection
- Peak memory usage analysis

## 🚀 Running Benchmarks

### Quick Start
```bash
# Run performance benchmarks
python benchmarks/benchmark_performance.py

# Run memory benchmarks
python benchmarks/benchmark_memory.py
