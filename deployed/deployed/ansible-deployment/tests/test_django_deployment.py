#!/usr/bin/env python3
"""
Property-based tests for Django deployment.
Feature: ansible-deployment, Property 4: Database Migration Integrity
Validates: Requirements 2.4
"""

import os
import subprocess
import sqlite3
from pathlib import Path


class TestDjangoDeployment:
    """Test Django application deployment and database migrations."""
    
    def __init__(self):
        """Set up test environment."""
        self.app_dir = "/opt/flight_booking"
        self.venv_path = f"{self.app_dir}/venv"
        self.app_user = "flightapp"
        self.database_path = f"{self.app_dir}/db.sqlite3"
        self.static_root = f"{self.app_dir}/staticfiles"
        self.media_root = f"{self.app_dir}/media"
        self.log_dir = f"{self.app_dir}/logs"
        self.service_name = "flight_booking"

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

    def test_django_application_structure(self):
        """Test Django application directory structure."""
        results = []
        
        app_path = Path(self.app_dir)
        if not app_path.exists():
            results.append(f"SKIP: Application directory {self.app_dir} does not exist")
            return results
        
        results.append(f"PASS: Application directory {self.app_dir} exists")
        
        # Check for essential Django files
        essential_files = [
            "manage.py",
            "requirements.txt"
        ]
        
        for file_name in essential_files:
            file_path = app_path / file_name
            if file_path.exists():
                results.append(f"PASS: Essential file {file_name} exists")
            else:
                results.append(f"FAIL: Essential file {file_name} is missing")
        
        # Check for Django project structure
        project_indicators = [
            "*/settings.py",
            "*/wsgi.py",
            "*/urls.py"
        ]
        
        for pattern in project_indicators:
            matching_files = list(app_path.glob(pattern))
            if matching_files:
                results.append(f"PASS: Django project structure found - {pattern}")
            else:
                results.append(f"FAIL: Django project structure missing - {pattern}")
        
        return results

    def test_django_directories(self):
        """Test Django application directories."""
        results = []
        
        required_dirs = [
            (self.static_root, "Static files directory"),
            (self.media_root, "Media files directory"),
            (self.log_dir, "Log directory"),
            (f"{self.app_dir}/tmp", "Temporary directory")
        ]
        
        for dir_path, description in required_dirs:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                results.append(f"PASS: {description} exists at {dir_path}")
                
                # Check ownership
                try:
                    import pwd
                    stat_info = path.stat()
                    owner = pwd.getpwuid(stat_info.st_uid).pw_name
                    
                    if owner == self.app_user:
                        results.append(f"PASS: {description} owned by correct user {self.app_user}")
                    else:
                        results.append(f"FAIL: {description} owned by {owner}, expected {self.app_user}")
                except (KeyError, OSError):
                    results.append(f"SKIP: Could not check ownership of {description}")
                    
            else:
                results.append(f"SKIP: {description} does not exist at {dir_path}")
        
        return results

    def test_database_setup(self):
        """Test Django database setup and migrations."""
        results = []
        
        db_path = Path(self.database_path)
        if not db_path.exists():
            results.append(f"SKIP: Database file {self.database_path} does not exist")
            return results
        
        results.append(f"PASS: Database file exists at {self.database_path}")
        
        # Test database connectivity
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Check if Django tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations';")
            migrations_table = cursor.fetchone()
            
            if migrations_table:
                results.append("PASS: Django migrations table exists")
                
                # Check if migrations have been applied
                cursor.execute("SELECT COUNT(*) FROM django_migrations;")
                migration_count = cursor.fetchone()[0]
                
                if migration_count > 0:
                    results.append(f"PASS: Database migrations applied ({migration_count} migrations)")
                else:
                    results.append("FAIL: No database migrations found")
            else:
                results.append("FAIL: Django migrations table does not exist")
            
            # Check for application tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%flight%';")
            app_tables = cursor.fetchall()
            
            if app_tables:
                results.append(f"PASS: Application tables found: {[table[0] for table in app_tables]}")
            else:
                results.append("INFO: No application-specific tables found (may be expected)")
            
            conn.close()
            
        except sqlite3.Error as e:
            results.append(f"FAIL: Database error: {e}")
        except Exception as e:
            results.append(f"FAIL: Could not test database: {e}")
        
        return results

    def test_static_files_collection(self):
        """Test Django static files collection."""
        results = []
        
        static_path = Path(self.static_root)
        if not static_path.exists():
            results.append(f"SKIP: Static files directory {self.static_root} does not exist")
            return results
        
        results.append(f"PASS: Static files directory exists at {self.static_root}")
        
        # Check for Django admin static files (indicates collectstatic was run)
        admin_static = static_path / "admin"
        if admin_static.exists():
            results.append("PASS: Django admin static files collected")
            
            # Check for specific admin files
            admin_files = ["css/base.css", "js/admin/RelatedObjectLookups.js"]
            for admin_file in admin_files:
                admin_file_path = admin_static / admin_file
                if admin_file_path.exists():
                    results.append(f"PASS: Admin static file {admin_file} exists")
                else:
                    results.append(f"FAIL: Admin static file {admin_file} missing")
        else:
            results.append("FAIL: Django admin static files not collected")
        
        # Check static files permissions
        try:
            import pwd
            stat_info = static_path.stat()
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
            
            if owner == self.app_user:
                results.append(f"PASS: Static files owned by correct user {self.app_user}")
            else:
                results.append(f"FAIL: Static files owned by {owner}, expected {self.app_user}")
        except (KeyError, OSError):
            results.append("SKIP: Could not check static files ownership")
        
        return results

    def test_django_service(self):
        """Test Django systemd service."""
        results = []
        
        # Check if service file exists
        service_file = Path(f"/etc/systemd/system/{self.service_name}.service")
        if service_file.exists():
            results.append(f"PASS: Systemd service file exists for {self.service_name}")
        else:
            results.append(f"SKIP: Systemd service file does not exist for {self.service_name}")
            return results
        
        # Check service status
        stdout, stderr = self.run_command(["systemctl", "is-active", self.service_name], check_return_code=False)
        if stdout == "active":
            results.append(f"PASS: Django service {self.service_name} is active")
        else:
            results.append(f"FAIL: Django service {self.service_name} is not active (status: {stdout})")
        
        # Check if service is enabled
        stdout, stderr = self.run_command(["systemctl", "is-enabled", self.service_name], check_return_code=False)
        if stdout == "enabled":
            results.append(f"PASS: Django service {self.service_name} is enabled")
        else:
            results.append(f"FAIL: Django service {self.service_name} is not enabled (status: {stdout})")
        
        return results

    def test_gunicorn_configuration(self):
        """Test Gunicorn configuration."""
        results = []
        
        gunicorn_config = Path(self.app_dir) / "gunicorn.conf.py"
        if gunicorn_config.exists():
            results.append("PASS: Gunicorn configuration file exists")
            
            try:
                with open(gunicorn_config, 'r') as f:
                    content = f.read()
                
                # Check for essential Gunicorn settings
                essential_settings = ["bind", "workers", "timeout", "user", "group"]
                for setting in essential_settings:
                    if setting in content:
                        results.append(f"PASS: Gunicorn setting '{setting}' configured")
                    else:
                        results.append(f"FAIL: Gunicorn setting '{setting}' missing")
                        
            except (IOError, OSError) as e:
                results.append(f"FAIL: Could not read Gunicorn configuration: {e}")
        else:
            results.append("SKIP: Gunicorn configuration file does not exist")
        
        return results

    def test_django_environment_configuration(self):
        """Test Django environment configuration."""
        results = []
        
        env_file = Path(self.app_dir) / ".env"
        if env_file.exists():
            results.append("PASS: Django environment file exists")
            
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Check for essential Django environment variables
                essential_vars = ["SECRET_KEY", "DEBUG", "ALLOWED_HOSTS", "DJANGO_SETTINGS_MODULE"]
                for var in essential_vars:
                    if var in content:
                        results.append(f"PASS: Environment variable '{var}' configured")
                    else:
                        results.append(f"FAIL: Environment variable '{var}' missing")
                        
            except (IOError, OSError) as e:
                results.append(f"FAIL: Could not read environment file: {e}")
        else:
            results.append("SKIP: Django environment file does not exist")
        
        return results

    def run_all_tests(self):
        """Run all tests and return results."""
        all_results = []
        
        print("Testing Django Deployment...")
        print("=" * 50)
        
        test_methods = [
            self.test_django_application_structure,
            self.test_django_directories,
            self.test_database_setup,
            self.test_static_files_collection,
            self.test_django_service,
            self.test_gunicorn_configuration,
            self.test_django_environment_configuration
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
    tester = TestDjangoDeployment()
    success = tester.run_all_tests()
    exit(0 if success else 1)