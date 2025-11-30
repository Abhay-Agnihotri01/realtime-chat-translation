import os
from typing import Dict, Any

class ScalabilityConfig:
    """Configuration for horizontal scaling"""
    
    def __init__(self):
        self.redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        
        # Load balancing
        self.max_connections_per_worker = int(os.getenv("MAX_CONNECTIONS", "1000"))
        self.worker_count = int(os.getenv("WORKER_COUNT", "4"))
        
        # Performance thresholds
        self.max_latency_ms = int(os.getenv("MAX_LATENCY_MS", "500"))
        self.target_throughput_rps = int(os.getenv("TARGET_RPS", "100"))
    
    def get_scaling_metrics(self) -> Dict[str, Any]:
        """Return current scaling configuration"""
        return {
            "redis_enabled": self.redis_enabled,
            "max_connections_per_worker": self.max_connections_per_worker,
            "worker_count": self.worker_count,
            "max_latency_ms": self.max_latency_ms,
            "target_throughput_rps": self.target_throughput_rps
        }

config = ScalabilityConfig()