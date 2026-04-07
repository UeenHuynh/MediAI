"""
Unit tests for Metrics Module
Tests Prometheus-compatible metrics collection and export
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import time


class TestMetricsCollectorInit:
    """Tests for MetricsCollector initialization"""

    def test_init_default(self):
        """Test default initialization"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()

        assert collector.request_count == 0
        assert collector.cache_hits == 0
        assert collector.cache_misses == 0
        assert collector.request_latencies == []
        assert collector.prediction_count == {"sepsis": 0, "mortality": 0}
        assert collector._start_time > 0

    def test_reset_clears_all_metrics(self):
        """Test reset() clears all metrics"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()

        # Add some data
        collector.request_count = 100
        collector.cache_hits = 50
        collector.cache_misses = 25
        collector.request_latencies = [10, 20, 30]
        collector.prediction_count["sepsis"] = 5

        # Reset
        collector.reset()

        # Verify everything is cleared
        assert collector.request_count == 0
        assert collector.cache_hits == 0
        assert collector.cache_misses == 0
        assert collector.request_latencies == []
        assert collector.prediction_count["sepsis"] == 0


class TestLatencyRecording:
    """Tests for latency recording methods"""

    def test_record_request_latency(self):
        """Test recording request latency"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_request_latency(150.5, "/api/predictions")

        assert len(collector.request_latencies) == 1
        assert collector.request_latencies[0] == 150.5

    def test_record_request_latency_truncates_at_10000(self):
        """Test request latency list truncates at 10000 entries"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()

        # Add 10001 entries
        for i in range(10001):
            collector.record_request_latency(float(i), "/api/test")

        # Should truncate to 5000 most recent
        assert len(collector.request_latencies) == 5000
        assert collector.request_latencies[0] == 5001.0

    def test_record_prediction_latency_sepsis(self):
        """Test recording sepsis prediction latency"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_prediction_latency("sepsis", 250.8)

        assert len(collector.prediction_latencies["sepsis"]) == 1
        assert collector.prediction_latencies["sepsis"][0] == 250.8

    def test_record_prediction_latency_mortality(self):
        """Test recording mortality prediction latency"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_prediction_latency("mortality", 180.3)

        assert len(collector.prediction_latencies["mortality"]) == 1
        assert collector.prediction_latencies["mortality"][0] == 180.3

    def test_record_prediction_latency_truncates_at_1000(self):
        """Test prediction latency list truncates at 1000 entries"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()

        # Add 1001 entries
        for i in range(1001):
            collector.record_prediction_latency("sepsis", float(i))

        # Should truncate to 500 most recent
        assert len(collector.prediction_latencies["sepsis"]) == 500
        assert collector.prediction_latencies["sepsis"][0] == 501.0

    def test_record_prediction_latency_unknown_type_ignored(self):
        """Test unknown prediction type is ignored"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_prediction_latency("unknown_type", 100.0)

        # Should not raise error, just ignore
        assert "unknown_type" not in collector.prediction_latencies

    def test_record_chat_latency(self):
        """Test recording chat latency"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_chat_latency(320.5)

        assert len(collector.chat_latencies) == 1
        assert collector.chat_latencies[0] == 320.5

    def test_record_chat_latency_truncates_at_1000(self):
        """Test chat latency list truncates at 1000 entries"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()

        # Add 1001 entries
        for i in range(1001):
            collector.record_chat_latency(float(i))

        # Should truncate to 500 most recent
        assert len(collector.chat_latencies) == 500
        assert collector.chat_latencies[0] == 501.0


class TestThroughputRecording:
    """Tests for throughput recording"""

    def test_increment_request_count_basic(self):
        """Test incrementing request count"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.increment_request_count("/api/health", 200)

        assert collector.request_count == 1
        assert collector.request_count_by_endpoint["/api/health"] == 1
        assert collector.request_count_by_status["200"] == 1

    def test_increment_request_count_multiple(self):
        """Test incrementing request count multiple times"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.increment_request_count("/api/predictions", 200)
        collector.increment_request_count("/api/predictions", 200)
        collector.increment_request_count("/api/chat", 201)

        assert collector.request_count == 3
        assert collector.request_count_by_endpoint["/api/predictions"] == 2
        assert collector.request_count_by_endpoint["/api/chat"] == 1
        assert collector.request_count_by_status["200"] == 2
        assert collector.request_count_by_status["201"] == 1

    def test_increment_request_count_error_status(self):
        """Test incrementing with error status codes"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.increment_request_count("/api/bad", 400)
        collector.increment_request_count("/api/error", 500)

        assert collector.request_count_by_status["400"] == 1
        assert collector.request_count_by_status["500"] == 1


