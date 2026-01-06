"""
Production Metrics Module

Prometheus-compatible metrics for MediAI API.
Tracks latency, throughput, cache efficiency, and resource usage.
"""

import time
import logging
import psutil
from typing import Optional
from functools import wraps

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# ==================== METRICS STORAGE ====================
# In-memory metrics (Prometheus-compatible format)

class MetricsCollector:
    """
    Collects and exposes metrics in Prometheus format.
    
    Metrics Categories:
    1. Latency - API response times
    2. Throughput - Request counts
    3. Cache - Hit/miss rates
    4. Predictions - Count by type and risk category
    5. Resources - Memory, CPU usage
    """
    
    def __init__(self):
        self.reset()
        self._start_time = time.time()
    
    def reset(self):
        """Reset all metrics"""
        # Latency metrics (histograms)
        self.request_latencies = []
        self.prediction_latencies = {"sepsis": [], "mortality": []}
        self.chat_latencies = []
        
        # Throughput metrics (counters)
        self.request_count = 0
        self.request_count_by_endpoint = {}
        self.request_count_by_status = {}
        
        # Cache metrics
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Prediction metrics
        self.prediction_count = {"sepsis": 0, "mortality": 0}
        self.prediction_by_risk = {
            "sepsis": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "mortality": {"low": 0, "medium": 0, "high": 0, "critical": 0}
        }
        
        # Chat metrics
        self.chat_sessions_created = 0
        self.chat_messages_count = 0
    
    # ==================== LATENCY ====================
    
    def record_request_latency(self, latency_ms: float, endpoint: str):
        """Record API request latency"""
        self.request_latencies.append(latency_ms)
        if len(self.request_latencies) > 10000:
            self.request_latencies = self.request_latencies[-5000:]
    
    def record_prediction_latency(self, prediction_type: str, latency_ms: float):
        """Record ML prediction latency"""
        if prediction_type in self.prediction_latencies:
            self.prediction_latencies[prediction_type].append(latency_ms)
            if len(self.prediction_latencies[prediction_type]) > 1000:
                self.prediction_latencies[prediction_type] = \
                    self.prediction_latencies[prediction_type][-500:]
    
    def record_chat_latency(self, latency_ms: float):
        """Record chat response latency"""
        self.chat_latencies.append(latency_ms)
        if len(self.chat_latencies) > 1000:
            self.chat_latencies = self.chat_latencies[-500:]
    
    # ==================== THROUGHPUT ====================
    
    def increment_request_count(self, endpoint: str, status_code: int):
        """Increment request counter"""
        self.request_count += 1
        self.request_count_by_endpoint[endpoint] = \
            self.request_count_by_endpoint.get(endpoint, 0) + 1
        status_str = str(status_code)
        self.request_count_by_status[status_str] = \
            self.request_count_by_status.get(status_str, 0) + 1
    
    # ==================== CACHE ====================
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.cache_misses += 1
    
    # ==================== PREDICTIONS ====================
    
    def record_prediction(self, prediction_type: str, risk_score: float):
        """Record prediction with risk category"""
        if prediction_type in self.prediction_count:
            self.prediction_count[prediction_type] += 1
            
            # Categorize risk
            if risk_score < 0.25:
                risk_cat = "low"
            elif risk_score < 0.50:
                risk_cat = "medium"
            elif risk_score < 0.75:
                risk_cat = "high"
            else:
                risk_cat = "critical"
            
            self.prediction_by_risk[prediction_type][risk_cat] += 1
    
    # ==================== CHAT ====================
    
    def record_chat_session(self):
        """Record new chat session"""
        self.chat_sessions_created += 1
    
    def record_chat_message(self):
        """Record chat message"""
        self.chat_messages_count += 1
    
    # ==================== COMPUTED METRICS ====================
    
    def get_latency_stats(self, latencies: list) -> dict:
        """Calculate latency statistics"""
        if not latencies:
            return {"avg": 0, "p50": 0, "p95": 0, "p99": 0, "min": 0, "max": 0}
        
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        
        return {
            "avg": sum(latencies) / n,
            "p50": sorted_lat[int(n * 0.50)],
            "p95": sorted_lat[int(n * 0.95)] if n > 20 else sorted_lat[-1],
            "p99": sorted_lat[int(n * 0.99)] if n > 100 else sorted_lat[-1],
            "min": sorted_lat[0],
            "max": sorted_lat[-1],
            "count": n
        }
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100
    
    def get_uptime_seconds(self) -> float:
        """Get API uptime in seconds"""
        return time.time() - self._start_time
    
    def get_requests_per_minute(self) -> float:
        """Calculate requests per minute"""
        uptime_minutes = self.get_uptime_seconds() / 60
        if uptime_minutes < 1:
            return self.request_count * (60 / max(self.get_uptime_seconds(), 1))
        return self.request_count / uptime_minutes
    
    # ==================== RESOURCE METRICS ====================
    
    def get_resource_metrics(self) -> dict:
        """Get current resource usage"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "memory_mb": memory_info.rss / (1024 * 1024),
                "memory_percent": process.memory_percent(),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "threads": process.num_threads(),
            }
        except Exception:
            return {
                "memory_mb": 0,
                "memory_percent": 0,
                "cpu_percent": 0,
                "threads": 0,
            }
    
    # ==================== EXPORT ====================
    
    def get_all_metrics(self) -> dict:
        """Get all metrics as dictionary"""
        return {
            "uptime_seconds": round(self.get_uptime_seconds(), 2),
            
            # Latency
            "latency": {
                "api": self.get_latency_stats(self.request_latencies),
                "prediction_sepsis": self.get_latency_stats(
                    self.prediction_latencies["sepsis"]
                ),
                "prediction_mortality": self.get_latency_stats(
                    self.prediction_latencies["mortality"]
                ),
                "chat": self.get_latency_stats(self.chat_latencies),
            },
            
            # Throughput
            "throughput": {
                "total_requests": self.request_count,
                "requests_per_minute": round(self.get_requests_per_minute(), 2),
                "by_endpoint": self.request_count_by_endpoint,
                "by_status": self.request_count_by_status,
            },
            
            # Cache
            "cache": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate_percent": round(self.get_cache_hit_rate(), 2),
            },
            
            # Predictions
            "predictions": {
                "total": self.prediction_count,
                "by_risk_category": self.prediction_by_risk,
            },
            
            # Chat
            "chat": {
                "sessions_created": self.chat_sessions_created,
                "messages_count": self.chat_messages_count,
            },
            
            # Resources
            "resources": self.get_resource_metrics(),
        }
    
    def to_prometheus_format(self) -> str:
        """Export metrics in Prometheus text format"""
        lines = []
        metrics = self.get_all_metrics()
        
        # Uptime
        lines.append(f"# HELP mediai_uptime_seconds API uptime in seconds")
        lines.append(f"# TYPE mediai_uptime_seconds gauge")
        lines.append(f"mediai_uptime_seconds {metrics['uptime_seconds']}")
        
        # Request count
        lines.append(f"# HELP mediai_requests_total Total HTTP requests")
        lines.append(f"# TYPE mediai_requests_total counter")
        lines.append(f"mediai_requests_total {metrics['throughput']['total_requests']}")
        
        # Requests per minute
        lines.append(f"# HELP mediai_requests_per_minute Current request rate")
        lines.append(f"# TYPE mediai_requests_per_minute gauge")
        lines.append(f"mediai_requests_per_minute {metrics['throughput']['requests_per_minute']}")
        
        # Request latency
        api_lat = metrics['latency']['api']
        lines.append(f"# HELP mediai_request_latency_ms Request latency in milliseconds")
        lines.append(f"# TYPE mediai_request_latency_ms gauge")
        lines.append(f'mediai_request_latency_ms{{quantile="0.5"}} {api_lat["p50"]}')
        lines.append(f'mediai_request_latency_ms{{quantile="0.95"}} {api_lat["p95"]}')
        lines.append(f'mediai_request_latency_ms{{quantile="0.99"}} {api_lat["p99"]}')
        
        # Prediction counts
        lines.append(f"# HELP mediai_predictions_total Total predictions by type")
        lines.append(f"# TYPE mediai_predictions_total counter")
        for pred_type, count in metrics['predictions']['total'].items():
            lines.append(f'mediai_predictions_total{{type="{pred_type}"}} {count}')
        
        # Prediction latency
        for pred_type in ["sepsis", "mortality"]:
            lat = metrics['latency'][f'prediction_{pred_type}']
            lines.append(f'mediai_prediction_latency_ms{{type="{pred_type}",quantile="0.5"}} {lat["p50"]}')
            lines.append(f'mediai_prediction_latency_ms{{type="{pred_type}",quantile="0.95"}} {lat["p95"]}')
        
        # Cache metrics
        lines.append(f"# HELP mediai_cache_hits_total Cache hit count")
        lines.append(f"# TYPE mediai_cache_hits_total counter")
        lines.append(f"mediai_cache_hits_total {metrics['cache']['hits']}")
        lines.append(f"# HELP mediai_cache_hit_rate Cache hit rate percentage")
        lines.append(f"# TYPE mediai_cache_hit_rate gauge")
        lines.append(f"mediai_cache_hit_rate {metrics['cache']['hit_rate_percent']}")
        
        # Resource metrics
        res = metrics['resources']
        lines.append(f"# HELP mediai_memory_mb Memory usage in MB")
        lines.append(f"# TYPE mediai_memory_mb gauge")
        lines.append(f"mediai_memory_mb {res['memory_mb']:.2f}")
        lines.append(f"# HELP mediai_cpu_percent CPU usage percentage")
        lines.append(f"# TYPE mediai_cpu_percent gauge")
        lines.append(f"mediai_cpu_percent {res['cpu_percent']:.2f}")
        
        return "\n".join(lines)


# ==================== GLOBAL INSTANCE ====================
metrics_collector = MetricsCollector()


# ==================== MIDDLEWARE ====================

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically track request metrics"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        endpoint = request.url.path
        
        # Record metrics
        metrics_collector.record_request_latency(latency_ms, endpoint)
        metrics_collector.increment_request_count(endpoint, response.status_code)
        
        # Add timing header
        response.headers["X-Response-Time"] = f"{latency_ms:.2f}ms"
        
        return response


# ==================== DECORATOR ====================

def track_prediction(prediction_type: str):
    """Decorator to track prediction latency and count"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            latency_ms = (time.time() - start_time) * 1000
            
            # Record latency
            metrics_collector.record_prediction_latency(prediction_type, latency_ms)
            
            # Record prediction with risk score (if available)
            if hasattr(result, 'risk_score'):
                metrics_collector.record_prediction(prediction_type, result.risk_score)
            
            return result
        return wrapper
    return decorator


def track_chat():
    """Decorator to track chat latency"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            latency_ms = (time.time() - start_time) * 1000
            
            metrics_collector.record_chat_latency(latency_ms)
            metrics_collector.record_chat_message()
            
            return result
        return wrapper
    return decorator


# ==================== HELPER FUNCTIONS ====================

def record_cache_hit():
    """Record a cache hit"""
    metrics_collector.record_cache_hit()


def record_cache_miss():
    """Record a cache miss"""
    metrics_collector.record_cache_miss()


def record_prediction(prediction_type: str, risk_score: float, latency_ms: float = None):
    """Record a prediction with optional latency"""
    metrics_collector.record_prediction(prediction_type, risk_score)
    if latency_ms is not None:
        metrics_collector.record_prediction_latency(prediction_type, latency_ms)


def get_metrics():
    """Get all metrics as dictionary"""
    return metrics_collector.get_all_metrics()


def get_prometheus_metrics():
    """Get metrics in Prometheus format"""
    return metrics_collector.to_prometheus_format()
