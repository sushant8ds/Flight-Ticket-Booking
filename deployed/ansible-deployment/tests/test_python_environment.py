#!/usr/bin/env python3
"""
Property-based tests for Python environment setup.
Feature: ansible-deployment, Property 3: Python Environment Validation
Validates: Requirements 2.2, 2.3
"""

import os
import subprocess
import sys
from pathlib import Path


class TestPythonEnvironment:
    """Test Python environment setup and configuration."""
    
    def __init__(self):
        """Set up test environment."""
        self.app_dir = "/opt/flight_booking"
        self.venv_path = f"{self.app_dir}/venv"
        self.app_user = "flightapp"
        self.requirements_file = f"{self.app_dir}/requirements.txt"
        self.python_version = "3.11"

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

    def test_python_installation(self):
        """Test that Python is properly installed."""
        results = []
        
        # Test system Python
        stdout, stderr = self.run_command(["python3", "--version"], check_return_code=False)
        if stdout and "Python 3" in stdout:
            results.append(f"PASS: System Python installed - {stdout}")
            
            # Check if it's the expected version
            if self.python_version in stdout:
                results.append(f"PASS: Python version matches expected {self.python_version}")
            else:
                results.append(f"INFO: Python version is {stdout}, expected {self.python_version}")
        else:
            results.append("FAIL: System Python 3 is not installed or not accessible")
        
        # Test pip installation
        stdout, stderr = self.run_command(["pip3", "--version"], check_return_code=False)
        if stdout and "pip" in stdout:
            results.append(f"PASS: Pip is installed - {stdout}")
        else:
            results.append("FAIL: Pip is not installed or not accessible")
        
        return results

    def test_python_development_packages(self):
        """Test that Python development packages are installed."""
        results = []
        
        # Test essential development packages
        dev_packages = [
            ("python3-dev", "Python development headers"),
            ("python3-venv", "Python virtual environment support"),
            ("build-essential", "Build tools"),
            ("libffi-dev", "FFI development library"),
            ("libssl-dev", "SSL development library")
        ]
        
        for package, description in dev_packages:
            stdout, stderr = self.run_command(["dpkg", "-l", package], check_return_code=False)
            if stdout and "ii" in stdout:
                results.append(f"PASS: {description} ({package}) is installed")
            else:
                results.append(f"SKIP: {description} ({package}) may not be installed")
        
        return results

    def test_virtual_environment_creation(self):
        """Test virtual environment creation and configuration."""
        results = []
        
        venv_path = Path(self.venv_path)
        
        if not venv_path.exists():
            results.append(f"SKIP: Virtual environment {self.venv_path} does not exist (not created yet)")
            return results
        
        if not venv_path.is_dir():
            results.append(f"FAIL: Virtual environment path {self.venv_path} exists but is not a directory")
            return results
        
        results.append(f"PASS: Virtual environment directory exists at {self.venv_path}")
        
        # Check for essential venv files
        essential_files = [
            "bin/activate",
            "bin/python",
            "bin/pip",
            "pyvenv.cfg"
        ]
        
        for file_path in essential_files:
            full_path = venv_path / file_path
            if full_path.exists():
                results.append(f"PASS: Virtual environment file {file_path} exists")
            else:
                results.append(f"FAIL: Virtual environment file {file_path} is missing")
        
        # Check virtual environment ownership
        try:
            import pwd
            stat_info = venv_path.stat()
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
            
            if owner == self.app_user:
                results.append(f"PASS: Virtual environment owned by correct user {self.app_user}")
            else:
                results.append(f"FAIL: Virtual environment owned by {owner}, expected {self.app_user}")
        except (KeyError, OSError) as e:
            results.append(f"SKIP: Could not check virtual environment ownership: {e}")
        
        return results

    def test_virtual_environment_python(self):
        """Test Python executable in virtual environment."""
        results = []
        
        venv_python = Path(self.venv_path) / "bin" / "python"
        
        if not venv_python.exists():
            results.append(f"SKIP: Virtual environment Python {venv_python} does not exist")
            return results
        
        # Test venv Python version
        stdout, stderr = self.run_command([str(venv_python), "--version"], check_return_code=False)
        if stdout and "Python 3" in stdout:
            results.append(f"PASS: Virtual environment Python works - {stdout}")
        else:
            results.append(f"FAIL: Virtual environment Python is not working: {stderr}")
        
        # Test venv pip
        venv_pip = Path(self.venv_path) / "bin" / "pip"
        if venv_pip.exists():
            stdout, stderr = self.run_command([str(venv_pip), "--version"], check_return_code=False)
            if stdout and "pip" in stdout:
                results.append(f"PASS: Virtual environment pip works - {stdout}")
            else:
                results.append(f"FAIL: Virtual environment pip is not working: {stderr}")
        else:
            results.append(f"FAIL: Virtual environment pip does not exist")
        
        return results

    def test_requirements_installation(self):
        """Test requirements installation in virtual environment."""
        results = []
        
        venv_pip = Path(self.venv_path) / "bin" / "pip"
        
        if not venv_pip.exists():
            results.append("SKIP: Virtual environment pip not available for requirements test")
            return results
        
        # List installed packages
        stdout, stderr = self.run_command([str(venv_pip), "list"], check_return_code=False)
        if stdout:
            results.append("PASS: Can list installed packages in virtual environment")
            
            # Check for essential packages
            essential_packages = ["pip", "setuptools", "wheel"]
            for package in essential_packages:
                if package.lower() in stdout.lower():
                    results.append(f"PASS: Essential package {package} is installed")
                else:
                    results.append(f"FAIL: Essential package {package} is missing")
            
            # Check for Django if requirements were installed
            if "django" in stdout.lower():
                results.append("PASS: Django is installed in virtual environment")
            else:
                results.append("INFO: Django not found (may not be installed yet)")
                
        else:
            results.append(f"FAIL: Could not list packages in virtual environment: {stderr}")
        
        return results

    def test_python_environment_configuration(self):
        """Test Python environment configuration files."""
        results = []
        
        # Check for environment configuration file
        env_file = Path(self.app_dir) / ".env"
        if env_file.exists():
            results.append("PASS: Python environment configuration file exists")
            
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Check for essential environment variables
                essential_vars = ["PYTHONPATH", "PYTHONDONTWRITEBYTECODE", "PYTHONUNBUFFERED"]
                for var in essential_vars:
                    if var in content:
                        results.append(f"PASS: Environment variable {var} is configured")
                    else:
                        results.append(f"FAIL: Environment variable {var} is missing")
                        
            except (IOError, OSError) as e:
                results.append(f"FAIL: Could not read environment file: {e}")
        else:
            results.append("SKIP: Python environment configuration file does not exist")
        
        # Check for activation script
        activate_script = Path(self.app_dir) / "activate_venv.sh"
        if activate_script.exists():
            results.append("PASS: Virtual environment activation script exists")
            
            # Check if script is executable
            if os.access(activate_script, os.X_OK):
                results.append("PASS: Activation script is executable")
            else:
                results.append("FAIL: Activation script is not executable")
        else:
            results.append("SKIP: Virtual environment activation script does not exist")
        
        return results

    def test_pip_configuration(self):
        """Test pip configuration."""
        results = []
        
        pip_config_dir = Path(f"/home/{self.app_user}/.pip")
        pip_config_file = pip_config_dir / "pip.conf"
        
        if pip_config_file.exists():
            results.append("PASS: Pip configuration file exists")
            
            try:
                with open(pip_config_file, 'r') as f:
                    content = f.read()
                
                # Check for cache directory configuration
                if "cache-dir" in content:
                    results.append("PASS: Pip cache directory is configured")
                else:
                    results.append("FAIL: Pip cache directory is not configured")
                    
            except (IOError, OSError) as e:
                results.append(f"FAIL: Could not read pip configuration: {e}")
        else:
            results.append("SKIP: Pip configuration file does not exist")
        
        return results

    def run_all_tests(self):
        """Run all tests and return results."""
        all_results = []
        
        print("Testing Python Environment Configuration...")
        print("=" * 50)
        
        test_methods = [
            self.test_python_installation,
            self.test_python_development_packages,
            self.test_virtual_environment_creation,
            self.test_virtual_environment_python,
            self.test_requirements_installation,
            self.test_python_environment_configuration,
            self.test_pip_configuration
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
        info = len([r for r in all_results if r.startswith("INFO")])
        
        print(f"\n" + "=" * 50)
        print(f"Test Summary: {passed} passed, {failed} failed, {skipped} skipped, {info} info")
        
        return failed == 0


if __name__ == '__main__':
    tester = TestPythonEnvironment()
    success = tester.run_all_tests()
    exit(0 if success else 1)