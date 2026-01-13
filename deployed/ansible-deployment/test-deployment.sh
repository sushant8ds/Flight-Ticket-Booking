#!/bin/bash
# Test script for Ansible deployment validation

set -e

echo "=== Ansible Deployment Test Suite ==="
echo "Testing Ansible project structure and configuration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${YELLOW}Running: $test_name${NC}"
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED: $test_name${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAILED: $test_name${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test 1: Project structure validation
run_test "Project Structure Validation" "python3 tests/test_project_structure.py"

# Test 2: Ansible syntax check
run_test "Ansible Syntax Check" "ansible-playbook --syntax-check site.yml"

# Test 3: Ansible lint (if available)
if command -v ansible-lint &> /dev/null; then
    run_test "Ansible Lint Check" "ansible-lint site.yml"
else
    echo -e "${YELLOW}Skipping ansible-lint (not installed)${NC}"
fi

# Test 4: YAML syntax validation
run_test "YAML Syntax Check" "python3 -c \"
import yaml
import sys
files = ['site.yml', 'group_vars/all.yml', 'inventories/development/hosts.yml']
for file in files:
    try:
        with open(file, 'r') as f:
            yaml.safe_load(f)
        print(f'✓ {file} is valid YAML')
    except Exception as e:
        print(f'✗ {file} has YAML errors: {e}')
        sys.exit(1)
\""

# Test 5: Role structure validation
run_test "Role Structure Validation" "python3 -c \"
import os
roles = ['common', 'security']
required_dirs = ['tasks', 'defaults', 'handlers', 'meta']
for role in roles:
    for dir in required_dirs:
        path = f'roles/{role}/{dir}'
        if not os.path.exists(path):
            print(f'✗ Missing directory: {path}')
            exit(1)
        print(f'✓ Found: {path}')
\""

# Test 6: Template validation
run_test "Template Validation" "python3 -c \"
import os
from pathlib import Path
template_dirs = ['roles/common/templates', 'roles/security/templates']
for template_dir in template_dirs:
    if os.path.exists(template_dir):
        templates = list(Path(template_dir).glob('*.j2'))
        for template in templates:
            print(f'✓ Found template: {template}')
    else:
        print(f'No templates in {template_dir}')
\""

# Test 7: Inventory validation
run_test "Inventory Validation" "ansible-inventory -i inventories/development/hosts.yml --list > /dev/null"

# Test 8: Variable validation
run_test "Variable Validation" "python3 -c \"
import yaml
with open('group_vars/all.yml', 'r') as f:
    vars = yaml.safe_load(f)
required_vars = ['app_name', 'app_user', 'app_port', 'repo_url', 'python_version']
for var in required_vars:
    if var not in vars:
        print(f'✗ Missing required variable: {var}')
        exit(1)
    print(f'✓ Found variable: {var} = {vars[var]}')
\""

# Summary
echo -e "\n=== Test Summary ==="
echo -e "Tests run: $TESTS_RUN"
echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Ansible deployment is ready.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please fix the issues before deployment.${NC}"
    exit 1
fi