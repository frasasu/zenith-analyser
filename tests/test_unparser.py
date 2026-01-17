# Copyright 2026 François TUMUSAVYEYESU.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Tests for the ASTUnparser class.
"""

import pytest

from src.zenith_analyser import ASTUnparser, ZenithAnalyser


def test_unparser_initialization(parser):
    """Test ASTUnparser initialization."""
    ast, errors = parser.parse()
    unparser = ASTUnparser(ast)

    assert unparser.ast == ast
    assert unparser.output_lines == []
    assert unparser.current_indent == 0


def test_unparse_basic(sample_code):
    """Test basic unparsing."""
    analyser = ZenithAnalyser(sample_code)
    unparser = ASTUnparser(analyser.ast)

    unparsed = unparser.unparse()

    assert isinstance(unparsed, str)
    assert len(unparsed) > 0

    # Check for key elements
    assert "target test_target:" in unparsed
    assert 'key:"Test key"' in unparsed
    assert "law test_law:" in unparsed
    assert "start_date:2024-01-01 at 10:00" in unparsed
    assert "end_law" in unparsed
    assert "end_target" in unparsed


def test_unparse_complex(complex_code):
    """Test unparsing complex hierarchy."""
    analyser = ZenithAnalyser(complex_code)
    unparser = ASTUnparser(analyser.ast)

    unparsed = unparser.unparse()

    # Check structure
    lines = unparsed.split("\n")

    # Count indentation levels
    indent_levels = []
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            indent_levels.append(indent // 4)  # 4 spaces per indent

    # Should have multiple indent levels
    assert max(indent_levels) >= 2

    # Check for all key elements
    assert "target parent:" in unparsed
    assert "target child:" in unparsed
    assert "law parent_law:" in unparsed
    assert "law child_law:" in unparsed


def test_format_code():
    """Test code formatting."""
    unparser = ASTUnparser({})  # Dummy AST

    # Test with unformatted code
    code = """target test:
key:"value"
law example:
start_date:2024-01-01 at 10:00
period:1.0
Event:
A:"test"
GROUP:(A 1.0^0)
end_law
end_target"""

    formatted = unparser.format_code(code)

    # Check indentation
    lines = formatted.split("\n")
    assert lines[0] == "target test:"
    assert lines[1] == '    key:"value"'
    assert lines[2] == "    law example:"
    assert lines[3] == "        start_date:2024-01-01 at 10:00"

    # Check that end blocks are properly dedented
    assert "    end_law" in formatted
    assert "end_target" in formatted


def test_validate_unparse(sample_code):
    """Test unparse validation."""
    analyser = ZenithAnalyser(sample_code)
    unparser = ASTUnparser(analyser.ast)

    is_valid = unparser.validate_unparse()
    assert is_valid is True


def test_get_unparse_stats(sample_code):
    """Test getting unparse statistics."""
    analyser = ZenithAnalyser(sample_code)
    unparser = ASTUnparser(analyser.ast)

    stats = unparser.get_unparse_stats()

    assert isinstance(stats, dict)
    assert "total_lines" in stats
    assert "non_empty_lines" in stats
    assert "law_count" in stats
    assert "target_count" in stats
    assert "event_count" in stats
    assert "total_length" in stats
    assert "valid_structure" in stats

    assert stats["law_count"] == 1
    assert stats["target_count"] == 1
    assert stats["valid_structure"] is True


def test_unparse_round_trip(sample_code):
    """Test unparse -> parse round trip."""
    analyser = ZenithAnalyser(sample_code)

    # Unparse
    unparser = ASTUnparser(analyser.ast)
    unparsed = unparser.unparse()

    # Parse again
    analyser2 = ZenithAnalyser(unparsed)

    # Basic checks
    assert analyser2.law_analyser.get_law_names() == ["test_law"]
    assert analyser2.target_analyser.get_target_names() == ["test_target"]

    # Compare some key properties
    law1 = analyser.law_analyser.get_law("test_law")
    law2 = analyser2.law_analyser.get_law("test_law")

    assert law1["date"] == law2["date"]
    assert law1["time"] == law2["time"]
    assert law1["period"] == law2["period"]


def test_unparse_empty_ast():
    """Test unparsing empty AST."""
    ast = {"type": "corpus_textuel", "elements": []}
    unparser = ASTUnparser(ast)

    unparsed = unparser.unparse()
    assert unparsed == "" or unparsed == "\n"


def test_unparse_malformed_ast():
    """Test unparsing malformed AST."""
    # Missing required fields
    ast = {"type": "law"}  # Missing name and contents
    unparser = ASTUnparser(ast)

    unparsed = unparser.unparse()
    # Should handle gracefully, not crash
    assert isinstance(unparsed, str)


def test_indentation_consistency():
    """Test indentation consistency in unparsed code."""
    code = """
