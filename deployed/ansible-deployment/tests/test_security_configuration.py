#!/usr/bin/env python3
"""
Property-based tests for security configuration.
Feature: ansible-deployment, Property 6: Security Configuration Enforcement
Validates: Requirements 9.1, 9.2
"""

import os
import subprocess
import socket
from pathlib import Path


class TestSecurityConfiguration:
    """Test security configuration and hardening."""
    
    def __init__(self):
        """Set up test environment."""
        self.ssh_config_path = "/etc/ssh/sshd_config"
        self.ufw_status_cmd = ["ufw", "status", "verbose"]
        self.ssh_port = 22
        self.required_ports = [22, 80, 443]

    def run_command(self, command, check_return_code=True):
        """Run a system command and return the result."""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                shell=isinstance(command, str)
            )
            if check_return_code and result.returncode != 0:
                return None, result.stderr
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return None, str(e)

    def test_ssh_configuration_security(self):
        """Test SSH daemon security configuration."""
        results = []
        
        if not Path(self.ssh_config_path).exists():
            results.append(f"SKIP: SSH config file {self.ssh_config_path} does not exist")
            return results
        
        try:
            with open(self.ssh_config_path, 'r') as f:
                ssh_config = f.read()
        except (IOError, OSError) as e:
            results.append(f"FAIL: Could not read SSH config: {e}")
            return results
        
        # Test security settings
        security_checks = [
            ("PermitRootLogin", "no", "Root login should be disabled"),
            ("PasswordAuthentication", "no", "Password authentication should be disabled"),
            ("PubkeyAuthentication", "yes", "Public key authentication should be enabled"),
            ("X11Forwarding", "no", "X11 forwarding should be disabled"),
            ("PermitEmptyPasswords", "no", "Empty passwords should not be permitted"),
            ("Protocol", "2", "SSH protocol 2 should be used"),
        ]
        
        for setting, expected_value, description in security_checks:
            # Look for the setting in the config
            lines = [line.strip() for line in ssh_config.split('\n') 
                    if line.strip() and not line.strip().startswith('#')]
            
            found = False
            for line in lines:
                if line.startswith(setting):
                    actual_value = line.split()[1].lower()
                    expected_lower = expected_value.lower()
                    
                    if actual_value == expected_lower:
                        results.append(f"PASS: {description} - {setting} is set to {expected_value}")
                    else:
                        results.append(f"FAIL: {description} - {setting} is set to {actual_value}, expected {expected_value}")
                    found = True
                    break
            
            if not found:
                results.append(f"SKIP: {setting} not explicitly configured (may use default)")
        
        return results

    def test_ssh_service_running(self):
        """Test that SSH service is running and accessible."""
        results = []
        
        # Check if SSH service is running
        stdout, stderr = self.run_command(["systemctl", "is-active", "ssh"], check_return_code=False)
        if stdout == "active":
            results.append("PASS: SSH service is active")
        else:
            # Try alternative service name
            stdout, stderr = self.run_command(["systemctl", "is-active", "sshd"], check_return_code=False)
            if stdout == "active":
                results.append("PASS: SSH service (sshd) is active")
            else:
                results.append("FAIL: SSH service is not active")
        
        # Test SSH port accessibility
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', self.ssh_port))
            sock.close()
            
            if result == 0:
                results.append(f"PASS: SSH port {self.ssh_port} is accessible")
            else:
                results.append(f"FAIL: SSH port {self.ssh_port} is not accessible")
        except Exception as e:
            results.append(f"FAIL: Could not test SSH port accessibility: {e}")
        
        return results

    def test_firewall_configuration(self):
        """Test firewall configuration and rules."""
        results = []
        
        # Check if UFW is installed and active
        stdout, stderr = self.run_command(["which", "ufw"], check_return_code=False)
        if not stdout:
            results.append("SKIP: UFW is not installed")
            return results
        
        # Check UFW status
        stdout, stderr = self.run_command(self.ufw_status_cmd, check_return_code=False)
        if not stdout:
            results.append("FAIL: Could not get UFW status")
            return results
        
        if "Status: active" in stdout:
            results.append("PASS: UFW firewall is active")
        else:
            results.append("FAIL: UFW firewall is not active")
            return results
        
        # Check default policies
        if "Default: deny (incoming)" in stdout:
            results.append("PASS: Default incoming policy is deny")
        else:
            results.append("FAIL: Default incoming policy is not deny")
        
        if "Default: allow (outgoing)" in stdout:
            results.append("PASS: Default outgoing policy is allow")
        else:
            results.append("FAIL: Default outgoing policy is not allow")
        
        # Check that required ports are allowed
        for port in self.required_ports:
            if f"{port}/tcp" in stdout and "ALLOW IN" in stdout:
                results.append(f"PASS: Port {port}/tcp is allowed")
            else:
                results.append(f"FAIL: Port {port}/tcp is not allowed")
        
        return results

    def test_fail2ban_configuration(self):
        """Test fail2ban installation and configuration."""
        results = []
        
        # Check if fail2ban is installed
        stdout, stderr = self.run_command(["which", "fail2ban-client"], check_return_code=False)
        if not stdout:
            results.append("SKIP: fail2ban is not installed")
            return results
        
        # Check fail2ban service status
        stdout, stderr = self.run_command(["systemctl", "is-active", "fail2ban"], check_return_code=False)
        if stdout == "active":
            results.append("PASS: fail2ban service is active")
        else:
            results.append("FAIL: fail2ban service is not active")
            return results
        
        # Check fail2ban status
        stdout, stderr = self.run_command(["fail2ban-client", "status"], check_return_code=False)
        if stdout and "Jail list:" in stdout:
            results.append("PASS: fail2ban is running with configured jails")
            
            # Check for SSH jail
            if "sshd" in stdout:
                results.append("PASS: SSH jail is configured in fail2ban")
            else:
                results.append("FAIL: SSH jail is not configured in fail2ban")
        else:
            results.append("FAIL: fail2ban is not properly configured")
        
        return results

    def test_unnecessary_services_disabled(self):
        """Test that unnecessary services are disabled."""
        results = []
        
        # List of services that should typically be disabled for security
        services_to_check = [
            "apache2",
            "nginx",  # Will be managed separately
            "telnet",
            "rsh-server",
            "rlogin",
            "vsftpd"
        ]
        
        for service in services_to_check:
            stdout, stderr = self.run_command(["systemctl", "is-enabled", service], check_return_code=False)
            if stdout == "disabled" or "not found" in stderr or "could not be found" in stderr:
                results.append(f"PASS: Service {service} is disabled or not installed")
            elif stdout == "enabled":
                results.append(f"FAIL: Service {service} is enabled (should be disabled for security)")
            else:
                results.append(f"SKIP: Could not determine status of service {service}")
        
        return results

    def test_system_file_permissions(self):
        """Test critical system file permissions."""
        results = []
        
        critical_files = [
            ("/etc/passwd", "644", "System password file"),
            ("/etc/shadow", "640", "System shadow file"),
            ("/etc/group", "644", "System group file"),
            ("/etc/ssh/sshd_config", "600", "SSH daemon configuration"),
        ]
        
        for file_path, expected_perms, description in critical_files:
            path = Path(file_path)
            if not path.exists():
                results.append(f"SKIP: {description} ({file_path}) does not exist")
                continue
            
            try:
                stat_info = path.stat()
                actual_perms = oct(stat_info.st_mode)[-3:]
                
                if actual_perms == expected_perms:
                    results.append(f"PASS: {description} has correct permissions ({expected_perms})")
                else:
                    results.append(f"FAIL: {description} has permissions {actual_perms}, expected {expected_perms}")
            except (OSError, IOError) as e:
                results.append(f"FAIL: Could not check permissions for {description}: {e}")
        
        return results

    def run_all_tests(self):
        """Run all tests and return results."""
        all_results = []
        
        print("Testing Security Configuration...")
        print("=" * 50)
        
        test_methods = [
            self.test_ssh_configuration_security,
            self.test_ssh_service_running,
            self.test_firewall_configuration,
            self.test_fail2ban_configuration,
            self.test_unnecessary_services_disabled,
            self.test_system_file_permissions
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
    tester = TestSecurityConfiguration()
    success = tester.run_all_tests()
    exit(0 if success else 1)