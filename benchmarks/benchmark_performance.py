"""
Performance benchmarks for Zenith Analyser.
"""

import json
import sys
import time
import timeit
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zenith_analyser import ASTUnparser, Lexer, Parser, ZenithAnalyser


class PerformanceBenchmark:
    """Benchmark suite for Zenith Analyser performance."""

    def __init__(self):
        """Initialize benchmark suite."""
        self.results = {}
        self.setup_test_data()

    def setup_test_data(self):
        """Setup test data for benchmarks."""
        # Small test case
        self.small_code = """
law small:
    start_date:2024-01-01 at 09:00
    period:1.0
    Event:
        A:"Event A"
    GROUP:(A 1.0^0)
end_law
"""

        # Medium test case
        self.medium_code = """
target medium:
    key:"Test project"
    dictionnary:
        ev1:"Event 1"
        ev2:"Event 2"
        ev3:"Event 3"

    law medium_law:
        start_date:2024-01-01 at 09:00
        period:8.0
        Event:
            A[ev1]:"Morning work"
            B[ev2]:"Afternoon work"
            C[ev3]:"Evening work"
        GROUP:(A 3.0^1.0 - B 3.0^1.0 - C 2.0^0)
    end_law
end_target
"""

        # Large test case (complex hierarchy)
        self.large_code = self._generate_large_test_case()

    def _generate_large_test_case(self, num_laws=100, events_per_law=10):
        """Generate a large test case for performance testing."""
        code_lines = [
            "target large_project:",
            '    key:"Large Performance Test"',
            "    dictionnary:",
        ]

        # Add dictionary entries
        for i in range(50):
            code_lines.append(f'        ev{i}:"Event {i}"')

        code_lines.append("")

        # Add multiple laws
        for i in range(num_laws):
            law_lines = [
                f"    law law_{i}:",
                f"        start_date:2024-01-{(i % 30)+1:02d} at 09:00",
                "        period:8.0",
                "        Event:",
            ]

            # Add events
            for j in range(events_per_law):
                event_num = (i * events_per_law + j) % 50
                law_lines.append(
                    f'            E{j}[ev{event_num}]:"Description {i}_{j}"'
                )

            law_lines.append("        GROUP:(")

            # Add group events
            group_parts = []
            for j in range(events_per_law):
                duration = 45 if j < events_per_law - 1 else 30
                dispersal = 15 if j < events_per_law - 1 else 0
                group_parts.append(f"E{j} {duration}^{dispersal}")

            law_lines.append(f"            {' - '.join(group_parts)}")
            law_lines.append("        )")
            law_lines.append("    end_law")
            law_lines.append("")

            code_lines.extend(law_lines)

        code_lines.append("end_target")
        return "\n".join(code_lines)

    def benchmark_lexer(self):
        """Benchmark lexer performance."""
        print("\n" + "=" * 60)
        print("LEXER PERFORMANCE BENCHMARK")
        print("=" * 60)

        results = {}

        for size, code in [
            ("Small", self.small_code),
            ("Medium", self.medium_code),
            ("Large", self.large_code),
        ]:
            print(f"\nTesting {size} code ({len(code):,} chars)...")

            # Time tokenization
            start_time = time.time()
            lexer = Lexer(code)
            tokens = lexer.tokenise()
            tokenization_time = time.time() - start_time

            results[size] = {
                "code_size_chars": len(code),
                "token_count": len(tokens),
                "tokenization_time_seconds": tokenization_time,
                "tokens_per_second": (
                    len(tokens) / tokenization_time if tokenization_time > 0 else 0
                ),
                "chars_per_second": (
                    len(code) / tokenization_time if tokenization_time > 0 else 0
                ),
            }

            print(f"  Tokens: {len(tokens):,}")
            print(f"  Time: {tokenization_time:.3f}s")
            print(f"  Speed: {results[size]['tokens_per_second']:,.0f} tokens/s")

        self.results["lexer"] = results
        return results

    def benchmark_parser(self):
        """Benchmark parser performance."""
        print("\n" + "=" * 60)
        print("PARSER PERFORMANCE BENCHMARK")
        print("=" * 60)

        results = {}

        for size, code in [
            ("Small", self.small_code),
            ("Medium", self.medium_code),
            ("Large", self.large_code),
        ]:
            print(f"\nTesting {size} code...")

            # Tokenize first
            lexer = Lexer(code)
            tokens = lexer.tokenise()

            # Time parsing
            start_time = time.time()
            parser = Parser(tokens)
            ast, errors = parser.parse()
            parsing_time = time.time() - start_time

            # Get AST stats
            ast_stats = parser.get_ast_summary(ast)

            results[size] = {
                "token_count": len(tokens),
                "parsing_time_seconds": parsing_time,
                "has_errors": len(errors) > 0,
                "ast_stats": ast_stats,
                "tokens_per_second": (
                    len(tokens) / parsing_time if parsing_time > 0 else 0
                ),
            }

            print(f"  Parse time: {parsing_time:.3f}s")
            print(
                f"  AST size: {ast_stats['total_laws']} laws, {ast_stats['total_targets']} targets"
            )
            print(f"  Speed: {results[size]['tokens_per_second']:,.0f} tokens/s")

        self.results["parser"] = results
        return results

    def benchmark_zenith_analyser(self):
        """Benchmark complete ZenithAnalyser performance."""
        print("\n" + "=" * 60)
        print("ZENITH ANALYSER PERFORMANCE BENCHMARK")
        print("=" * 60)

        results = {}

        for size, code in [
            ("Small", self.small_code),
            ("Medium", self.medium_code),
            ("Large", self.large_code),
        ]:
            print(f"\nTesting {size} code...")

            # Time complete analysis
            start_time = time.time()
            analyser = ZenithAnalyser(code)
            initialization_time = time.time() - start_time

            # Time law analysis
            law_names = analyser.law_analyser.get_law_names()
            law_analysis_times = []

            for law_name in law_names[:10]:  # Analyze first 10 laws
                start_time = time.time()
                analyser.law_description(law_name)
                law_analysis_times.append(time.time() - start_time)

            avg_law_analysis = (
                sum(law_analysis_times) / len(law_analysis_times)
                if law_analysis_times
                else 0
            )

            # Time corpus analysis
            start_time = time.time()
            corpus_analysis = analyser.analyze_corpus()
            corpus_analysis_time = time.time() - start_time

            results[size] = {
                "initialization_time_seconds": initialization_time,
                "law_count": len(law_names),
                "avg_law_analysis_time_seconds": avg_law_analysis,
                "corpus_analysis_time_seconds": corpus_analysis_time,
                "total_events": corpus_analysis["corpus_statistics"]["total_events"],
            }

            print(f"  Initialization: {initialization_time:.3f}s")
            print(f"  Laws: {len(law_names)}")
            print(f"  Avg law analysis: {avg_law_analysis:.3f}s")
            print(f"  Corpus analysis: {corpus_analysis_time:.3f}s")

        self.results["zenith_analyser"] = results
        return results

    def benchmark_memory_usage(self):
        """Benchmark memory usage."""
        print("\n" + "=" * 60)
        print("MEMORY USAGE BENCHMARK")
        print("=" * 60)

        try:
            import gc
            import tracemalloc
        except ImportError:
            print("tracemalloc not available. Skipping memory benchmark.")
            return {}

        results = {}

        for size, code in [("Small", self.small_code), ("Medium", self.medium_code)]:
            print(f"\nTesting {size} code...")

            # Force garbage collection
            gc.collect()

            # Start tracking
            tracemalloc.start()

            # Create analyser
            snapshot1 = tracemalloc.take_snapshot()
            analyser = ZenithAnalyser(code)
            snapshot2 = tracemalloc.take_snapshot()

            # Analyze a law
            law_names = analyser.law_analyser.get_law_names()
            if law_names:
                analyser.law_description(law_names[0])

            snapshot3 = tracemalloc.take_snapshot()

            # Calculate memory usage
            stats_init = snapshot2.compare_to(snapshot1, "lineno")
            stats_analysis = snapshot3.compare_to(snapshot2, "lineno")

            total_init = sum(
                stat.size_diff for stat in stats_init if stat.size_diff > 0
            )
            total_analysis = sum(
                stat.size_diff for stat in stats_analysis if stat.size_diff > 0
            )

            results[size] = {
                "initialization_memory_kb": total_init / 1024,
                "analysis_memory_kb": total_analysis / 1024,
                "total_memory_kb": (total_init + total_analysis) / 1024,
            }

            print(f"  Init memory: {results[size]['initialization_memory_kb']:.1f} KB")
            print(f"  Analysis memory: {results[size]['analysis_memory_kb']:.1f} KB")
            print(f"  Total memory: {results[size]['total_memory_kb']:.1f} KB")

            tracemalloc.stop()

        self.results["memory"] = results
        return results

    def benchmark_unparser(self):
        """Benchmark AST unparser performance."""
        print("\n" + "=" * 60)
        print("UNPARSER PERFORMANCE BENCHMARK")
        print("=" * 60)

        results = {}

        for size, code in [
            ("Small", self.small_code),
            ("Medium", self.medium_code),
            ("Large", self.large_code),
        ]:
            print(f"\nTesting {size} code...")

            # Create analyser and get AST
            analyser = ZenithAnalyser(code)

            # Time unparsing
            start_time = time.time()
            unparser = ASTUnparser(analyser.ast)
            unparsed = unparser.unparse()
            unparsing_time = time.time() - start_time

            # Get stats
            stats = unparser.get_unparse_stats()

            results[size] = {
                "unparsing_time_seconds": unparsing_time,
                "unparsed_length": len(unparsed),
                "valid_structure": stats["valid_structure"],
                "lines_per_second": (
                    stats["total_lines"] / unparsing_time if unparsing_time > 0 else 0
                ),
            }

            print(f"  Unparse time: {unparsing_time:.3f}s")
            print(f"  Unparsed length: {len(unparsed):,} chars")
            print(f"  Valid structure: {stats['valid_structure']}")
            print(f"  Speed: {results[size]['lines_per_second']:,.0f} lines/s")

        self.results["unparser"] = results
        return results

    def benchmark_concurrent_analysis(self):
        """Benchmark concurrent analysis performance."""
        print("\n" + "=" * 60)
        print("CONCURRENT ANALYSIS BENCHMARK")
        print("=" * 60)

        try:
            import concurrent.futures
        except ImportError:
            print("concurrent.futures not available. Skipping concurrent benchmark.")
            return {}

        # Test with medium code
        code = self.medium_code
        num_concurrent = 10

        print(f"\nTesting {num_concurrent} concurrent analyses...")

        # Sequential analysis
        start_time = time.time()
        for _ in range(num_concurrent):
            analyser = ZenithAnalyser(code)
            analyser.analyze_corpus()
        sequential_time = time.time() - start_time

        # Concurrent analysis
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for _ in range(num_concurrent):
                future = executor.submit(lambda: ZenithAnalyser(code).analyze_corpus())
                futures.append(future)

            # Wait for all to complete
            concurrent.futures.wait(futures)
        concurrent_time = time.time() - start_time

        results = {
            "sequential_time_seconds": sequential_time,
            "concurrent_time_seconds": concurrent_time,
            "speedup": sequential_time / concurrent_time if concurrent_time > 0 else 0,
            "num_concurrent": num_concurrent,
        }

        print(f"  Sequential time: {sequential_time:.3f}s")
        print(f"  Concurrent time: {concurrent_time:.3f}s")
        print(f"  Speedup: {results['speedup']:.2f}x")

        self.results["concurrent"] = results
        return results

    def run_all_benchmarks(self):
        """Run all benchmarks."""
        print("🚀 ZENITH ANALYSER PERFORMANCE BENCHMARKS")
        print("=" * 60)

        self.benchmark_lexer()
        self.benchmark_parser()
        self.benchmark_zenith_analyser()
        self.benchmark_memory_usage()
        self.benchmark_unparser()
        self.benchmark_concurrent_analysis()

        # Generate summary
        self.generate_summary()

        # Save results
        self.save_results()

        return self.results

    def generate_summary(self):
        """Generate benchmark summary."""
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)

        if not self.results:
            print("No benchmark results available.")
            return

        # Overall performance metrics
        print("\n📊 Overall Performance:")

        # Lexer performance
        if "lexer" in self.results:
            lexer_large = self.results["lexer"].get("Large", {})
            if lexer_large:
                print(
                    f"  Lexer: {lexer_large.get('tokens_per_second', 0):,.0f} tokens/s"
                )

        # Parser performance
        if "parser" in self.results:
            parser_large = self.results["parser"].get("Large", {})
            if parser_large:
                print(
                    f"  Parser: {parser_large.get('tokens_per_second', 0):,.0f} tokens/s"
                )

        # Zenith Analyser performance
        if "zenith_analyser" in self.results:
            za_large = self.results["zenith_analyser"].get("Large", {})
            if za_large:
                laws_per_second = (
                    1 / za_large.get("avg_law_analysis_time_seconds", 1)
                    if za_large.get("avg_law_analysis_time_seconds", 0) > 0
                    else 0
                )
                print(f"  Law analysis: {laws_per_second:.1f} laws/s")

        # Memory usage
        if "memory" in self.results:
            memory_medium = self.results["memory"].get("Medium", {})
            if memory_medium:
                print(
                    f"  Memory usage: {memory_medium.get('total_memory_kb', 0):.1f} KB"
                )

        # Scalability analysis
        print("\n📈 Scalability Analysis:")

        # Check how performance scales with size
        sizes = ["Small", "Medium", "Large"]

        for component in ["lexer", "parser", "zenith_analyser"]:
            if component in self.results:
                times = []
                for size in sizes:
                    if size in self.results[component]:
                        time_val = (
                            self.results[component][size].get(
                                "tokenization_time_seconds"
                            )
                            or self.results[component][size].get("parsing_time_seconds")
                            or self.results[component][size].get(
                                "initialization_time_seconds"
                            )
                        )
                        if time_val:
                            times.append((size, time_val))

                if len(times) >= 2:
                    # Calculate scaling factor
                    small_time = times[0][1]
                    large_time = times[-1][1]
                    if small_time > 0:
                        scaling = large_time / small_time
                        print(
                            f"  {component.title()}: {scaling:.1f}x slower for {times[-1][0].lower()} input"
                        )

    def save_results(self, filename="benchmark_results.json"):
        """Save benchmark results to file."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n📁 Results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Could not save results: {e}")

    def compare_with_previous(self, previous_file="previous_benchmark_results.json"):
        """Compare with previous benchmark results."""
        try:
            with open(previous_file, "r", encoding="utf-8") as f:
                previous = json.load(f)

            print("\n" + "=" * 60)
            print("PERFORMANCE COMPARISON WITH PREVIOUS RESULTS")
            print("=" * 60)

            # Compare key metrics
            comparisons = []

            for component in ["lexer", "parser", "zenith_analyser"]:
                if component in self.results and component in previous:
                    current_large = self.results[component].get("Large", {})
                    previous_large = previous[component].get("Large", {})

                    if current_large and previous_large:
                        # Find comparable metric
                        for metric in ["tokens_per_second", "lines_per_second"]:
                            if metric in current_large and metric in previous_large:
                                current_val = current_large[metric]
                                previous_val = previous_large[metric]

                                if previous_val > 0:
                                    change = (
                                        (current_val - previous_val) / previous_val
                                    ) * 100
                                    comparisons.append(
                                        (
                                            component,
                                            metric,
                                            current_val,
                                            previous_val,
                                            change,
                                        )
                                    )

            if comparisons:
                print("\n📊 Performance Changes:")
                for component, metric, current, previous, change in comparisons:
                    direction = "↑" if change > 0 else "↓"
                    print(
                        f"  {component.title()}: {current:,.0f} {metric} ({direction}{abs(change):.1f}%)"
                    )
            else:
                print("\nNo comparable metrics found.")

        except FileNotFoundError:
            print(f"\nPrevious results file not found: {previous_file}")
        except Exception as e:
            print(f"\nCould not compare with previous results: {e}")


def main():
    """Main function to run benchmarks."""
    try:
        # Create benchmark suite
        benchmark = PerformanceBenchmark()

        # Run all benchmarks
        results = benchmark.run_all_benchmarks()

        # Optional: Compare with previous results
        # benchmark.compare_with_previous()

        print("\n" + "=" * 60)
        print("BENCHMARKS COMPLETE 🎉")
        print("=" * 60)

        return results

    except Exception as e:
        print(f"\n❌ Error during benchmarking: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
