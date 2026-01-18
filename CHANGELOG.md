# Changelog

All notable changes to Zenith Analyser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-05-20

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
- [Documentation](https://zenith-analyser.readthedocs.io/)