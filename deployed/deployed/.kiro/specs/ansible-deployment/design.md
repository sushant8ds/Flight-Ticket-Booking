# Design Document: Ansible Deployment Automation

## Overview

This design document outlines the architecture and implementation approach for automating the deployment of the Django Flight Ticket Booking application using Ansible. The solution provides a comprehensive automation framework that handles server provisioning, application deployment, configuration management, and operational tasks across multiple environments.

The design follows Ansible best practices with a modular role-based architecture, supporting both traditional server deployments and containerized Docker deployments. The system is designed to be environment-agnostic, supporting development, staging, and production deployments with appropriate configuration management.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Control Node"
        AC[Ansible Controller]
        PB[Playbooks]
        INV[Inventory]
        VAULT[Ansible Vault]
    end
    
    subgraph "Target Infrastructure"
        subgraph "Load Balancer"
            LB[Nginx Load Balancer]
        end
        
        subgraph "Application Servers"
            AS1[App Server 1<br/>Django + Gunicorn]
            AS2[App Server 2<br/>Django + Gunicorn]
            AS3[App Server N<br/>Django + Gunicorn]
        end
        
        subgraph "Database"
            DB[(SQLite/PostgreSQL)]
        end
        
        subgraph "Monitoring"
            MON[Health Checks<br/>Log Aggregation]
        end
    end
    
    AC --> LB
    AC --> AS1
    AC --> AS2
    AC --> AS3
    AC --> DB
    AC --> MON
    
    LB --> AS1
    LB --> AS2
    LB --> AS3
    
    AS1 --> DB
    AS2 --> DB
    AS3 --> DB
```

### Deployment Architecture Options

The system supports two primary deployment architectures:

1. **Traditional Deployment**: Direct installation on target servers with systemd service management
2. **Containerized Deployment**: Docker-based deployment with container orchestration

Both architectures share common infrastructure components (Nginx, monitoring, security) but differ in application runtime management.

## Components and Interfaces

### Ansible Project Structure

```
ansible-deployment/
├── ansible.cfg                 # Ansible configuration
├── requirements.yml            # Ansible Galaxy requirements
├── site.yml                   # Main playbook entry point
├── inventories/               # Environment-specific inventories
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   ├── staging/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
├── group_vars/               # Global group variables
│   ├── all.yml
│   └── vault.yml            # Encrypted secrets
├── host_vars/               # Host-specific variables
├── roles/                   # Custom roles
│   ├── common/             # Base system configuration
│   ├── python/             # Python environment setup
│   ├── django-app/         # Django application deployment
│   ├── nginx/              # Web server configuration
│   ├── database/           # Database setup and management
│   ├── docker/             # Docker deployment (optional)
│   ├── monitoring/         # Health checks and monitoring
│   └── security/           # Security hardening
├── playbooks/              # Specific operation playbooks
│   ├── deploy.yml          # Application deployment
│   ├── rollback.yml        # Rollback operations
│   ├── backup.yml          # Database backup
│   └── maintenance.yml     # Maintenance tasks
└── files/                  # Static files and templates
    ├── nginx/
    ├── systemd/
    └── scripts/
```

### Core Roles Design

#### 1. Common Role
**Purpose**: Base system configuration and hardening
**Responsibilities**:
- System package installation and updates
- User account management
- SSH configuration and security
- Firewall setup
- Timezone and locale configuration

**Key Tasks**:
- Install essential packages (git, curl, wget, unzip)
- Create application user with appropriate permissions
- Configure SSH key-based authentication
- Set up UFW firewall rules
- Configure system timezone and locale

#### 2. Python Role
**Purpose**: Python environment setup and management
**Responsibilities**:
- Python installation and version management
- Virtual environment creation
- Package dependency management
- Environment variable configuration

**Key Tasks**:
- Install Python 3.11+ and pip
- Create and activate virtual environment
- Install requirements from requirements.txt
- Configure Python path and environment variables

#### 3. Django-App Role
**Purpose**: Django application deployment and configuration
**Responsibilities**:
- Source code deployment
- Database migration execution
- Static file collection
- Application service management

**Key Tasks**:
- Clone/update application code from repository
- Run Django migrations
- Collect static files
- Configure Gunicorn service
- Set up application logging

#### 4. Nginx Role
**Purpose**: Web server configuration and SSL setup
**Responsibilities**:
- Nginx installation and configuration
- Virtual host setup
- SSL certificate management
- Load balancing configuration

**Key Tasks**:
- Install and configure Nginx
- Create virtual host configurations
- Set up SSL with Let's Encrypt (optional)
- Configure reverse proxy to Gunicorn
- Set up static file serving

#### 5. Database Role
**Purpose**: Database setup and management
**Responsibilities**:
- Database initialization
- Migration execution
- Backup configuration
- Data loading

**Key Tasks**:
- Initialize SQLite database with proper permissions
- Load initial data from CSV files
- Set up automated backup scripts
- Configure database connection settings

#### 6. Docker Role (Optional)
**Purpose**: Containerized deployment management
**Responsibilities**:
- Docker installation and configuration
- Container image building
- Docker Compose orchestration
- Container health monitoring

**Key Tasks**:
- Install Docker and Docker Compose
- Build application Docker image
- Deploy using Docker Compose
- Configure container networking and volumes

#### 7. Monitoring Role
**Purpose**: Application and system monitoring
**Responsibilities**:
- Health check configuration
- Log management
- Performance monitoring
- Alert configuration

**Key Tasks**:
- Set up application health endpoints
- Configure log rotation
- Install monitoring agents
- Set up notification channels

#### 8. Security Role
**Purpose**: System security hardening
**Responsibilities**:
- Security configuration
- Access control
- Vulnerability management
- Compliance enforcement

**Key Tasks**:
- Disable unnecessary services
- Configure fail2ban
- Set up automatic security updates
- Implement security headers

### Playbook Design

#### Main Site Playbook (site.yml)
```yaml
---
- name: Deploy Django Flight Booking Application
  hosts: all
  become: yes
  gather_facts: yes
  
  pre_tasks:
    - name: Update package cache
      apt:
        update_cache: yes
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"
  
  roles:
    - common
    - security
    - python
    - { role: docker, when: deployment_method == "docker" }
    - { role: django-app, when: deployment_method == "traditional" }
    - nginx
    - database
    - monitoring
  
  post_tasks:
    - name: Verify deployment
      uri:
        url: "http://{{ ansible_default_ipv4.address }}"
        method: GET
        status_code: 200
      delegate_to: localhost
