"""
Fast log search utilities for searching structured JSON logs
"""

import os
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Generator, Tuple
from pathlib import Path

__all__ = ["LogSearcher"]

# Try to use orjson for better performance
try:
    import orjson
    USE_ORJSON = True
    
    def parse_json(line: str) -> Optional[Dict[str, Any]]:
        """Parse JSON line with orjson"""
        try:
            return orjson.loads(line.encode())
        except Exception:
            return None
    
except ImportError:
    import json
    USE_ORJSON = False
    
    def parse_json(line: str) -> Optional[Dict[str, Any]]:
        """Parse JSON line with standard json"""
        try:
            return json.loads(line)
        except Exception:
            return None


class LogSearcher:
    """
    Fast log searcher for structured JSON logs.
    
    Optimized for NDJSON format (newline-delimited JSON).
    Uses orjson when available for 3-5x better performance.
    """
    
    def __init__(self, base_log_dir: str = "logs"):
        """
        Initialize log searcher.
        
        Args:
            base_log_dir: Base directory containing log files
        """
        self.base_log_dir = Path(base_log_dir)
    
    def find_log_files(
        self,
        app_name: str,
        days_back: int = 7,
        include_rotated: bool = True
    ) -> List[Path]:
        """
        Find all log files for an app within date range.
        
        Args:
            app_name: Application name
            days_back: Number of days to look back
            include_rotated: Include rotated backup files
        
        Returns:
            List of log file paths
        """
        log_files = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Search through month directories
        app_dir = self.base_log_dir / app_name
        if not app_dir.exists():
            return log_files
        
        for month_dir in app_dir.iterdir():
            if not month_dir.is_dir():
                continue
            
            # Parse YYYY-MM from directory name
            try:
                month_date = datetime.strptime(month_dir.name, "%Y-%m")
                if month_date.date() < start_date.date() - timedelta(days=31):
                    continue  # Skip months too far back
            except ValueError:
                continue  # Skip non-date directories
            
            # Find daily log files in this month
            for log_file in month_dir.glob("*.log*"):
                # Skip rotated files if not requested
                if not include_rotated and log_file.suffix != ".log":
                    continue
                
                log_files.append(log_file)
        
        return sorted(log_files)
    
    def search_logs(
        self,
        app_name: str,
        query: str = None,
        level: Optional[str] = None,
        days_back: int = 7,
        max_results: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Search logs for matching entries.
        
        Args:
            app_name: Application name
            query: Text to search for in message
            level: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            days_back: Number of days to search back
            max_results: Maximum results to return
        
        Returns:
            List of matching log entries
        """
        log_files = self.find_log_files(app_name, days_back)
        results = []
        
        # Compile regex if query provided
        regex = None
        if query:
            regex = re.compile(query, re.IGNORECASE)
        
        for log_file in log_files:
            if len(results) >= max_results:
                break
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if len(results) >= max_results:
                        break
                    
                    # Parse JSON line
                    log_entry = parse_json(line)
                    if not log_entry:
                        continue
                    
                    # Filter by level
                    if level and log_entry.get("level") != level:
                        continue
                    
                    # Filter by query
                    if regex:
                        message = log_entry.get("message", "")
                        if not regex.search(message):
                            continue
                    
                    results.append(log_entry)
        
        return results
    
    def get_logs_by_time_range(
        self,
        app_name: str,
        start_time: datetime,
        end_time: datetime,
        level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all logs within a time range.
        
        Args:
            app_name: Application name
            start_time: Start datetime (inclusive)
            end_time: End datetime (inclusive)
            level: Filter by log level (optional)
        
        Returns:
            List of log entries in time range
        """
        # Find relevant files
        days_back = (datetime.now() - start_time).days + 1
        log_files = self.find_log_files(app_name, days_back)
        results = []
        
        start_ts = start_time.timestamp()
        end_ts = end_time.timestamp()
        
        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    log_entry = parse_json(line)
                    if not log_entry:
                        continue
                    
                    # Parse timestamp
                    timestamp_str = log_entry.get("timestamp", "")
                    try:
                        # Handle ISO format with Z suffix
                        ts_str = timestamp_str.replace('Z', '+00:00')
                        entry_time = datetime.fromisoformat(ts_str)
                        entry_ts = entry_time.timestamp()
                        
                        if not (start_ts <= entry_ts <= end_ts):
                            continue
                    except (ValueError, AttributeError):
                        continue
                    
                    # Filter by level
                    if level and log_entry.get("level") != level:
                        continue
                    
                    results.append(log_entry)
        
        return sorted(results, key=lambda x: x.get("timestamp", ""))
    
    def count_logs(
        self,
        app_name: str,
        level: Optional[str] = None,
        days_back: int = 7
    ) -> Dict[str, int]:
        """
        Count logs by level.
        
        Args:
            app_name: Application name
            level: Filter by specific level (optional)
            days_back: Number of days to count back
        
        Returns:
            Dict with level counts
        """
        log_files = self.find_log_files(app_name, days_back)
        counts: Dict[str, int] = {}
        
        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    log_entry = parse_json(line)
                    if not log_entry:
                        continue
                    
                    entry_level = log_entry.get("level", "UNKNOWN")
                    
                    if level and entry_level != level:
                        continue
                    
                    counts[entry_level] = counts.get(entry_level, 0) + 1
        
        return counts

