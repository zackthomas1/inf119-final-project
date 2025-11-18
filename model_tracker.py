# Defines a utility class that tracks how often each
# model is called and how many tokens are used in total per model.

from dataclasses import dataclass
from typing import Dict, Any

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

    def record_call(self, model_name: str, tokens_used: int) -> None: 
        """
        Record a single API call to `model_name` and the number of tokens used. 
        Should be called every time a model is invoked via MCP.
        """

        if model_name not in self._usage:
            self._usage[model_name] = ModelUsage()

        stats = self._usage[model_name]
        stats.num_api_calls += 1
        stats.total_tokens += tokens_used

    def to_dict(self) -> Dict[str, Dict[str, int]]:
        """
        Convert tracked usage into JSON structure:
        {
            "model1: {"numApiCalls": int, "totalTokens": number},
            ...
        }
        """

        return {
            model_name: {
                "numApiCalls": stats.num_api_calls,
                "totalTokens": stats.total_tokens,
            }
            for model_name, stats in self._usage.items()
        }
    def reset(self) -> None:
        """
        Reset all usage stats. Use between different user runs.
        """
        self._usage.clear()
    