target level1:
    key:"test"
    target level2:
        key:"nested"
        law test:
            start_date:2024-01-01 at 10:00
            period:1.0
            Event:
                A:"test"
            GROUP:(A 1.0^0)
        end_law
    end_target
end_target
"""

    analyser = ZenithAnalyser(code)
    unparser = ASTUnparser(analyser.ast)
    unparsed = unparser.unparse()

    # Check indentation
    lines = unparsed.split("\n")
    for line in lines:
        if line.strip():
            # Indentation should be multiple of 4
            indent = len(line) - len(line.lstrip())
            assert indent % 4 == 0, f"Invalid indentation in line: {line}"


def test_event_description_preservation():
    """Test that event descriptions are preserved in unparsing."""
    code = """
target test:
    key:"test"
    dictionnary:
        ev1:"First event description"
        ev2:"Second event description"

    law example:
        start_date:2024-01-01 at 10:00
        period:1.0
        Event:
            A[ev1]:"Custom description"
            B[ev2]:"Another description"
        GROUP:(A 30^15 - B 15^0)
    end_law
end_target
"""

    analyser = ZenithAnalyser(code)
    unparser = ASTUnparser(analyser.ast)
    unparsed = unparser.unparse()

    # Check that descriptions are preserved
    assert '"First event description"' in unparsed
    assert '"Second event description"' in unparsed
    assert '"Custom description"' in unparsed
    assert '"Another description"' in unparsed


def test_group_structure_preservation():
    """Test that GROUP structure is preserved in unparsing."""
    code = """
law test:
    start_date:2024-01-01 at 10:00
    period:2.0
    Event:
        A:"Event A"
        B:"Event B"
        C:"Event C"
    GROUP:(A 45^15 - B 30^30 - C 15^0)
end_law
"""

    analyser = ZenithAnalyser(code)
    unparser = ASTUnparser(analyser.ast)
    unparsed = unparser.unparse()

    # Check GROUP line
    lines = unparsed.split("\n")
    group_line = [line for line in lines if "GROUP:" in line][0]

    assert "A 45^15" in group_line
    assert "B 30^30" in group_line
    assert "C 15^0" in group_line
    assert " - " in group_line  # Separators


@pytest.mark.integration
def test_complete_unparse_integration():
    """Test complete unparse integration with formatting."""
    # Create complex code
    code = """
target project:
    key:"Software project"
    dictionnary:
        design:"Design phase"
        dev:"Development"
        test:"Testing"

    target frontend:
        key:"Frontend development"
        dictionnary:
            ui[design]:"User interface"
            ux[design]:"User experience"

        law sprint1:
            start_date:2024-01-01 at 09:00
            period:8.0
            Event:
                A[ui]:"Design UI"
                B[ux]:"Test UX"
            GROUP:(A 4.0^1.0 - B 3.0^0)
        end_law
    end_target

    law planning:
        start_date:2024-01-01 at 08:00
        period:1.0
        Event:
            C[design]:"Project planning"
        GROUP:(C 1.0^0)
    end_law
end_target
"""

    analyser = ZenithAnalyser(code)
    unparser = ASTUnparser(analyser.ast)

    # Test regular unparse
    unparsed = unparser.unparse()
    assert "target project:" in unparsed
    assert "target frontend:" in unparsed
    assert "law sprint1:" in unparsed
    assert "law planning:" in unparsed

    # Test formatted unparse
    formatted = unparser.format_code(unparsed)

    # Parse formatted code to ensure it's valid
    analyser2 = ZenithAnalyser(formatted)
    assert len(analyser2.parser_errors) == 0

    # Get stats
    stats = unparser.get_unparse_stats()
    assert stats["valid_structure"] is True
