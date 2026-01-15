#!/bin/bash 

### 53. **scripts/setup_environment.sh**
```bash
#!/bin/bash
# Zenith Analyser - Development Environment Setup Script
# This script sets up a development environment for Zenith Analyser

set -e  # Exit on error

echo "🚀 Setting up Zenith Analyser development environment..."
echo "====================================================="

# Check Python version
echo "📦 Checking Python version..."
python --version || { echo "❌ Python not found. Please install Python 3.8+"; exit 1; }

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "❌ Could not find activate script"
    exit 1
fi

# Upgrade pip
echo "⬆ Upgrading pip..."
python -m pip install --upgrade pip

# Install package in development mode
echo "📦 Installing Zenith Analyser in development mode..."
pip install -e .

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Run initial checks
echo "🔍 Running initial checks..."

echo "📋 Checking installation..."
python -c "import zenith_analyser; print(f'✅ Zenith Analyser v{zenith_analyser.__version__} installed successfully')"

echo "🧪 Running tests..."
python -m pytest tests/test_lexer.py -v

echo "✨ Checking code style..."
black --check src tests || echo "⚠ Black formatting issues found"

echo "🔍 Running linter..."
flake8 src tests || echo "⚠ Flake8 issues found"

echo "📊 Checking type hints..."
mypy src || echo "⚠ Type checking issues found"

echo "====================================================="
echo "🎉 Development environment setup complete!"
echo ""
echo "📚 Quick Start:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate  # Linux/Mac"
echo "     venv\\Scripts\\activate     # Windows"
echo ""
echo "  2. Run tests:"
echo "     pytest"
echo ""
echo "  3. Run examples:"
echo "     python examples/basic_usage.py"
echo ""
echo "  4. Format code:"
echo "     black src tests"
echo ""
echo "  5. Build documentation:"
echo "     cd docs && make html"
echo ""
echo "🔧 Available commands:"
echo "   - pytest              # Run all tests"
echo "   - black src tests     # Format code"
echo "   - flake8 src tests    # Lint code"
echo "   - mypy src           # Type checking"
echo "   - pre-commit run --all-files  # Run all pre-commit hooks"
echo ""
echo "📖 Documentation: https://zenith-analyser.readthedocs.io/"
echo "🐛 Issues: https://github.com/yourusername/zenith-analyser/issues"
echo "====================================================="