class TestCacheMetrics:
    """Tests for cache metrics"""

    def test_record_cache_hit(self):
        """Test recording cache hit"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_cache_hit()

        assert collector.cache_hits == 1
        assert collector.cache_misses == 0

    def test_record_cache_miss(self):
        """Test recording cache miss"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_cache_miss()

        assert collector.cache_hits == 0
        assert collector.cache_misses == 1

    def test_record_multiple_cache_operations(self):
        """Test recording multiple cache operations"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_cache_hit()
        collector.record_cache_hit()
        collector.record_cache_miss()
        collector.record_cache_hit()

        assert collector.cache_hits == 3
        assert collector.cache_misses == 1


class TestPredictionMetrics:
    """Tests for prediction metrics"""

    def test_record_prediction_sepsis_low_risk(self):
        """Test recording low risk sepsis prediction"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_prediction("sepsis", 0.15)  # < 0.25 = low

        assert collector.prediction_count["sepsis"] == 1
        assert collector.prediction_by_risk["sepsis"]["low"] == 1
        assert collector.prediction_by_risk["sepsis"]["medium"] == 0

    def test_record_prediction_sepsis_medium_risk(self):
        """Test recording medium risk sepsis prediction"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_prediction("sepsis", 0.35)  # 0.25-0.50 = medium

        assert collector.prediction_count["sepsis"] == 1
        assert collector.prediction_by_risk["sepsis"]["medium"] == 1

    def test_record_prediction_sepsis_high_risk(self):
        """Test recording high risk sepsis prediction"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_prediction("sepsis", 0.65)  # 0.50-0.75 = high

        assert collector.prediction_count["sepsis"] == 1
        assert collector.prediction_by_risk["sepsis"]["high"] == 1

    def test_record_prediction_sepsis_critical_risk(self):
        """Test recording critical risk sepsis prediction"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_prediction("sepsis", 0.85)  # >= 0.75 = critical

        assert collector.prediction_count["sepsis"] == 1
        assert collector.prediction_by_risk["sepsis"]["critical"] == 1

    def test_record_prediction_mortality(self):
        """Test recording mortality prediction"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_prediction("mortality", 0.45)

        assert collector.prediction_count["mortality"] == 1
        assert collector.prediction_by_risk["mortality"]["medium"] == 1

    def test_record_prediction_boundary_values(self):
        """Test risk categorization boundary values"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()

        # Exactly on boundaries
        collector.record_prediction("sepsis", 0.25)  # Should be medium
        collector.record_prediction("sepsis", 0.50)  # Should be high
        collector.record_prediction("sepsis", 0.75)  # Should be critical

        assert collector.prediction_by_risk["sepsis"]["medium"] == 1
        assert collector.prediction_by_risk["sepsis"]["high"] == 1
        assert collector.prediction_by_risk["sepsis"]["critical"] == 1

    def test_record_prediction_unknown_type_ignored(self):
        """Test unknown prediction type is ignored"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_prediction("unknown_type", 0.5)

        # Should not raise error, count stays 0
        assert collector.prediction_count.get("unknown_type", 0) == 0


