 #!/usr/bin/env python3
"""
Zenith Analyser - Code Analysis Script
Analyzes code complexity, metrics, and generates reports.
"""

import ast
import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any
import tabulate

class CodeAnalyzer:
    """Analyzes Python code for complexity and metrics."""
    
    def __init__(self, directory: str = "src"):
        self.directory = Path(directory)
        self.results: Dict[str, Any] = {
            "files": {},
            "summary": {},
            "issues": []
        }
    
    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a single Python file."""
        metrics = {
            "filename": str(filepath),
            "lines": 0,
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "complexity": 0,
            "docstrings": 0,
            "comments": 0
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                metrics["lines"] = len(content.splitlines())
                
                # Count comments and docstrings
                lines = content.splitlines()
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        metrics["comments"] += 1
                    elif '"""' in line or "'''" in line:
                        metrics["docstrings"] += 1
                
                # Parse AST for more detailed analysis
                tree = ast.parse(content)
                
                # Count functions and classes
                metrics["functions"] = len([node for node in ast.walk(tree) 
                                          if isinstance(node, ast.FunctionDef)])
                metrics["classes"] = len([node for node in ast.walk(tree) 
                                        if isinstance(node, ast.ClassDef)])
                metrics["imports"] = len([node for node in ast.walk(tree) 
                                         if isinstance(node, ast.Import) 
                                         or isinstance(node, ast.ImportFrom)])
                
                # Calculate cyclomatic complexity (simplified)
                metrics["complexity"] = self.calculate_complexity(tree)
                
        except (SyntaxError, UnicodeDecodeError) as e:
            self.results["issues"].append({
                "file": str(filepath),
                "issue": f"Parse error: {str(e)}",
                "severity": "error"
            })
        
        return metrics
    
    def calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                               ast.Try, ast.ExceptHandler, ast.Assert)):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def analyze_directory(self) -> Dict[str, Any]:
        """Analyze all Python files in directory."""
        python_files = list(self.directory.rglob("*.py"))
        
        if not python_files:
            print(f"No Python files found in {self.directory}")
            return self.results
        
        print(f"Analyzing {len(python_files)} Python files...")
        
        for filepath in python_files:
            relative_path = filepath.relative_to(self.directory.parent)
            metrics = self.analyze_file(filepath)
            self.results["files"][str(relative_path)] = metrics
        
        # Calculate summary statistics
        self._calculate_summary()
        
        return self.results
    
    def _calculate_summary(self) -> None:
        """Calculate summary statistics."""
        files = list(self.results["files"].values())
        
        if not files:
            return
        
        self.results["summary"] = {
            "total_files": len(files),
            "total_lines": sum(f["lines"] for f in files),
            "total_functions": sum(f["functions"] for f in files),
            "total_classes": sum(f["classes"] for f in files),
            "average_complexity": sum(f["complexity"] for f in files) / len(files),
            "files_with_issues": len(self.results["issues"]),
            "lines_per_function": sum(f["lines"] for f in files) / max(sum(f["functions"] for f in files), 1),
            "comment_ratio": (sum(f["comments"] for f in files) / sum(f["lines"] for f in files)) * 100
        }
    
    def print_report(self, output_format: str = "table") -> None:
        """Print analysis report."""
        if output_format == "json":
            print(json.dumps(self.results, indent=2))
            return
        
        # Print summary
        print("\n" + "="*60)
        print("CODE ANALYSIS SUMMARY")
        print("="*60)
        
        summary = self.results["summary"]
        summary_data = [
            ["Total Files", summary["total_files"]],
            ["Total Lines", summary["total_lines"]],
            ["Total Functions", summary["total_functions"]],
            ["Total Classes", summary["total_classes"]],
            ["Average Complexity", f"{summary['average_complexity']:.2f}"],
            ["Lines per Function", f"{summary['lines_per_function']:.2f}"],
            ["Comment Ratio", f"{summary['comment_ratio']:.2f}%"],
            ["Files with Issues", summary["files_with_issues"]]
        ]
        
        print(tabulate.tabulate(summary_data, tablefmt="grid"))
        
        # Print file details
        if output_format == "detailed":
            print("\n" + "="*60)
            print("FILE DETAILS")
            print("="*60)
            
            file_data = []
            for filename, metrics in self.results["files"].items():
                file_data.append([
                    os.path.basename(filename),
                    metrics["lines"],
                    metrics["functions"],
                    metrics["classes"],
                    metrics["complexity"],
                    metrics["comments"]
                ])
            
            headers = ["File", "Lines", "Functions", "Classes", "Complexity", "Comments"]
            print(tabulate.tabulate(file_data, headers=headers, tablefmt="grid"))
        
        # Print issues
        if self.results["issues"]:
            print("\n" + "="*60)
            print("ISSUES FOUND")
            print("="*60)
            
            for issue in self.results["issues"]:
                print(f"[{issue['severity'].upper()}] {issue['file']}: {issue['issue']}")
        
        # Recommendations
        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)
        
        if summary["average_complexity"] > 10:
            print("⚠️  High complexity detected. Consider refactoring complex functions.")
        
        if summary["comment_ratio"] < 10:
            print("⚠️  Low comment ratio. Consider adding more documentation.")
        
        if summary["lines_per_function"] > 50:
            print("⚠️  Long functions detected. Consider breaking them down.")
        
        if not self.results["issues"]:
            print("✅ Code quality looks good!")

def analyze_test_coverage():
    """Analyze test coverage."""
    import coverage
    
    cov = coverage.Coverage()
    cov.load()
    
    print("\n" + "="*60)
    print("TEST COVERAGE ANALYSIS")
    print("="*60)
    
    # Get coverage report
    cov.report(show_missing=True)
    
    # Get detailed file coverage
    data = cov.get_data()
    covered_files = data.measured_files()
    
    if covered_files:
        print(f"\nCovered files: {len(covered_files)}")
        
        # Analyze coverage by file
        coverage_by_file = []
        for file in covered_files:
            analysis = cov.analysis2(file)
            if analysis:
                total_lines = len(analysis[1])
                excluded = len(analysis[2])
                missing = len(analysis[3])
                executed = total_lines - missing - excluded
                coverage_pct = (executed / (total_lines - excluded)) * 100 if (total_lines - excluded) > 0 else 0
                
                coverage_by_file.append({
                    "file": os.path.basename(file),
                    "coverage": coverage_pct,
                    "executed": executed,
                    "missing": missing
                })
        
        # Sort by coverage
        coverage_by_file.sort(key=lambda x: x["coverage"])
        
        print("\nLowest coverage files:")
        for file_info in coverage_by_file[:5]:
            print(f"  {file_info['file']}: {file_info['coverage']:.1f}% "
                  f"({file_info['missing']} lines missing)")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze Zenith Analyser code")
    parser.add_argument("--format", choices=["table", "json", "detailed"], 
                       default="table", help="Output format")
    parser.add_argument("--directory", default="src", help="Directory to analyze")
    parser.add_argument("--coverage", action="store_true", 
                       help="Include test coverage analysis")
    
    args = parser.parse_args()
    
    # Analyze source code
    analyzer = CodeAnalyzer(args.directory)
    results = analyzer.analyze_directory()
    analyzer.print_report(args.format)
    
    # Analyze test coverage if requested
    if args.coverage:
        try:
            analyze_test_coverage()
        except Exception as e:
            print(f"\n⚠️  Coverage analysis failed: {e}")
    
    # Exit with error code if issues found
    if results["issues"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
