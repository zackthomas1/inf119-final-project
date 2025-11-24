"""
File: model_tracker.py
Authors: 
    - [Zachery Thomas] ([47642149])
    - [Collin Vinh Tran] ([47304556])
    - [Jenny Thao Ly] ([83605957])
    - [Lina Nguyen] ([70703520])
Description: [
- Defines a utility class that tracks how often each
- model is called and how many tokens are used in total per model.
]
"""

# Defines a utility class that tracks how often each
# model is called and how many tokens are used in total per model.

from dataclasses import dataclass
from typing import Dict, Any
from logging_config import get_model_tracker_logger

logger = get_model_tracker_logger()

@dataclass
class ModelUsage:

    "Tracks statistics for a single model."
    num_api_calls: int = 0
    total_tokens: int = 0

class UsageTracker: 
    """
    UsageTracker keeps track of model usage across entire system. 
    Stores number of API calls and total tokens used by each model. 
    """

    def __init__(self) -> None:
        self._usage: Dict[str, ModelUsage] = {}
        logger.info("UsageTracker initialized")

    def record_call(self, agent_name: str, model_name: str, tokens_used: int) -> None: 
        """
        Record a single API call to `model_name` and the number of tokens used. 
        Should be called every time a model is invoked via MCP.
        """
        logger.debug(f"Recording call for model: {agent_name}, tokens: {tokens_used}")

        if agent_name not in self._usage:
            logger.info(f"First call to model: {agent_name} - creating new usage entry")
            self._usage[agent_name] = ModelUsage()

        stats = self._usage[agent_name]
        stats.num_api_calls += 1
        stats.total_tokens += tokens_used
        
        logger.info(f"Model {agent_name}: {stats.num_api_calls} calls, {stats.total_tokens} total tokens")

    def to_dict(self) -> Dict[str, Dict[str, int]]:
        """
        Convert tracked usage into JSON structure:
        {
            "model1: {"numApiCalls": int, "totalTokens": number},
            ...
        }
        """
        logger.debug(f"Converting usage data to dict for {len(self._usage)} models")
        result = {
            model_name: {
                "numApiCalls": stats.num_api_calls,
                "totalTokens": stats.total_tokens,
            }
            for model_name, stats in self._usage.items()
        }
        logger.debug(f"Generated usage dictionary: {result}")
        return result
    
    def reset(self) -> None:
        """
        Reset all usage stats. Use between different user runs.
        """
        logger.info(f"Resetting usage tracker (had {len(self._usage)} models tracked)")
        self._usage.clear()
        logger.info("Usage tracker reset completed")
    