class TestChatMetrics:
    """Tests for chat metrics"""

    def test_record_chat_session(self):
        """Test recording chat session"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_chat_session()

        assert collector.chat_sessions_created == 1

    def test_record_chat_message(self):
        """Test recording chat message"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_chat_message()

        assert collector.chat_messages_count == 1

    def test_record_multiple_chat_operations(self):
        """Test recording multiple chat operations"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_chat_session()
        collector.record_chat_message()
        collector.record_chat_message()
        collector.record_chat_message()
        collector.record_chat_session()

        assert collector.chat_sessions_created == 2
        assert collector.chat_messages_count == 3


class TestComputedMetrics:
    """Tests for computed metrics"""

    def test_get_latency_stats_with_data(self):
        """Test latency stats calculation with data"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        latencies = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        stats = collector.get_latency_stats(latencies)

        assert stats["avg"] == 55.0
        assert stats["p50"] == 60  # p50 is at index int(10*0.5) = 5, which is 60
        assert stats["min"] == 10
        assert stats["max"] == 100
        assert stats["count"] == 10

    def test_get_latency_stats_empty_list(self):
        """Test latency stats with empty list"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        stats = collector.get_latency_stats([])

        assert stats["avg"] == 0
        assert stats["p50"] == 0
        assert stats["p95"] == 0
        assert stats["p99"] == 0
        assert stats["min"] == 0
        assert stats["max"] == 0

    def test_get_latency_stats_single_value(self):
        """Test latency stats with single value"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        stats = collector.get_latency_stats([42.5])

        assert stats["avg"] == 42.5
        assert stats["p50"] == 42.5
        assert stats["min"] == 42.5
        assert stats["max"] == 42.5

    def test_get_cache_hit_rate_with_data(self):
        """Test cache hit rate calculation"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.cache_hits = 75
        collector.cache_misses = 25

        hit_rate = collector.get_cache_hit_rate()

        assert hit_rate == 75.0

    def test_get_cache_hit_rate_zero_total(self):
        """Test cache hit rate with no cache operations"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()

        hit_rate = collector.get_cache_hit_rate()

        assert hit_rate == 0.0

    def test_get_cache_hit_rate_all_misses(self):
        """Test cache hit rate with all misses"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.cache_misses = 100

        hit_rate = collector.get_cache_hit_rate()

        assert hit_rate == 0.0

    def test_get_uptime_seconds(self):
        """Test uptime calculation"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        time.sleep(0.1)  # Sleep for 100ms

        uptime = collector.get_uptime_seconds()

        assert uptime >= 0.1
        assert uptime < 1.0

    def test_get_requests_per_minute_with_uptime(self):
        """Test requests per minute calculation"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.request_count = 120

        # Mock uptime to 2 minutes
        with patch.object(collector, 'get_uptime_seconds', return_value=120.0):
            rpm = collector.get_requests_per_minute()

        assert rpm == 60.0  # 120 requests / 2 minutes

    def test_get_requests_per_minute_less_than_one_minute(self):
        """Test RPM calculation with uptime < 1 minute"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.request_count = 10

        # Mock uptime to 30 seconds
        with patch.object(collector, 'get_uptime_seconds', return_value=30.0):
            rpm = collector.get_requests_per_minute()

        assert rpm == 20.0  # 10 * (60/30)


class TestResourceMetrics:
    """Tests for resource metrics"""

    @patch('api.core.metrics.psutil.Process')
    def test_get_resource_metrics_success(self, mock_process_class):
        """Test successful resource metrics collection"""
        from api.core.metrics import MetricsCollector

        # Mock process and memory info
        mock_memory_info = Mock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100 MB in bytes

        mock_process = Mock()
        mock_process.memory_info.return_value = mock_memory_info
        mock_process.memory_percent.return_value = 5.5
        mock_process.cpu_percent.return_value = 25.3
        mock_process.num_threads.return_value = 8

        mock_process_class.return_value = mock_process

        collector = MetricsCollector()
        metrics = collector.get_resource_metrics()

        assert metrics["memory_mb"] == 100.0
        assert metrics["memory_percent"] == 5.5
        assert metrics["cpu_percent"] == 25.3
        assert metrics["threads"] == 8

    @patch('api.core.metrics.psutil.Process', side_effect=Exception("Process error"))
    def test_get_resource_metrics_error_handling(self, mock_process_class):
        """Test resource metrics error handling"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        metrics = collector.get_resource_metrics()

        # Should return zeros on error
        assert metrics["memory_mb"] == 0
        assert metrics["memory_percent"] == 0
        assert metrics["cpu_percent"] == 0
        assert metrics["threads"] == 0


class TestGetAllMetrics:
    """Tests for get_all_metrics() export method"""

    def test_get_all_metrics_structure(self):
        """Test get_all_metrics returns correct structure"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()

        # Add some data
        collector.record_request_latency(100.0, "/api/test")
        collector.record_prediction("sepsis", 0.3)
        collector.record_cache_hit()
        collector.increment_request_count("/api/test", 200)

        metrics = collector.get_all_metrics()

        # Check structure
        assert "uptime_seconds" in metrics
        assert "latency" in metrics
        assert "throughput" in metrics
        assert "cache" in metrics
        assert "predictions" in metrics
        assert "chat" in metrics
        assert "resources" in metrics

    def test_get_all_metrics_latency_section(self):
        """Test latency section in metrics"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_request_latency(50.0, "/api/test")
        collector.record_prediction_latency("sepsis", 100.0)

        metrics = collector.get_all_metrics()

        assert "api" in metrics["latency"]
        assert "prediction_sepsis" in metrics["latency"]
        assert "prediction_mortality" in metrics["latency"]
        assert "chat" in metrics["latency"]

    def test_get_all_metrics_cache_section(self):
        """Test cache section in metrics"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.cache_hits = 80
        collector.cache_misses = 20

        metrics = collector.get_all_metrics()

        assert metrics["cache"]["hits"] == 80
        assert metrics["cache"]["misses"] == 20
        assert metrics["cache"]["hit_rate_percent"] == 80.0


