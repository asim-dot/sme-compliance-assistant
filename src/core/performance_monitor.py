import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass, asdict
import json

@dataclass
class PerformanceMetric:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    active_queries: int
    total_queries: int
    avg_response_time: float
    success_rate: float

class PerformanceMonitor:
    """Monitor system performance and query metrics"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetric] = []
        self.active_queries = 0
        self.total_queries = 0
        self.failed_queries = 0
        self.response_times: List[float] = []
        self.start_time = datetime.now()
        
        # Start background monitoring
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._collect_metrics, daemon=True)
        self.monitor_thread.start()
    
    def _collect_metrics(self):
        """Background thread to collect system metrics"""
        while self.monitoring:
            try:
                metric = PerformanceMetric(
                    timestamp=datetime.now(),
                    cpu_percent=psutil.cpu_percent(),
                    memory_percent=psutil.virtual_memory().percent,
                    active_queries=self.active_queries,
                    total_queries=self.total_queries,
                    avg_response_time=sum(self.response_times[-10:]) / max(len(self.response_times[-10:]), 1),
                    success_rate=(self.total_queries - self.failed_queries) / max(self.total_queries, 1)
                )
                
                self.metrics_history.append(metric)
                
                # Keep only last hour of metrics
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                time.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(60)
    
    def start_query(self):
        """Mark start of query processing"""
        self.active_queries += 1
        return time.time()
    
    def end_query(self, start_time: float, success: bool = True):
        """Mark end of query processing"""
        self.active_queries = max(0, self.active_queries - 1)
        self.total_queries += 1
        
        response_time = time.time() - start_time
        self.response_times.append(response_time)
        
        if not success:
            self.failed_queries += 1
        
        # Keep only last 100 response times
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
    
    def get_current_stats(self) -> Dict:
        """Get current performance statistics"""
        uptime = datetime.now() - self.start_time
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime).split('.')[0],
            "total_queries": self.total_queries,
            "failed_queries": self.failed_queries,
            "success_rate": (self.total_queries - self.failed_queries) / max(self.total_queries, 1),
            "active_queries": self.active_queries,
            "avg_response_time": sum(self.response_times[-10:]) / max(len(self.response_times[-10:]), 1),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "queries_per_minute": len([t for t in self.response_times if time.time() - t < 60]) if self.response_times else 0
        }
    
    def get_performance_history(self) -> List[Dict]:
        """Get performance metrics history"""
        return [asdict(metric) for metric in self.metrics_history[-20:]]  # Last 20 data points
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False

# Global performance monitor
performance_monitor = PerformanceMonitor()