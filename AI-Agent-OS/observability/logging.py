"""Observability - Logging, Metrics, Tracing"""
import logging
import time
from typing import Dict, Any
from datetime import datetime
import json
import asyncio


class StructuredLogger:
    """Structured logging for better observability"""
    
    def __init__(self, name: str, log_file: str = None):
        self.logger = logging.getLogger(name)
        self.log_file = log_file
        
        # Setup handlers
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log_event(self, level: str, event: str, **kwargs):
        """Log structured event"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "metadata": kwargs
        }
        
        message = json.dumps(log_data)
        
        if level == "info":
            self.logger.info(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "debug":
            self.logger.debug(message)


class MetricsCollector:
    """Collect system metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
    
    def record_metric(self, name: str, value: float, tags: Dict = None):
        """Record metric"""
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            "value": value,
            "timestamp": time.time(),
            "tags": tags or {}
        })
        
        # Keep only last 1000 entries
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metrics(self, name: str = None) -> Dict:
        """Get metrics"""
        if name:
            return self.metrics.get(name, [])
        return self.metrics.copy()


class PerformanceTracer:
    """Trace performance of operations"""
    
    def __init__(self):
        self.traces: Dict[str, list] = {}
    
    async def trace_operation(self, op_name: str, operation, *args, **kwargs):
        """Trace operation performance"""
        start = time.time()
        
        try:
            if asyncio.iscoroutinefunction(operation):
                result = await operation(*args, **kwargs)
            else:
                result = operation(*args, **kwargs)
            
            duration = (time.time() - start) * 1000  # ms
            
            if op_name not in self.traces:
                self.traces[op_name] = []
            
            self.traces[op_name].append({
                "duration_ms": duration,
                "timestamp": time.time(),
                "success": True
            })
            
            return result
        
        except Exception as e:
            duration = (time.time() - start) * 1000
            
            if op_name not in self.traces:
                self.traces[op_name] = []
            
            self.traces[op_name].append({
                "duration_ms": duration,
                "timestamp": time.time(),
                "success": False,
                "error": str(e)
            })
            
            raise
    
    def get_stats(self, op_name: str) -> Dict:
        """Get operation statistics"""
        if op_name not in self.traces:
            return {}
        
        traces = self.traces[op_name]
        successful = [t for t in traces if t.get("success", False)]
        
        if not successful:
            return {"count": 0}
        
        durations = [t["duration_ms"] for t in successful]
        
        return {
            "count": len(traces),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "success_rate": len(successful) / len(traces)
        }