class TestPrometheusFormat:
    """Tests for Prometheus format export"""

    def test_to_prometheus_format_basic(self):
        """Test basic Prometheus format export"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.request_count = 100
        collector.cache_hits = 50

        prom_text = collector.to_prometheus_format()

        assert "mediai_uptime_seconds" in prom_text
        assert "mediai_requests_total 100" in prom_text
        assert "mediai_cache_hits_total 50" in prom_text

    def test_to_prometheus_format_includes_help_and_type(self):
        """Test Prometheus format includes HELP and TYPE lines"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        prom_text = collector.to_prometheus_format()

        assert "# HELP" in prom_text
        assert "# TYPE" in prom_text

    def test_to_prometheus_format_includes_quantiles(self):
        """Test Prometheus format includes quantile labels"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_request_latency(100.0, "/api/test")

        prom_text = collector.to_prometheus_format()

        assert 'quantile="0.5"' in prom_text
        assert 'quantile="0.95"' in prom_text
        assert 'quantile="0.99"' in prom_text

    def test_to_prometheus_format_includes_prediction_types(self):
        """Test Prometheus format includes prediction type labels"""
        from api.core.metrics import MetricsCollector

        collector = MetricsCollector()
        collector.record_prediction("sepsis", 0.5)
        collector.record_prediction("mortality", 0.3)

        prom_text = collector.to_prometheus_format()

        assert 'type="sepsis"' in prom_text
        assert 'type="mortality"' in prom_text


class TestMetricsMiddleware:
    """Tests for MetricsMiddleware"""

    @pytest.mark.asyncio
    async def test_middleware_records_metrics(self):
        """Test middleware records request metrics"""
        from api.core.metrics import MetricsMiddleware, MetricsCollector

        # Reset global collector
        collector = MetricsCollector()

        # Mock request and response
        mock_request = Mock()
        mock_request.url.path = "/api/test"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        middleware = MetricsMiddleware(app=None)

        with patch('api.core.metrics.metrics_collector', collector):
            response = await middleware.dispatch(mock_request, mock_call_next)

        assert collector.request_count == 1
        assert collector.request_count_by_endpoint["/api/test"] == 1
        assert len(collector.request_latencies) == 1

    @pytest.mark.asyncio
    async def test_middleware_adds_timing_header(self):
        """Test middleware adds X-Response-Time header"""
        from api.core.metrics import MetricsMiddleware

        mock_request = Mock()
        mock_request.url.path = "/api/test"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        middleware = MetricsMiddleware(app=None)
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert "X-Response-Time" in response.headers
        assert "ms" in response.headers["X-Response-Time"]


class TestHelperFunctions:
    """Tests for helper functions"""

    def test_record_cache_hit_function(self):
        """Test record_cache_hit() helper function"""
        from api.core.metrics import record_cache_hit, metrics_collector

        metrics_collector.reset()
        record_cache_hit()

        assert metrics_collector.cache_hits == 1

    def test_record_cache_miss_function(self):
        """Test record_cache_miss() helper function"""
        from api.core.metrics import record_cache_miss, metrics_collector

        metrics_collector.reset()
        record_cache_miss()

        assert metrics_collector.cache_misses == 1

    def test_record_prediction_function(self):
        """Test record_prediction() helper function"""
        from api.core.metrics import record_prediction, metrics_collector

        metrics_collector.reset()
        record_prediction("sepsis", 0.6)

        assert metrics_collector.prediction_count["sepsis"] == 1

    def test_record_prediction_with_latency(self):
        """Test record_prediction() with latency parameter"""
        from api.core.metrics import record_prediction, metrics_collector

        metrics_collector.reset()
        record_prediction("mortality", 0.4, latency_ms=250.0)

        assert metrics_collector.prediction_count["mortality"] == 1
        assert len(metrics_collector.prediction_latencies["mortality"]) == 1

    def test_get_metrics_function(self):
        """Test get_metrics() helper function"""
        from api.core.metrics import get_metrics, metrics_collector

        metrics_collector.reset()
        metrics_collector.request_count = 50

        metrics = get_metrics()

        assert metrics["throughput"]["total_requests"] == 50

    def test_get_prometheus_metrics_function(self):
        """Test get_prometheus_metrics() helper function"""
        from api.core.metrics import get_prometheus_metrics

        prom_text = get_prometheus_metrics()

        assert isinstance(prom_text, str)
        assert "mediai_" in prom_text
