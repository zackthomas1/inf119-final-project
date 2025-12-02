"""
File: logging_config.py
Authors: 
    - [Zachery Thomas] ([47642149])
    - [Collin Vinh Tran] ([47304556])
    - [Jenny Thao Ly] ([83605957])
    - [Lina Nguyen] ([70703520])
Description: Provides a centralized logging configuration for the application. It sets up file and console logging with rotation, custom formatting, and helper functions to get loggers for specific components.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime

def setup_logging(
    level: str = "INFO", 
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_file_name: str = None,
    max_file_size_mb: int = 10,
    backup_count: int = 5,
    include_full_path: bool = False
):
    """
    Configure comprehensive logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        log_file_name: Custom log file name (default: ai_coder_YYYYMMDD.log)
        max_file_size_mb: Maximum size of each log file in MB
        backup_count: Number of backup log files to keep
        include_full_path: Whether to include full file path instead of just filename
    """
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if log_to_file and not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Generate log file name with timestamp if not provided
    if log_file_name is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file_name = f"ai_coder_{timestamp}.log"
    
    log_file_path = os.path.join(logs_dir, log_file_name) if log_to_file else None
    
    # Create formatters based on detail level
    if include_full_path:
        # Ultra-detailed formatter with full path
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        # Standard detailed formatter with filename only
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console formatter with filename for better debugging
        console_formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Add console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler with rotation
    if log_to_file and log_file_path:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=max_file_size_mb * 1024 * 1024,  # Convert MB to bytes
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("AI CODER APPLICATION LOGGING INITIALIZED")
    logger.info(f"Log level: {level.upper()}")
    logger.info(f"Console logging: {'ON' if log_to_console else 'OFF'}")
    logger.info(f"File logging: {'ON' if log_to_file else 'OFF'}")
    if log_to_file:
        logger.info(f"Log file: {log_file_path}")
        logger.info(f"Max file size: {max_file_size_mb} MB")
        logger.info(f"Backup count: {backup_count}")
    logger.info("=" * 60)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    Ensures consistent logging configuration across modules.
    """
    return logging.getLogger(name)

# Pre-configured loggers for different components
def get_app_logger():
    """Get logger for main application (app.py)"""
    return get_logger("ai_coder.app")

def get_orchestrator_logger():
    """Get logger for orchestrator"""
    return get_logger("ai_coder.orchestrator")

def get_mcp_client_logger():
    """Get logger for MCP client"""
    return get_logger("ai_coder.mcp_client")

def get_model_tracker_logger():
    """Get logger for model usage tracker"""
    return get_logger("ai_coder.model_tracker")

def get_planner_agent_logger():
    """Get logger for planner agent"""
    return get_logger("ai_coder.agents.planner")

def get_coder_agent_logger():
    """Get logger for coder agent (when implemented)"""
    return get_logger("ai_coder.agents.coder")

def get_tester_agent_logger():
    """Get logger for tester agent (when implemented)"""
    return get_logger("ai_coder.agents.tester")

def log_system_info():
    """Log system information for debugging purposes"""
    logger = get_logger("ai_coder.system")
    logger.info("=" * 40)
    logger.info("SYSTEM INFORMATION")
    logger.info("=" * 40)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Environment variables:")
    
    # Log relevant environment variables (but not sensitive ones)
    env_vars_to_log = ['PATH', 'PYTHONPATH', 'VIRTUAL_ENV']
    for var in env_vars_to_log:
        value = os.getenv(var, 'Not set')
        logger.info(f"  {var}: {value[:100]}..." if len(value) > 100 else f"  {var}: {value}")
    
    # Check for API key presence (but don't log the actual key)
    api_key = os.getenv('GEMINI_API_KEY')
    logger.info(f"GEMINI_API_KEY: {'Present' if api_key else 'Not set'}")
    if api_key:
        logger.info(f"API key ends with: ...{api_key[-4:]}")
    
    logger.info("=" * 40)
