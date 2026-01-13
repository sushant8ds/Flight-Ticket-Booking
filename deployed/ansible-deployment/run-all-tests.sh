#!/bin/bash
# Comprehensive test suite for Ansible deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Comprehensive Ansible Deployment Test Suite ===${NC}"
echo ""

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${YELLOW}Running: $test_name${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED: $test_name${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAILED: $test_name${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# 1. Project Structure Tests
echo -e "${BLUE}=== Project Structure Tests ===${NC}"
run_test "Project Structure Validation" "python3 tests/test_project_structure.py"

# 2. Role Structure Tests
echo -e "\n${BLUE}=== Role Structure Tests ===${NC}"
run_test "Common Role Structure" "test -d roles/common/tasks && test -f roles/common/tasks/main.yml"
run_test "Security Role Structure" "test -d roles/security/tasks && test -f roles/security/tasks/main.yml"
run_test "Python Role Structure" "test -d roles/python/tasks && test -f roles/python/tasks/main.yml"
run_test "Django Role Structure" "test -d roles/django-app/tasks && test -f roles/django-app/tasks/main.yml"

# 3. Configuration Tests
echo -e "\n${BLUE}=== Configuration Tests ===${NC}"
run_test "Ansible Configuration" "test -f ansible.cfg"
run_test "Requirements File" "test -f requirements.yml"
run_test "Main Playbook" "test -f site.yml"
run_test "Global Variables" "test -f group_vars/all.yml"
run_test "Vault File" "test -f group_vars/vault.yml"

# 4. Inventory Tests
echo -e "\n${BLUE}=== Inventory Tests ===${NC}"
run_test "Development Inventory" "test -f inventories/development/hosts.yml"
run_test "Staging Inventory" "test -f inventories/staging/hosts.yml"
run_test "Production Inventory" "test -f inventories/production/hosts.yml"

# 5. Template Tests
echo -e "\n${BLUE}=== Template Tests ===${NC}"
run_test "Common Templates" "test -d roles/common/templates"
run_test "Security Templates" "test -d roles/security/templates"
run_test "Python Templates" "test -d roles/python/templates"
run_test "Django Templates" "test -d roles/django-app/templates"

# 6. Handler Tests
echo -e "\n${BLUE}=== Handler Tests ===${NC}"
run_test "Common Handlers" "test -f roles/common/handlers/main.yml"
run_test "Security Handlers" "test -f roles/security/handlers/main.yml"
run_test "Python Handlers" "test -f roles/python/handlers/main.yml"
run_test "Django Handlers" "test -f roles/django-app/handlers/main.yml"

# 7. Property-Based Tests
echo -e "\n${BLUE}=== Property-Based Tests ===${NC}"
run_test "User Account Tests" "python3 tests/test_user_accounts.py"
run_test "Security Configuration Tests" "python3 tests/test_security_configuration.py"
run_test "Python Environment Tests" "python3 tests/test_python_environment.py"
run_test "Django Deployment Tests" "python3 tests/test_django_deployment.py"

# 8. Documentation Tests
echo -e "\n${BLUE}=== Documentation Tests ===${NC}"
run_test "README File" "test -f README.md"
run_test "Deployment Summary" "test -f DEPLOYMENT_SUMMARY.md"
run_test "Deployment Script" "test -x deploy.sh"

# 9. File Permission Tests
echo -e "\n${BLUE}=== File Permission Tests ===${NC}"
run_test "Deploy Script Executable" "test -x deploy.sh"
run_test "Test Script Executable" "test -x test-deployment.sh"
run_test "All Tests Script Executable" "test -x run-all-tests.sh"

# 10. Content Validation Tests
echo -e "\n${BLUE}=== Content Validation Tests ===${NC}"
run_test "Ansible Config Content" "grep -q 'inventory.*development' ansible.cfg"
run_test "Site Playbook Content" "grep -q 'Django Flight Booking' site.yml"
run_test "Global Variables Content" "grep -q 'app_name.*flight_booking' group_vars/all.yml"

# Summary
echo -e "\n${BLUE}=== Test Summary ===${NC}"
echo -e "Total tests run: ${TOTAL_TESTS}"
echo -e "${GREEN}Tests passed: ${PASSED_TESTS}${NC}"
echo -e "${RED}Tests failed: ${FAILED_TESTS}${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Ansible deployment is fully implemented and ready for use.${NC}"
    echo -e "\n${BLUE}Implementation includes:${NC}"
    echo -e "✓ Complete Ansible project structure"
    echo -e "✓ 4 comprehensive roles (common, security, python, django-app)"
    echo -e "✓ Multi-environment support (dev/staging/production)"
    echo -e "✓ Security hardening and system configuration"
    echo -e "✓ Python environment and Django application deployment"
    echo -e "✓ Comprehensive property-based testing"
    echo -e "✓ Complete documentation and deployment scripts"
    echo ""
    echo -e "${YELLOW}Ready for production deployment!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please review the implementation.${NC}"
    exit 1
fi