# zenith_analyser
# Zenith Analyser

[![PyPI version](https://badge.fury.io/py/zenith-analyser.svg)](https://pypi.org/project/zenith-analyser/)
[![Python Versions](https://img.shields.io/pypi/pyversions/zenith-analyser.svg)](https://pypi.org/project/zenith-analyser/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI Status](https://github.com/frasasu/zenith-analyser/actions/workflows/ci.yml/badge.svg)](https://github.com/frasasu/zenith-analyser/actions)


A powerful Python library for analyzing structured temporal laws with events, chronocoherence, chronodispersal, and hierarchical targets.

## Features

- **Complete Lexer & Parser**: Full Zenith language syntax support
- **Temporal Analysis**: Analyze laws with events, chronocoherence, and chronodispersal
- **Target Hierarchy**: Navigate through nested targets with inheritance
- **Event Simulation**: Simulate event sequences with temporal constraints
- **Time Conversion**: Convert between Zenith point format (Y.M.D.H.M) and minutes
- **AST Manipulation**: Parse, analyze, and unparse Zenith code
- **Validation**: Comprehensive syntax and semantic validation
- **Extensible**: Easy to extend with custom analyzers

## Installation

### From PyPI

```bash
pip install zenith-analyser

```

# Zenith-Analyser - Complete Documentation

## 📚 Table of Contents
1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [API Documentation](#api-documentation)
4. [CLI Usage](#cli-usage)
5. [Zenith Language Specification](#zenith-language-specification)
6. [Advanced Features](#advanced-features)
7. [Examples](#examples)
8. [Installation](#installation)

---

## Introduction

Zenith-Analyser is a comprehensive time management and temporal analysis library that provides tools for modeling, analyzing, and visualizing temporal structures using the Zenith language. It helps users plan, analyze, and optimize their time allocation across various objectives and activities.

### Key Features
- **Temporal Modeling**: Define laws (temporal sessions) and targets (objectives)
- **Hierarchical Analysis**: Analyze objectives across generations and populations
- **Advanced Metrics**: Calculate complexity, density, rhythm, and entropy metrics
- **Visualization**: Generate comprehensive visualizations of temporal data
- **CLI Interface**: Full command-line interface for analysis workflows

---

## Core Concepts

### 1. Generation & Population

#### Generation
In Zenith, a **generation** refers to the hierarchical level of an objective within a goal system. It expresses the structural depth of an objective, from global intentions to concrete and immediate actions. Each objective belongs to a single generation, allowing precise positioning of its role, degree of specialization, and connection with more general or specific objectives.

#### Population
The **population** represents the set of active and influential objectives at a given moment. Unlike generation, which is a positional concept, population is a contextual concept. It groups objectives from several generations that interact simultaneously and guide decisions, priorities, and time allocation in lived reality.

#### Relationship Between Generation and Population
Generation allows understanding where an objective is located, while population allows understanding with which other objectives it acts. An objective can only belong to one generation, but it always participates in a broader population. In Zenith, this distinction enables coherent temporal analysis by separating the structure of objectives from their actual influence on time dynamics.

### 2. Target (Objective)

#### Definition
A target is a general or specific objective within a time management project framework. It represents a plannable, hierarchical, and analytically exploitable entity.

#### Characteristics
1. **Key**: A unique textual identifier for the target
2. **Dictionary**: List of specific objectives associated with the target
3. **Laws**: Planned sessions for working on target objectives
4. **Sub-targets**: A target can contain other targets for hierarchical structuring

#### Example
```zenith
target programming:
    key: "programming"
    dictionnary:
        d1[d1]: "Software development expertise."
        d2[d1]: "Android and IOS development expertise."
```

### 3. Law (Temporal Session)

#### Definition
A law is a planned session designed to achieve one or more specific objectives of a target. It allows quantifying and structuring time dedicated to each objective.

#### Characteristics
1. **start_date**: Date and time when the session begins
2. **period**: Total planned duration for the session
3. **Event**: List of actions or learnings, referenced via the target's dictionary
4. **GROUP**: Notation (A subscript^superscript) where:
   - subscript represents chronocoherence duration (useful and directly contributive time)
   - superscript represents chronodispersal duration (used but not directly contributive time)

#### Example
```zenith
law a2025_12_25_15_45:
    start_date:2025-12-25 at 15:45
    period:30
    Event:
        A[d1]: "Learning pandas."
    GROUP:(A 30^0)
```

### 4. Chronocoherence & Chronodispersal

- **Chronocoherence**: Time that is useful and directly contributive to objectives
- **Chronodispersal**: Time that is used but not directly contributive to objectives

---

## API Documentation

### 1. LawAnalyser

#### Role
Manipulates temporal laws - planning structures that define events, their durations (chronocoherence/chronodispersal), and their relationships (order, simultaneity, exclusive/inclusive choices).

#### Methods

##### `get_law_names()`
**Parameters**: None  
**Returns**: `List[str]` - names of all defined laws  
**Interpretation**: Provides a list of all available temporal programs. Useful for visualizing planning options before deciding which one to use.

```python
names = analyser.law_analyser.get_law_names()
print(names)
# Returns: ['DailyWork', 'WeeklyPlanning', 'ResearchSessions']
```

##### `get_law(name)`
**Parameters**: `name (str)` - law name  
**Returns**: `dict` - complete law structure  
**Interpretation**: Allows reading the time exploitation plan in detail before simulation.

```python
law = analyser.law_analyser.get_law("DailyWork")
print(law.keys())
# Keys returned:
# - name: law name
# - date: start date
# - time: start time
# - period: total planned duration
# - dictionnary: internal dictionary of events
# - group: list of events with durations (chronocoherence^chronodispersal)
# - source_node: internal AST representation of the law

# Access events:
for event_name, event_data in law['dictionnary'].items():
    print(event_name, event_data)
```

##### `validate_law(name)`
**Parameters**: `name (str)` - law name  
**Returns**: `List[str]` - detected errors (empty if valid)  
**Interpretation**: Verifies that the law is temporally coherent.

```python
errors = analyser.law_analyser.validate_law("DailyWork")
if errors:
    print("Errors detected:", errors)
else:
    print("Valid law!")
# Returns: [] or ['Event A overlaps Event B', 'Total period exceeds planned duration']
```

### 2. TargetAnalyser

#### Role
Manages objectives (targets), their hierarchy (generations), and their active context (populations). Allows visualizing how time is invested in different objectives.

#### Methods

##### `get_targets_by_generation(generation)`
**Parameters**: `generation (int)` - hierarchical level of objectives  
**Returns**: `List[dict]` - objectives of this generation  
**Interpretation**: Isolates objectives at the same level to understand where time is concentrated.

```python
targets_gen1 = analyser.target_analyser.get_targets_by_generation(1)
for t in targets_gen1:
    print(t['name'])
```

##### `extract_laws_for_target(target_name)`
**Parameters**: `target_name (str)` - objective name  
**Returns**: `dict` - laws directly and indirectly linked to the objective  
**Interpretation**: Shows the temporal field mobilized to achieve an objective.

```python
laws = analyser.target_analyser.extract_laws_for_target("MyTarget")
for law_name, law_data in laws.items():
    print(law_name, law_data['group'])
```

##### `extract_laws_population(population)`
**Parameters**: `population (int)` - cumulative depth of generations  
**Returns**: `dict` - set of active laws up to this population  
**Interpretation**: Simulates the lived temporal reality where multiple objectives interact.

```python
population_laws = analyser.target_analyser.extract_laws_population(2)
print(list(population_laws.keys()))
```

### 3. ZenithAnalyser

#### Role
Simulates the actual exploitation of time. Combines laws, objectives, and populations to produce concrete readings on temporal coherence, dispersion, and efficiency.

#### Methods

##### `law_description(name, population=0)`
**Parameters**:
- `name (str)` - law name
- `population (int)` - population context

**Returns**: `dict` - complete description of the simulated law

```python
desc = analyser.law_description("DailyWork")
print(desc.keys())
# Main dictionary keys:
# - name, start_date, start_time, start_datetime
# - period, period_minutes, end_datetime
# - sum_duration, coherence, dispersal
# - event_count, unique_event_count
# - simulation, event_metrics
# - dispersion_metrics, mean_coherence, mean_dispersal
# - events

# Mini-simulation:
for event in desc['simulation']:
    print(event['event_name'], event['start'], event['end'], event['duration_minutes'])
```

##### `target_description(target_name)`
**Parameters**: `target_name (str)` - objective name  
**Returns**: `dict` - complete temporal synthesis of the objective  
**Interpretation**: Shows the time actually invested per objective.

```python
target_desc = analyser.target_description("MyTarget")
print(target_desc['events'])
```

##### `population_description(population=-1)`
**Parameters**: `population (int)` - population to analyze (-1 = maximum)  
**Returns**: `dict` - complete population simulation  
**Interpretation**: Represents cumulative temporal load.

```python
pop = analyser.population_description(population=2)
print(pop['sum_duration'])
```

##### `analyze_corpus()`
**Parameters**: None  
**Returns**: `dict` - global corpus diagnostic  
**Interpretation**: Provides a complete time management dashboard.

```python
corpus = analyser.analyze_corpus()
print(corpus['corpus_statistics'])
# Main keys returned:
# - corpus_statistics, ast_summary, laws, targets, validation
```
# ⏱️ Zenith Point System

## Time Conversion Functions

### `point_to_minutes(point: str) → int`
Converts Zenith point notation to total minutes.

**Format:** `minutes.hours.days.months.years` (dot-separated)
**Multipliers:** 1 minute = 1 min, 1 hour = 60 min, 1 day = 1440 min (24h), 1 month = 43200 min (30d), 1 year = 518400 min (360d)

```python
point_to_minutes("30")      # → 30 minutes
point_to_minutes("1.0")     # → 60 minutes (1 hour)
point_to_minutes("0.1.30")  # → 90 minutes (1h30)
point_to_minutes("30.0.0")  # → 43200 minutes (30 days)
point_to_minutes("-1.30")   # → -90 minutes
```

### `minutes_to_point(total_minutes: int | float) → str`
Converts total minutes back to Zenith point notation.

```python
minutes_to_point(30)    # → "30"
minutes_to_point(60)    # → "1.0"
minutes_to_point(90)    # → "0.1.30"
minutes_to_point(150)   # → "0.2.30" (2h30)
minutes_to_point(1440)  # → "0.0.1" (1 day)
```

## Quick Reference

| Minutes | Point Format | Meaning |
|---------|--------------|---------|
| 30 | `"30"` | 30 minutes |
| 60 | `"1.0"` | 1 hour |
| 90 | `"0.1.30"` | 1 hour 30 minutes |
| 150 | `"0.2.30"` | 2 hours 30 minutes |
| 1440 | `"0.0.1"` | 1 day |
| 43200 | `"30.0.0"` | 30 days |

## Common Usage

```python
# Calculate total duration
total = point_to_minutes("2.30") + point_to_minutes("1.15")  # 225 minutes
formatted = minutes_to_point(total)  # "0.3.45" (3h45)

# Convert for display
duration = point_to_minutes("1.45")  # 105 minutes
hours = duration // 60               # 1
minutes = duration % 60              # 45
```

## 🛠️ Development Tools

### Zenith Time - VS Code Extension

To streamline the creation and editing of `.zenith` ,`.zth` et `.znth`files, we've developed a dedicated VS Code extension available on the [Visual Studio Code Marketplace](https://marketplace.visualstudio.com/items?itemName=zenith-dev.zenith-time).

#### ✨ Key Features

**Syntax Highlighting**
- Full language support for Zenith Time syntax
- Color-coded elements: targets, laws, events, dictionaries, dates, and operators
- Clear visual distinction between different language constructs

**Smart Code Snippets**
- `target` - Complete target block structure with dictionary
- `law` - Law block with event and group configurations
- `event` - Quick event declaration
- `dict` - Dictionary definition template
- `mevents` - Multiple events with group configuration

**Enhanced Productivity**
- **Automatic bracket/parenthesis/quotes completion**
- **Code folding** for target and law blocks
- **Custom file icons** for `.zenith`, `.znth`, `.zth` extensions
- **Theme-aware icons** that adapt to light/dark themes

#### 🚀 Installation

**Method 1: VS Code Marketplace**
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "Zenith Time"
4. Click Install

**Method 2: Command Line**
```bash
code --install-extension zenith-dev.zenith-time
```

#### 🎯 Usage Examples

The extension automatically activates when you open `.zenith` files. Try these shortcuts:

1. **Create a target block**: Type `target` and press Tab
2. **Add a law**: Type `law` and press Tab
3. **Quick events**: Type `event` or `mevents`

#### 🛠️ Development Features

- **Language Server Protocol ready** structure
- **Scalable syntax definitions** for future language updates
- **Cross-platform compatibility** (Windows, macOS, Linux)
- **Regular updates** with new features and improvements

#### 📁 File Support
- `.zenith` - Primary Zenith Time files
- `.znth` - Alternative extension
- `.zth` - Short extension format

The Zenith Time extension significantly improves development workflow by providing intelligent code completion, syntax validation, and visual enhancements specifically tailored for the Zenith Time language ecosystem.

#### 🔗 Integration with Zenith Analyser
The extension works seamlessly with `zenith-analyser` projects, ensuring consistent syntax highlighting and code structure validation across your development environment.

*Note: The extension focuses on front-end syntax support; actual parsing and validation are handled by the zenith-analyser core.*
---

## CLI Usage

### Installation
```bash
# Installation via pip
pip install zenith-analyser

# Or from source
git clone <repository>
cd zenith-analyser
pip install -e .
```

### Available Commands

#### `zenith analyze` - Main Analysis
Analyzes a Zenith corpus and produces a structured report.

```bash
# Basic analysis
zenith analyze corpus.zenith --format json --pretty

# Analyze specific law
zenith analyze corpus.zenith --law "TemporalLaw" --format text

# Analyze from stdin
cat corpus.zenith | zenith analyze -
```

#### `zenith validate` - Syntax Validation
Validates Zenith file syntax.

```bash
# Basic validation
zenith validate corpus.zenith

# Strict validation
zenith validate corpus.zenith --strict
```

#### `zenith metrics` - Advanced Metrics
Calculates advanced temporal metrics.

```bash
# All metrics
zenith metrics corpus.zenith --type all --format json --pretty

# Temporal metrics in CSV
zenith metrics corpus.zenith --type temporal --format csv -o metrics.csv

# Detailed metrics for a law
zenith metrics corpus.zenith --law "MainSequence" --detailed
```

#### `zenith visualize` - Visualization
Creates visualizations of temporal data.

```bash
# Duration histogram
zenith visualize corpus.zenith --type histogram -o histogram.png

# All visualizations
zenith visualize corpus.zenith --type all --output-dir ./visualizations

# Specific timeline
zenith visualize corpus.zenith --law "KeyEvents" --type timeline --title "Chronology"
```

#### Complete Analysis Pipeline
```bash
# Step 1: Validation
zenith validate my_corpus.zenith --strict

# Step 2: Analysis
zenith analyze my_corpus.zenith --pretty -o analysis.json

# Step 3: Metrics
zenith metrics my_corpus.zenith --type all --detailed -o metrics.json

# Step 4: Visualizations
zenith visualize my_corpus.zenith --type all --output-dir ./viz

# Step 5: Complete export
zenith export my_corpus.zenith --formats png pdf json --zip
```

---

## Zenith Language Specification

### 1. General Presentation
Zenith is a specialized language designed to structure and organize temporal textual corpora. It allows modeling temporal laws, events, and their relationships within an organized hierarchy.

### 2. Basic Structure

#### Law Example
```zenith
law LawName:
    start_date: YYYY-MM-DD at HH:MM:SS
    period: number
    Event:
        event1: "description"
        event2[index]: "description"
    GROUP:
        (event1 0.5^0.3 event2 0.7^0.4)
end law
```

#### Target Example
```zenith
target TargetName:
    key: "main_key"
    dictionnary:
        entry1: "description"
        entry2[index]: "description"
    # Nested blocks (laws or targets)
end target
```

### 3. Syntax Components

#### Token Types
- **Structural keywords**: `law`, `target`, `end_law`, `end_target`
- **Sections**: `Event`, `GROUP`, `start_date`, `period`, `key`, `dictionnary`
- **Operators**: `:`, `^`, `-`, `(`, `)`, `[`, `]`
- **Data types**: `identifier`, `string`, `date`, `time`, `number`, `dotted_number`

#### AST Structure
```
corpus_textuel
├── law
│   ├── name
│   └── contents
│       ├── start_date (date + time)
│       ├── period
│       ├── events[]
│       └── group[]
└── target
    ├── name
    └── contents
        ├── key
        ├── dictionnary[]
        └── blocks[]
```

### 4. Complete Example
```zenith
target HistoricalProject:
    key: "industrial_revolution"
    dictionnary:
        innovation: "period of technical innovations"
        social[impact]: "major social changes"
    
    law MainPeriod:
        start_date: 1760-01-01 at 00:00:00
        period: 100
        Event:
            steam_engine: "invention of the steam engine"
            textile: "textile mechanization"
        GROUP:
            (steam_engine 0.8^0.2-textile 0.7^0.3)
    end law
end target
```

---

## Advanced Features

### 1. ZenithMetrics
Advanced statistical analysis, pattern detection, and temporal characterization.

#### Key Methods:
- `calculate_temporal_statistics()`: Duration statistics
- `calculate_sequence_complexity()`: Sequence complexity scoring
- `detect_patterns()`: Pattern detection using Suffix Array O(n log n)
- `calculate_temporal_density()`: Event density in time
- `calculate_event_frequency()`: Event frequency counting

#### Example:
```python
from zenith.metrics import ZenithMetrics

metrics = ZenithMetrics(code_zenith)
simulations = metrics.law_description("TemporalLaw", population=3)["simulation"]
comprehensive = metrics.get_comprehensive_metrics(simulations)

print(f"Complexity Score: {comprehensive['sequence_complexity']['complexity_score']:.1f}")
print(f"Temporal Density: {comprehensive['temporal_density']['temporal_density']:.2f}")
```

### 2. ZenithVisualizer
Comprehensive visualization of temporal data.

#### Key Methods:
- `plot_duration_histogram()`: Duration distribution
- `plot_event_pie_chart()`: Event proportion
- `plot_sequence_scatter()`: Temporal sequence scatter plot
- `plot_timeline()`: Event timeline
- `create_all_plots()`: Generate all visualizations at once

#### Example:
```python
from zenith.visualizer import ZenithVisualizer

visualizer = ZenithVisualizer(metrics)

# Generate all plots
files = visualizer.create_all_plots(
    simulations,
    metrics_data=metrics_data,
    prefix="analysis_law",
    output_dir="./visualizations"
)
```

---

## Examples

### Example 1: Complete Historical Analysis
```bash
#!/bin/bash
# historical_analysis.sh

INPUT="europe_history.zenith"
OUTPUT_DIR="./historical_analysis_$(date +%Y%m%d)"

mkdir -p "$OUTPUT_DIR"

echo "🔍 Analyzing historical corpus..."
zenith analyze "$INPUT" --pretty > "$OUTPUT_DIR/analysis.json"

echo "📊 Calculating metrics..."
zenith metrics "$INPUT" --type all --detailed > "$OUTPUT_DIR/metrics.json"

echo "🎨 Generating visualizations..."
zenith visualize "$INPUT" --type all --output-dir "$OUTPUT_DIR/viz"

echo "📦 Final export..."
zenith export "$INPUT" --output-dir "$OUTPUT_DIR/export" --zip

echo "✅ Analysis completed in: $OUTPUT_DIR"
```

### Example 2: Python Integration
```python
import subprocess
import json

# Execute zenith from Python
result = subprocess.run(
    ["zenith", "analyze", "corpus.zenith", "--format", "json"],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)

# Process the data
print(f"Total events: {data['corpus_statistics']['total_events']}")
print(f"Total duration: {data['corpus_statistics']['total_duration_minutes']} minutes")
```

### Example 3: Anomaly Detection
```python
def detect_anomalies(metrics, simulations, threshold=2.0):
    """Detect temporal anomalies in event sequences."""
    stats = metrics.calculate_temporal_statistics(simulations)
    anomalies = []
    
    for sim in simulations:
        duration = sim["duration_minutes"]
        z_score = abs(duration - stats["avg_duration"]) / stats["duration_std"]
        
        if z_score > threshold:
            anomalies.append({
                "event": sim["event_name"],
                "duration": duration,
                "z_score": z_score,
                "position": simulations.index(sim)
            })
    
    return anomalies
```

---

## Installation

### Basic Installation
```bash
pip install zenith-analyser
```

### Development Installation
```bash
git clone https://github.com/yourusername/zenith-analyser.git
cd zenith-analyser
pip install -e ".[dev]"
```

### Optional Dependencies
```bash
# For scientific features (pandas, numpy)
pip install zenith-analyser[science]

# For development
pip install zenith-analyser[dev]

# For all features
pip install zenith-analyser[all]
```

### Dependencies
- **Required**: Python 3.8+
- **Core**: matplotlib, numpy
- **Optional**: pandas (for advanced metrics)

---

## Conclusion

Zenith-Analyser provides a comprehensive framework for temporal management and analysis. By distinguishing between generations (structural hierarchy) and populations (contextual activity), it offers unique insights into time allocation and objective management.

### Key Benefits:
1. **Structural Clarity**: Clear separation between objective hierarchy and active context
2. **Temporal Precision**: Accurate modeling of time allocation with chronocoherence/dispersal
3. **Analytical Depth**: Advanced metrics for complexity, rhythm, and pattern analysis
4. **Visual Insight**: Comprehensive visualization of temporal structures
5. **Workflow Integration**: Full CLI and Python API for seamless integration

### Use Cases:
- **Personal Time Management**: Plan and analyze daily/weekly activities
- **Project Management**: Structure objectives and track temporal investment
- **Research Analysis**: Model historical or sequential processes
- **Process Optimization**: Identify temporal patterns and inefficiencies

For more information, examples, and contributions, visit the [GitHub repository](https://github.com/yourusername/zenith-analyser).
