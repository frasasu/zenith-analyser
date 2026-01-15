#!/bin/bash 
#!/bin/bash
# Zenith Analyser - Release Script
# This script automates the release process for Zenith Analyser

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_NAME="zenith-analyser"
PYPI_REPOSITORY="pypi"
TEST_PYPI_REPOSITORY="testpypi"

# Functions
print_header() {
    echo -e "\n${BLUE}==> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_requirements() {
    print_header "Checking requirements"
    
    # Check Python
    if ! command -v python &> /dev/null; then
        print_error "Python not found"
        exit 1
    fi
    print_success "Python found: $(python --version)"
    
    # Check pip
    if ! command -v pip &> /dev/null; then
        print_error "pip not found"
        exit 1
    fi
    print_success "pip found: $(pip --version)"
    
    # Check twine (for upload)
    if ! command -v twine &> /dev/null; then
        print_warning "twine not found, installing..."
        pip install twine
    fi
    print_success "twine found"
    
    # Check build
    if ! command -v python -m build --help &> /dev/null; then
        print_warning "build not found, installing..."
        pip install build
    fi
    print_success "build found"
}

get_current_version() {
    python -c "import sys; sys.path.insert(0, 'src'); from zenith_analyser import __version__; print(__version__)"
}

validate_version() {
    local version=$1
    
    # Check semantic versioning format
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+(?:-[a-zA-Z0-9]+)?$ ]]; then
        print_error "Version must follow semantic versioning (X.Y.Z or X.Y.Z-label)"
        return 1
    fi
    
    # Check if version is newer than current
    local current_version=$(get_current_version)
    
    # Simple version comparison
    IFS='.-' read -ra CURRENT <<< "$current_version"
    IFS='.-' read -ra NEW <<< "$version"
    
    for i in {0..2}; do
        if [[ ${NEW[$i]} -gt ${CURRENT[$i]} ]]; then
            return 0
        elif [[ ${NEW[$i]} -lt ${CURRENT[$i]} ]]; then
            print_error "New version ($version) must be greater than current version ($current_version)"
            return 1
        fi
    done
    
    # If we get here, versions are equal
    if [[ "$version" == "$current_version" ]]; then
        print_error "New version ($version) is the same as current version"
        return 1
    fi
    
    return 0
}

update_version() {
    local version=$1
    
    print_header "Updating version to $version"
    
    # Update __init__.py
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"$version\"/" src/zenith_analyser/__init__.py
    rm -f src/zenith_analyser/__init__.py.bak
    
    # Update pyproject.toml
    sed -i.bak "s/version = \".*\"/version = \"$version\"/" pyproject.toml
    rm -f pyproject.toml.bak
    
    # Update setup.py if exists
    if [ -f "setup.py" ]; then
        sed -i.bak "s/version=\".*\"/version=\"$version\"/" setup.py
        rm -f setup.py.bak
    fi
    
    print_success "Version updated to $version"
}

run_tests() {
    print_header "Running tests"
    
    if ! python -m pytest tests/ -xvs; then
        print_error "Tests failed"
        exit 1
    fi
    print_success "All tests passed"
}

run_checks() {
    print_header "Running code checks"
    
    # Format check
    if ! black --check src tests; then
        print_error "Code formatting issues found"
        exit 1
    fi
    print_success "Code formatting OK"
    
    # Lint check
    if ! flake8 src tests; then
        print_error "Linting issues found"
        exit 1
    fi
    print_success "Linting OK"
    
    # Type check
    if ! mypy src; then
        print_error "Type checking issues found"
        exit 1
    fi
    print_success "Type checking OK"
    
    # Security check
    if command -v bandit &> /dev/null; then
        if ! bandit -r src -c pyproject.toml; then
            print_warning "Security issues found"
        else
            print_success "Security check OK"
        fi
    fi
}

build_package() {
    print_header "Building package"
    
    # Clean previous builds
    rm -rf dist/ build/ *.egg-info/
    
    # Build source distribution and wheel
    python -m build
    
    # Check built files
    if [ ! -f "dist/${PACKAGE_NAME}-*.tar.gz" ] || [ ! -f "dist/${PACKAGE_NAME}-*.whl" ]; then
        print_error "Build failed - distribution files not found"
        exit 1
    fi
    
    print_success "Package built successfully"
    ls -la dist/
}

