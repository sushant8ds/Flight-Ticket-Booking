# 🚀 Render Cloud Deployment Guide - Django Flight Booking System

## 📋 Overview

This guide provides comprehensive instructions for deploying the Django Flight Booking System to Render cloud platform with complete DevOps infrastructure including MongoDB, Redis caching, and monitoring capabilities.

---

## 🎯 Deployment Options

### Option 1: Standard Deployment (PostgreSQL + Redis)
- **Configuration**: `render.yaml`
- **Database**: PostgreSQL (Render managed)
- **Cache**: Redis (Render managed)
- **Best for**: Production deployments with managed services

### Option 2: MongoDB Deployment (MongoDB + Redis)
- **Configuration**: `render-mongodb.yaml`
- **Database**: MongoDB (containerized)
- **Cache**: Redis (Render managed)
- **Best for**: Applications requiring MongoDB features

---

## 🔧 Pre-Deployment Setup

### 1. Repository Preparation

```bash
# Ensure all deployment files are present
ls -la render*.yaml build-render.sh requirements-render.txt

# Test deployment configuration
./deploy-render.sh
```

### 2. Required Files Checklist

- ✅ `render.yaml` - Standard deployment configuration
- ✅ `render-mongodb.yaml` - MongoDB deployment configuration
- ✅ `build-render.sh` - Build script for Render
- ✅ `requirements-render.txt` - Python dependencies
- ✅ `capstone/settings_render.py` - Render-specific Django settings
- ✅ `Dockerfile.render` - Docker configuration
- ✅ `mongodb/Dockerfile` - MongoDB container configuration
- ✅ `mongodb/mongo-init.js` - MongoDB initialization script

---

## 🚀 Deployment Steps

### Step 1: GitHub Repository Setup

1. **Push code to GitHub**:
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

2. **Ensure repository is public or accessible to Render**

### Step 2: Render Account Setup

