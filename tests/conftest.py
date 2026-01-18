"""
Pytest configuration and fixtures for Zenith Analyser tests.
"""

import os
import tempfile

import pytest

from src.zenith_analyser import (
    Lexer,
    Parser,
    Validator,
    ZenithAnalyser,
)


@pytest.fixture
def sample_code():
    """Sample Zenith code for testing."""
    return """
target test_target:
    key:"Test key"
    dictionnary:
        ev1:"Test event 1"
        ev2:"Test event 2"

    law test_law:
        start_date:2024-01-01 at 10:00
        period:1.0
        Event:
            A[ev1]:"First event"
            B[ev2]:"Second event"
        GROUP:(A 30^15 - B 15^0)
    end_law
end_target
"""


@pytest.fixture
def complex_code():
    """Complex Zenith code with hierarchy."""
    return """
target parent:
    key:"Parent key"
    dictionnary:
        base:"Base event"

    target child:
        key:"Child key"
        dictionnary:
            derived[base]:"Derived event"

        law child_law:
            start_date:2024-01-01 at 09:00
            period:2.0
            Event:
                X[derived]:"Child event"
            GROUP:(X 2.0^0)
        end_law
    end_target

    law parent_law:
        start_date:2024-01-01 at 14:00
        period:1.0
        Event:
            Y[base]:"Parent event"
        GROUP:(Y 1.0^0)
    end_law
end_target
"""


@pytest.fixture
def analyser(sample_code):
    """ZenithAnalyser instance with sample code."""
    return ZenithAnalyser(sample_code)


@pytest.fixture
def lexer(sample_code):
    """Lexer instance with sample code."""
    return Lexer(sample_code)


@pytest.fixture
def parser(sample_code):
    """Parser instance with sample code."""
    lexer = Lexer(sample_code)
    tokens = lexer.tokenise()
    return Parser(tokens)


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".zenith") as f:
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def validator():
    """Validator instance."""
    return Validator()


@pytest.fixture(params=[1, 2, 3])
def population_level(request):
    """Parameterized population levels."""
    return request.param


# Custom markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "benchmark: benchmark tests")
    config.addinivalue_line("markers", "security: security tests")


# Test data
SAMPLE_LAWS = [
    {
        "name": "simple_law",
        "date": "2024-01-01",
        "time": "10:00",
        "period": "1.0",
        "events": [{"name": "A", "description": "Event A"}],
        "group": [{"name": "A", "chronocoherence": "1.0", "chronodispersal": "0"}],
    }
]
