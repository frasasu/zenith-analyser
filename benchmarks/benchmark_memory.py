 #!/usr/bin/env python3
"""
Memory usage benchmarks for Zenith Analyser.
"""

import sys
import tracemalloc
import gc
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zenith_analyser import ZenithAnalyser, Lexer, Parser, ASTUnparser


class MemoryBenchmark:
    """Memory usage benchmark suite for Zenith Analyser."""
    
    def __init__(self):
        """Initialize memory benchmark suite."""
        self.results = {}
        self.setup_test_data()
    
    def setup_test_data(self):
        """Setup test data for memory benchmarks."""
        # Test cases of different sizes
        self.test_cases = {
            'tiny': self._generate_test_case(1, 2),
            'small': self._generate_test_case(5, 5),
            'medium': self._generate_test_case(20, 10),
            'large': self._generate_test_case(100, 20),
            'huge': self._generate_test_case(500, 30)
        }
    
    def _generate_test_case(self, num_laws, events_per_law):
        """Generate a test case with specified complexity."""
        code_lines = ["target memory_test:", '    key:"Memory Test"', '    dictionnary:']
        
        # Add dictionary entries
        dict_size = min(50, num_laws * events_per_law // 2)
        for i in range(dict_size):
            code_lines.append(f'        ev{i}:"Event {i}"')
        
        code_lines.append("")
        
        # Add laws
        for i in range(num_laws):
            law_lines = [
                f"    law law_{i}:",
                f"        start_date:2024-01-{(i % 30)+1:02d} at 09:00",
                "        period:8.0",
                "        Event:"
            ]
            
            # Add events
            for j in range(events_per_law):
                event_num = (i * events_per_law + j) % dict_size
                law_lines.append(f'            E{j}[ev{event_num}]:"Description {i}_{j}"')
            
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
            
            # Add some targets for hierarchy testing
            if i % 10 == 0 and i > 0:
                law_lines.append("")
                law_lines.append(f"    target sub_target_{i}:")
                law_lines.append('        key:"Sub target"')
                law_lines.append("    end_target")
            
            code_lines.extend(law_lines)
            if i < num_laws - 1:
                code_lines.append("")
        
        code_lines.append("end_target")
        return "\n".join(code_lines)
    
    def benchmark_component_memory(self):
        """Benchmark memory usage of individual components."""
        print("\n" + "=" * 60)
        print("COMPONENT MEMORY USAGE BENCHMARK")
        print("=" * 60)
        
        results = {}
        
        for size_name, code in self.test_cases.items():
            if size_name == 'huge':
                print(f"\nSkipping '{size_name}' due to memory constraints...")
                continue
                
            print(f"\nTesting '{size_name}' ({len(code):,} chars)...")
            
            size_results = {}
            
            # Force garbage collection before each test
            gc.collect()
            
            # 1. Lexer memory
            tracemalloc.start()
            snapshot1 = tracemalloc.take_snapshot()
            lexer = Lexer(code)
            tokens = lexer.tokenise()
            snapshot2 = tracemalloc.take_snapshot()
            lexer_memory = self._calculate_memory_usage(snapshot1, snapshot2)
            tracemalloc.stop()
            
            size_results['lexer'] = {
                'memory_kb': lexer_memory / 1024,
                'token_count': len(tokens),
                'memory_per_token_bytes': lexer_memory / len(tokens) if tokens else 0
            }
            
            # 2. Parser memory
            gc.collect()
            tracemalloc.start()
            snapshot1 = tracemalloc.take_snapshot()
            parser = Parser(tokens)
            ast, errors = parser.parse()
            snapshot2 = tracemalloc.take_snapshot()
            parser_memory = self._calculate_memory_usage(snapshot1, snapshot2)
            tracemalloc.stop()
            
            ast_stats = parser.get_ast_summary(ast) if ast else {}
            size_results['parser'] = {
                'memory_kb': parser_memory / 1024,
                'ast_size': self._estimate_ast_size(ast),
                'has_errors': len(errors) > 0
            }
            
            # 3. ZenithAnalyser memory (full initialization)
            gc.collect()
            tracemalloc.start()
            snapshot1 = tracemalloc.take_snapshot()
            analyser = ZenithAnalyser(code)
            snapshot2 = tracemalloc.take_snapshot()
            analyser_memory = self._calculate_memory_usage(snapshot1, snapshot2)
            tracemalloc.stop()
            
            size_results['zenith_analyser'] = {
                'memory_kb': analyser_memory / 1024,
                'law_count': len(analyser.law_analyser.laws) if analyser else 0,
                'target_count': len(analyser.target_analyser.targets) if analyser else 0
            }
            
            # 4. Analysis memory (performing actual analysis)
            if analyser and analyser.law_analyser.get_law_names():
                gc.collect()
                tracemalloc.start()
                snapshot1 = tracemalloc.take_snapshot()
                law_name = analyser.law_analyser.get_law_names()[0]
                analyser.law_description(law_name)
                snapshot2 = tracemalloc.take_snapshot()
                analysis_memory = self._calculate_memory_usage(snapshot1, snapshot2)
                tracemalloc.stop()
                
                size_results['analysis'] = {
                    'memory_kb': analysis_memory / 1024
                }
            
            # 5. Unparser memory
            if ast:
                gc.collect()
                tracemalloc.start()
                snapshot1 = tracemalloc.take_snapshot()
                unparser = ASTUnparser(ast)
                unparsed = unparser.unparse()
                snapshot2 = tracemalloc.take_snapshot()
                unparser_memory = self._calculate_memory_usage(snapshot1, snapshot2)
                tracemalloc.stop()
                
                size_results['unparser'] = {
                    'memory_kb': unparser_memory / 1024,
                    'unparsed_length': len(unparsed)
                }
            
            results[size_name] = size_results
            
            # Print summary for this size
            print(f"  Lexer: {size_results['lexer']['memory_kb']:.1f} KB")
            print(f"  Parser: {size_results['parser']['memory_kb']:.1f} KB")
            print(f"  ZenithAnalyser: {size_results['zenith_analyser']['memory_kb']:.1f} KB")
            if 'analysis' in size_results:
                print(f"  Analysis: {size_results['analysis']['memory_kb']:.1f} KB")
        
        self.results['component_memory'] = results
        return results
    
    def benchmark_memory_scaling(self):
        """Benchmark how memory usage scales with input size."""
        print("\n" + "=" * 60)
        print("MEMORY SCALING BENCHMARK")
        print("=" * 60)
        
        results = {}
        
        for size_name, code in self.test_cases.items():
            if size_name == 'huge':
                print(f"\nSkipping '{size_name}' due to memory constraints...")
                continue
                
            print(f"\nTesting '{size_name}'...")
            
            # Measure total memory for complete analysis
            gc.collect()
            tracemalloc.start()
            snapshot1 = tracemalloc.take_snapshot()
            
            analyser = ZenithAnalyser(code)
            
            # Perform some analysis
            if analyser.law_analyser.get_law_names():
                analyser.law_description(analyser.law_analyser.get_law_names()[0])
                analyser.analyze_corpus()
            
            snapshot2 = tracemalloc.take_snapshot()
            total_memory = self._calculate_memory_usage(snapshot1, snapshot2)
            tracemalloc.stop()
            
            results[size_name] = {
                'code_size_chars': len(code),
                'total_memory_kb': total_memory / 1024,
                'memory_per_char_bytes': total_memory / len(code) if len(code) > 0 else 0,
                'laws': len(analyser.law_analyser.laws) if analyser else 0,
                'targets': len(analyser.target_analyser.targets) if analyser else 0
            }
            
            print(f"  Code: {len(code):,} chars")
            print(f"  Memory: {total_memory/1024:.1f} KB")
            print(f"  Memory/char: {total_memory/len(code):.2f} bytes" if len(code) > 0 else "  Memory/char: N/A")
            print(f"  Laws: {results[size_name]['laws']}")
        
        # Calculate scaling factors
        sizes = ['tiny', 'small', 'medium', 'large']
        scaling_data = []
        
        for i in range(len(sizes) - 1):
            small = sizes[i]
            large = sizes[i + 1]
            
            if small in results and large in results:
                size_ratio = results[large]['code_size_chars'] / results[small]['code_size_chars']
                memory_ratio = results[large]['total_memory_kb'] / results[small]['total_memory_kb']
                scaling_factor = memory_ratio / size_ratio
                
                scaling_data.append({
                    'from': small,
                    'to': large,
                    'size_increase': size_ratio,
                    'memory_increase': memory_ratio,
                    'scaling_factor': scaling_factor
                })
        
        print("\n📈 Memory Scaling Analysis:")
        for data in scaling_data:
            print(f"  {data['from']} → {data['to']}:")
            print(f"    Size: {data['size_increase']:.1f}x, Memory: {data['memory_increase']:.1f}x")
            print(f"    Scaling: {data['scaling_factor']:.2f} (1.0 = linear)")
        
        self.results['scaling'] = {
            'size_results': results,
            'scaling_analysis': scaling_data
        }
        return results
    
    def benchmark_memory_leaks(self):
        """Test for memory leaks by repeated operations."""
        print("\n" + "=" * 60)
        print("MEMORY LEAK DETECTION")
        print("=" * 60)
        
        # Use medium test case
        code = self.test_cases['medium']
        
        print(f"\nTesting with medium code ({len(code):,} chars)...")
        print("Running 100 iterations of analysis...")
        
        # Track memory over iterations
        memory_readings = []
        
        for iteration in range(100):
            # Force GC before each iteration
            gc.collect()
            
            tracemalloc.start()
            snapshot1 = tracemalloc.take_snapshot()
            
            # Create analyser and perform analysis
            analyser = ZenithAnalyser(code)
            if analyser.law_analyser.get_law_names():
                analyser.law_description(analyser.law_analyser.get_law_names()[0])
            
            snapshot2 = tracemalloc.take_snapshot()
            memory_used = self._calculate_memory_usage(snapshot1, snapshot2)
            tracemalloc.stop()
            
            memory_readings.append(memory_used / 1024)  # Convert to KB
            
            # Clean up explicitly
            del analyser
            
            if iteration % 20 == 0:
                print(f"  Iteration {iteration}: {memory_readings[-1]:.1f} KB")
        
        # Analyze memory readings
        initial_memory = memory_readings[0] if memory_readings else 0
        final_memory = memory_readings[-1] if memory_readings else 0
        max_memory = max(memory_readings) if memory_readings else 0
        avg_memory = sum(memory_readings) / len(memory_readings) if memory_readings else 0
        
        # Check for leaks (significant increase over iterations)
        memory_increase = final_memory - initial_memory
        leak_detected = memory_increase > (initial_memory * 0.1)  # More than 10% increase
        
        results = {
            'iterations': len(memory_readings),
            'initial_memory_kb': initial_memory,
            'final_memory_kb': final_memory,
            'max_memory_kb': max_memory,
            'avg_memory_kb': avg_memory,
            'memory_increase_kb': memory_increase,
            'percent_increase': (memory_increase / initial_memory * 100) if initial_memory > 0 else 0,
            'leak_detected': leak_detected,
            'memory_readings': memory_readings[:10]  # First 10 readings
        }
        
        print(f"\n📊 Memory Leak Analysis:")
        print(f"  Initial: {initial_memory:.1f} KB")
        print(f"  Final: {final_memory:.1f} KB")
        print(f"  Increase: {memory_increase:.1f} KB ({results['percent_increase']:.1f}%)")
        print(f"  Max: {max_memory:.1f} KB")
        print(f"  Average: {avg_memory:.1f} KB")
        
        if leak_detected:
            print(f"  ⚠️  POSSIBLE MEMORY LEAK DETECTED!")
        else:
            print(f"  ✅ No significant memory leak detected")
        
        self.results['leak_detection'] = results
        return results
    
    def benchmark_peak_memory(self):
        """Measure peak memory usage during analysis."""
        print("\n" + "=" * 60)
        print("PEAK MEMORY USAGE BENCHMARK")
        print("=" * 60)
        
        results = {}
        
        # Test with progressively larger inputs
        for size_name in ['tiny', 'small', 'medium', 'large']:
            code = self.test_cases[size_name]
            
            print(f"\nTesting '{size_name}' ({len(code):,} chars)...")
            
            # Clear memory and start tracking
            gc.collect()
            tracemalloc.start()
            
            # Perform analysis that might peak memory
            analyser = ZenithAnalyser(code)
            
            # Analyze all laws (peak usage)
            peak_memory = 0
            for law_name in analyser.law_analyser.get_law_names():
                analyser.law_description(law_name)
                
                # Check current memory
                current_snapshot = tracemalloc.take_snapshot()
                current_memory = sum(stat.size for stat in current_snapshot.statistics('filename'))
                peak_memory = max(peak_memory, current_memory)
            
            # Perform corpus analysis (another potential peak)
            analyser.analyze_corpus()
            final_snapshot = tracemalloc.take_snapshot()
            final_memory = sum(stat.size for stat in final_snapshot.statistics('filename'))
            peak_memory = max(peak_memory, final_memory)
            
            tracemalloc.stop()
            
            results[size_name] = {
                'peak_memory_kb': peak_memory / 1024,
                'final_memory_kb': final_memory / 1024,
                'code_size_chars': len(code),
                'law_count': len(analyser.law_analyser.laws),
                'peak_per_char_bytes': peak_memory / len(code) if len(code) > 0 else 0
            }
            
            print(f"  Peak memory: {peak_memory/1024:.1f} KB")
            print(f"  Final memory: {final_memory/1024:.1f} KB")
            print(f"  Peak/char: {peak_memory/len(code):.2f} bytes" if len(code) > 0 else "  Peak/char: N/A")
        
        # Calculate memory efficiency
        print("\n📈 Peak Memory Efficiency:")
        sizes = list(results.keys())
        
        for i in range(len(sizes) - 1):
            small = sizes[i]
            large = sizes[i + 1]
            
            if small in results and large in results:
                size_ratio = results[large]['code_size_chars'] / results[small]['code_size_chars']
                memory_ratio = results[large]['peak_memory_kb'] / results[small]['peak_memory_kb']
                
                print(f"  {small} → {large}: Size {size_ratio:.1f}x, Memory {memory_ratio:.1f}x")
                print(f"    Efficiency: {size_ratio/memory_ratio:.2f}")
        
        self.results['peak_memory'] = results
        return results
    
    def _calculate_memory_usage(self, snapshot1, snapshot2):
        """Calculate memory usage between two snapshots."""
        stats = snapshot2.compare_to(snapshot1, 'lineno')
        return sum(stat.size_diff for stat in stats if stat.size_diff > 0)
    
    def _estimate_ast_size(self, ast):
        """Estimate the size of an AST."""
        if not ast:
            return 0
        
        def count_nodes(node):
            count = 1
            if isinstance(node, dict):
                for value in node.values():
                    if isinstance(value, (dict, list)):
                        count += count_nodes(value)
                    else:
                        count += 1
            elif isinstance(node, list):
                for item in node:
                    count += count_nodes(item)
            return count
        
        return count_nodes(ast)
    
    def run_all_benchmarks(self):
        """Run all memory benchmarks."""
        print("🧠 ZENITH ANALYSER MEMORY BENCHMARKS")
        print("=" * 60)
        
        self.benchmark_component_memory()
        self.benchmark_memory_scaling()
        self.benchmark_memory_leaks()
        self.benchmark_peak_memory()
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def generate_summary(self):
        """Generate memory benchmark summary."""
        print("\n" + "=" * 60)
        print("MEMORY BENCHMARK SUMMARY")
        print("=" * 60)
        
        if not self.results:
            print("No benchmark results available.")
            return
        
        # Component memory summary
        if 'component_memory' in self.results:
            print("\n📊 Component Memory Usage (Medium test case):")
            medium = self.results['component_memory'].get('medium', {})
            
            for component, data in medium.items():
                if 'memory_kb' in data:
                    print(f"  {component.title()}: {data['memory_kb']:.1f} KB")
        
        # Memory scaling summary
        if 'scaling' in self.results:
            print("\n📈 Memory Scaling:")
            scaling_data = self.results['scaling'].get('scaling_analysis', [])
            for data in scaling_data:
                print(f"  {data['from']} → {data['to']}: {data['scaling_factor']:.2f}x")
        
        # Leak detection summary
        if 'leak_detection' in self.results:
            leak_data = self.results['leak_detection']
            print(f"\n🔍 Memory Leak Detection:")
            print(f"  Leak detected: {'Yes' if leak_data.get('leak_detected') else 'No'}")
            print(f"  Memory increase: {leak_data.get('percent_increase', 0):.1f}%")
        
        # Peak memory summary
        if 'peak_memory' in self.results:
            print("\n🏔️  Peak Memory Usage:")
            for size, data in self.results['peak_memory'].items():
                print(f"  {size}: {data.get('peak_memory_kb', 0):.1f} KB")
    
    def save_results(self, filename="memory_benchmark_results.json"):
        """Save benchmark results to file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n📁 Results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Could not save results: {e}")


def main():
    """Main function to run memory benchmarks."""
    try:
        # Create benchmark suite
        benchmark = MemoryBenchmark()
        
        # Run all benchmarks
        results = benchmark.run_all_benchmarks()
        
        print("\n" + "=" * 60)
        print("MEMORY BENCHMARKS COMPLETE 🎉")
        print("=" * 60)
        
        return results
        
    except MemoryError:
        print("\n❌ Memory error during benchmarking. Consider using smaller test cases.")
        return None
    except Exception as e:
        print(f"\n❌ Error during memory benchmarking: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