```

#### Deployment Playbook (playbooks/deploy.yml)
```yaml
---
- name: Deploy Application Updates
  hosts: webservers
  become: yes
  serial: 1  # Rolling deployment
  
  pre_tasks:
    - name: Create deployment backup
      include_role:
        name: database
        tasks_from: backup
  
  roles:
    - django-app
  
  post_tasks:
    - name: Verify application health
      uri:
        url: "http://{{ ansible_default_ipv4.address }}/health/"
        method: GET
        status_code: 200
      retries: 5
      delay: 10
```

## Data Models

### Inventory Structure

#### Development Environment
```yaml
# inventories/development/hosts.yml
all:
  children:
    webservers:
      hosts:
        dev-web-01:
          ansible_host: 192.168.1.10
          ansible_user: ubuntu
    databases:
      hosts:
        dev-web-01:  # Same server for development
    loadbalancers:
      hosts:
        dev-web-01:  # Same server for development
```

#### Production Environment
```yaml
# inventories/production/hosts.yml
all:
  children:
    webservers:
      hosts:
        prod-web-01:
          ansible_host: 10.0.1.10
        prod-web-02:
          ansible_host: 10.0.1.11
        prod-web-03:
          ansible_host: 10.0.1.12
    databases:
      hosts:
        prod-db-01:
          ansible_host: 10.0.2.10
    loadbalancers:
      hosts:
        prod-lb-01:
          ansible_host: 10.0.3.10
```

### Variable Structure

#### Global Variables (group_vars/all.yml)
```yaml
# Application Configuration
app_name: flight_booking
app_user: flightapp
app_group: flightapp
app_port: 8000

# Repository Configuration
repo_url: https://github.com/user/Flight-Ticket-Booking.git
repo_branch: main
app_dir: /opt/{{ app_name }}

# Python Configuration
python_version: "3.11"
venv_dir: "{{ app_dir }}/venv"

# Database Configuration
database_name: "{{ app_name }}"
database_path: "{{ app_dir }}/db.sqlite3"

# Nginx Configuration
nginx_server_name: "{{ ansible_default_ipv4.address }}"
nginx_client_max_body_size: 50M

# SSL Configuration
ssl_enabled: false
ssl_cert_email: admin@example.com

# Backup Configuration
backup_dir: /opt/backups
backup_retention_days: 30
```

#### Environment-Specific Variables
```yaml
# inventories/production/group_vars/all.yml
debug_mode: false
allowed_hosts:
  - "{{ nginx_server_name }}"
  - "production.example.com"

ssl_enabled: true
nginx_server_name: production.example.com

# Database backup schedule
backup_schedule: "0 2 * * *"  # Daily at 2 AM

# Security settings
fail2ban_enabled: true
automatic_updates: true
```

### Secret Management

#### Vault Structure (group_vars/vault.yml)
```yaml
# Encrypted with ansible-vault
vault_django_secret_key: "your-secret-key-here"
vault_database_password: "secure-password"
vault_ssl_cert_email: "admin@yourdomain.com"

# GitHub deploy key (if using private repo)
vault_deploy_key: |
  -----BEGIN OPENSSH PRIVATE KEY-----
  ...
  -----END OPENSSH PRIVATE KEY-----
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Idempotent Deployment
*For any* target server and deployment configuration, running the Ansible playbook multiple times should produce the same end state without errors or unintended changes.
**Validates: Requirements 2.1, 2.6**

