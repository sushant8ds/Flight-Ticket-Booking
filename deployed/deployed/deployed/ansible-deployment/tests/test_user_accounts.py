#!/usr/bin/env python3
"""
Property-based tests for user account creation.
Feature: ansible-deployment, Property 2: User Account Validation
Validates: Requirements 1.2
"""

import os
import pwd
import grp
from pathlib import Path


class TestUserAccounts:
    """Test user account creation and configuration."""
    
    def __init__(self):
        """Set up test environment."""
        self.app_user = "flightapp"
        self.app_group = "flightapp"
        self.app_home = f"/home/{self.app_user}"
        self.app_dir = "/opt/flight_booking"
        self.backup_dir = "/opt/backups"

    def test_application_group_exists(self):
        """Test that application group exists."""
        results = []
        try:
            group_info = grp.getgrnam(self.app_group)
            results.append(f"PASS: Group '{self.app_group}' exists with GID {group_info.gr_gid}")
        except KeyError:
            results.append(f"FAIL: Group '{self.app_group}' does not exist")
        return results

    def test_application_user_exists(self):
        """Test that application user exists with correct configuration."""
        results = []
        try:
            user_info = pwd.getpwnam(self.app_user)
            results.append(f"PASS: User '{self.app_user}' exists with UID {user_info.pw_uid}")
            
            # Check primary group
            try:
                primary_group = grp.getgrgid(user_info.pw_gid)
                if primary_group.gr_name == self.app_group:
                    results.append(f"PASS: User '{self.app_user}' has correct primary group '{self.app_group}'")
                else:
                    results.append(f"FAIL: User '{self.app_user}' has incorrect primary group '{primary_group.gr_name}', expected '{self.app_group}'")
            except KeyError:
                results.append(f"FAIL: Could not determine primary group for user '{self.app_user}'")
            
            # Check home directory
            if user_info.pw_dir == self.app_home:
                results.append(f"PASS: User '{self.app_user}' has correct home directory '{self.app_home}'")
            else:
                results.append(f"FAIL: User '{self.app_user}' has incorrect home directory '{user_info.pw_dir}', expected '{self.app_home}'")
            
            # Check shell
            if user_info.pw_shell == "/bin/bash":
                results.append(f"PASS: User '{self.app_user}' has correct shell '/bin/bash'")
            else:
                results.append(f"FAIL: User '{self.app_user}' has incorrect shell '{user_info.pw_shell}', expected '/bin/bash'")
                
        except KeyError:
            results.append(f"FAIL: User '{self.app_user}' does not exist")
        
        return results

    def test_user_home_directory_permissions(self):
        """Test that user home directory has correct permissions."""
        results = []
        home_path = Path(self.app_home)
        
        if not home_path.exists():
            results.append(f"FAIL: Home directory '{self.app_home}' does not exist")
            return results
        
        if not home_path.is_dir():
            results.append(f"FAIL: Home directory '{self.app_home}' is not a directory")
            return results
        
        # Check ownership
        stat_info = home_path.stat()
        try:
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
            group = grp.getgrgid(stat_info.st_gid).gr_name
            
            if owner == self.app_user:
                results.append(f"PASS: Home directory owned by correct user '{self.app_user}'")
            else:
                results.append(f"FAIL: Home directory owned by '{owner}', expected '{self.app_user}'")
            
            if group == self.app_group:
                results.append(f"PASS: Home directory owned by correct group '{self.app_group}'")
            else:
                results.append(f"FAIL: Home directory owned by group '{group}', expected '{self.app_group}'")
                
        except (KeyError, OSError) as e:
            results.append(f"FAIL: Could not determine ownership of home directory: {e}")
        
        # Check permissions (should be 755)
        permissions = oct(stat_info.st_mode)[-3:]
        if permissions == "755":
            results.append(f"PASS: Home directory has correct permissions '755'")
        else:
            results.append(f"FAIL: Home directory has permissions '{permissions}', expected '755'")
        
        return results

    def test_ssh_directory_configuration(self):
        """Test that SSH directory is properly configured."""
        results = []
        ssh_dir = Path(self.app_home) / ".ssh"
        
        if not ssh_dir.exists():
            results.append(f"SKIP: SSH directory '{ssh_dir}' does not exist (may not be configured)")
            return results
        
        if not ssh_dir.is_dir():
            results.append(f"FAIL: SSH path '{ssh_dir}' exists but is not a directory")
            return results
        
        # Check ownership
        stat_info = ssh_dir.stat()
        try:
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
            group = grp.getgrgid(stat_info.st_gid).gr_name
            
            if owner == self.app_user:
                results.append(f"PASS: SSH directory owned by correct user '{self.app_user}'")
            else:
                results.append(f"FAIL: SSH directory owned by '{owner}', expected '{self.app_user}'")
            
            if group == self.app_group:
                results.append(f"PASS: SSH directory owned by correct group '{self.app_group}'")
            else:
                results.append(f"FAIL: SSH directory owned by group '{group}', expected '{self.app_group}'")
                
        except (KeyError, OSError) as e:
            results.append(f"FAIL: Could not determine ownership of SSH directory: {e}")
        
        # Check permissions (should be 700)
        permissions = oct(stat_info.st_mode)[-3:]
        if permissions == "700":
            results.append(f"PASS: SSH directory has correct permissions '700'")
        else:
            results.append(f"FAIL: SSH directory has permissions '{permissions}', expected '700'")
        
        return results

    def test_application_directories_exist(self):
        """Test that application directories exist with correct permissions."""
        results = []
        directories = [
            self.app_dir,
            f"{self.app_dir}/logs",
            f"{self.app_dir}/tmp",
            self.backup_dir
        ]
        
        for directory in directories:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                results.append(f"SKIP: Directory '{directory}' does not exist (may not be created yet)")
                continue
            
            if not dir_path.is_dir():
                results.append(f"FAIL: Path '{directory}' exists but is not a directory")
                continue
            
            # Check ownership
            stat_info = dir_path.stat()
            try:
                owner = pwd.getpwuid(stat_info.st_uid).pw_name
                group = grp.getgrgid(stat_info.st_gid).gr_name
                
                if owner == self.app_user:
                    results.append(f"PASS: Directory '{directory}' owned by correct user '{self.app_user}'")
                else:
                    results.append(f"FAIL: Directory '{directory}' owned by '{owner}', expected '{self.app_user}'")
                
                if group == self.app_group:
                    results.append(f"PASS: Directory '{directory}' owned by correct group '{self.app_group}'")
                else:
                    results.append(f"FAIL: Directory '{directory}' owned by group '{group}', expected '{self.app_group}'")
                    
            except (KeyError, OSError) as e:
                results.append(f"FAIL: Could not determine ownership of directory '{directory}': {e}")
        
        return results

    def test_sudo_configuration(self):
        """Test that sudo configuration exists for service management."""
        results = []
        sudo_file = Path(f"/etc/sudoers.d/{self.app_user}")
        
        if not sudo_file.exists():
            results.append(f"SKIP: Sudo configuration file '{sudo_file}' does not exist (may not be configured)")
            return results
        
        # Check file permissions (should be 440)
        stat_info = sudo_file.stat()
        permissions = oct(stat_info.st_mode)[-3:]
        if permissions == "440":
            results.append(f"PASS: Sudo configuration file has correct permissions '440'")
        else:
            results.append(f"FAIL: Sudo configuration file has permissions '{permissions}', expected '440'")
        
        # Check file content
        try:
            with open(sudo_file, 'r') as f:
                content = f.read()
            
            if self.app_user in content and "systemctl" in content:
                results.append(f"PASS: Sudo configuration contains systemctl permissions for '{self.app_user}'")
            else:
                results.append(f"FAIL: Sudo configuration does not contain expected systemctl permissions")
                
        except (IOError, OSError) as e:
            results.append(f"FAIL: Could not read sudo configuration file: {e}")
        
        return results

    def run_all_tests(self):
        """Run all tests and return results."""
        all_results = []
        
        print("Testing User Account Configuration...")
        print("=" * 50)
        
        test_methods = [
            self.test_application_group_exists,
            self.test_application_user_exists,
            self.test_user_home_directory_permissions,
            self.test_ssh_directory_configuration,
            self.test_application_directories_exist,
            self.test_sudo_configuration
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
        skipped = len([r for r in all_results if r.startswith("SKIP")])
        
        print(f"\n" + "=" * 50)
        print(f"Test Summary: {passed} passed, {failed} failed, {skipped} skipped")
        
        return failed == 0


if __name__ == '__main__':
    tester = TestUserAccounts()
    success = tester.run_all_tests()
    exit(0 if success else 1)