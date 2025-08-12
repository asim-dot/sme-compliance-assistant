import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

class ProductionLogger:
    """Production-grade logging system for compliance assistant"""
    
    def __init__(self, name: str = "compliance_assistant"):
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self):
        """Configure structured logging for production"""
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        self.logger.setLevel(logging.INFO)
        
        # File handler for all logs
        file_handler = logging.FileHandler(
            log_dir / f"compliance_assistant_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Custom formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_query(self, query: str, response_time: float, confidence: float, 
                  sources_count: int, success: bool = True):
        """Log query processing with structured data"""
        log_data = {
            "event_type": "query_processed",
            "query": query[:100],  # Truncate for privacy
            "response_time": response_time,
            "confidence": confidence,
            "sources_count": sources_count,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            self.logger.info(f"QUERY_SUCCESS | {json.dumps(log_data)}")
        else:
            self.logger.error(f"QUERY_FAILED | {json.dumps(log_data)}")
    
    def log_system_event(self, event: str, details: dict = None):
        """Log system events"""
        log_data = {
            "event_type": "system_event",
            "event": event,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"SYSTEM_EVENT | {json.dumps(log_data)}")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context"""
        log_data = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.error(f"ERROR | {json.dumps(log_data)}")

# Global logger instance
logger = ProductionLogger()