### Property 2: Service Availability During Rolling Updates
*For any* multi-server deployment, updating one server at a time should maintain overall service availability with at least one server responding to requests.
**Validates: Requirements 10.5**

### Property 3: Configuration Consistency
*For any* environment deployment, all servers in the same environment group should have identical configuration files and service states.
**Validates: Requirements 5.1, 10.4**

### Property 4: Database Migration Integrity
*For any* Django application deployment, database migrations should be applied in the correct order and complete successfully before the application starts serving requests.
**Validates: Requirements 3.2**

### Property 5: Rollback State Restoration
*For any* failed deployment, executing the rollback playbook should restore the system to the previous working state with all services operational.
**Validates: Requirements 8.1, 8.2**

### Property 6: Security Configuration Enforcement
*For any* server provisioning, security hardening tasks should disable unnecessary services, configure firewalls, and implement secure SSH access.
**Validates: Requirements 9.1, 9.2, 9.4**

### Property 7: Health Check Validation
*For any* completed deployment, health check endpoints should return successful responses indicating all application components are functioning correctly.
**Validates: Requirements 7.1, 7.2, 7.3**

### Property 8: Environment Variable Isolation
*For any* environment-specific deployment, only the appropriate environment variables and secrets should be accessible to the application.
**Validates: Requirements 5.2, 5.4**

### Property 9: Static File Serving
*For any* web server configuration, static files should be served directly by Nginx without proxying to the Django application.
**Validates: Requirements 4.4**

### Property 10: Backup Creation and Restoration
*For any* database backup operation, the created backup should be restorable and produce a functionally equivalent database state.
**Validates: Requirements 3.4, 8.4**

## Error Handling

### Deployment Failure Recovery

The system implements comprehensive error handling at multiple levels:

1. **Task-Level Error Handling**
   - Each critical task includes error conditions and retry logic
   - Failed tasks trigger appropriate rollback procedures
   - Error messages provide actionable information for troubleshooting

2. **Service Validation**
   - Post-deployment health checks verify service functionality
   - Failed health checks trigger automatic rollback
   - Service startup failures are logged with detailed error information

3. **Database Migration Safety**
   - Migration tasks include backup creation before execution
   - Failed migrations trigger automatic database restoration
   - Migration state is tracked to prevent partial application

4. **Network and Connectivity Issues**
   - Repository access failures include retry logic with exponential backoff
   - Network timeouts are handled gracefully with appropriate error messages
   - SSH connection failures provide clear troubleshooting guidance

### Rollback Mechanisms

1. **Application Code Rollback**
   - Previous version tracking using Git tags or commit hashes
   - Automated rollback to last known good deployment
   - Service restart with previous configuration

2. **Database Rollback**
   - Pre-deployment database snapshots
   - Migration rollback procedures
   - Data integrity verification after rollback

3. **Configuration Rollback**
   - Configuration file versioning
   - Service configuration restoration
   - Nginx configuration rollback with reload

## Testing Strategy

### Unit Testing Approach

**Ansible Playbook Testing**:
- Use `ansible-playbook --check` for dry-run validation
- Test individual roles in isolation using molecule framework
- Validate YAML syntax and Ansible best practices using ansible-lint
- Test variable interpolation and template rendering

**Infrastructure Testing**:
- Verify service installation and configuration
- Test file permissions and ownership
- Validate network connectivity and port accessibility
- Check user account creation and permissions

### Property-Based Testing Configuration

**Testing Framework**: Molecule with Docker driver for role testing, Testinfra for infrastructure validation

**Test Configuration**:
- Minimum 100 test scenarios per property test
- Each property test references its design document property
- Tag format: **Feature: ansible-deployment, Property {number}: {property_text}**

**Property Test Implementation**:
- **Property 1**: Test idempotency by running playbooks multiple times and comparing system state
- **Property 2**: Test rolling updates by monitoring service availability during deployments
- **Property 3**: Test configuration consistency by comparing files across multiple servers
- **Property 4**: Test migration integrity by validating database schema after deployments
- **Property 5**: Test rollback functionality by inducing failures and verifying restoration
- **Property 6**: Test security configuration by scanning for open ports and service states
- **Property 7**: Test health checks by making HTTP requests to deployed applications
- **Property 8**: Test environment isolation by verifying variable accessibility
- **Property 9**: Test static file serving by requesting static assets directly
- **Property 10**: Test backup/restore by creating backups and restoring to new instances

**Integration Testing**:
- End-to-end deployment testing in isolated environments
- Multi-environment deployment validation
- Load balancer configuration testing
- SSL certificate generation and renewal testing

**Performance Testing**:
- Deployment time measurement and optimization
- Resource utilization monitoring during deployments
- Concurrent deployment testing for multi-server environments
- Network bandwidth usage optimization