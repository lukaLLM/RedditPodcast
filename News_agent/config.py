"""
Configuration constants and default values.
"""
from enum import Enum

# =============================================================================
# ENUMS
# =============================================================================

class TimeFilter(Enum):
    """Reddit time filter options."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"


# =============================================================================
# DEFAULT CONFIGURATIONS
# =============================================================================

DEFAULT_SUBREDDIT_CONFIG = {
    "LocalLLaMA": 10,
    "artificial": 5,
    "MachineLearning": 2,
    "OpenAI": 2,
    "AI_Agents": 2,
    "ArtificialInteligence": 5
}

DEFAULT_TIME_FILTER = TimeFilter.DAY
DEFAULT_TOP_COMMENTS = 10
DEFAULT_REPLIES_PER_COMMENT = 5
DEFAULT_MODEL = "gemini-2.5-pro"

DEFAULT_SYSTEM_PROMPT = """You are a Reddit research analyst. Analyze the provided Reddit posts and comments based on specific criteria.

Your task:
1. Topic Analysis: Identify the most interesting topics based on user-specified criteria
2. Comments: Select the best comments that add value to the discussions of topics.
3. Key Insights: Extract notable insights and trends.
4. If you find conflicting opinions, highlight them.
5. Summarize your findings and provide only URL link to posts and aggregate insights so they are not repeated multiple times in the analysis. So the final analysis is as concise and informative as possible.
"""

DEFAULT_USER_PROMPT = """Look for most insightful posts and comments that would enrich my knowledge as AI Engineer. Look for New AI models, performance benchmarks, ideas for projects, novel ideas/techniques around AI."""

# =============================================================================
# SCHEDULE CONFIGURATION
# =============================================================================

SCHEDULE_CONFIG_FILE = "schedule_config.json"
DEFAULT_SCHEDULE_HOUR = 7
DEFAULT_SCHEDULE_MINUTE = 0

# =============================================================================
# FILE PATHS
# =============================================================================

OUTPUTS_DIR = "outputs"
DATA_DIR = "data"
SCHEDULE_CONFIG_FILE = "data/schedule_config.json"