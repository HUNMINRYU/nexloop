from typing import Any

# Global In-Memory State
# Access should be confined to the main event loop to ensure safety without locks
PIPELINE_STATUS: dict[str, dict[str, Any]] = {}
PIPELINE_RESULTS: dict[str, dict[str, Any]] = {}
