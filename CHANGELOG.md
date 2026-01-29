# Changelog

All notable changes to Zenith Analyser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-30

### Added
- **Advanced Metrics Module**: Comprehensive temporal analysis with new metrics:
  - Sequence complexity scoring
  - Temporal density calculation
  - Rhythm and entropy analysis
  - Pattern detection using optimized Suffix Array algorithm (O(n log n))
- **Visualization System**: Complete plotting capabilities:
  - Duration histograms and pie charts
  - Event timelines and scatter plots
  - Metrics summary visualizations
  - Event frequency analysis
- **Enhanced CLI Interface**: New commands and options:
  - `zenith metrics` for advanced statistical analysis
  - `zenith visualize` for generating visualizations
  - `zenith export` for complete data export
  - `zenith compare` for multi-corpus comparison

- **Corpus Management**: Improved file handling:
  - Support for `.zenith`, `.zth`, and `.znth` extensions
  - Structured corpus loading and validation
- **VS Code Extension Integration**: Documentation and support for the Zenith Time extension

### Changed
- **API Refactoring**: More intuitive module structure:
  - Separated `metrics` module from core analysers
  - Created dedicated `visuals` module for plotting
  - Improved import paths and namespace organization
- **Performance Optimizations**:
  - Pattern detection now uses O(n log n) algorithm instead of O(n²)
  - Memory usage improvements for large corpora
  - Faster AST traversal and validation
- **Documentation Overhaul**: Complete rewrite with:
  - Detailed API documentation for all modules
  - Comprehensive examples section
  - Installation and usage guides
  - CLI command reference

### Fixed
- **Parsing Issues**: 
  - Fixed edge cases in date/time parsing
  - Improved error messages for malformed Zenith code
  - Better handling of nested targets and laws
- **Calculation Bugs**:
  - Corrected duration calculations for complex time formats
  - Fixed metric aggregation across multiple generations
  - Resolved issues with population-level analysis
- **CLI Improvements**:
  - Better argument validation and error handling
  - Consistent output formatting across commands
  - Fixed file path resolution for relative paths

### Security
- **Input Validation**: Enhanced security measures:
  - Stricter parsing of external files
  - Resource limits for large AST processing
  - Sanitization of user-provided data in visualizations
- **Dependency Updates**: Pinned secure versions of all dependencies

---

## [1.0.0] - 2024-01-23

### Added
- **Core Engine**: Complete Zenith language parser and lexer implementation.
- **Analysis Tools**:
    - Temporal analysis supporting chronocoherence and chronodispersal.
    - Law analyser with full event simulation.
    - Target analyser with hierarchical support.
- **Utilities**:
    - AST unparser and manipulation tools.
    - High-precision time conversion utilities.
- **Quality Assurance**:
    - Comprehensive test suite with high coverage.
    - Automated CI/CD pipeline for PyPI publishing and GitHub releases.
    - Detailed documentation and contribution guidelines.

### Security
- Strict input validation for all parsers to prevent malformed data injection.
- Resource limit enforcement during complex AST parsing.
- Overflow-safe time calculations.

---

## Versioning Scheme
- **MAJOR**: Incompatible API changes.
- **MINOR**: New functionality (backwards compatible).
- **PATCH**: Bug fixes (backwards compatible).

## Links
- [GitHub Repository](https://github.com/frasasu/zenith-analyser)
- [Documentation](https://github.com/frasasu/zenith-analyser#readme)
- [PyPI Package](https://pypi.org/project/zenith-analyser/)
- [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=zenith-dev.zenith-time)