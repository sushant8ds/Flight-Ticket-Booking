# Ansible Deployment for Django Flight Booking Application

This Ansible project provides automated deployment and configuration management for the Django Flight Booking application.

## Features

- **Multi-environment support**: Development, staging, and production configurations
- **Security hardening**: SSH configuration, firewall setup, fail2ban integration
- **System configuration**: User management, package installation, system tuning
- **Comprehensive testing**: Property-based tests for validation
- **Modular design**: Role-based architecture for maintainability

## Project Structure

```
ansible-deployment/
├── ansible.cfg                 # Ansible configuration
├── requirements.yml            # Galaxy requirements
├── site.yml                   # Main playbook
├── inventories/               # Environment inventories
│   ├── development/
│   ├── staging/
│   └── production/
├── group_vars/               # Global variables
├── roles/                    # Custom roles
│   ├── common/              # Base system configuration
│   └── security/            # Security hardening
├── tests/                   # Property-based tests
└── playbooks/              # Specific operation playbooks
```

## Quick Start

### Prerequisites

1. Install Ansible (version 2.9+)
2. Install required collections:
   ```bash
   ansible-galaxy install -r requirements.yml
   ```

### Basic Usage

1. **Configure inventory**: Update `inventories/development/hosts.yml` with your server details
2. **Set variables**: Modify `group_vars/all.yml` and environment-specific variables
3. **Run deployment**:
   ```bash
   ansible-playbook -i inventories/development/hosts.yml site.yml
   ```

### Environment-Specific Deployment

```bash
# Development
ansible-playbook -i inventories/development/hosts.yml site.yml

# Staging  
ansible-playbook -i inventories/staging/hosts.yml site.yml

# Production
ansible-playbook -i inventories/production/hosts.yml site.yml
```

## Configuration

### Global Variables (`group_vars/all.yml`)

Key configuration options:

- `app_name`: Application name (default: flight_booking)
- `app_user`: Application user (default: flightapp)
- `app_port`: Application port (default: 8000)
- `repo_url`: Git repository URL
- `python_version`: Python version (default: 3.11)

### Environment Variables

Each environment has specific configurations in `inventories/{env}/group_vars/all.yml`:

- **Development**: Debug enabled, SSL disabled, relaxed security
- **Staging**: Production-like with SSL, moderate security
- **Production**: Full security hardening, SSL required

### Security Configuration

Security features can be controlled via variables:

- `fail2ban_enabled`: Enable/disable fail2ban (default: true)
- `firewall_enabled`: Enable/disable firewall (default: true)
- `automatic_updates`: Enable automatic security updates
- `ssl_enabled`: Enable SSL/TLS configuration

## Roles

### Common Role

Handles base system configuration:
- System package installation
- User account management
- System configuration (timezone, locale, limits)
- Service management

### Security Role

Implements security hardening:
- SSH daemon hardening
- Firewall configuration (UFW/firewalld)
- Fail2ban setup
- System hardening
- Automatic security updates

## Testing

The project includes comprehensive property-based tests:

```bash
# Test project structure
python3 tests/test_project_structure.py

# Test user accounts (after deployment)
python3 tests/test_user_accounts.py

# Test security configuration (after deployment)
python3 tests/test_security_configuration.py
```

## Playbook Tags

Use tags to run specific parts of the deployment:

```bash
# Only security hardening
ansible-playbook site.yml --tags security

# Only common system setup
ansible-playbook site.yml --tags common

# Skip security hardening
ansible-playbook site.yml --skip-tags security
```

## Troubleshooting

### Common Issues

1. **SSH Connection Issues**:
   - Verify SSH key authentication is set up
   - Check firewall rules allow SSH access
   - Ensure target user has sudo privileges

2. **Permission Errors**:
   - Verify `become: yes` is set in playbook
   - Check sudo configuration for target user

3. **Package Installation Failures**:
   - Update package cache: `apt update`
   - Check internet connectivity on target hosts

### Verification

After deployment, verify the setup:

```bash
# Check services
systemctl status ssh
systemctl status fail2ban
ufw status

# Check user creation
id flightapp
ls -la /opt/flight_booking

# Check security configuration
sudo sshd -t
fail2ban-client status
```

## Security Considerations

This deployment implements several security best practices:

- SSH hardening (disable root login, password auth)
- Firewall configuration with minimal open ports
- Fail2ban for intrusion prevention
- Automatic security updates
- Proper file permissions
- Service account with minimal privileges

## Contributing

When adding new features:

1. Follow the existing role structure
2. Add appropriate tags to tasks
3. Include property-based tests
4. Update documentation
5. Test across all supported environments

## License

MIT License - see LICENSE file for details.