test_upload() {
    local repository=${1:-$TEST_PYPI_REPOSITORY}
    
    print_header "Testing upload to $repository"
    
    if ! twine upload --repository "$repository" --verbose dist/*; then
        print_error "Test upload failed"
        exit 1
    fi
    print_success "Test upload successful"
}

create_tag() {
    local version=$1
    
    print_header "Creating Git tag v$version"
    
    # Check if tag already exists
    if git tag -l | grep -q "v$version"; then
        print_error "Tag v$version already exists"
        exit 1
    fi
    
    # Create and push tag
    git tag -a "v$version" -m "Release version $version"
    git push origin "v$version"
    
    print_success "Tag v$version created and pushed"
}

update_changelog() {
    local version=$1
    
    print_header "Updating CHANGELOG.md"
    
    # Get current date
    local date=$(date +%Y-%m-%d)
    
    # Create temporary changelog
    cat > CHANGELOG.new << EOF
# Changelog

## [Unreleased]

## [$version] - $date

### Added
- 

### Changed
- 

### Fixed
- 

### Security
- 

$(tail -n +2 CHANGELOG.md)
EOF
    
    # Replace original changelog
    mv CHANGELOG.new CHANGELOG.md
    
    print_success "CHANGELOG.md updated"
    print_warning "Please review and update the changelog with actual changes"
}

show_help() {
    cat << EOF
Zenith Analyser Release Script

Usage: $0 [OPTIONS] VERSION

Options:
  -h, --help      Show this help message
  -t, --test      Test release (build and test upload only)
  -d, --dry-run   Dry run (build only, no upload or tag)
  -u, --upload    Upload to PyPI (requires --test first or confirmation)

Examples:
  $0 1.0.1           # Prepare release 1.0.1
  $0 -t 1.0.1        # Test release 1.0.1
  $0 -u              # Upload to PyPI after testing
  $0 --dry-run 1.1.0 # Dry run for 1.1.0

Environment variables:
  TWINE_USERNAME     PyPI username (optional)
  TWINE_PASSWORD     PyPI password (optional)
  TEST_TWINE_USERNAME TestPyPI username (optional)
  TEST_TWINE_PASSWORD TestPyPI password (optional)
EOF
}

# Main script
main() {
    local mode="normal"
    local version=""
    local upload_only=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show                show_help
                exit 0
                ;;
            -t|--test)
                mode="test"
                shift
                ;;
            -d|--dry-run)
                mode="dry-run"
                shift
                ;;
            -u|--upload)
                upload_only=true
                shift
                ;;
            *)
                if [[ -z "$version" ]]; then
                    version="$1"
                    shift
                else
                    print_error "Unknown argument: $1"
                    show_help
                    exit 1
                fi
                ;;
        esac
    done
    
    # If upload only mode
    if [[ "$upload_only" == true ]]; then
        print_header "Uploading to PyPI"
        
        # Check if dist directory exists
        if [ ! -d "dist" ] || [ -z "$(ls -A dist/ 2>/dev/null)" ]; then
            print_error "No distribution files found. Run build first."
            exit 1
        fi
        
        # Upload to PyPI
        if ! twine upload --repository "$PYPI_REPOSITORY" dist/*; then
            print_error "Upload to PyPI failed"
            exit 1
        fi
        
        print_success "Package uploaded to PyPI successfully"
        exit 0
    fi
    
    # Check if version is provided
    if [[ -z "$version" ]]; then
        print_error "Version argument is required"
        show_help
        exit 1
    fi
    
    # Validate version format
    if ! validate_version "$version"; then
        exit 1
    fi
    
    # Show current status
    print_header "Starting release process for $PACKAGE_NAME"
    echo "Current version: $(get_current_version)"
    echo "New version: $version"
    echo "Mode: $mode"
    echo ""
    
    # Check requirements
    check_requirements
    
    # Run tests
    run_tests
    
    # Run checks
    run_checks
    
    # Update version
    update_version "$version"
    
    # Update changelog
    update_changelog "$version"
    
    # Build package
    build_package
    
    case "$mode" in
        "test")
            print_header "TEST MODE - Uploading to TestPyPI"
            test_upload "$TEST_PYPI_REPOSITORY"
            print_success "Test release complete. Check TestPyPI before proceeding to real release."
            ;;
            
        "dry-run")
            print_header "DRY RUN MODE - No upload or tag creation"
            print_success "Dry run complete. Distribution files are in dist/"
            ;;
            
        "normal")
            # Ask for confirmation
            echo ""
            print_warning "Are you sure you want to release version $version to PyPI? (y/N)"
            read -r confirmation
            
            if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
                print_error "Release cancelled"
                exit 0
            fi
            
            # Upload to PyPI
            print_header "Uploading to PyPI"
            if ! twine upload --repository "$PYPI_REPOSITORY" dist/*; then
                print_error "Upload to PyPI failed"
                exit 1
            fi
            print_success "Package uploaded to PyPI successfully"
            
            # Create Git tag
            create_tag "$version"
            
            # Commit changes
            print_header "Committing release changes"
            git add src/zenith_analyser/__init__.py pyproject.toml setup.py CHANGELOG.md
            git commit -m "Release version $version"
            git push origin main
            
            print_success "Release $version completed successfully!"
            
            # Show next steps
            echo ""
            print_header "Next steps:"
            echo "1. Review the release on PyPI: https://pypi.org/project/$PACKAGE_NAME/$version/"
            echo "2. Update GitHub Releases: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]//' | sed 's/\.git$//')/releases/new"
            echo "3. Announce the release to users"
            ;;
    esac
}

# Run main function with all arguments
main "$@"