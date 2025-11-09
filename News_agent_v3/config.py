"""
Configuration constants and default values.
"""
from enum import Enum
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
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

DEFAULT_SYSTEM_PROMPT = """You are an expert AI research analyst, tasked with filtering and summarizing Reddit discussions and email news for a AI Engineer. Your goal is to deliver a concise, insightful, and well-structured detailed report.

Your Analysis Must Focus On:

• New AI Models: Announcements, capabilities, and comparisons of new models.
• Performance Benchmarks: Discussions about model performance, hardware (GPUs, NPUs), and software.
• Project Ideas: Novel applications, open-source projects, and new tools.
• Novel AI Techniques: New methods and ideas like Cache-to-Cache communication, schema-based prompting, or efficient fine-tuning.

Required Output Structure:

For each relevant Reddit post, create a distinct section with the following format. Present the most interesting topics first.

1. Topic: Create a short, descriptive title for the main discussion in the post.

2. Key Insights:
   • Distill the most important takeaways, trends, or conflicting opinions from the post and comments into 3-5 clear, concise bullet points.
   • If there are strong conflicting opinions, present them here as a "Point/Counterpoint."

3. Most Insightful Comment:
   • Quote the single most insightful or valuable comment that best enriches an AI Engineer's knowledge.

4. Source:
   • Provide the direct URL to the information.

Tone and Style Guidelines:

• Be Concise: Use clear, direct language. Avoid filler words and long, complex sentences. The final output should be a dense summary of valuable information.
• Objective Analysis: Summarize the findings and opinions from the text without adding your own external opinions.
"""

DEFAULT_USER_PROMPT = """Analyze the following data and generate your report."""

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
SCHEDULER_DIR = "scheduler"  
SCHEDULE_CONFIG_FILE = "scheduler/schedule_config.json" 

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================

# Email credentials (optional - loaded from .env)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # App-specific password for Gmail
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))

# Validate email configuration if provided
if EMAIL_ADDRESS and EMAIL_PASSWORD:
    print(f"✅ Email configured: {EMAIL_ADDRESS}")
elif EMAIL_ADDRESS or EMAIL_PASSWORD:
    print("⚠️ Incomplete email configuration. Both EMAIL_ADDRESS and EMAIL_PASSWORD required.")

# Default email settings
DEFAULT_EMAIL_MAX_LENGTH = None  # None = no limit, or set to e.g., 10000 for 10k chars
DEFAULT_EMAIL_HOURS_BACK = 24
DEFAULT_MAX_EMAILS = 20
DEFAULT_ALLOWED_SENDERS = [
    "thebatch@deeplearning.ai",  # DeepLearning.AI Newsletter
    "newsletter@openai.com",
    "news@anthropic.com",
]

# =============================================================================
# AI GENERATION CONFIGURATION
# =============================================================================

DEFAULT_MAX_OUTPUT_TOKENS = 65535  # Maximum output length
DEFAULT_TEMPERATURE = 1.0         # Creativity (0.0-2.0)
DEFAULT_TOP_P = 0.95             # Nucleus sampling
DEFAULT_TOP_K = 64               # Top-k sampling

# Google Gemini specific settings
DEFAULT_THINKING_BUDGET = 8192   # Thinking tokens for reasoning (max 32768)

# Model-specific max output tokens Chcekced only for google
MODEL_MAX_TOKENS = {
    "gemini-2.5-pro": 65535,
    "gemini-2.5-flash": 8192,
    "openai:gpt-4o": 16384,
    "openai:gpt-4o-mini": 16384,
    "openai:gpt-5": 32768
}
# https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-pro