1. **Create Render Account**:
   - Visit [render.com](https://render.com)
   - Sign up with GitHub account
   - Verify email address

2. **Connect GitHub Repository**:
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing your Django app

### Step 3: Service Configuration

#### For Standard Deployment (PostgreSQL):

1. **Web Service Configuration**:
   - **Name**: `flight-booking-app`
   - **Runtime**: `Python 3`
   - **Build Command**: `sh build-render.sh`
   - **Start Command**: `gunicorn capstone.wsgi:application --bind 0.0.0.0:$PORT --workers 3`

2. **Environment Variables**:
```bash
DEBUG=False
DJANGO_SETTINGS_MODULE=capstone.settings_render
SECRET_KEY=[auto-generated]
ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
```

3. **Add PostgreSQL Database**:
   - Go to Dashboard → "New +" → "PostgreSQL"
   - Name: `flight-booking-db`
   - Plan: Free or Starter
   - Copy DATABASE_URL to web service environment

4. **Add Redis Cache**:
   - Go to Dashboard → "New +" → "Redis"
   - Name: `flight-booking-redis`
   - Plan: Starter
   - Copy REDIS_URL to web service environment

#### For MongoDB Deployment:

1. **Use Blueprint Deployment**:
   - In repository root, ensure `render-mongodb.yaml` is present
   - Render will automatically detect and use this configuration
   - All services (Web, MongoDB, Redis) will be created automatically

2. **Manual Service Creation** (Alternative):
   - Create Web Service as above
   - Create Private Service for MongoDB using `mongodb/Dockerfile`
   - Create Redis service
   - Configure environment variables to connect services

---

## 🔐 Environment Variables Configuration

### Required Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DEBUG` | `False` | Disable debug mode for production |
| `DJANGO_SETTINGS_MODULE` | `capstone.settings_render` | Use Render-specific settings |
| `SECRET_KEY` | `[auto-generated]` | Django secret key (let Render generate) |
| `ALLOWED_HOSTS` | `.onrender.com,localhost,127.0.0.1` | Allowed hostnames |
| `DATABASE_URL` | `[auto-provided]` | PostgreSQL connection string |
| `MONGODB_URI` | `[from MongoDB service]` | MongoDB connection string |
| `REDIS_URL` | `[auto-provided]` | Redis connection string |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_NAME` | `flight_booking_db` | MongoDB database name |
| `EMAIL_BACKEND` | `console` | Email backend configuration |
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP server for emails |

---

## 📊 Service Architecture

### Standard Deployment Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │   PostgreSQL    │    │     Redis       │
│  (Django App)   │◄──►│   Database      │    │     Cache       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### MongoDB Deployment Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │ Private Service │    │     Redis       │
│  (Django App)   │◄──►│   (MongoDB)     │    │     Cache       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🔍 Health Monitoring

### Health Check Endpoints

1. **Application Health**: `https://your-app.onrender.com/health/`
   - Returns JSON with service status
   - Checks database, cache, and MongoDB connections
   - HTTP 200 for healthy, 503 for degraded

2. **Readiness Check**: `https://your-app.onrender.com/ready/`
   - Verifies application is ready to serve traffic
   - Performs basic database operations
   - HTTP 200 for ready, 503 for not ready

### Sample Health Response
```json
{
  "status": "healthy",
  "timestamp": "2026-01-13T12:00:00Z",
  "services": {
    "database": "healthy",
    "cache": "healthy", 
    "mongodb": "healthy"
  }
}
```

---

## 🛠️ Build Process

### Build Script (`build-render.sh`)

The build script performs the following operations:

1. **Dependency Installation**:
```bash
pip install --upgrade pip
pip install -r requirements-render.txt
```

2. **Static Files Collection**:
```bash
python manage.py collectstatic --noinput --clear
```

3. **Database Migration**:
```bash
python manage.py migrate --noinput
```

4. **Superuser Creation**:
```bash
# Creates admin user if it doesn't exist
python manage.py shell -c "create_superuser_script"
```

5. **Initial Data Loading**:
```bash
# Loads flight data if database is empty
python manage.py shell -c "load_initial_data_script"
```

---

## 🔒 Security Configuration

### Production Security Settings

1. **HTTPS Enforcement**:
```python
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

2. **Security Headers**:
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
```

3. **Cookie Security**:
```python
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### CORS Configuration
```python
CORS_ALLOWED_ORIGINS = [
    "https://your-app.onrender.com",
    "http://localhost:3000",  # For development
]
```

---

## 📈 Performance Optimization

### Gunicorn Configuration
```bash
gunicorn capstone.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 3 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### Static Files (WhiteNoise)
- Automatic compression and caching
- CDN-ready static file serving
- Optimized for production performance

### Database Optimization
- Connection pooling enabled
- Query optimization with indexes
- Redis caching for frequent queries

---

## 🧪 Testing Deployment

### Local Testing

1. **Test Render Settings**:
```bash
export DJANGO_SETTINGS_MODULE=capstone.settings_render
python manage.py check
python manage.py runserver
```

2. **Test Build Script**:
```bash
./build-render.sh
```

3. **Test Health Endpoints**:
```bash
curl http://localhost:8000/health/
curl http://localhost:8000/ready/
```

### Production Testing

1. **Application Access**:
```bash
curl https://your-app.onrender.com/
```

2. **Health Monitoring**:
```bash
curl https://your-app.onrender.com/health/
curl https://your-app.onrender.com/ready/
```

3. **Admin Panel**:
```bash
# Visit: https://your-app.onrender.com/admin/
# Login: admin / admin123
```

---

## 📊 Monitoring & Logging

### Render Dashboard Monitoring

1. **Service Metrics**:
   - CPU and memory usage
   - Request rates and response times
   - Error rates and status codes

2. **Log Streaming**:
   - Real-time application logs
   - Build and deployment logs
   - Error tracking and debugging

### Application Logging

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

---

## 🔄 CI/CD Integration

### Automatic Deployments

1. **GitHub Integration**:
   - Automatic deployments on push to main branch
   - Build status notifications
   - Rollback capabilities

2. **Deploy Hooks**:
```bash
# Add to render.yaml for custom deploy hooks
buildCommand: |
  sh build-render.sh
  python manage.py test
  python manage.py check --deploy
```

### Manual Deployments

1. **Render Dashboard**:
   - Manual deploy button
   - Deploy specific commits
   - Environment-specific deployments

2. **CLI Deployment**:
```bash
# Using Render CLI (if available)
render deploy --service flight-booking-app
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**:
```bash
# Check build logs in Render dashboard
# Verify requirements-render.txt
# Test build script locally
```

2. **Database Connection Issues**:
```bash
# Verify DATABASE_URL environment variable
# Check database service status
# Test connection in Django shell
```

3. **Static Files Not Loading**:
```bash
# Verify STATIC_ROOT and STATIC_URL settings
# Check WhiteNoise configuration
# Ensure collectstatic runs in build
```

4. **MongoDB Connection Issues**:
```bash
# Verify MONGODB_URI environment variable
# Check MongoDB service logs
# Test connection with pymongo
```

### Debug Commands

```bash
# Check Django configuration
python manage.py check --deploy

# Test database connection
python manage.py dbshell

# Verify static files
python manage.py collectstatic --dry-run

# Test MongoDB connection
python manage.py shell -c "import pymongo; print('MongoDB OK')"
```

---

## 📚 Additional Resources

### Render Documentation
- [Render Python Guide](https://render.com/docs/python)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render Databases](https://render.com/docs/databases)

### Django Deployment
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Django Static Files](https://docs.djangoproject.com/en/4.2/howto/static-files/deployment/)

### MongoDB Resources
- [MongoDB Atlas](https://www.mongodb.com/atlas)
- [MongoEngine Documentation](http://mongoengine.org/)

---

## 🎉 Deployment Success Checklist

### Pre-Deployment
- [ ] All configuration files present
- [ ] Environment variables configured
- [ ] Build script tested locally
- [ ] Health endpoints working
- [ ] Static files collecting properly

### Post-Deployment
- [ ] Application accessible via HTTPS
- [ ] Health endpoints returning 200
- [ ] Admin panel accessible
- [ ] Database operations working
- [ ] Static files loading correctly
- [ ] Logs showing no errors

### Production Readiness
- [ ] SSL certificate active
- [ ] Custom domain configured (optional)
- [ ] Monitoring alerts set up
- [ ] Backup strategy implemented
- [ ] Performance testing completed

---

## 🏆 Success Metrics

### Performance Targets
- **Response Time**: < 500ms for 95% of requests
- **Uptime**: > 99.5% availability
- **Error Rate**: < 1% of total requests
- **Build Time**: < 5 minutes

### Monitoring KPIs
- Application health status
- Database connection stability
- Cache hit rates
- Static file delivery performance

---

**🚀 Your Django Flight Booking System is now ready for Render cloud deployment!**

**Next Steps:**
1. Run `./deploy-render.sh` to validate configuration
2. Push code to GitHub repository
3. Create Render services using `render.yaml`
4. Monitor deployment and test application
5. Configure custom domain and SSL (optional)

**Support:** For deployment issues, check Render documentation or contact support through the Render dashboard.

---

*Deployment Guide Version: 1.0*  
*Last Updated: January 13, 2026*  
*Compatible with: Django 4.2+, Python 3.11+, Render Platform*