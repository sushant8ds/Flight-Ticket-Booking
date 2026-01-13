"""
Health check URLs for Render deployment
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Render deployment
    """
    try:
        # Basic health check
        from django.db import connection
        from django.core.cache import cache
        
        health_status = {
            "status": "healthy",
            "timestamp": "2026-01-13T12:00:00Z",
            "services": {
                "database": "unknown",
                "cache": "unknown",
                "mongodb": "unknown"
            }
        }
        
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status["services"]["database"] = "healthy"
        except Exception as e:
            health_status["services"]["database"] = f"unhealthy: {str(e)}"
        
        # Check cache connection
        try:
            cache.set("health_check", "ok", 30)
            if cache.get("health_check") == "ok":
                health_status["services"]["cache"] = "healthy"
            else:
                health_status["services"]["cache"] = "unhealthy: cache test failed"
        except Exception as e:
            health_status["services"]["cache"] = f"unhealthy: {str(e)}"
        
        # Check MongoDB connection (if configured)
        try:
            from django.conf import settings
            if hasattr(settings, 'MONGODB_SETTINGS'):
                import pymongo
                client = pymongo.MongoClient(settings.MONGODB_SETTINGS['host'])
                client.admin.command('ping')
                health_status["services"]["mongodb"] = "healthy"
            else:
                health_status["services"]["mongodb"] = "not_configured"
        except Exception as e:
            health_status["services"]["mongodb"] = f"unhealthy: {str(e)}"
        
        # Determine overall status
        unhealthy_services = [k for k, v in health_status["services"].items() 
                            if v.startswith("unhealthy")]
        
        if unhealthy_services:
            health_status["status"] = "degraded"
            return JsonResponse(health_status, status=503)
        
        return JsonResponse(health_status, status=200)
        
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2026-01-13T12:00:00Z"
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check endpoint for Kubernetes/Render
    """
    try:
        # Check if application is ready to serve traffic
        from flight.models import User
        
        # Simple database query to ensure models are working
        user_count = User.objects.count()
        
        return JsonResponse({
            "status": "ready",
            "timestamp": "2026-01-13T12:00:00Z",
            "user_count": user_count
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            "status": "not_ready",
            "error": str(e),
            "timestamp": "2026-01-13T12:00:00Z"
        }, status=503)