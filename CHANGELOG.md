# Changelog

All notable changes to Zenith Analyser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Zenith-Analyser v1.1.1


## [1.1.1] - 2026-02-11

This release brings major enhancements in temporal modelling, calendar integration, and timezone handling, making the library more robust and aligned with real-world planning workflows while staying faithful to Chrononomy principles.

### Added

- **Support for simultaneity modelling**  
  A relationship operators is now fully supported inside `GROUP` blocks:  
  - `|` for **simultaneity** (events must start and end at exactly the same instants)  
  Example syntax:
  GROUP ParallelTasks
 (MorningMeeting | Briefing)


- **Native support for .ics calendar file parsing**  
New function `load_ics(path: str)` directly imports standard iCalendar (.ics) files and converts them into the internal Zenith corpus format.  
Automatically extracts: event names (summary), start/end times, and computes durations.

- **Timezone-aware event normalization using zoneinfo**  
All datetimes from ICS files are now properly converted and normalized to **UTC** (stored as naive datetimes):  
- Events with explicit TZID → correctly shifted to UTC using `zoneinfo`  
- Floating/naive events (no TZID) → assumed to be in UTC (standard convention)  
This guarantees consistent, offset-free calculations for chronocoherence, chronodispersal, durations, and temporal laws.

### Improved

- **Better internal datetime normalization**  
Unified and more reliable handling of both aware and naive datetimes throughout the pipeline. All internal dates are now consistently stored as naive UTC-equivalent datetimes, eliminating previous inconsistencies when importing events from different timezones.

- **Enhanced event structure compatibility with Chrononomy principles**  
Event objects are now richer and include:  
- Original start/end times  
- Computed duration  
- Chronocoherence / chronodispersal flags  
Full compatibility with core chrononomy concepts: time usefulness vs dispersion, strict sequencing, and now true concurrency via `=` and `>` operators.

### Example usage (v1.1.1)

```python
import zenith_analyser as zn

# Import calendar with proper timezone → UTC normalization
corpus = zn.load_ics("planning_bujumbura.ics")

# Analyze and simulate over a period
analyser = zn.ZenithAnalyser(corpus)
result = analyser.period_description(
  method="population",
  key=0,
  start="2025-01-01 00:00",
  end="2030-12-31 23:59"
)
simulations = result["simulation"]

# Export the discovered temporal laws (including new simultaneity operators)
code_law = zn.export_zenith(simulations=simulations)
with open("zenith_laws_v1.1.1.zth", "w", encoding="utf-8") as f:
  f.write(code_law)
```

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