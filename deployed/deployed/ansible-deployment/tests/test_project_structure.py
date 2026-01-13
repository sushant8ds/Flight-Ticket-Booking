#!/usr/bin/env python3
"""
Property-based tests for Ansible project structure validation.
Feature: ansible-deployment, Property 1: Configuration Consistency
Validates: Requirements 5.1
"""

import os
from pathlib import Path


class TestProjectStructure:
    """Test Ansible project structure and configuration consistency."""
    
    def __init__(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        self.required_files = [
            'ansible.cfg',
            'requirements.yml',
            'group_vars/all.yml',
            'group_vars/vault.yml'
        ]
        self.required_dirs = [
            'inventories/development',
            'inventories/staging', 
            'inventories/production',
            'roles',
            'playbooks'
        ]
        self.inventory_environments = ['development', 'staging', 'production']

    def test_required_files_exist(self):
        """Test that all required configuration files exist."""
        results = []
        for file_path in self.required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                results.append(f"FAIL: Required file {file_path} does not exist")
            elif not full_path.is_file():
                results.append(f"FAIL: {file_path} exists but is not a file")
            else:
                results.append(f"PASS: {file_path} exists and is a file")
        return results

    def test_required_directories_exist(self):
        """Test that all required directories exist."""
        results = []
        for dir_path in self.required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                results.append(f"FAIL: Required directory {dir_path} does not exist")
            elif not full_path.is_dir():
                results.append(f"FAIL: {dir_path} exists but is not a directory")
            else:
                results.append(f"PASS: {dir_path} exists and is a directory")
        return results

    def test_ansible_cfg_valid(self):
        """Test that ansible.cfg is valid and contains required settings."""
        results = []
        ansible_cfg_path = self.project_root / 'ansible.cfg'
        
        if not ansible_cfg_path.exists():
            results.append("FAIL: ansible.cfg does not exist")
            return results
        
        # Read and parse ansible.cfg
        with open(ansible_cfg_path, 'r') as f:
            content = f.read()
        
        # Check for required sections and settings
        required_settings = [
            'inventory',
            'remote_user',
            'host_key_checking',
            'roles_path',
            'become'
        ]
        
        for setting in required_settings:
            if setting in content:
                results.append(f"PASS: Required setting '{setting}' found in ansible.cfg")
            else:
                results.append(f"FAIL: Required setting '{setting}' not found in ansible.cfg")
        
        return results

    def test_inventory_files_exist(self):
        """Test that inventory files exist for all environments."""
        results = []
        for environment in self.inventory_environments:
            inventory_path = self.project_root / f'inventories/{environment}/hosts.yml'
            if inventory_path.exists():
                results.append(f"PASS: Inventory for {environment} exists")
            else:
                results.append(f"FAIL: Inventory for {environment} does not exist")
        return results

    def test_vault_file_encrypted(self):
        """Test that vault.yml file is properly encrypted."""
        results = []
        vault_path = self.project_root / 'group_vars/vault.yml'
        
        if not vault_path.exists():
            results.append("FAIL: vault.yml does not exist")
            return results
        
        with open(vault_path, 'r') as f:
            content = f.read()
        
        # Check that file starts with Ansible Vault header
        if content.startswith('$ANSIBLE_VAULT;'):
            results.append("PASS: vault.yml is encrypted with Ansible Vault")
        else:
            results.append("FAIL: vault.yml should be encrypted with Ansible Vault")
        
        return results

    def run_all_tests(self):
        """Run all tests and return results."""
        all_results = []
        
        print("Testing Ansible Project Structure...")
        print("=" * 50)
        
        test_methods = [
            self.test_required_files_exist,
            self.test_required_directories_exist,
            self.test_ansible_cfg_valid,
            self.test_inventory_files_exist,
            self.test_vault_file_encrypted
        ]
        
        for test_method in test_methods:
            print(f"\nRunning {test_method.__name__}:")
            results = test_method()
            for result in results:
                print(f"  {result}")
                all_results.append(result)
        
        # Summary
        passed = len([r for r in all_results if r.startswith("PASS")])
        failed = len([r for r in all_results if r.startswith("FAIL")])
        
        print(f"\n" + "=" * 50)
        print(f"Test Summary: {passed} passed, {failed} failed")
        
        return failed == 0


if __name__ == '__main__':
    tester = TestProjectStructure()
    success = tester.run_all_tests()
    exit(0 if success else 1)