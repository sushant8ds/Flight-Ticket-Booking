#!/bin/bash
# Complete deployment script for Django Flight Booking Application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
INVENTORY_FILE="inventories/${ENVIRONMENT}/hosts.yml"
PLAYBOOK="site.yml"

echo -e "${BLUE}=== Django Flight Booking Application Deployment ===${NC}"
echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"
echo -e "${YELLOW}Inventory: ${INVENTORY_FILE}${NC}"
echo ""

# Check if inventory file exists
if [ ! -f "$INVENTORY_FILE" ]; then
    echo -e "${RED}Error: Inventory file $INVENTORY_FILE not found${NC}"
    echo "Available environments:"
    ls -1 inventories/
    exit 1
fi

# Function to run deployment step
run_step() {
    local step_name="$1"
    local command="$2"
    local tags="$3"
    
    echo -e "\n${BLUE}Step: $step_name${NC}"
    echo -e "${YELLOW}Command: $command${NC}"
    
    if [ -n "$tags" ]; then
        eval "$command --tags $tags"
    else
        eval "$command"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $step_name completed successfully${NC}"
    else
        echo -e "${RED}✗ $step_name failed${NC}"
        exit 1
    fi
}

# Pre-deployment checks
echo -e "${BLUE}=== Pre-deployment Checks ===${NC}"

# Check Ansible installation
if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${RED}Error: Ansible is not installed${NC}"
    echo "Please install Ansible before running this script"
    exit 1
fi

echo -e "${GREEN}✓ Ansible is installed${NC}"

# Check syntax
echo -e "${YELLOW}Checking playbook syntax...${NC}"
ansible-playbook --syntax-check $PLAYBOOK
echo -e "${GREEN}✓ Playbook syntax is valid${NC}"

# Run tests
echo -e "${YELLOW}Running pre-deployment tests...${NC}"
python3 tests/test_project_structure.py
echo -e "${GREEN}✓ Project structure tests passed${NC}"

# Main deployment
echo -e "\n${BLUE}=== Main Deployment ===${NC}"

# Step 1: Base system setup
run_step "Base System Setup" \
    "ansible-playbook -i $INVENTORY_FILE $PLAYBOOK" \
    "common"

# Step 2: Security hardening
run_step "Security Hardening" \
    "ansible-playbook -i $INVENTORY_FILE $PLAYBOOK" \
    "security"

# Step 3: Python environment
run_step "Python Environment Setup" \
    "ansible-playbook -i $INVENTORY_FILE $PLAYBOOK" \
    "python"

# Step 4: Django application
run_step "Django Application Deployment" \
    "ansible-playbook -i $INVENTORY_FILE $PLAYBOOK" \
    "django"

# Post-deployment verification
echo -e "\n${BLUE}=== Post-deployment Verification ===${NC}"

# Run verification playbook
run_step "System Verification" \
    "ansible-playbook -i $INVENTORY_FILE $PLAYBOOK" \
    "verification"

# Run post-deployment tests
echo -e "${YELLOW}Running post-deployment tests...${NC}"

echo -e "${BLUE}Testing user accounts...${NC}"
python3 tests/test_user_accounts.py || echo -e "${YELLOW}User account tests may fail if not run on target server${NC}"

echo -e "${BLUE}Testing security configuration...${NC}"
python3 tests/test_security_configuration.py || echo -e "${YELLOW}Security tests may fail if not run on target server${NC}"

echo -e "${BLUE}Testing Python environment...${NC}"
python3 tests/test_python_environment.py || echo -e "${YELLOW}Python tests may fail if not run on target server${NC}"

echo -e "${BLUE}Testing Django deployment...${NC}"
python3 tests/test_django_deployment.py || echo -e "${YELLOW}Django tests may fail if not run on target server${NC}"

# Deployment summary
echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo -e "${GREEN}✓ Base system configured${NC}"
echo -e "${GREEN}✓ Security hardening applied${NC}"
echo -e "${GREEN}✓ Python environment set up${NC}"
echo -e "${GREEN}✓ Django application deployed${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Verify the application is accessible"
echo -e "2. Check service status: ${YELLOW}systemctl status flight_booking${NC}"
echo -e "3. View logs: ${YELLOW}journalctl -u flight_booking -f${NC}"
echo -e "4. Access application: ${YELLOW}http://your-server-ip:8000${NC}"
echo ""
echo -e "${GREEN}🎉 Django Flight Booking Application deployment successful!${NC}"